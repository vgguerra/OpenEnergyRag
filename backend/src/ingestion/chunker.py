"""Structural chunker for Brazilian energy-sector normatives.

The PRODIST and Resoluções Normativas use a recurring layout in the markdown
docling produces:

    ## Seção X.Y Title
    ## Subsection title (no numbering, also a "##" heading)
    1. Numbered item
    2. ...
    ## Seção X.(Y+1) ...

Hierarchy is therefore flat at the markdown level (all "##"), but we treat
"Seção X.Y" and "Anexo Y" headings as the **main** boundary and any other
"##" as a **subsection** that hangs under the most recent main heading.

Strategy:
1. Walk lines, tracking the current (main, subsection) pair.
2. Buffer content until the estimated token count exceeds chunk_size_tokens.
3. Emit a chunk with the heading pair attached as metadata.
4. Always flush on a new main heading so a chunk never crosses Seção
   boundaries (citations stay clean).
5. Keep the last few lines as overlap into the next chunk.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
MAIN_HEADING_RE = re.compile(
    r"^(Se[çc][ãa]o|Anexo|Subm[óo]dulo)\b",
    re.IGNORECASE,
)
ITEM_RE = re.compile(r"^(\d+(?:-[A-Z])?)\.\s")


@dataclass
class Chunk:
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


def _estimate_tokens(text: str) -> int:
    """Rough proxy: ~4 chars per token. Off by a constant factor but fine for
    chunking decisions; the embedder will tokenize for real later."""
    return max(1, len(text) // 4)


def _classify(title: str) -> str:
    """Returns 'main' for Seção/Anexo/Submódulo headings, 'sub' otherwise."""
    return "main" if MAIN_HEADING_RE.match(title) else "sub"


def _first_item_number(lines: list[str]) -> str | None:
    for line in lines:
        match = ITEM_RE.match(line.strip())
        if match:
            return match.group(1)
    return None


def chunk_document(
    markdown: str,
    *,
    source: str,
    chunk_size_tokens: int = 300,
    overlap_tokens: int = 40,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    main_heading = ""
    sub_heading = ""
    buffer: list[str] = []
    buffer_tokens = 0

    def emit(*, retain_overlap: bool) -> None:
        nonlocal buffer, buffer_tokens
        text = "\n".join(buffer).strip()
        if not text:
            buffer = []
            buffer_tokens = 0
            return

        metadata: dict[str, str] = {"source": source}
        if main_heading:
            metadata["section"] = main_heading
        if sub_heading:
            metadata["subsection"] = sub_heading
        item = _first_item_number(buffer)
        if item is not None:
            metadata["item"] = item

        chunks.append(Chunk(text=text, metadata=metadata))

        if not retain_overlap:
            buffer = []
            buffer_tokens = 0
            return

        kept: list[str] = []
        kept_tokens = 0
        for line in reversed(buffer):
            t = _estimate_tokens(line)
            if kept_tokens + t > overlap_tokens:
                break
            kept.insert(0, line)
            kept_tokens += t
        buffer = kept
        buffer_tokens = kept_tokens

    for raw in markdown.splitlines():
        heading_match = HEADING_RE.match(raw)
        if heading_match:
            title = heading_match.group(2).strip()
            kind = _classify(title)
            if kind == "main":
                emit(retain_overlap=False)
                main_heading = title
                sub_heading = ""
            else:
                # Sub-heading inside the current main section.
                # Flush so the subsection title becomes a clean chunk boundary,
                # but keep the main heading association.
                emit(retain_overlap=False)
                sub_heading = title
            continue

        line_tokens = _estimate_tokens(raw)
        if buffer_tokens + line_tokens > chunk_size_tokens and buffer:
            emit(retain_overlap=True)
        buffer.append(raw)
        buffer_tokens += line_tokens

    emit(retain_overlap=False)

    # Filter chunks that are clearly noise (single line, very short).
    return [c for c in chunks if len(c.text) >= 60]


def iter_chunks(
    markdown: str,
    *,
    source: str,
    chunk_size_tokens: int = 300,
    overlap_tokens: int = 40,
) -> Iterator[Chunk]:
    yield from chunk_document(
        markdown,
        source=source,
        chunk_size_tokens=chunk_size_tokens,
        overlap_tokens=overlap_tokens,
    )
