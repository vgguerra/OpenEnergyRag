"""Run the curated eval set against dense and hybrid retrieval, then
write a Markdown benchmark report.

Usage:
    cd backend
    uv run python -m src.eval.runner

The report goes to evals/results/<timestamp>.md and the latest run is
also written as evals/results/latest.md so the README can link to it.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal

import yaml

from src.eval.metrics import (
    EvalSample,
    GoldSpec,
    RetrievedChunk,
    first_hit_rank,
    mrr,
    recall_at_k,
)
from src.retrieval.embeddings import embed_query, sparse_embed_query
from src.retrieval.qdrant import search_dense, search_hybrid

Mode = Literal["dense", "hybrid"]
TOP_K = 10
RECALL_KS = (1, 3, 5, 10)


def _load_questions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("queries") or []


def _to_golds(entries: list[dict[str, Any]]) -> list[GoldSpec]:
    return [
        GoldSpec(source=e["source"], items=tuple(str(i) for i in e.get("items") or []))
        for e in entries
    ]


def _search(query: str, mode: Mode) -> list[RetrievedChunk]:
    dense = embed_query(query)
    if mode == "hybrid":
        sparse = sparse_embed_query(query)
        hits = search_hybrid(dense, sparse, top_k=TOP_K)
    else:
        hits = search_dense(dense, top_k=TOP_K)
    return [RetrievedChunk(metadata=h.metadata) for h in hits]


def _run_mode(questions: list[dict[str, Any]], mode: Mode) -> list[EvalSample]:
    samples: list[EvalSample] = []
    for q in questions:
        retrieved = _search(q["query"], mode)
        samples.append(
            EvalSample(
                query_id=q["id"],
                retrieved=retrieved,
                golds=_to_golds(q.get("gold") or []),
            )
        )
    return samples


def _summary(samples: list[EvalSample]) -> dict[str, float]:
    return {
        **{f"recall@{k}": recall_at_k(samples, k) for k in RECALL_KS},
        "mrr": mrr(samples),
    }


def _format_markdown(
    timestamp: str,
    dense_summary: dict[str, float],
    hybrid_summary: dict[str, float],
    dense_samples: list[EvalSample],
    hybrid_samples: list[EvalSample],
) -> str:
    def cell(value: float) -> str:
        return f"{value:.3f}"

    def delta(d: float, h: float) -> str:
        diff = h - d
        sign = "+" if diff >= 0 else ""
        return f"{sign}{diff:.3f}"

    lines: list[str] = [
        f"# Retrieval benchmark — {timestamp}",
        "",
        (
            f"Eval set: {len(dense_samples)} curated queries. Both modes share "
            "the same Qdrant collection (dense e5-large + sparse BM25 named "
            "vectors); only the retrieval strategy differs."
        ),
        "",
        "## Summary",
        "",
        "| Metric | Dense-only | Hybrid (RRF) | Δ |",
        "|---|---|---|---|",
    ]
    for key in ["recall@1", "recall@3", "recall@5", "recall@10", "mrr"]:
        lines.append(
            f"| {key} | {cell(dense_summary[key])} | {cell(hybrid_summary[key])} | "
            f"{delta(dense_summary[key], hybrid_summary[key])} |"
        )

    lines += [
        "",
        "## Per-query rank of the first gold chunk (top-10 window)",
        "",
        "| Query id | Dense | Hybrid |",
        "|---|---|---|",
    ]
    for d, h in zip(dense_samples, hybrid_samples):
        dr = first_hit_rank(d)
        hr = first_hit_rank(h)
        lines.append(
            f"| {d.query_id} | {dr if dr is not None else 'miss'} | "
            f"{hr if hr is not None else 'miss'} |"
        )

    return "\n".join(lines) + "\n"


def run(
    questions_path: Path,
    results_dir: Path,
    *,
    write: bool = True,
    progress: Callable[[str], None] | None = None,
) -> Path | None:
    questions = _load_questions(questions_path)
    if not questions:
        raise SystemExit(f"No queries found in {questions_path}")
    if progress:
        progress(f"loaded {len(questions)} queries")

    if progress:
        progress("running dense retrieval...")
    dense_samples = _run_mode(questions, "dense")
    if progress:
        progress("running hybrid retrieval...")
    hybrid_samples = _run_mode(questions, "hybrid")

    dense_summary = _summary(dense_samples)
    hybrid_summary = _summary(hybrid_samples)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report = _format_markdown(
        timestamp, dense_summary, hybrid_summary, dense_samples, hybrid_samples
    )

    if not write:
        print(report)
        return None

    results_dir.mkdir(parents=True, exist_ok=True)
    slug = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    out_path = results_dir / f"{slug}.md"
    out_path.write_text(report, encoding="utf-8")
    (results_dir / "latest.md").write_text(report, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--questions",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "evals" / "questions.yaml",
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "evals" / "results",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="print report to stdout instead of writing files",
    )
    args = parser.parse_args()

    out = run(
        args.questions,
        args.results,
        write=not args.stdout,
        progress=lambda msg: print(f"[eval] {msg}"),
    )
    if out:
        print(f"[eval] report written to {out}")


if __name__ == "__main__":
    main()
