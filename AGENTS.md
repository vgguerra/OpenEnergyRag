# AGENTS.md

Notas para agentes de IA (Claude Code, Cursor, etc.) trabalhando no open-energy-rag.

## O que é

Assistente RAG sobre normativos do setor elétrico brasileiro (ANEEL, ONS, MME). Citation-first. Dataset público.

Documento canônico do projeto: [README.md](./README.md). Roadmap detalhado: [docs/ROADMAP.md](./docs/ROADMAP.md).

## Stack

- Python 3.12, gerenciado com [uv](https://docs.astral.sh/uv/) (não use pip).
- Backend: FastAPI + async, pydantic-settings para config.
- Vector DB: Qdrant via docker-compose.
- Embeddings: `intfloat/multilingual-e5-large` via fastembed (default). BGE-M3 não está no `TextEmbedding` do fastembed; se for testado em Phase 1, será via outra biblioteca.
- Extração: docling.
- LLM: provider abstraction (Groq default, OpenRouter / Gemini / OpenAI / Ollama configuráveis).

## Caminhos importantes

- `backend/src/api/server.py`: endpoints FastAPI.
- `backend/src/config/settings.py`: pydantic-settings, fonte única de variáveis.
- `backend/src/llm/provider.py`: abstração unificada via OpenAI-compatible.
- `backend/src/retrieval/qdrant.py`: client Qdrant + ensure_collection.
- `backend/src/retrieval/embeddings.py`: wrapper fastembed.
- `backend/src/ingestion/`: pipeline PDF → chunks (skeleton, ver Fase 0 do roadmap).
- `backend/src/eval/`: métricas e harness.
- `evals/questions.yaml`: eval set versionado.
- `data/raw/`: PDFs originais, gitignored.

## Convenções

- Sem LangChain. RAG direto e legível.
- Commits: lowercase imperative, conventional (`feat:`, `fix:`, `docs:`, `refactor:`).
- Sem `Co-Authored-By` em commits.
- Sem em-dashes no texto que vai para o repo.
- Variáveis de ambiente: declarar em `src/config/settings.py`, nunca `os.getenv` no código.
- Estrutura de chunks: levar metadata (`source`, `artigo`, `capitulo`, `page_start`) até a citação na resposta.

## Não faça

- Não comite `.env`, PDFs raw ou `qdrant_storage/`.
- Não rode `pip install`; sempre `uv add` / `uv sync`.
- Não gere eval set inteiramente por LLM; 30 perguntas curadas valem mais que 200 sintéticas.
- Não responda perguntas regulatórias interpretando os textos; o sistema só retrieve + cite.

## Pendências de Fase 0

1. Coletar 5 a 50 PDFs piloto em `data/raw/` (PRODIST + RENs).
2. Implementar `ingestion/chunker.py` (split por Artigo).
3. Implementar `ingestion/pipeline.py` (docling → chunk → embed → upsert).
4. Smoke test: ingestar 5 PDFs e fazer 1 consulta via `/ask`.
