---
title: Open Energy RAG API
emoji: ⚡
colorFrom: purple
colorTo: yellow
sdk: docker
app_port: 8000
pinned: false
license: mit
short_description: RAG over Brazilian electricity-sector normatives (PRODIST/ANEEL/ONS)
---

# Open Energy RAG API

FastAPI backend for the [Open Energy RAG](https://github.com/vgguerra/OpenEnergyRag) project. Citation-first retrieval over Brazilian electricity-sector regulations using hybrid dense (multilingual-e5-large) + sparse (BM25) search with reciprocal rank fusion.

## Endpoints

- `GET /health`: liveness probe with provider/model info
- `POST /search`: top-k chunk retrieval, no generation
- `POST /ask`: retrieval + LLM-generated answer with citations

## Required secrets

Configure under **Settings → Variables and secrets** in this Space:

| Name | Type | Example | Notes |
|---|---|---|---|
| `GROQ_API_KEY` | secret | `gsk_...` | From https://console.groq.com/keys |
| `QDRANT_URL` | variable | `https://xxx.cloud.qdrant.io:6333` | Your Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | secret | `...` | From the Qdrant Cloud dashboard |
| `CORS_ALLOWED_ORIGINS` | variable | `https://your-frontend.vercel.app` | Comma-separated; required for browser calls |

Optional overrides (env vars):

- `LLM_PROVIDER` (default `groq`), `LLM_MODEL` (default `llama-3.3-70b-versatile`)
- `EMBEDDING_MODEL` (default `intfloat/multilingual-e5-large`)
- `QDRANT_COLLECTION` (default `open-energy`)

## Notes

- First boot is slow (~2 minutes): the e5-large ONNX model (~2.5 GB) downloads to the Space's ephemeral filesystem on cold start.
- The free CPU basic tier (2 vCPU, 16 GB RAM) has enough headroom for retrieval + a single LLM forward; ingestion runs locally against the same Qdrant cluster, not on the Space.
- See the [GitHub repo](https://github.com/vgguerra/OpenEnergyRag) for the source code, benchmark and full architecture.
