from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.service import CustomerSupportAgent
from app.core.metrics import increment

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])
agent = CustomerSupportAgent()


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    customer_id: str | None = Field(default=None, max_length=32)


class AgentResponse(BaseModel):
    response: str
    tool_calls: list[str]
    trace: list[dict[str, Any]]


@router.post("/invoke", response_model=AgentResponse)
def invoke_agent(request: AgentRequest) -> AgentResponse:
    try:
        increment("agent_invocations_total")
        result = agent.invoke(request.message, request.customer_id)
        increment("agent_invocations_succeeded_total")
        return AgentResponse(**result)
    except ValueError as exc:
        increment("agent_invocations_failed_total")
        raise HTTPException(status_code=400, detail=str(exc)) from exc