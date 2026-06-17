from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Stock Analyst Backend"
    database_url: str = (
        "postgresql+psycopg://ai_stock_analyst:"
        "ai_stock_analyst_password@localhost:5432/ai_stock_analyst"
    )

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
