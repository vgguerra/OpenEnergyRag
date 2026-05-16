"""Retrieval and generation metrics.

Retrieval:
    recall@k: fraction of queries whose gold chunk appears in top-k.
    MRR:      mean reciprocal rank of the gold chunk across queries.

Generation:
    faithfulness: implementation pending (see roadmap Fase 2).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievalSample:
    query_id: str
    retrieved_ids: list[str]
    gold_ids: list[str]


def recall_at_k(samples: list[RetrievalSample], k: int) -> float:
    if not samples:
        return 0.0
    hits = 0
    for sample in samples:
        top_k = set(sample.retrieved_ids[:k])
        if top_k & set(sample.gold_ids):
            hits += 1
    return hits / len(samples)


def mrr(samples: list[RetrievalSample]) -> float:
    if not samples:
        return 0.0
    total = 0.0
    for sample in samples:
        gold = set(sample.gold_ids)
        rank = next(
            (i + 1 for i, cid in enumerate(sample.retrieved_ids) if cid in gold),
            None,
        )
        if rank is not None:
            total += 1.0 / rank
    return total / len(samples)
