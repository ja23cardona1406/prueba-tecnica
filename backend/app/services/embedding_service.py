from functools import lru_cache

from ..core.config import get_settings


@lru_cache
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    model_name = settings.embedding_model
    return SentenceTransformer(model_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    import numpy as np

    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    array = np.asarray(embeddings, dtype=np.float32)
    return array.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
