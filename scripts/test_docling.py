"""One-off validation: run docling on a single PDF and inspect the output.

Usage:
    cd backend && uv run python ../scripts/test_docling.py

Reads data/raw/<file>.pdf, writes data/processed/<file>.md, and prints
structural diagnostics that drive the chunker design.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter


DEFAULT_PDF = "prodist-modulo-01-glossario.pdf"
ROOT = Path(__file__).resolve().parent.parent
PDF_NAME = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
RAW = ROOT / "data" / "raw" / PDF_NAME
OUT = ROOT / "data" / "processed" / (PDF_NAME.removesuffix(".pdf") + ".md")


def main() -> int:
    if not RAW.exists():
        print(f"missing: {RAW}", file=sys.stderr)
        return 1

    from docling.document_converter import DocumentConverter

    print(f"converting {RAW.name} ...")
    t0 = perf_counter()
    converter = DocumentConverter()
    result = converter.convert(str(RAW))
    elapsed = perf_counter() - t0

    document = result.document
    markdown = document.export_to_markdown()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(markdown, encoding="utf-8")
    print(f"  wrote {OUT.relative_to(ROOT)}  ({len(markdown):,} chars, {elapsed:.1f}s)\n")

    diagnostics(markdown)

    print("\nfirst 60 lines of markdown:\n" + "-" * 64)
    for i, line in enumerate(markdown.splitlines()[:60], start=1):
        print(f"{i:>3}  {line}")

    return 0


def diagnostics(markdown: str) -> None:
    lines = markdown.splitlines()
    heading_counts = Counter()
    for line in lines:
        match = re.match(r"^(#{1,6})\s", line)
        if match:
            heading_counts[match.group(1)] += 1

    artigo_matches = re.findall(r"^Art\.\s*\d+", markdown, re.MULTILINE)
    paragrafo_matches = re.findall(r"^§\s*\d+", markdown, re.MULTILINE)
    inciso_matches = re.findall(r"^[IVX]+\s*-", markdown, re.MULTILINE)
    capitulo_matches = re.findall(r"^CAP[ÍI]TULO\s+[IVX]+", markdown, re.MULTILINE | re.IGNORECASE)
    secao_matches = re.findall(r"^Se[çc][ãa]o\s+[IVX]+", markdown, re.MULTILINE | re.IGNORECASE)

    print("structural diagnostics:")
    print(f"  total lines       : {len(lines):,}")
    print(f"  non-empty lines   : {sum(1 for l in lines if l.strip()):,}")
    print(f"  markdown headings : {dict(sorted(heading_counts.items()))}")
    print(f"  Art. NNN          : {len(artigo_matches)} occurrences")
    print(f"  § NNN             : {len(paragrafo_matches)} occurrences")
    print(f"  CAPÍTULO X        : {len(capitulo_matches)} occurrences")
    print(f"  Seção X           : {len(secao_matches)} occurrences")
    print(f"  Roman numeral I-  : {len(inciso_matches)} occurrences (likely incisos)")

    if artigo_matches:
        print(f"  first three Art.s : {artigo_matches[:3]}")


if __name__ == "__main__":
    raise SystemExit(main())
