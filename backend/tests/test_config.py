from app.core.config import Settings


def test_settings_parse_cors_origins_from_comma_separated_string() -> None:
    settings = Settings(backend_cors_origins="http://localhost:3000, http://127.0.0.1:3000")

    assert settings.backend_cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_settings_llm_defaults() -> None:
    # Code defaults in isolation — don't read the developer's local .env.
    settings = Settings(_env_file=None)

    assert settings.llm_base_url == ""
    assert settings.llm_api_key == ""
    assert settings.llm_model == "deepseek-v4-flash"
