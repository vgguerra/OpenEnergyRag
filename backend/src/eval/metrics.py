"""Retrieval metrics for the open-energy-rag benchmark.

A retrieved chunk is a hit if its metadata matches any of the gold specs
attached to the query. Each gold spec is a (source, items) tuple:
  - source: the originating PDF filename (must be exact).
  - items: optional list of item numbers; empty matches any chunk from
    that source (weaker ground truth, useful when items can't be pinned).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GoldSpec:
    source: str
    items: tuple[str, ...] = ()


@dataclass(frozen=True)
class RetrievedChunk:
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalSample:
    query_id: str
    retrieved: list[RetrievedChunk]
    golds: list[GoldSpec]


def _chunk_matches(metadata: dict[str, Any], gold: GoldSpec) -> bool:
    if metadata.get("source") != gold.source:
        return False
    if not gold.items:
        return True
    return metadata.get("item") in gold.items


def chunk_is_gold(metadata: dict[str, Any], golds: list[GoldSpec]) -> bool:
    return any(_chunk_matches(metadata, g) for g in golds)


def recall_at_k(samples: list[EvalSample], k: int) -> float:
    if not samples:
        return 0.0
    hits = sum(
        1
        for s in samples
        if any(chunk_is_gold(c.metadata, s.golds) for c in s.retrieved[:k])
    )
    return hits / len(samples)


def mrr(samples: list[EvalSample]) -> float:
    if not samples:
        return 0.0
    total = 0.0
    for s in samples:
        for rank, c in enumerate(s.retrieved, start=1):
            if chunk_is_gold(c.metadata, s.golds):
                total += 1.0 / rank
                break
    return total / len(samples)


def first_hit_rank(sample: EvalSample) -> int | None:
    """Rank (1-indexed) of the first gold chunk, or None if no gold appeared."""
    for rank, c in enumerate(sample.retrieved, start=1):
        if chunk_is_gold(c.metadata, sample.golds):
            return rank
    return None
