from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "agentguard"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agentguard"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    risk_critical_failures_block: int = 1
    risk_injection_failure_rate_block: float = 0.10
    risk_hallucination_rate_block: float = 0.20
    risk_p95_latency_warning_ms: float = 1000.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
