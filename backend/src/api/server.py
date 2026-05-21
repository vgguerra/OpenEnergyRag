"""FastAPI server for open-energy-rag.

Phase 0 surface:
    GET  /health           liveness probe
    POST /search           top-k chunk retrieval, no generation
    POST /ask              retrieval + LLM-generated answer with citations
"""
from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import settings
from src.llm.provider import Message, llm
from src.retrieval.embeddings import embed_query, sparse_embed_query
from src.retrieval.qdrant import search_dense, search_hybrid

app = FastAPI(
    title="open-energy-rag",
    description="RAG over Brazilian electricity-sector normatives (ANEEL, ONS, MME).",
    version="0.1.0",
)

_allowed_origins = [
    origin.strip()
    for origin in settings.CORS_ALLOWED_ORIGINS.split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins or ["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


RetrievalMode = Literal["hybrid", "dense"]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)
    mode: RetrievalMode = "hybrid"


class SearchHit(BaseModel):
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any]


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)
    mode: RetrievalMode = "hybrid"


class AskResponse(BaseModel):
    answer: str
    sources: list[SearchHit]


SYSTEM_PROMPT = """Você é um assistente especializado em regulação do setor elétrico brasileiro (ANEEL, ONS, MME).

Regras inegociáveis:
1. Responda apenas com base nos trechos fornecidos abaixo.
2. Cite a fonte ao final de cada afirmação, exatamente como vem no cabeçalho do trecho, entre colchetes.
3. Se a informação não estiver nos trechos, responda exatamente: "Não encontrei isso nos documentos indexados."
4. Nunca opine sobre interpretação regulatória. Apresente o que está escrito.
"""


def _format_citation(metadata: dict[str, Any]) -> str:
    parts: list[str] = []
    source = metadata.get("source")
    if source:
        parts.append(f"doc={source}")
    section = metadata.get("section")
    if section:
        parts.append(f"seção={section}")
    subsection = metadata.get("subsection")
    if subsection:
        parts.append(f"subseção={subsection}")
    item = metadata.get("item")
    if item:
        parts.append(f"item={item}")
    return "[" + ", ".join(parts) + "]" if parts else "[?]"


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "provider": settings.LLM_PROVIDER, "model": settings.LLM_MODEL}


@app.post("/search", response_model=list[SearchHit])
async def search(req: SearchRequest) -> list[SearchHit]:
    try:
        dense = embed_query(req.query)
        if req.mode == "hybrid":
            sparse = sparse_embed_query(req.query)
            hits = search_hybrid(dense, sparse, top_k=req.top_k)
        else:
            hits = search_dense(dense, top_k=req.top_k)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Retrieval failure: {exc}") from exc

    return [
        SearchHit(
            chunk_id=hit.chunk_id,
            score=hit.score,
            text=hit.text,
            metadata=hit.metadata,
        )
        for hit in hits
    ]


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    hits = await search(SearchRequest(query=req.query, top_k=req.top_k, mode=req.mode))
    if not hits:
        return AskResponse(
            answer="Não encontrei isso nos documentos indexados.",
            sources=[],
        )

    context_block = "\n\n".join(
        f"{_format_citation(h.metadata)}\n{h.text}" for h in hits
    )
    user_message = f"Pergunta: {req.query}\n\nTrechos disponíveis:\n{context_block}"

    answer = await llm.chat(
        [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=user_message),
        ],
        temperature=0.1,
        max_tokens=800,
    )
    return AskResponse(answer=answer, sources=hits)
