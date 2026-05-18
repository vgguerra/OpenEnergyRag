# open-energy-rag

Assistente RAG sobre normativos do setor elétrico brasileiro (PRODIST/ANEEL, ONS, MME). Cada resposta cita documento, seção e item. Dataset 100% público.

> Status: Fase 2 fechada. 12/12 PDFs ingeridos (1065 chunks), retrieval híbrido dense + sparse (RRF) ligado, benchmark publicado em [evals/results/latest.md](./evals/results/latest.md). Roadmap completo em [docs/ROADMAP.md](./docs/ROADMAP.md).

## Por que existe

1. Une duas linhas de trabalho: pesquisa acadêmica do IFSC em sistemas multi-agente para o setor elétrico e RAG híbrido em produção.
2. Domínio pouco explorado: quase nenhum repositório público faz RAG sobre regulação setorial brasileira.
3. Citation-first: sem citação, sem resposta.

## Benchmark

25 perguntas curadas, ground truth versionado em [evals/questions.yaml](./evals/questions.yaml). Ambos modos compartilham a mesma coleção Qdrant (vetor denso `e5-large` + vetor esparso `BM25` em named vectors); só muda a estratégia de busca.

| Métrica | Dense-only | Hybrid (RRF) | Δ |
|---|---|---|---|
| recall@1  | 0.720 | 0.760 | **+0.040** |
| recall@3  | 0.800 | 0.840 | **+0.040** |
| recall@5  | 0.840 | 0.880 | **+0.040** |
| recall@10 | 0.920 | **1.000** | **+0.080** |
| MRR       | 0.782 | 0.819 | **+0.037** |

Hybrid bate dense em todas as métricas. Recall@10 atinge 100% (o chunk gold aparece no top-10 de toda pergunta do eval set). Relatório completo (per-query) em [evals/results/latest.md](./evals/results/latest.md). Reproduza com `cd backend && uv run python -m src.eval.runner`.

## Stack

| Camada | Escolha |
|---|---|
| Backend | FastAPI + async |
| Vector DB | Qdrant (named vectors: dense + sparse, RRF server-side) |
| Embeddings denso | `intfloat/multilingual-e5-large` via fastembed (prefixos `query:` / `passage:` aplicados) |
| Embeddings esparso | `Qdrant/bm25` via fastembed (BM25, language-agnostic) |
| Extração de PDF | docling |
| LLM | Groq (Llama 3.3 70B) por default. OpenRouter, Gemini, OpenAI e Ollama configuráveis via `.env` |
| Observability | Langfuse (opcional) |
| Eval | harness próprio: recall@k, MRR, matching por metadata |

Decisão deliberada: sem LangChain. RAG bem feito é boilerplate pequeno; abstrair demais atrapalha entender o que o retrieval está fazendo.

## Como rodar

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

### 3. Ingerir os PDFs

Os PDFs do PRODIST e do ONS estão sob `data/raw/` (gitignored). Para repopular a coleção:

```bash
cd backend
uv run python -m src.ingestion.cli ../data/raw/*.pdf
```

A ingestão converte cada PDF via docling (cacheando o markdown em `data/processed/`), chunkifica preservando seção/item, embeda denso + esparso e faz upsert no Qdrant.

### 4. Perguntar

```bash
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Como classificar a tensão de atendimento?","top_k":4}' | jq
```

Resposta inclui `answer` (gerada pelo LLM) e `sources` (chunks usados, com metadata).

### 5. Endpoints

| Método | Endpoint | Notas |
|---|---|---|
| GET | `/health` | liveness, retorna provider + modelo ativo |
| POST | `/search` | top-k chunks; aceita `"mode": "hybrid"` (default) ou `"dense"` |
| POST | `/ask` | retrieval + geração com citação; mesmo `mode` |

### 6. Reproduzir o benchmark

```bash
cd backend
uv run python -m src.eval.runner
# relatório em evals/results/<timestamp>.md e evals/results/latest.md
```

## Estrutura

```
open-energy-rag/
├── backend/
│   ├── src/
│   │   ├── api/          FastAPI: /search, /ask, /health
│   │   ├── config/       pydantic-settings
│   │   ├── ingestion/    docling → chunker estrutural → embed → upsert
│   │   ├── retrieval/    embeddings denso + esparso, qdrant hybrid + RRF
│   │   ├── llm/          provider abstraction (Groq / OpenRouter / Gemini / OpenAI / Ollama)
│   │   └── eval/         métricas (recall@k, MRR) + runner do benchmark
│   ├── pyproject.toml
│   └── run.py
├── evals/
│   ├── questions.yaml    eval set curado (25 queries)
│   └── results/          relatórios de benchmark gerados
├── scripts/              smoke tests (docling, chunker, retrieval compare)
├── data/raw/             [gitignored] PDFs raw
├── data/processed/       [gitignored] markdowns produzidos pelo docling
├── docs/                 ROADMAP
├── docker-compose.yml    Qdrant
└── .env.example
```

## Limitações conhecidas

- Tabelas dentro de PDFs são extraídas mas o chunking estrutural não as preserva como blocos: o conteúdo entra junto do texto adjacente.
- O chunker grava apenas o primeiro item numerado de cada chunk em `metadata.item`. Itens adjacentes do glossário acabam agrupados no mesmo chunk; o ground truth do eval set se ajusta usando `items: []` quando isso acontece.
- Sem reranker no MVP. Roadmap prevê testar `bge-reranker-v2-m3` sobre o top-20 do hybrid.
- LLM responde apenas em PT-BR e segue rigorosamente o citation-first: sem informação no contexto, devolve "Não encontrei isso nos documentos indexados.".

## Licença

MIT (a definir antes do lançamento público).
