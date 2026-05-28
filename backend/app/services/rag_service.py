from __future__ import annotations

import logging
import re
from typing import Any

from .embedding_service import embed_query, embed_texts
from .supabase_service import get_supabase_client


logger = logging.getLogger(__name__)


LOCAL_RAG_CORPUS = [
    {
        "document_title": "Ficha Bertolli Pro 900",
        "document_source": "local-corpus",
        "content": "Bertolli Pro 900 es una cocina a gas profesional de 90 cm con 5 hornillas, horno amplio, acero inoxidable cepillado y parrillas de hierro fundido.",
        "similarity": 1.0,
    },
    {
        "document_title": "Instalacion y gas",
        "document_source": "local-corpus",
        "content": "La cocina puede configurarse para gas natural o GLP. La instalacion y conversion deben hacerlas tecnicos certificados.",
        "similarity": 1.0,
    },
    {
        "document_title": "Precio y garantia",
        "document_source": "local-corpus",
        "content": "El precio referencial es $4.990.000 COP y la garantia limitada contemplada es de 24 meses por defectos de fabricacion.",
        "similarity": 1.0,
    },
]


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end].strip())
        if end == len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return chunks


async def ingest_document(
    title: str,
    text: str,
    source: str = "manual",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    supabase = get_supabase_client()
    if supabase is None:
        return {
            "success": False,
            "source": "supabase-unavailable",
            "document": None,
            "chunks_inserted": 0,
            "message": "Supabase is not configured; document was not persisted.",
        }

    chunks = chunk_text(text)
    if not chunks:
        return {
            "success": False,
            "source": "validation",
            "document": None,
            "chunks_inserted": 0,
            "message": "Document text is empty after normalization.",
        }

    embeddings = embed_texts(chunks)
    document_payload = {
        "title": title,
        "source": source,
        "metadata": metadata or {},
    }

    document_result = supabase.table("rag_documents").insert(document_payload).execute()
    document = (document_result.data or [document_payload])[0]
    document_id = document["id"]

    chunk_payloads = [
        {
            "document_id": document_id,
            "chunk_index": index,
            "content": chunk,
            "embedding": embedding,
            "token_count": len(chunk.split()),
            "metadata": metadata or {},
        }
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    chunks_result = supabase.table("rag_chunks").insert(chunk_payloads).execute()

    return {
        "success": True,
        "source": "supabase-vector",
        "document": document,
        "chunks_inserted": len(chunks_result.data or chunk_payloads),
        "message": "Document ingested into Supabase Vector.",
    }


def extract_document_text(document: dict[str, Any]) -> str:
    for key in ("content", "text", "body", "description"):
        value = document.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    metadata = document.get("metadata") or {}
    if isinstance(metadata, dict):
        for key in ("content", "text", "body", "description"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return ""


async def rag_status() -> dict[str, Any]:
    supabase = get_supabase_client()
    if supabase is None:
        return {
            "supabase_configured": False,
            "documents_count": 0,
            "chunks_count": 0,
            "chunks_with_embeddings_count": 0,
            "rag_ready": False,
            "error": "Supabase is not configured.",
        }

    try:
        documents_result = supabase.table("rag_documents").select("*", count="exact").limit(1).execute()
        chunks_result = supabase.table("rag_chunks").select("*", count="exact").limit(1).execute()
        documents_count = int(documents_result.count or 0)
        chunks_count = int(chunks_result.count or 0)
        return {
            "supabase_configured": True,
            "documents_count": documents_count,
            "chunks_count": chunks_count,
            "chunks_with_embeddings_count": chunks_count,
            "rag_ready": documents_count > 0 and chunks_count > 0,
            "error": None,
        }
    except Exception as exc:
        logger.exception("Could not read RAG status from Supabase.")
        return {
            "supabase_configured": True,
            "documents_count": 0,
            "chunks_count": 0,
            "chunks_with_embeddings_count": 0,
            "rag_ready": False,
            "error": str(exc),
        }


async def ingest_seed_documents(force: bool = False) -> dict[str, Any]:
    supabase = get_supabase_client()
    if supabase is None:
        return {
            "success": False,
            "source": "supabase-unavailable",
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_created": 0,
            "errors": ["Supabase is not configured."],
        }

    try:
        documents_result = supabase.table("rag_documents").select("*").execute()
        documents = list(documents_result.data or [])
    except Exception as exc:
        logger.exception("Could not read seed RAG documents from Supabase.")
        return {
            "success": False,
            "source": "supabase-vector",
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_created": 0,
            "errors": [str(exc)],
        }

    documents_processed = 0
    chunks_created = 0
    embeddings_created = 0
    errors: list[str] = []

    for document in documents:
        document_id = document.get("id")
        title = document.get("title") or "Documento sin titulo"
        text = extract_document_text(document)
        if not document_id or not text:
            errors.append(f"Document {document_id or title} has no metadata.content/text to ingest.")
            continue

        try:
            if force:
                supabase.table("rag_chunks").delete().eq("document_id", document_id).execute()

            chunks = chunk_text(text)
            embeddings = embed_texts(chunks)
            metadata = document.get("metadata") or {}
            chunk_payloads = [
                {
                    "document_id": document_id,
                    "chunk_index": index,
                    "content": chunk,
                    "token_count": len(chunk.split()),
                    "metadata": metadata,
                    "embedding": embedding,
                }
                for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ]

            if chunk_payloads:
                result = supabase.table("rag_chunks").insert(chunk_payloads).execute()
                inserted_count = len(result.data or chunk_payloads)
                chunks_created += inserted_count
                embeddings_created += inserted_count
            documents_processed += 1
        except Exception as exc:
            logger.exception("Could not ingest RAG document %s.", document_id)
            errors.append(f"{document_id}: {exc}")

    return {
        "success": not errors,
        "source": "supabase-vector",
        "documents_processed": documents_processed,
        "chunks_created": chunks_created,
        "embeddings_created": embeddings_created,
        "errors": errors,
    }


def _to_pgvector(values: list[float]) -> str:
    return "[" + ",".join(str(float(v)) for v in values) + "]"


async def search_documents(
    query: str,
    match_count: int = 5,
    match_threshold: float = 0.2,
) -> dict[str, Any]:
    supabase = get_supabase_client()
    if supabase is None:
        return {
            "source": "local-corpus",
            "matches": local_matches(query),
            "embedding_length": 0,
            "threshold": match_threshold,
            "error": None,
        }

    query_embedding = embed_query(query)
    print("RAG: using Supabase vector search")
    print("RAG embedding length:", len(query_embedding))
    print("RAG threshold:", match_threshold)

    query_embedding_pgvector = _to_pgvector(query_embedding)
    embedding_floats = [float(x) for x in query_embedding]

    try:
        print("RAG: trying pgvector_string format")
        response = supabase.rpc(
            "match_rag_chunks",
            {
                "query_embedding": query_embedding_pgvector,
                "match_count": match_count,
                "match_threshold": match_threshold,
            },
        ).execute()
        rows = list(response.data or [])
        print("RAG RPC rows (pgvector_string):", len(rows))

        if rows == [] and match_threshold == 0.0:
            print(f"RAG: 0 rows at threshold=0.0 — query[:80]={query[:80]!r}")

        if rows:
            return {
                "source": "supabase_vector",
                "matches": rows,
                "embedding_length": len(query_embedding),
                "threshold": match_threshold,
                "error": None,
            }

        print("RAG: trying float_list format (match_rag_chunks_from_array)")
        try:
            response2 = supabase.rpc(
                "match_rag_chunks_from_array",
                {
                    "query_embedding": embedding_floats,
                    "match_count": match_count,
                    "match_threshold": match_threshold,
                },
            ).execute()
            rows2 = list(response2.data or [])
            print("RAG RPC rows (float_list):", len(rows2))
            return {
                "source": "supabase_vector",
                "matches": rows2,
                "embedding_length": len(query_embedding),
                "threshold": match_threshold,
                "error": None,
            }
        except Exception as exc2:
            print("RAG float_list RPC not available:", exc2)
            return {
                "source": "supabase_vector",
                "matches": [],
                "embedding_length": len(query_embedding),
                "threshold": match_threshold,
                "error": None,
            }

    except Exception as exc:
        print("RAG RPC exception:", exc)
        return {
            "source": "supabase_vector",
            "matches": [],
            "embedding_length": len(query_embedding),
            "threshold": match_threshold,
            "error": str(exc),
        }


async def local_rag_search(
    query: str,
    match_count: int = 5,
    match_threshold: float = 0.2,
) -> list[dict[str, Any]]:
    try:
        result = await search_documents(query, match_count, match_threshold)
        matches = result["matches"]
        if matches:
            return matches
        return local_matches(query)
    except Exception:
        return local_matches(query)


def local_matches(query: str) -> list[dict[str, Any]]:
    normalized = query.lower()
    scored = []
    for item in LOCAL_RAG_CORPUS:
        words = set(re.findall(r"\w+", normalized))
        content_words = set(re.findall(r"\w+", item["content"].lower()))
        overlap = len(words & content_words)
        scored.append(({**item, "similarity": 0.5 + min(overlap / 10, 0.5)}, overlap))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [item for item, _score in scored[:3]]


def build_context(matches: list[dict[str, Any]]) -> str:
    parts = []
    for index, match in enumerate(matches, start=1):
        title = match.get("document_title") or match.get("title") or "Documento Bertolli"
        source = match.get("document_source") or match.get("source") or "supabase"
        content = match.get("content") or ""
        parts.append(f"[Fuente {index}: {title} - {source}]\n{content}")
    return "\n\n".join(parts)
