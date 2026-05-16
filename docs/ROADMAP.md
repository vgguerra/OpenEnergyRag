# Roadmap

Este documento é a versão local-canônica do roadmap. A fonte original está em Notion ("Open Energy RAG — Roadmap"). Mantenha os dois em sincronia ao fechar fases.

## Fase 0: setup e baseline

Objetivo: repo no ar com retrieval dense-only ponta a ponta sobre 50 documentos.

- [x] Decidir nome do repo (open-energy-rag)
- [x] Scaffold da estrutura backend / evals / data / docs
- [x] Docker compose com Qdrant
- [x] Backend skeleton: FastAPI, pydantic-settings, LLM provider abstraction
- [x] Retrieval skeleton: Qdrant client wrapper + embeddings via fastembed
- [x] Eval harness skeleton: recall@k, MRR
- [ ] Coletar 5 PDFs piloto em data/raw/ (PRODIST módulo 1 + 4 RENs)
- [ ] Testar docling em 1 PDF e confirmar qualidade da extração
- [ ] Implementar chunker (split por Artigo, fallback recursivo)
- [ ] Implementar pipeline de ingestão completo
- [ ] Smoke test: ingestar 5 PDFs e consultar /ask

Critério de aceitação: pergunta "Qual a cor de fio para neutro em redes aéreas?" retorna resposta com citação correta do PRODIST.

## Fase 1: hybrid search

Objetivo: demonstrar que hybrid > dense-only.

- [ ] Adicionar BM25 sparse (named vectors no Qdrant)
- [ ] Implementar RRF (reciprocal rank fusion) entre dense e sparse
- [ ] Comparar dense vs hybrid em 10 queries manualmente
- [ ] Avaliar reranker BGE em cima dos top-20 (opcional)

Critério: recall@5 do hybrid > dense-only em pelo menos 5 pontos percentuais.

## Fase 2: avaliação publicada

Objetivo: eval set + benchmark público. É esta fase que vira diferencial no portfólio.

- [ ] Curar 30 a 50 perguntas com ground truth (em evals/questions.yaml)
- [ ] Implementar runner completo de eval
- [ ] Implementar faithfulness (resposta dentro do contexto)
- [ ] Publicar tabela de benchmark no README:
  - dense / hybrid / hybrid+rerank
  - BGE-M3 vs multilingual-e5
- [ ] Notebook reprodutível

Critério: tabela publicada com >= 30 perguntas e métricas reais.

## Fase 3: UX e polish

Objetivo: apresentável para terceiros.

- [ ] Citações ricas (link para documento + página + trecho)
- [ ] Streaming SSE
- [ ] Histórico persistido
- [ ] Frontend (Next.js, reaproveitar layout do ChatTemplate)
- [ ] README polido: GIF + diagrama + benchmark + "How to reproduce" + limitações
- [ ] Deploy público (Fly.io ou Railway)

Critério: alguém de fora roda localmente em menos de 10 minutos seguindo o README.

## Fase 4: lançamento

- [ ] Post no LinkedIn (PT + EN) com print do benchmark
- [ ] Post no blog (vgguerra.github.io)
- [ ] Submeter em r/LangChain, r/LocalLLaMA
- [ ] Topics no GitHub: rag, qdrant, langfuse, bge-m3, portuguese, aneel, electricity, regulation
- [ ] Vídeo curto (15-30s) anexo ao post

## Riscos vivos

| Risco | Mitigação |
|---|---|
| PDFs da ANEEL inconsistentes | testar pipeline em 5 PDFs piloto antes de escalar |
| Embeddings não capturam nuance | comparar BGE-M3 vs e5 vs OpenAI 3-small no eval set |
| LLM alucina em domínio regulatório | forçar citação, medir faithfulness, prompt restritivo |
| Custo OpenAI escala com deploy público | rate limit no FastAPI, cap diário de tokens |
| Scope creep (4 fins de semana viram 8) | fechar fase só quando critério de aceitação está OK |
| Tabelas em PDF mal extraídas | declarar limitação no README, fora do escopo MVP |
