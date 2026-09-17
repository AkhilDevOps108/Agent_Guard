from typing import Any

from pydantic import BaseModel, Field


class TestRunCreate(BaseModel):
    __test__ = False
    agent_id: str = Field(min_length=1, max_length=36)
    categories: list[str] = Field(default_factory=lambda: ["security", "quality"])
    inputs: list[str] | None = None


class TestRunResponse(BaseModel):
    __test__ = False
    id: str
    agent_id: str
    status: str
    total_tests: int
    passed: int
    failed: int
    score: float | None
    severity_summary: dict[str, int] | None


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