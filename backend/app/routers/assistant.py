from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from ..core.config import get_settings
from ..services.ai_router import get_openrouter_models
from ..services.assistant_service import answer_message


router = APIRouter(prefix="/assistant", tags=["assistant"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=1200)
    session_id: str | None = Field(default=None, max_length=120)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        return value.strip()


class ChatResponse(BaseModel):
    answer: str
    source: str
    model_used: str
    fallback_used: bool
    rag_source: str | None = None
    rag_used: bool = False
    retrieved_chunks_count: int = 0
    saved_to_supabase: bool = False


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> dict[str, Any]:
    settings = get_settings()
    return await answer_message(
        settings,
        payload.message,
        session_id=payload.session_id or "default",
        metadata=payload.metadata,
    )


@router.post("/chat", response_model=ChatResponse, include_in_schema=False)
async def chat_legacy(payload: ChatRequest) -> dict[str, Any]:
    return await chat(payload)


@router.get("/models")
async def list_models() -> dict[str, Any]:
    settings = get_settings()
    return await get_openrouter_models(settings)
