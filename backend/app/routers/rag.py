from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from ..core.config import get_settings
from ..services.rag_service import (
    ingest_document,
    ingest_seed_documents,
    rag_status,
    search_documents,
)


router = APIRouter(prefix="/rag", tags=["rag"])


class RagDocumentRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=180)
    text: str = Field(..., min_length=10)
    source: str = Field("manual", max_length=120)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title", "text", "source")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class RagDocumentResponse(BaseModel):
    success: bool
    source: str
    document: dict[str, Any] | None
    chunks_inserted: int
    message: str


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    match_count: int | None = Field(default=None, ge=1, le=20)
    match_threshold: float | None = Field(default=None, ge=0.0, le=1.0)

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        return value.strip()


class RagSearchResponse(BaseModel):
    success: bool
    source: str
    matches: list[dict[str, Any]]
    embedding_length: int | None = None
    threshold: float | None = None
    error: str | None = None


class RagIngestSeedRequest(BaseModel):
    force: bool = False


@router.post("/documents", response_model=RagDocumentResponse)
async def create_rag_document(payload: RagDocumentRequest) -> dict[str, Any]:
    return await ingest_document(
        title=payload.title,
        text=payload.text,
        source=payload.source,
        metadata=payload.metadata,
    )


@router.post("/search", response_model=RagSearchResponse)
async def search_rag(payload: RagSearchRequest) -> dict[str, Any]:
    settings = get_settings()
    result = await search_documents(
        payload.query,
        match_count=payload.match_count or settings.rag_top_k,
        match_threshold=payload.match_threshold
        if payload.match_threshold is not None
        else settings.rag_min_score,
    )
    return {
        "success": True,
        "source": result["source"],
        "matches": result["matches"],
        "embedding_length": result.get("embedding_length"),
        "threshold": result.get("threshold"),
        "error": result.get("error"),
    }


@router.get("/status")
async def get_rag_status() -> dict[str, Any]:
    return await rag_status()


@router.post("/ingest-seed")
async def ingest_rag_seed(payload: RagIngestSeedRequest) -> dict[str, Any]:
    return await ingest_seed_documents(force=payload.force)
