from app.core.config import Settings


def test_settings_read_environment_overrides(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@db:5432/test")

    settings = Settings()

    assert settings.app_env == "test"
    assert settings.app_debug is False
    assert settings.database_url == "postgresql+psycopg://test:test@db:5432/test"