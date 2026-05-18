"""Side-by-side comparison of dense vs hybrid retrieval.

Hits the running API at http://localhost:8000/search with mode=dense and
mode=hybrid for each query and prints the top-k for both, plus which
chunks one mode found that the other missed.

Usage:
    cd backend && uv run python ../scripts/compare_retrieval.py
"""
from __future__ import annotations

import json
import urllib.request


API = "http://localhost:8000/search"
TOP_K = 5


QUERIES: list[str] = [
    # Definitional: stresses lexical match (BM25 should shine).
    "O que é cogeração de energia segundo o PRODIST?",
    "O que significa microgeração distribuída?",
    "Definição de tensão precária",
    # Procedural / paraphrased: dense should shine.
    "Como classificar a tensão de atendimento? Quais são as faixas?",
    "Quais critérios a distribuidora usa para previsão de demanda?",
    "Quando a distribuidora pode desconectar uma unidade consumidora?",
    # Acronym-heavy: BM25 typically wins.
    "Requisitos do sistema de medição SED no SDAT",
    "Indicadores DEC e FEC: como são calculados?",
    # Open-ended: tougher for both.
    "Quais informações vão na fatura de energia elétrica?",
    "O que é um cogerador qualificado?",
]


def _search(query: str, mode: str) -> list[dict]:
    body = json.dumps({"query": query, "top_k": TOP_K, "mode": mode}).encode("utf-8")
    req = urllib.request.Request(
        API,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def _format_hit(h: dict) -> str:
    md = h.get("metadata", {})
    src = md.get("source", "?")
    item = md.get("item", "-")
    section = md.get("section", "")
    return f"{h['score']:.3f} {src} item={item} | {section[:60]}"


def _ids(hits: list[dict]) -> set[str]:
    return {h["chunk_id"] for h in hits}


def main() -> None:
    for i, query in enumerate(QUERIES, start=1):
        print(f"\n=== Q{i}: {query}")
        dense = _search(query, "dense")
        hybrid = _search(query, "hybrid")

        print("  -- dense top-5 --")
        for h in dense:
            print(f"    {_format_hit(h)}")
        print("  -- hybrid top-5 --")
        for h in hybrid:
            print(f"    {_format_hit(h)}")

        only_dense = _ids(dense) - _ids(hybrid)
        only_hybrid = _ids(hybrid) - _ids(dense)
        overlap = _ids(dense) & _ids(hybrid)
        print(
            f"  overlap={len(overlap)}/5  "
            f"only_in_dense={len(only_dense)}  "
            f"only_in_hybrid={len(only_hybrid)}"
        )


if __name__ == "__main__":
    main()
