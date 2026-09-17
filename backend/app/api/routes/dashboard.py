from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.agent import Agent
from app.models.evaluation_result import EvaluationResult
from app.models.test_run import TestRun
from app.services.risk import calculate_risk

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    runs = list(db.scalars(select(TestRun).order_by(TestRun.created_at.desc()).limit(10)))
    risk = calculate_risk(db)
    total_results = db.scalar(select(func.count(EvaluationResult.id))) or 0
    return {
        "agents": db.scalar(select(func.count(Agent.id))) or 0,
        "test_runs": db.scalar(select(func.count(TestRun.id))) or 0,
        "evaluations": total_results,
        "pass_rate": round(risk["passed"] / risk["total_tests"] * 100, 2) if risk["total_tests"] else 0,
        "critical_failures": risk["critical"],
        "security_score": risk["security_score"],
        "quality_score": risk["quality_score"],
        "reliability_score": risk["reliability_score"],
        "overall_score": risk["overall_score"],
        "deployment_decision": risk["deployment_decision"],
        "recent_runs": [{"id": run.id, "agent_id": run.agent_id, "status": run.status, "score": run.score} for run in runs],
    }