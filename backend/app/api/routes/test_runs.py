import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.evaluation_result import EvaluationResult
from app.models.test_run import TestRun
from app.models.trace import TraceRecord
from app.schemas.test_run import EvaluationResponse, TestRunCreate, TestRunResponse, TraceResponse
from app.services.registry import get_agent
from app.evaluation.runner import run_evaluation
from app.worker import run_test_run
from app.services.risk import calculate_risk

router = APIRouter(prefix="/api/v1/test-runs", tags=["test-runs"])


def _run_response(run: TestRun) -> TestRunResponse:
    return TestRunResponse(
        id=run.id,
        agent_id=run.agent_id,
        status=run.status,
        total_tests=run.total_tests,
        passed=run.passed,
        failed=run.failed,
        score=run.score,
        severity_summary=json.loads(run.severity_summary) if run.severity_summary else None,
    )


@router.post("", response_model=TestRunResponse, status_code=201)
def create_test_run(request: TestRunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> TestRunResponse:
    if get_agent(db, request.agent_id) is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    run = TestRun(id=str(uuid.uuid4()), agent_id=request.agent_id, status="queued")
    db.add(run)
    db.commit()
    try:
        run_test_run.delay(run.id, request.categories, request.inputs)
    except Exception:
        background_tasks.add_task(_execute_run, run.id, request.categories, request.inputs)
    return _run_response(run)


def _execute_run(run_id: str, categories: list[str], inputs: list[str] | None) -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        run = db.get(TestRun, run_id)
        if run:
            run.status = "running"
            db.commit()
            run_evaluation(db, run, categories, inputs)
    finally:
        db.close()


@router.get("", response_model=list[TestRunResponse])
def list_test_runs(db: Session = Depends(get_db)) -> list[TestRunResponse]:
    return [_run_response(run) for run in db.scalars(select(TestRun).order_by(TestRun.created_at.desc()))]


@router.get("/{run_id}", response_model=TestRunResponse)
def get_test_run(run_id: str, db: Session = Depends(get_db)) -> TestRunResponse:
    run = db.get(TestRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Test run not found")
    return _run_response(run)


@router.get("/{run_id}/results", response_model=list[EvaluationResponse])
def get_results(run_id: str, db: Session = Depends(get_db)) -> list[EvaluationResponse]:
    return [EvaluationResponse.model_validate(result, from_attributes=True) for result in db.scalars(select(EvaluationResult).where(EvaluationResult.run_id == run_id))]


@router.get("/{run_id}/traces", response_model=list[TraceResponse])
def get_traces(run_id: str, db: Session = Depends(get_db)) -> list[TraceResponse]:
    records = db.scalars(select(TraceRecord).where(TraceRecord.run_id == run_id))
    return [TraceResponse(id=record.id, agent_id=record.agent_id, run_id=record.run_id, status=record.status, start_time=record.start_time, end_time=record.end_time, duration=record.duration, payload=json.loads(record.payload) if record.payload else None) for record in records]


@router.get("/{run_id}/risk")
def get_run_risk(run_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    return calculate_risk(db, run_id)