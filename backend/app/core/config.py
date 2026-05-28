import json
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    port: int = 8000
    allowed_origins: str = "http://localhost:5500,http://127.0.0.1:5500,https://prueba-tecnica-e5sn.onrender.com"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    stripe_secret_key: str = ""
    stripe_price_id: str = ""
    stripe_success_url: str = "http://localhost:5500/success.html"
    stripe_cancel_url: str = "http://localhost:5500/cancel.html"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    chat_primary_llm: str = "google/gemini-2.0-flash-exp:free"
    chat_fallback_llm: str = "mistralai/mistral-small-24b-instruct-2501:free"
    chat_enhancement_llm: str = "deepseek/deepseek-r1-distill-llama-70b:free"
    chat_judge_llm: str = "meta-llama/llama-3.3-70b-instruct:free"
    chat_use_fallback: bool = True
    chat_use_enhancement: bool = False
    chat_use_judge: bool = False
    chat_temperature: float = 0.2
    chat_top_p: float = 0.8
    chat_max_tokens: int = 450
    chat_timeout_ms: int = 12000

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 5
    rag_min_score: float = 0.2

    @property
    def cors_origins(self) -> list[str]:
        value = self.allowed_origins.strip()
        if not value:
            return []
        if value.startswith("["):
            try:
                parsed = json.loads(value)
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
            except json.JSONDecodeError:
                pass
        cleaned = value.strip("[]")
        return [
            origin.strip().strip('"').strip("'")
            for origin in cleaned.split(",")
            if origin.strip()
        ]

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @property
    def is_stripe_configured(self) -> bool:
        return bool(self.stripe_secret_key)

    @property
    def is_openrouter_configured(self) -> bool:
        return bool(self.openrouter_api_key and self.openrouter_base_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
