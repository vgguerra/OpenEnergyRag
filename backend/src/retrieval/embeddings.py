"""Embedding wrappers.

Phase 1: dense + sparse embeddings for hybrid retrieval.

- Dense: multilingual-e5-large via fastembed. e5 is trained with asymmetric
  prefixes ("query: " / "passage: "); skipping them silently degrades recall,
  so we always apply them here.
- Sparse: BM25 via Qdrant/bm25 (also fastembed). BM25 is language-agnostic and
  exposes `passage_embed` / `query_embed` with the right weighting per side.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from fastembed import SparseTextEmbedding, TextEmbedding

from src.config import settings


_QUERY_PREFIX = "query: "
_PASSAGE_PREFIX = "passage: "

_SPARSE_MODEL = "Qdrant/bm25"

# fastembed's default (256) blows past 9 GB of RSS on CPU with e5-large on
# documents the size of the bigger PRODIST modules and gets OOM-killed.
# 16 keeps peak RSS under ~3 GB without a noticeable wall-clock cost.
_DENSE_BATCH_SIZE = 16


@dataclass(frozen=True)
class SparseVec:
    indices: list[int]
    values: list[float]


@lru_cache(maxsize=1)
def get_dense_embedder() -> TextEmbedding:
    return TextEmbedding(model_name=settings.EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def get_sparse_embedder() -> SparseTextEmbedding:
    return SparseTextEmbedding(model_name=_SPARSE_MODEL)


def embed_query(text: str) -> list[float]:
    embedder = get_dense_embedder()
    [vector] = list(embedder.embed([_QUERY_PREFIX + text]))
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    embedder = get_dense_embedder()
    prefixed = [_PASSAGE_PREFIX + t for t in texts]
    return [
        v.tolist()
        for v in embedder.embed(prefixed, batch_size=_DENSE_BATCH_SIZE, parallel=1)
    ]


def sparse_embed_query(text: str) -> SparseVec:
    embedder = get_sparse_embedder()
    [v] = list(embedder.query_embed([text]))
    return SparseVec(indices=v.indices.tolist(), values=v.values.tolist())


def sparse_embed_batch(texts: list[str]) -> list[SparseVec]:
    embedder = get_sparse_embedder()
    return [
        SparseVec(indices=v.indices.tolist(), values=v.values.tolist())
        for v in embedder.passage_embed(texts)
    ]
