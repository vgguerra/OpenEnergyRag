# Retrieval benchmark - 2026-05-18 19:19 UTC

Eval set: 25 curated queries. Both modes share the same Qdrant collection (dense e5-large + sparse BM25 named vectors); only the retrieval strategy differs.

## Summary

| Metric | Dense-only | Hybrid (RRF) | Δ |
|---|---|---|---|
| recall@1 | 0.720 | 0.760 | +0.040 |
| recall@3 | 0.800 | 0.840 | +0.040 |
| recall@5 | 0.840 | 0.880 | +0.040 |
| recall@10 | 0.920 | 1.000 | +0.080 |
| mrr | 0.782 | 0.819 | +0.037 |

## Per-query rank of the first gold chunk (top-10 window)

| Query id | Dense | Hybrid |
|---|---|---|
| def-tensao-precaria | 1 | 1 |
| def-tensao-critica | 1 | 1 |
| def-tensao-adequada | 1 | 1 |
| def-microgeracao | 2 | 1 |
| def-cogeracao | 6 | 6 |
| def-cogerador | 1 | 3 |
| def-cintilacao | 2 | 2 |
| def-tarifa | 4 | 1 |
| def-bt | 1 | 1 |
| def-drc | 1 | 1 |
| def-consumidor | miss | 9 |
| req-conexao-microgeracao | 1 | 1 |
| req-tp-trifasico | 1 | 1 |
| req-medicao-perdas-sed | 1 | 1 |
| req-previsao-demanda | 1 | 1 |
| req-cadastro-central-geradora | 1 | 1 |
| exc-tp-tipo-v | miss | 4 |
| exc-desconexao-microgeracao | 1 | 1 |
| calc-dec-fec | 7 | 9 |
| calc-perdas-tecnicas | 1 | 1 |
| info-bdgd | 1 | 1 |
| info-fatura | 1 | 1 |
| info-ressarcimento | 1 | 1 |
| info-intervencoes | 1 | 1 |
| info-ons | 1 | 1 |
