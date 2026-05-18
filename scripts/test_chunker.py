"""Run the chunker on the already-converted markdowns and inspect output.

Usage:
    cd backend && uv run python ../scripts/test_chunker.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

sys.path.insert(0, str(ROOT / "backend"))

from src.ingestion.chunker import chunk_document  # noqa: E402
from src.config import settings  # noqa: E402


def main() -> int:
    md_files = sorted(PROCESSED.glob("*.md"))
    if not md_files:
        print(f"no markdown files in {PROCESSED} — run test_docling.py first.")
        return 1

    print(f"chunk_size_tokens={settings.CHUNK_SIZE_TOKENS}  overlap={settings.CHUNK_OVERLAP_TOKENS}\n")

    for md in md_files:
        text = md.read_text(encoding="utf-8")
        chunks = chunk_document(
            text,
            source=md.stem + ".pdf",
            chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
            overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
        )

        sizes = [len(c.text) for c in chunks]
        sections = Counter(c.metadata.get("section", "(none)") for c in chunks)

        print(f"{md.name}")
        print(f"  chunks            : {len(chunks)}")
        print(f"  size chars  avg   : {round(mean(sizes)) if sizes else 0}")
        print(f"  size chars  median: {round(median(sizes)) if sizes else 0}")
        print(f"  size chars  min   : {min(sizes) if sizes else 0}")
        print(f"  size chars  max   : {max(sizes) if sizes else 0}")
        print(f"  with item number  : {sum(1 for c in chunks if 'item' in c.metadata)}")
        print(f"  top sections      :")
        for section, count in sections.most_common(5):
            print(f"    {count:3d}  {section[:80]}")
        print()

    # Show one full sample chunk from the largest file
    sample_md = max(md_files, key=lambda p: p.stat().st_size)
    sample_chunks = chunk_document(
        sample_md.read_text(encoding="utf-8"),
        source=sample_md.stem + ".pdf",
        chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
        overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
    )
    if sample_chunks:
        i = min(5, len(sample_chunks) - 1)
        c = sample_chunks[i]
        print(f"--- sample chunk {i} from {sample_md.stem} ---")
        for k, v in c.metadata.items():
            print(f"  {k}: {v}")
        print()
        print(c.text[:800])
        if len(c.text) > 800:
            print(f"... [{len(c.text) - 800} more chars]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
