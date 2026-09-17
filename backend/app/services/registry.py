import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent


def _serialize(agent: Agent) -> dict[str, Any]:
    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "version": agent.version,
        "status": agent.status,
        "config": json.loads(agent.config) if agent.config else None,
    }


def create_agent(db: Session, data: dict[str, Any]) -> dict[str, Any]:
    agent = Agent(
        id=str(uuid.uuid4()),
        name=data["name"].strip(),
        description=data.get("description"),
        version=data.get("version", "1.0.0"),
        config=json.dumps(data.get("config")) if data.get("config") is not None else None,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return _serialize(agent)


def list_agents(db: Session) -> list[dict[str, Any]]:
    return [_serialize(agent) for agent in db.scalars(select(Agent).order_by(Agent.created_at.desc()))]


def get_agent(db: Session, agent_id: str) -> Agent | None:
    return db.get(Agent, agent_id)


def serialize_agent(agent: Agent) -> dict[str, Any]:
    return _serialize(agent)


def update_agent(db: Session, agent: Agent, data: dict[str, Any]) -> dict[str, Any]:
    for field in ("name", "description", "version", "status"):
        if data.get(field) is not None:
            setattr(agent, field, data[field])
    if "config" in data and data["config"] is not None:
        agent.config = json.dumps(data["config"])
    db.commit()
    db.refresh(agent)
    return _serialize(agent)