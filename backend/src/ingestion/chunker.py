"""Structural + recursive chunking for Brazilian energy-sector normatives.

Normatives have a strong hierarchy: Título → Capítulo → Seção → Artigo →
Inciso. We aim to keep each Artigo together when it fits the token budget,
and fall back to recursive splitting only when an Artigo is too large.

This module is a Phase 0 skeleton: the real implementation comes once we
inspect a handful of docling-extracted PDFs and confirm the hierarchy markers.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    metadata: dict[str, str | int | None]


def chunk_document(
    full_text: str,
    *,
    source: str,
    chunk_size_tokens: int,
    overlap_tokens: int,
) -> list[Chunk]:
    """Split a document into retrieval-sized chunks.

    metadata keys to populate when the real implementation lands:
        source, titulo, capitulo, secao, artigo, page_start, page_end
    """
    raise NotImplementedError(
        "chunk_document not implemented yet (Phase 0 follow-up)."
    )
