"""Embedding model wrapper.

Phase 0: dense embeddings via multilingual-e5-large (or whatever
EMBEDDING_MODEL points to) through fastembed.

e5 models are trained with asymmetric prefixes: "query: " for the user
question and "passage: " for the indexed text. Skipping the prefixes
silently degrades recall; we always apply them here so callers can stay
prefix-agnostic.
"""
from __future__ import annotations

from functools import lru_cache

from fastembed import TextEmbedding

from src.config import settings


_QUERY_PREFIX = "query: "
_PASSAGE_PREFIX = "passage: "


@lru_cache(maxsize=1)
def get_dense_embedder() -> TextEmbedding:
    return TextEmbedding(model_name=settings.EMBEDDING_MODEL)


def embed_query(text: str) -> list[float]:
    embedder = get_dense_embedder()
    [vector] = list(embedder.embed([_QUERY_PREFIX + text]))
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    embedder = get_dense_embedder()
    prefixed = [_PASSAGE_PREFIX + t for t in texts]
    return [v.tolist() for v in embedder.embed(prefixed)]
