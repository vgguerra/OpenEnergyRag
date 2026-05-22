# Deploy

Production stack, all free tier, **no credit card required**:

- **Frontend (Next.js)** → Vercel
- **Backend (FastAPI)** → Hugging Face Spaces (Docker, CPU basic, 2 vCPU / 16 GB RAM)
- **Qdrant** → Qdrant Cloud (1 GB cluster free forever)
- **LLM** → Groq API (Llama 3.3 70B, generous free quota)

The frontend's `src/app/api/ask/route.ts` is a server-side proxy that calls `BACKEND_URL`, so the browser never touches the backend directly.

```
browser ──> Vercel (Next.js + /api/ask proxy) ──> HF Spaces (FastAPI) ──> Qdrant Cloud
                                                       │
                                                       └──> Groq API (LLM)
```

## Prereqs

Accounts (no card needed for any of them):

- [GitHub](https://github.com) (host the source code)
- [Hugging Face](https://huggingface.co) (host the backend)
- [Qdrant Cloud](https://cloud.qdrant.io) (host the vector store)
- [Vercel](https://vercel.com) (host the frontend)
- [Groq](https://console.groq.com/keys) (LLM API key)

Local tools:

```bash
# Vercel CLI (optional; you can also deploy via the dashboard)
npm i -g vercel
vercel login
```

## 1. Provision Qdrant Cloud

1. Sign in at https://cloud.qdrant.io (Google/GitHub OAuth, no card).
2. **Clusters → Create cluster** → pick the free tier (1 GB, 0.5 vCPU, AWS, region close to you).
3. After it boots (~1 min), open the cluster and copy:
   - **Cluster URL** (looks like `https://abc-def.eu-central.aws.cloud.qdrant.io:6333`)
   - **API key** (under "API keys" → "Create API key")

Save both: they go into the backend's secrets in step 2.

## 2. Deploy the FastAPI backend on Hugging Face Spaces

### 2a. Create the Space

1. Go to https://huggingface.co/new-space.
2. Settings:
   - **Owner**: your username (e.g., `vgguerra`)
   - **Space name**: `open-energy-rag-api`
   - **License**: MIT (or whatever you prefer)
   - **Space SDK**: **Docker** (blank template is fine)
   - **Space hardware**: **CPU basic · 2 vCPU · 16 GB · FREE**
   - **Visibility**: Public
3. Create.

### 2b. Push the backend code

The HF Space is its own git repo. Clone it as a **sibling** of the main repo so the source-of-truth stays on GitHub:

```bash
HF_USER=vgguerra            # change to your HF username
SPACE_NAME=open-energy-rag-api

cd ~/portfolio
git clone "https://huggingface.co/spaces/$HF_USER/$SPACE_NAME" oer-hf-space
cd oer-hf-space

# Copy the backend code into the Space repo. The HF Space's root must
# contain the Dockerfile, pyproject.toml, src/, etc.
rsync -av --delete \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='.venv' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='qdrant_storage' \
  --exclude='.fastembed_cache' \
  --exclude='.hf_cache' \
  ../open-energy-rag/backend/ .

# Use the HF-specific README that includes the YAML frontmatter the
# Space metadata needs.
mv huggingface-README.md README.md

git add .
git commit -m "initial deploy"
git push
```

The push triggers the build. It takes ~5 min the first time (installs deps, no model download yet).

### 2c. Set secrets in the Space

Go to your Space → **Settings → Variables and secrets** and add:

| Name | Type | Value |
|---|---|---|
| `GROQ_API_KEY` | secret | from https://console.groq.com/keys |
| `QDRANT_URL` | variable | the Qdrant Cloud URL from step 1 |
| `QDRANT_API_KEY` | secret | from the Qdrant Cloud dashboard |

`CORS_ALLOWED_ORIGINS` comes after step 4 once Vercel gives you a URL.

Changing secrets restarts the Space automatically.

### 2d. Smoke test

The first request triggers the e5-large download (~2 min the first time):

```bash
curl "https://$HF_USER-$SPACE_NAME.hf.space/health"
# {"status":"ok","provider":"groq","model":"llama-3.3-70b-versatile"}
```

## 3. Ingest the PDFs against Qdrant Cloud

Ingestion runs locally (faster, no resource limits) and writes to the cloud cluster:

```bash
cd open-energy-rag/backend

QDRANT_URL=https://abc-def.eu-central.aws.cloud.qdrant.io:6333 \
QDRANT_API_KEY=<the key from step 1> \
  uv run python -m src.ingestion.cli ../data/raw/*.pdf
```

Expected: ~1065 chunks across 12 PDFs (PRODIST 01-11 + ONS 1.1).

Verify the cloud has the chunks:

```bash
curl -H "api-key: $QDRANT_API_KEY" \
  "$QDRANT_URL/collections/open-energy" | python3 -m json.tool
```

## 4. Deploy the frontend on Vercel

```bash
cd open-energy-rag/frontend

vercel link
vercel env add BACKEND_URL production
# paste: https://<hf-username>-open-energy-rag-api.hf.space

vercel --prod
```

Note the production URL (e.g., `https://open-energy-rag.vercel.app`).

## 5. Wire CORS

Strictly speaking the browser never calls the backend directly (it goes through Vercel's `/api/ask` proxy), so CORS is not required. Set it anyway for hygiene if you ever expose `/search` or `/ask` from the browser:

Back in the HF Space settings → Variables and secrets → add:

| Name | Type | Value |
|---|---|---|
| `CORS_ALLOWED_ORIGINS` | variable | `https://open-energy-rag.vercel.app` |

## 6. Smoke-test the full stack

```bash
curl https://open-energy-rag.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"O que é tensão precária?","top_k":3}'
```

Expected: a JSON `{"answer":..., "sources":[...]}` with citations to PRODIST module 01.

## Re-deploys

```bash
# Backend (sync from main repo, push to HF):
cd ~/portfolio/oer-hf-space
rsync -av --delete \
  --exclude='__pycache__' --exclude='.venv' --exclude='.env' \
  --exclude='qdrant_storage' --exclude='.fastembed_cache' --exclude='.hf_cache' \
  --exclude='README.md' --exclude='.git' \
  ../open-energy-rag/backend/ .
git add . && git commit -m "deploy: sync" && git push

# Frontend:
cd open-energy-rag/frontend && vercel --prod
```

## Free-tier limits to know about

- **HF Spaces CPU basic**: 2 vCPU, 16 GB RAM, ephemeral filesystem. Sleeps after ~48 h of inactivity; first call after sleep is slow (~30-60 s) because the e5-large model must download again.
- **Qdrant Cloud free cluster**: 1 GB, single node, no SLA. 1065 chunks × ~2 KB each ≈ 2 MB, so this fits comfortably.
- **Vercel**: 100 GB-hours of serverless compute / month on the Hobby plan. The `/api/ask` proxy is well within that.
- **Groq**: free tier has rate limits (RPM and TPM), no daily token cap. Generous for a portfolio demo.

## Tearing it down

- HF: open the Space → Settings → "Delete Space"
- Qdrant Cloud: dashboard → cluster → Delete
- Vercel: dashboard → project → Settings → Delete Project
- Groq: revoke the API key at https://console.groq.com/keys

No bills to cancel, no recurring charges. Everything stops on delete.
