"""Qdrant client wrapper.

Phase 0: dense-only retrieval. Phase 1 adds sparse vectors + RRF fusion.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.config import settings


@dataclass
class RetrievedChunk:
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any]


_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )
    return _client


def ensure_collection(vector_size: int) -> None:
    """Create the collection if it doesn't exist. Idempotent."""
    client = get_client()
    if client.collection_exists(settings.QDRANT_COLLECTION):
        return
    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def search_dense(query_vector: list[float], top_k: int = 5) -> list[RetrievedChunk]:
    client = get_client()
    hits = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    return [
        RetrievedChunk(
            chunk_id=str(hit.id),
            score=hit.score,
            text=(hit.payload or {}).get("text", ""),
            metadata=(hit.payload or {}).get("metadata", {}),
        )
        for hit in hits
    ]
