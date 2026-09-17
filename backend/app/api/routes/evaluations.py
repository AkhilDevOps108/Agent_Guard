from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.evaluation_result import EvaluationResult
from app.schemas.test_run import EvaluationResponse

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)) -> EvaluationResponse:
    result = db.get(EvaluationResult, evaluation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return EvaluationResponse.model_validate(result, from_attributes=True)