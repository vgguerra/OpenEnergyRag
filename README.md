# open-energy-rag

Assistente RAG sobre normativos do setor elétrico brasileiro (ANEEL, ONS, MME). Cada resposta cita documento e artigo. Dataset 100% público.

> Status: Fase 0 (scaffold pronto, ingestão e retrieval ainda em construção). Roadmap completo em [docs/ROADMAP.md](./docs/ROADMAP.md).

## Por que existe

1. Une duas linhas de trabalho: pesquisa acadêmica do IFSC em sistemas multi-agente para o setor elétrico e RAG híbrido em produção.
2. Domínio pouco explorado: quase nenhum repositório público faz RAG sobre regulação setorial brasileira.
3. Citation-first: sem citação, sem resposta.

## Stack

| Camada | Escolha |
|---|---|
| Backend | FastAPI + async |
| Vector DB | Qdrant (hybrid search) |
| Embeddings | `intfloat/multilingual-e5-large` via fastembed (BGE-M3 via outra rota em Phase 1) |
| Extração de PDF | docling |
| LLM | Groq (Llama 3.3 70B) por default. OpenRouter, Gemini, OpenAI e Ollama configuráveis |
| Observability | Langfuse (opcional) |
| Eval | harness próprio: recall@k, MRR, faithfulness |

Decisão deliberada: sem LangChain. RAG bem feito é boilerplate pequeno; abstrair demais atrapalha entender o que o retrieval está fazendo.

## Como rodar (estado atual: Fase 0)

Pré-requisitos: Docker, Python 3.12, [uv](https://docs.astral.sh/uv/).

### 1. Qdrant

```bash
docker compose up -d qdrant
```

Disponível em `http://localhost:6333`.

### 2. Backend

```bash
cd backend
uv sync
cp ../.env.example ../.env
# preencher GROQ_API_KEY (ou outra) no .env

uv run python run.py
```

API em `http://localhost:8000`. Docs em `/docs`.

### 3. Endpoints disponíveis

| Método | Endpoint | Status |
|---|---|---|
| GET | `/health` | ✅ funciona |
| POST | `/search` | ✅ retorna top-k chunks (precisa de coleção ingerida) |
| POST | `/ask` | ✅ retrieval + geração (precisa de coleção ingerida e API key) |

### Para chegar em respostas reais

Falta concluir a ingestão (`backend/src/ingestion/`). Os próximos passos estão em [docs/ROADMAP.md](./docs/ROADMAP.md), seção "Fase 0".

## Estrutura

```
open-energy-rag/
├── backend/
│   ├── src/
│   │   ├── api/          FastAPI: /search, /ask, /health
│   │   ├── config/       pydantic-settings
│   │   ├── ingestion/    docling → chunk → embed → upsert (skeleton)
│   │   ├── retrieval/    Qdrant client + embeddings
│   │   ├── llm/          provider abstraction (Groq / OpenRouter / Gemini / OpenAI / Ollama)
│   │   └── eval/         métricas + runner
│   ├── pyproject.toml
│   └── run.py
├── evals/
│   ├── questions.yaml    eval set version-controlled
│   └── results/          relatórios de benchmark
├── data/raw/             [gitignored] PDFs raw
├── docs/                 ROADMAP, ARCHITECTURE
├── docker-compose.yml    Qdrant
└── .env.example
```

## Licença

MIT (a definir antes do lançamento público).
