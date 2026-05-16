"""Eval harness entry point.

Reads evals/questions.yaml, runs each query through retrieval, computes
recall@1/5/10 and MRR, and writes a JSON report to evals/results/.

Phase 0 skeleton: real implementation lands when we have a real eval set
and ingested data.
"""
from __future__ import annotations


def run_eval(eval_path: str, output_dir: str) -> dict:
    raise NotImplementedError(
        "run_eval not implemented yet (Phase 2 deliverable)."
    )
