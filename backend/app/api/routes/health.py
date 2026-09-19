from fastapi import APIRouter
from redis import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "agentguard"}


@router.get("/ready")
def readiness_check() -> dict[str, object]:
    settings = get_settings()
    database = "ok"
    redis = "ok"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database = "error"
    try:
        Redis.from_url(settings.redis_url).ping()
    except Exception:
        redis = "error"
    ready = database == "ok" and redis == "ok"
    return {"status": "ready" if ready else "not_ready", "database": database, "redis": redis}
