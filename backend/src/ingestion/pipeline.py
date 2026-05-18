"""End-to-end ingestion: PDF → markdown (docling) → chunks → embeddings → Qdrant.

The CLI entry point is `backend.src.ingestion.cli`. This module exposes the
function so it can be called programmatically (tests, scripts, etc.).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import settings
from src.ingestion.chunker import chunk_document
from src.retrieval.embeddings import (
    embed_batch,
    get_dense_embedder,
    sparse_embed_batch,
)
from src.retrieval.qdrant import ensure_collection, upsert_chunks


@dataclass
class IngestionReport:
    pdf: Path
    chunk_count: int
    vector_count: int
    elapsed_seconds: float


def _vector_size() -> int:
    embedder = get_dense_embedder()
    [probe] = list(embedder.embed(["probe"]))
    return len(probe)


def ingest_pdf(pdf_path: Path, *, processed_dir: Path | None = None) -> IngestionReport:
    """Convert one PDF, chunk it, embed and upsert into Qdrant.

    If processed_dir is provided, the intermediate markdown is cached there
    so re-runs skip the (expensive) docling conversion.
    """
    from docling.document_converter import DocumentConverter
    from time import perf_counter

    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    started = perf_counter()

    markdown_cache = None
    if processed_dir is not None:
        processed_dir.mkdir(parents=True, exist_ok=True)
        markdown_cache = processed_dir / (pdf_path.stem + ".md")

    if markdown_cache and markdown_cache.exists():
        markdown = markdown_cache.read_text(encoding="utf-8")
    else:
        converter = DocumentConverter()
        markdown = converter.convert(str(pdf_path)).document.export_to_markdown()
        if markdown_cache:
            markdown_cache.write_text(markdown, encoding="utf-8")

    chunks = chunk_document(
        markdown,
        source=pdf_path.name,
        chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
        overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
    )

    if not chunks:
        return IngestionReport(pdf_path, 0, 0, perf_counter() - started)

    ensure_collection(_vector_size())

    texts = [c.text for c in chunks]
    dense = embed_batch(texts)
    sparse = sparse_embed_batch(texts)
    payloads = [
        {"text": c.text, "metadata": c.metadata}
        for c in chunks
    ]

    written = upsert_chunks(dense, sparse, payloads)

    return IngestionReport(
        pdf=pdf_path,
        chunk_count=len(chunks),
        vector_count=written,
        elapsed_seconds=perf_counter() - started,
    )


def ingest_paths(paths: list[Path], *, processed_dir: Path | None = None) -> list[IngestionReport]:
    reports: list[IngestionReport] = []
    for path in paths:
        reports.append(ingest_pdf(path, processed_dir=processed_dir))
    return reports
