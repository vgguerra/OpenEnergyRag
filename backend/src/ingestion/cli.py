"""Ingestion CLI.

Usage:
    cd backend
    uv run python -m src.ingestion.cli ../data/raw/*.pdf

Each PDF is converted, chunked, embedded and upserted to Qdrant. The
intermediate markdown is cached in data/processed/ so re-runs skip
docling.
"""
from __future__ import annotations

import sys
from pathlib import Path

from src.ingestion.pipeline import ingest_paths


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python -m src.ingestion.cli <pdf-path> [<pdf-path> ...]", file=sys.stderr)
        return 2

    paths = [Path(arg).resolve() for arg in argv]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"missing: {p}", file=sys.stderr)
        return 1

    # Convention: cache markdown alongside data/raw/ → data/processed/
    processed_dir = paths[0].parent.parent / "processed"

    print(f"ingesting {len(paths)} file(s); markdown cache: {processed_dir}\n")
    reports = ingest_paths(paths, processed_dir=processed_dir)

    total_chunks = 0
    total_vectors = 0
    for r in reports:
        print(
            f"  {r.pdf.name:48s}  chunks={r.chunk_count:4d}  vectors={r.vector_count:4d}  {r.elapsed_seconds:6.1f}s"
        )
        total_chunks += r.chunk_count
        total_vectors += r.vector_count
    print(f"\ndone: {total_chunks} chunks, {total_vectors} vectors written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
