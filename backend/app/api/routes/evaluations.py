from fastapi import APIRouter, Depends, HTTPException
import json
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.evaluation_result import EvaluationResult
from app.models.trace import TraceRecord
from app.schemas.test_run import EvaluationResponse
from app.services.regression import generate_regression_test
from app.services.root_cause import analyze_failure

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)) -> EvaluationResponse:
    result = db.get(EvaluationResult, evaluation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return EvaluationResponse.model_validate(result, from_attributes=True)


@router.post("/{evaluation_id}/analyze")
def analyze_evaluation(evaluation_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    result = db.get(EvaluationResult, evaluation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    trace = db.get(TraceRecord, result.trace_id) if result.trace_id else None
    payload = json.loads(trace.payload) if trace and trace.payload else {}
    return analyze_failure(
        failure={"category": result.category, "test_name": result.test_name, "actual_behavior": result.actual_behavior, "failure_reason": result.failure_reason, "severity": result.severity},
        trace=payload.get("spans", []),
    )


@router.post("/{evaluation_id}/regression")
def generate_evaluation_regression(evaluation_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    result = db.get(EvaluationResult, evaluation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return generate_regression_test(
        name=result.test_name,
        category=result.category,
        severity=result.severity,
        root_cause=result.failure_reason or "The evaluation did not satisfy its expected behavior.",
        fix=result.recommendation or "Add a guardrail and keep this scenario in the regression suite.",
    )