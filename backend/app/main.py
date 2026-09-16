from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.agent import router as agent_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name.title(),
    version="0.1.0",
    description="AgentGuard is an AI agent evaluation, security, and reliability platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(agent_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AgentGuard API is running."}
