"""End-to-end ingestion: PDF → chunks → embeddings → Qdrant upsert.

CLI entry point lives at scripts/ingest.py. This module just exposes the
function so it can be called programmatically too.
"""
from __future__ import annotations

from pathlib import Path


def ingest_path(path: Path) -> int:
    """Ingest a single PDF (or a directory of PDFs) into Qdrant.

    Returns the number of chunks indexed.
    Phase 0 skeleton: real implementation depends on docling validation.
    """
    raise NotImplementedError(
        "ingest_path not implemented yet (Phase 0 follow-up)."
    )
