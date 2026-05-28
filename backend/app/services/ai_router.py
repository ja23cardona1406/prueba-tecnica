import logging
from typing import Any

import httpx

from ..core.config import Settings


logger = logging.getLogger(__name__)


def chat_completions_url(settings: Settings) -> str:
    base_url = settings.openrouter_base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def openrouter_api_base_url(settings: Settings) -> str:
    base_url = settings.openrouter_base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url[: -len("/chat/completions")]
    return base_url


def build_messages(message: str, context: str | None = None) -> list[dict[str, str]]:
    system = (
        "Eres el asesor oficial de Bertolli Pro 900. Responde siempre en espanol, "
        "con tono comercial claro y sin inventar datos. Si falta informacion, "
        "invita a solicitar una cotizacion."
    )

    if context:
        system += (
            "\n\nContexto disponible del producto y documentos internos:\n"
            f"{context[:4000]}"
        )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": message},
    ]


def _extract_answer(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("OpenRouter returned no choices")

    content = choices[0].get("message", {}).get("content", "")
    if not content or not content.strip():
        raise RuntimeError("OpenRouter returned an empty answer")
    return content.strip()


async def call_openrouter(
    settings: Settings,
    model: str,
    message: str,
    context: str | None = None,
) -> str:
    if not settings.is_openrouter_configured:
        raise RuntimeError("OpenRouter is not configured")

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5500",
        "X-Title": "Bertolli Pro 900",
    }
    payload = {
        "model": model,
        "messages": build_messages(message, context),
        "temperature": settings.chat_temperature,
        "top_p": settings.chat_top_p,
        "max_tokens": settings.chat_max_tokens,
    }

    url = chat_completions_url(settings)
    timeout = max(settings.chat_timeout_ms / 1000, 1)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        if not response.is_success:
            logger.warning("OpenRouter %s error for model %s: %s", response.status_code, model, response.text[:400])
        response.raise_for_status()
        return _extract_answer(response.json())


async def get_openrouter_models(settings: Settings) -> dict[str, Any]:
    if not settings.is_openrouter_configured:
        return {"configured": False, "models": [], "message": "OpenRouter API key not configured"}

    url = f"{openrouter_api_base_url(settings)}/models"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": "http://localhost:5500",
        "X-Title": "Bertolli Pro 900",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers=headers)

    if not response.is_success:
        return {"configured": True, "status_code": response.status_code, "error": response.text[:400], "models": []}

    models = response.json().get("data", [])
    free_models = []
    for m in models:
        pricing = m.get("pricing") or {}
        model_id = m.get("id", "")
        is_free = (
            model_id.endswith(":free")
            or str(pricing.get("prompt")) in {"0", "0.0"}
            or str(pricing.get("completion")) in {"0", "0.0"}
        )
        if is_free:
            free_models.append({
                "id": model_id,
                "name": m.get("name"),
                "context_length": m.get("context_length"),
            })

    return {"configured": True, "count": len(free_models), "models": free_models}


async def route_chat_completion(
    settings: Settings,
    message: str,
    context: str | None = None,
) -> dict[str, Any]:
    if not settings.is_openrouter_configured:
        raise RuntimeError("OpenRouter is not configured")

    try:
        answer = await call_openrouter(settings, settings.chat_primary_llm, message, context)
        return {
            "answer": answer,
            "source": "openrouter",
            "model_used": settings.chat_primary_llm,
            "fallback_used": False,
        }
    except Exception as primary_error:
        logger.warning("Primary OpenRouter model failed: %s", primary_error)

    if settings.chat_use_fallback:
        try:
            answer = await call_openrouter(settings, settings.chat_fallback_llm, message, context)
            return {
                "answer": answer,
                "source": "openrouter",
                "model_used": settings.chat_fallback_llm,
                "fallback_used": True,
            }
        except Exception as fallback_error:
            logger.warning("Fallback OpenRouter model failed: %s", fallback_error)

    raise RuntimeError("OpenRouter models failed")
