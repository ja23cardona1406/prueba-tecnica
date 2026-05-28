import asyncio
import logging
import unicodedata
from typing import Any

from ..core.config import Settings
from .ai_router import route_chat_completion
from .rag_service import build_context, local_matches, local_rag_search
from .supabase_service import try_insert_variants


logger = logging.getLogger(__name__)


PRODUCT_CORPUS = {
    "price": "El precio referencial de lanzamiento de la Bertolli Pro 900 es $4.990.000 COP. Para cerrar compra, usa el formulario o WhatsApp para confirmar disponibilidad e instalacion.",
    "warranty": "La garantia contemplada es de 24 meses limitada por defectos de fabricacion. Requiere instalacion correcta y uso segun recomendaciones del fabricante.",
    "dimensions": "Sus dimensiones de referencia son 90 cm de ancho, 60 cm de fondo y 89 cm de alto.",
    "materials": "La Bertolli Pro 900 usa acero inoxidable cepillado, parrillas de hierro fundido, perillas metalicas y doble vidrio templado en el horno.",
    "power": "Tiene 5 quemadores con potencia combinada estimada de hasta 12,8 kW. El quemador triple corona entrega aproximadamente 3,8 kW.",
    "cleaning": "Para limpieza, usa pano suave, agua tibia y jabon neutro. Evita fibras abrasivas sobre el acero inoxidable y seca al terminar.",
    "installation": "La instalacion debe realizarla un tecnico certificado. Conviene validar ventilacion, presion de gas, espacio de 90 cm y conexion segun norma local.",
    "gas": "Puede configurarse para gas natural o GLP usando el kit de conversion correspondiente. La conversion no debe hacerse de forma casera.",
    "benefits": "Sus beneficios principales son mayor superficie de trabajo, llama potente para sellar, estabilidad con ollas pesadas, horno amplio y acabado premium para cocina abierta.",
}

RULES = [
    (("precio", "valor", "cuesta", "costo", "comprar", "cotizacion"), PRODUCT_CORPUS["price"]),
    (("garantia", "garantias", "cobertura"), PRODUCT_CORPUS["warranty"]),
    (("dimension", "dimensiones", "medida", "medidas", "tamano", "ancho", "alto", "fondo"), PRODUCT_CORPUS["dimensions"]),
    (("material", "materiales", "acero", "inoxidable", "hierro", "vidrio"), PRODUCT_CORPUS["materials"]),
    (("potencia", "kw", "quemador", "quemadores", "hornilla", "hornillas", "triple"), PRODUCT_CORPUS["power"]),
    (("limpieza", "limpiar", "grasa", "mantenimiento", "cuidar"), PRODUCT_CORPUS["cleaning"]),
    (("instalacion", "instalar", "tecnico", "conexion", "ventilacion"), PRODUCT_CORPUS["installation"]),
    (("gas", "glp", "natural", "propano", "conversion"), PRODUCT_CORPUS["gas"]),
    (("beneficio", "beneficios", "ventaja", "ventajas", "porque", "premium"), PRODUCT_CORPUS["benefits"]),
]


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def local_corpus_answer(message: str) -> str:
    normalized = normalize(message)
    matches = [answer for keys, answer in RULES if any(key in normalized for key in keys)]
    if matches:
        return " ".join(dict.fromkeys(matches))

    return (
        "Puedo ayudarte con precio, garantia, dimensiones, materiales, potencia, "
        "limpieza, instalacion, tipo de gas y beneficios de la Bertolli Pro 900. "
        "Tambien puedes dejar tus datos para recibir una cotizacion."
    )


def compact_retrieved_chunks(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chunks = []
    for match in matches:
        chunks.append(
            {
                "id": match.get("id"),
                "document_id": match.get("document_id"),
                "document_title": match.get("document_title") or match.get("title"),
                "document_source": match.get("document_source") or match.get("source"),
                "chunk_index": match.get("chunk_index"),
                "similarity": match.get("similarity"),
                "content": (match.get("content") or "")[:800],
            }
        )
    return chunks


def save_assistant_message(
    session_id: str,
    user_message: str,
    result: dict[str, Any],
    rag_used: bool,
    retrieved_chunks: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> bool:
    metadata_payload = metadata or {}
    payload = {
        "session_id": session_id,
        "user_message": user_message,
        "assistant_answer": result["answer"],
        "model_used": result["model_used"],
        "source": result["source"],
        "fallback_used": bool(result.get("fallback_used")),
        "rag_used": rag_used,
        "retrieved_chunks": len(retrieved_chunks),
        "metadata": {**metadata_payload, "retrieved_chunks": retrieved_chunks},
    }
    json_retrieved_chunks_payload = {**payload, "retrieved_chunks": retrieved_chunks}

    created, error = try_insert_variants(
        "assistant_messages",
        [payload, json_retrieved_chunks_payload],
    )
    if created is None:
        logger.error("Could not save assistant message to Supabase: %s", error)
        return False
    return True


async def answer_message(
    settings: Settings,
    message: str,
    session_id: str = "default",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rag_source = "local-corpus"
    rag_matches: list[dict[str, Any]] = []
    try:
        rag_matches = await asyncio.wait_for(
            local_rag_search(
                message,
                match_count=settings.rag_top_k,
                match_threshold=settings.rag_min_score,
            ),
            timeout=20.0,
        )
        context = build_context(rag_matches) if rag_matches else build_context(local_matches(message))
        if rag_matches and rag_matches[0].get("document_source") != "local-corpus":
            rag_source = "supabase-vector"
    except asyncio.TimeoutError:
        logger.warning("RAG search timed out (20s); using local corpus fallback.")
        rag_matches = local_matches(message)
        context = build_context(rag_matches)
    except Exception:
        logger.exception("RAG search failed; using local corpus fallback.")
        rag_matches = local_matches(message)
        context = build_context(rag_matches)

    if settings.is_openrouter_configured:
        try:
            result = await route_chat_completion(settings, message, context)
            result["rag_source"] = rag_source
            retrieved_chunks = compact_retrieved_chunks(rag_matches)
            rag_used = rag_source == "supabase-vector" and bool(retrieved_chunks)
            result["rag_used"] = rag_used
            result["retrieved_chunks_count"] = len(retrieved_chunks)
            result["saved_to_supabase"] = save_assistant_message(
                session_id=session_id,
                user_message=message,
                result=result,
                rag_used=rag_used,
                retrieved_chunks=retrieved_chunks,
                metadata=metadata,
            )
            return result
        except Exception:
            logger.exception("OpenRouter assistant failed; using local corpus fallback.")

    result = {
        "answer": local_corpus_answer(message),
        "source": "local-corpus",
        "model_used": "local-corpus",
        "fallback_used": True,
        "rag_source": rag_source,
    }
    retrieved_chunks = compact_retrieved_chunks(rag_matches)
    rag_used = rag_source == "supabase-vector" and bool(retrieved_chunks)
    result["rag_used"] = rag_used
    result["retrieved_chunks_count"] = len(retrieved_chunks)
    result["saved_to_supabase"] = save_assistant_message(
        session_id=session_id,
        user_message=message,
        result=result,
        rag_used=rag_used,
        retrieved_chunks=retrieved_chunks,
        metadata=metadata,
    )
    return result
