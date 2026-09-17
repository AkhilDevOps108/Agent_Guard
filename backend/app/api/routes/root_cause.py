from typing import Any

from fastapi import APIRouter

from app.services.root_cause import analyze_failure

router = APIRouter(prefix="/api/v1/root-cause", tags=["root-cause"])


@router.post("/analyze")
def analyze_root_cause(payload: dict[str, Any]) -> dict[str, Any]:
    failure = payload.get("failure") or {}
    trace = payload.get("trace") or []
    agent_config = payload.get("agent_config") or {}
    retrieved_context = payload.get("retrieved_context") or []
    tool_calls = payload.get("tool_calls") or []
    return analyze_failure(
        failure=failure,
        trace=trace,
        agent_config=agent_config,
        retrieved_context=retrieved_context,
        tool_calls=tool_calls,
    )
