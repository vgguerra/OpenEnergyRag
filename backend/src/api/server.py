"""FastAPI server for open-energy-rag.

Phase 0 surface:
    GET  /health           liveness probe
    POST /search           top-k chunk retrieval, no generation
    POST /ask              retrieval + LLM-generated answer with citations
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import settings
from src.llm.provider import Message, llm
from src.retrieval.embeddings import embed_query
from src.retrieval.qdrant import search_dense

app = FastAPI(
    title="open-energy-rag",
    description="RAG over Brazilian electricity-sector normatives (ANEEL, ONS, MME).",
    version="0.1.0",
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class SearchHit(BaseModel):
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any]


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    sources: list[SearchHit]


SYSTEM_PROMPT = """Você é um assistente especializado em regulação do setor elétrico brasileiro (ANEEL, ONS, MME).

Regras inegociáveis:
1. Responda apenas com base nos trechos fornecidos abaixo.
2. Cite a fonte (documento e artigo) em cada afirmação, no formato [doc=..., art=...].
3. Se a informação não estiver nos trechos, responda exatamente: "Não encontrei isso nos documentos indexados."
4. Nunca opine sobre interpretação regulatória. Apresente o que está escrito.
"""


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "provider": settings.LLM_PROVIDER, "model": settings.LLM_MODEL}


@app.post("/search", response_model=list[SearchHit])
async def search(req: SearchRequest) -> list[SearchHit]:
    try:
        query_vector = embed_query(req.query)
        hits = search_dense(query_vector, top_k=req.top_k)
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
    hits = await search(SearchRequest(query=req.query, top_k=req.top_k))
    if not hits:
        return AskResponse(
            answer="Não encontrei isso nos documentos indexados.",
            sources=[],
        )

    context_block = "\n\n".join(
        f"[doc={h.metadata.get('source', '?')}, art={h.metadata.get('artigo', '?')}]\n{h.text}"
        for h in hits
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
