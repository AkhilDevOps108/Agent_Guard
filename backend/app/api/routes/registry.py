from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.services.registry import create_agent, get_agent, list_agents, serialize_agent, update_agent
from app.models.agent_version import AgentVersion
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=201)
def register_agent(request: AgentCreate, db: Session = Depends(get_db)) -> AgentResponse:
    return AgentResponse(**create_agent(db, request.model_dump()))


@router.get("", response_model=list[AgentResponse])
def get_agents(db: Session = Depends(get_db)) -> list[AgentResponse]:
    return [AgentResponse(**item) for item in list_agents(db)]


@router.get("/{agent_id}", response_model=AgentResponse)
def get_registered_agent(agent_id: str, db: Session = Depends(get_db)) -> AgentResponse:
    agent = get_agent(db, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**serialize_agent(agent))


@router.get("/{agent_id}/versions")
def get_agent_versions(agent_id: str, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    if get_agent(db, agent_id) is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return [
        {"id": item.id, "agent_id": item.agent_id, "version": item.version, "environment": item.environment, "created_at": item.created_at}
        for item in db.scalars(select(AgentVersion).where(AgentVersion.agent_id == agent_id).order_by(AgentVersion.created_at.desc()))
    ]


@router.patch("/{agent_id}", response_model=AgentResponse)
def update_registered_agent(agent_id: str, request: AgentUpdate, db: Session = Depends(get_db)) -> AgentResponse:
    agent = get_agent(db, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**update_agent(db, agent, request.model_dump(exclude_unset=True)))