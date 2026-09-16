from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.service import CustomerSupportAgent

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
        return AgentResponse(**agent.invoke(request.message, request.customer_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc