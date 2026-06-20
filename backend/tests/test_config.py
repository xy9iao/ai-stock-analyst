from app.core.config import Settings


def test_settings_parse_cors_origins_from_comma_separated_string() -> None:
    settings = Settings(backend_cors_origins="http://localhost:3000, http://127.0.0.1:3000")

    assert settings.backend_cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_settings_include_future_llm_defaults() -> None:
    settings = Settings()

    assert settings.llm_base_url == ""
    assert settings.llm_api_key == ""
    assert settings.llm_model == "deepseek-chat"
