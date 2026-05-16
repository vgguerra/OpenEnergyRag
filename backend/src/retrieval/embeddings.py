"""Embedding model wrapper.

Phase 0: dense embeddings via BGE-M3 (or whatever EMBEDDING_MODEL points to)
through fastembed. Phase 1 will use BGE-M3 sparse output as well.
"""
from __future__ import annotations

from functools import lru_cache

from fastembed import TextEmbedding

from src.config import settings


@lru_cache(maxsize=1)
def get_dense_embedder() -> TextEmbedding:
    return TextEmbedding(model_name=settings.EMBEDDING_MODEL)


def embed_query(text: str) -> list[float]:
    embedder = get_dense_embedder()
    [vector] = list(embedder.embed([text]))
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    embedder = get_dense_embedder()
    return [v.tolist() for v in embedder.embed(texts)]
