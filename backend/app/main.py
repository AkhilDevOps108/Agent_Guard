from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.routes.health import router as health_router
from app.api.routes.agent import router as agent_router
from app.api.routes.evaluations import router as evaluations_router
from app.core.config import get_settings
from app.api.routes.registry import router as registry_router
from app.api.routes.test_runs import router as test_runs_router
from app.api.routes.dashboard import router as dashboard_router
from app.core.metrics import prometheus_text
from app.api.routes.root_cause import router as root_cause_router

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
app.include_router(registry_router)
app.include_router(test_runs_router)
app.include_router(evaluations_router)
app.include_router(dashboard_router)
app.include_router(root_cause_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AgentGuard API is running."}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    return prometheus_text()
