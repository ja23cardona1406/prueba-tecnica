from functools import lru_cache
import logging
from typing import Any

from ..core.config import get_settings


logger = logging.getLogger(__name__)


@lru_cache
def get_supabase_client() -> Any | None:
    settings = get_settings()
    if not settings.is_supabase_configured:
        return None
    if settings.supabase_url.startswith(("postgres://", "postgresql://")):
        logger.error("SUPABASE_URL must be the Supabase project URL, not a Postgres connection string.")
        return None

    try:
        from supabase import create_client
    except ImportError:
        logger.exception("Supabase package is not installed.")
        return None

    try:
        return create_client(settings.supabase_url, settings.supabase_service_role_key)
    except Exception:
        logger.exception("Could not create Supabase client.")
        return None


def is_supabase_available() -> bool:
    return get_supabase_client() is not None


def insert_row(table: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        return None

    try:
        result = client.table(table).insert(payload).execute()
        if result.data:
            return result.data[0]
        return payload
    except Exception:
        logger.exception("Supabase insert failed for table %s.", table)
        raise


def insert_rows(table: str, payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not payloads:
        return []

    client = get_supabase_client()
    if client is None:
        return []

    try:
        result = client.table(table).insert(payloads).execute()
        return list(result.data or payloads)
    except Exception:
        logger.exception("Supabase bulk insert failed for table %s.", table)
        raise


def try_insert_variants(table: str, payloads: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str | None]:
    client = get_supabase_client()
    if client is None:
        return None, "Supabase is not configured."

    last_error: str | None = None
    for payload in payloads:
        try:
            result = client.table(table).insert(payload).execute()
            return (result.data[0] if result.data else payload), None
        except Exception as exc:
            last_error = str(exc)
            logger.exception("Supabase insert variant failed for table %s.", table)

    return None, last_error


def count_table(table: str) -> int:
    client = get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase is not configured.")

    result = client.table(table).select("*", count="exact").limit(1).execute()
    return int(result.count or 0)


def diagnose_supabase() -> dict[str, Any]:
    settings = get_settings()
    configured = settings.is_supabase_configured
    if not configured:
        return {
            "supabase_configured": False,
            "connected": False,
            "counts": {},
            "error": "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing.",
        }

    client = get_supabase_client()
    if client is None:
        return {
            "supabase_configured": True,
            "connected": False,
            "counts": {},
            "error": "Supabase client could not be created. Check backend logs.",
        }

    try:
        client.table("products").select("id").limit(1).execute()
    except Exception as exc:
        logger.exception("Supabase connection check failed.")
        return {
            "supabase_configured": True,
            "connected": False,
            "counts": {},
            "error": str(exc),
        }

    tables = ["products", "leads", "assistant_messages", "rag_documents", "rag_chunks"]
    counts: dict[str, int | None] = {}
    errors: dict[str, str] = {}
    for table in tables:
        try:
            counts[table] = count_table(table)
        except Exception as exc:
            logger.exception("Supabase count failed for table %s.", table)
            counts[table] = None
            errors[table] = str(exc)

    return {
        "supabase_configured": True,
        "connected": True,
        "counts": counts,
        "error": None if not errors else f"Some counts failed: {errors}",
    }
