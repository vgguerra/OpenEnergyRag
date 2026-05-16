"""Qdrant client wrapper.

Phase 0: dense-only retrieval. Phase 1 adds sparse vectors + RRF fusion.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Iterable

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

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


def upsert_chunks(
    vectors: Iterable[list[float]],
    payloads: Iterable[dict[str, Any]],
    *,
    batch_size: int = 64,
) -> int:
    """Upsert dense vectors with payloads. Returns the number of points written."""
    client = get_client()
    buffer: list[PointStruct] = []
    written = 0
    for vector, payload in zip(vectors, payloads):
        buffer.append(
            PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload)
        )
        if len(buffer) >= batch_size:
            client.upsert(collection_name=settings.QDRANT_COLLECTION, points=buffer)
            written += len(buffer)
            buffer = []
    if buffer:
        client.upsert(collection_name=settings.QDRANT_COLLECTION, points=buffer)
        written += len(buffer)
    return written


def collection_size() -> int:
    client = get_client()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        return 0
    return client.get_collection(settings.QDRANT_COLLECTION).points_count or 0


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
