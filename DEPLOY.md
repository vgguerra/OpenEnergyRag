# Deploy

Deploy layout:

- **Frontend (Next.js)** → Vercel
- **Backend (FastAPI)** → Fly.io
- **Qdrant** → Fly.io (private network, no public IP)

The frontend's `src/app/api/ask/route.ts` is a server-side proxy that
calls `BACKEND_URL`, so the browser never touches the backend directly.

```
browser ──> Vercel (Next.js + /api/ask proxy) ──> Fly (FastAPI) ──> Fly (Qdrant private)
                                                      │
                                                      └──> Groq API (LLM)
```

## Prereqs

```bash
# Fly CLI
curl -L https://fly.io/install.sh | sh

# Vercel CLI (optional; you can also deploy via the dashboard)
npm i -g vercel

flyctl auth login
vercel login
```

You'll also need:

- A Groq API key (https://console.groq.com/keys) for the LLM
- A GitHub repo with this project pushed to `main`

## 1. Deploy Qdrant on Fly

```bash
# From the repo root.

# 1a. Create the app (won't deploy yet).
flyctl launch --config infra/qdrant/fly.toml --no-deploy --copy-config

# 1b. Create a 3 GB persistent volume in São Paulo.
flyctl volumes create qdrant_data --size 3 --region gru -a open-energy-rag-qdrant

# 1c. Generate and set a long API key (used by the backend to authenticate).
QDRANT_API_KEY=$(openssl rand -hex 32)
flyctl secrets set "QDRANT__SERVICE__API_KEY=$QDRANT_API_KEY" -a open-energy-rag-qdrant

# 1d. Deploy.
flyctl deploy --config infra/qdrant/fly.toml

# Save QDRANT_API_KEY: you'll plug it into the backend app's secrets in step 2c.
echo "Save this: $QDRANT_API_KEY"
```

Verify the app is up internally (it has no public address):

```bash
flyctl ssh console -a open-energy-rag-qdrant -C 'curl -s http://localhost:6333/healthz'
# expected: healthz check passed
```

## 2. Deploy the FastAPI backend on Fly

```bash
# 2a. Create the app.
flyctl launch --config backend/fly.toml --no-deploy --copy-config

# 2b. Create a 5 GB volume for the fastembed model cache.
flyctl volumes create fastembed_cache --size 5 --region gru -a open-energy-rag-api

# 2c. Set secrets. CORS_ALLOWED_ORIGINS is set after step 3.
flyctl secrets set \
  "GROQ_API_KEY=$YOUR_GROQ_KEY" \
  "QDRANT_API_KEY=$QDRANT_API_KEY" \
  -a open-energy-rag-api

# 2d. Deploy.
flyctl deploy --config backend/fly.toml
```

First request will be slow (~2 min): the e5-large model downloads to the
volume. After that, restarts reuse the cache.

Verify:

```bash
curl https://open-energy-rag-api.fly.dev/health
# {"status":"ok","provider":"groq","model":"llama-3.3-70b-versatile"}
```

## 3. Ingest the PDFs against the production Qdrant

Open a temporary tunnel to the private Qdrant, then run the ingestion
locally:

```bash
# In one terminal:
flyctl proxy 6333:6333 -a open-energy-rag-qdrant

# In another:
cd backend
QDRANT_URL=http://localhost:6333 \
  QDRANT_API_KEY=$QDRANT_API_KEY \
  uv run python -m src.ingestion.cli ../data/raw/*.pdf
```

Expected: ~1065 chunks across 12 PDFs (PRODIST 01-11 + ONS 1.1).

## 4. Deploy the frontend on Vercel

```bash
cd frontend

# 4a. Link the directory to a new Vercel project.
vercel link

# 4b. Set the backend URL the server-side proxy uses.
vercel env add BACKEND_URL production
# paste: https://open-energy-rag-api.fly.dev

# 4c. Deploy.
vercel --prod
```

Take note of the production URL (e.g. `https://open-energy-rag.vercel.app`).

## 5. Wire CORS so the backend accepts the frontend

```bash
flyctl secrets set \
  "CORS_ALLOWED_ORIGINS=https://open-energy-rag.vercel.app" \
  -a open-energy-rag-api
```

Strictly speaking the browser never calls the backend directly (it goes
through Vercel's `/api/ask` proxy), so CORS isn't required for the demo.
Setting it correctly is still good hygiene if you ever expose `/search`
or `/ask` directly from the browser.

## 6. Smoke-test the full stack

```bash
curl https://open-energy-rag.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"O que é tensão precária?","top_k":3}'
```

Expected: a JSON `{"answer":..., "sources":[...]}` with citations.

## Re-deploys

```bash
# Backend only:
flyctl deploy --config backend/fly.toml

# Qdrant rarely changes; only re-deploy on image upgrade:
flyctl deploy --config infra/qdrant/fly.toml

# Frontend:
cd frontend && vercel --prod
```

## Cost expectation

Rough monthly estimate at idle (auto-stop on the backend, single Qdrant
machine always-on):

- Qdrant: shared-cpu-1x / 1 GB always-on ≈ $5
- Backend: shared-cpu-2x / 4 GB auto-stop ≈ $1-3 idle, $5-15 with traffic
- Vercel: free tier covers a portfolio demo

A real expense projection requires actual traffic; Fly bills per second
of usage.

## Tearing it down

```bash
flyctl apps destroy open-energy-rag-api
flyctl apps destroy open-energy-rag-qdrant
vercel remove open-energy-rag
```

This deletes the apps and the volumes attached to them.
