from typing import Any

from pydantic import BaseModel, Field, field_validator


class TestRunCreate(BaseModel):
    __test__ = False
    agent_id: str = Field(min_length=1, max_length=36)
    categories: list[str] = Field(default_factory=lambda: ["security", "quality"])
    inputs: list[str] | None = None

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, values: list[str]) -> list[str]:
        allowed = {"security", "quality", "reliability"}
        values = list(dict.fromkeys(value.lower() for value in values))
        if not values or any(value not in allowed for value in values):
            raise ValueError("categories must contain security, quality, or reliability")
        return values


class TestRunResponse(BaseModel):
    __test__ = False
    id: str
    agent_id: str
    agent_version: str = "1.0.0"
    status: str
    categories: list[str] = Field(default_factory=list)
    total_tests: int
    passed: int
    failed: int
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    score: float | None
    severity_summary: dict[str, int] | None
    deployment_decision: str | None = None
    completed_at: Any | None = None


class EvaluationResponse(BaseModel):
    __test__ = False
    id: str
    run_id: str
    agent_id: str
    category: str
    test_name: str
    input: str | None
    expected_behavior: str | None
    actual_behavior: str | None
    passed: bool
    severity: str
    score: float | None
    latency: float | None
    trace_id: str | None
    failure_reason: str | None
    recommendation: str | None


class TraceResponse(BaseModel):
    __test__ = False
    id: str
    agent_id: str
    run_id: str
    status: str
    start_time: Any
    end_time: Any
    duration: float | None
    payload: dict[str, Any] | None