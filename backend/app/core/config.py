from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Stock Analyst Backend"
    database_url: str = (
        "postgresql+psycopg://ai_stock_analyst:"
        "ai_stock_analyst_password@localhost:5432/ai_stock_analyst"
    )
    # NoDecode: pydantic-settings would otherwise require JSON for list fields;
    # we accept a plain comma-separated env var (split in the validator below).
    backend_cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "deepseek-v4-flash"
    llm_timeout_seconds: float = 60.0
    market_data_provider: str = "yfinance"

    # Phase 14 RAG: embeddings are a separate provider from the LLM (DeepSeek has
    # no embeddings API). Dimensions are baked into the pgvector column — changing
    # the model means re-embedding the corpus and a migration.
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Public-demo hardening. All OFF by default so local use is unchanged:
    # DEMO_MODE=true enables anonymous session isolation, per-session LLM caps,
    # and the LLM master switch (default off, enabled via the admin endpoint).
    demo_mode: bool = False
    admin_token: str = ""
    demo_session_ttl_days: int = 7
    demo_report_limit: int = 3
    demo_chat_llm_limit: int = 20
    llm_switch_ttl_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
