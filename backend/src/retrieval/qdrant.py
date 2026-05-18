"""Qdrant client wrapper.

Phase 1: named vectors with dense (e5) + sparse (BM25), retrieved via
Reciprocal Rank Fusion (RRF). Each point carries both vectors under the
names "dense" and "sparse"; queries prefetch both and Qdrant fuses the
ranks server-side.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Fusion,
    FusionQuery,
    PointStruct,
    Prefetch,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from src.config import settings
from src.retrieval.embeddings import SparseVec

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


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


def ensure_collection(dense_size: int) -> None:
    """Create the named-vector collection if missing. Idempotent."""
    client = get_client()
    if client.collection_exists(settings.QDRANT_COLLECTION):
        return
    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config={
            DENSE_VECTOR_NAME: VectorParams(size=dense_size, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            SPARSE_VECTOR_NAME: SparseVectorParams(),
        },
    )


def upsert_chunks(
    dense_vectors: Iterable[list[float]],
    sparse_vectors: Iterable[SparseVec],
    payloads: Iterable[dict[str, Any]],
    *,
    batch_size: int = 64,
) -> int:
    """Upsert dense + sparse vectors with payloads.

    Returns the number of points written.
    """
    client = get_client()
    buffer: list[PointStruct] = []
    written = 0
    for dense, sparse, payload in zip(dense_vectors, sparse_vectors, payloads):
        buffer.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    DENSE_VECTOR_NAME: dense,
                    SPARSE_VECTOR_NAME: SparseVector(
                        indices=sparse.indices, values=sparse.values
                    ),
                },
                payload=payload,
            )
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


def _to_chunks(points: Sequence[Any]) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk_id=str(p.id),
            score=p.score,
            text=(p.payload or {}).get("text", ""),
            metadata=(p.payload or {}).get("metadata", {}),
        )
        for p in points
    ]


def search_dense(query_vector: list[float], top_k: int = 5) -> list[RetrievedChunk]:
    """Dense-only retrieval. Kept for benchmarking against hybrid."""
    client = get_client()
    hits = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        using=DENSE_VECTOR_NAME,
        limit=top_k,
        with_payload=True,
    ).points
    return _to_chunks(hits)


def search_hybrid(
    dense_vector: list[float],
    sparse_vector: SparseVec,
    *,
    top_k: int = 5,
    prefetch_limit: int = 20,
) -> list[RetrievedChunk]:
    """Hybrid retrieval: prefetch dense + sparse top-N each, fuse with RRF."""
    client = get_client()
    hits = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        prefetch=[
            Prefetch(
                query=dense_vector,
                using=DENSE_VECTOR_NAME,
                limit=prefetch_limit,
            ),
            Prefetch(
                query=SparseVector(
                    indices=sparse_vector.indices, values=sparse_vector.values
                ),
                using=SPARSE_VECTOR_NAME,
                limit=prefetch_limit,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
        with_payload=True,
    ).points
    return _to_chunks(hits)
