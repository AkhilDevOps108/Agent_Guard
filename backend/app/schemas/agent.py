from typing import Any

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    __test__ = False
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    version: str = Field(default="1.0.0", max_length=64)
    environment: str = Field(default="development", min_length=1, max_length=64)
    config: dict[str, Any] | None = None


class AgentUpdate(BaseModel):
    __test__ = False
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    version: str | None = Field(default=None, max_length=64)
    status: str | None = Field(default=None, max_length=32)
    config: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    __test__ = False
    id: str
    name: str
    description: str | None
    version: str
    environment: str
    status: str
    config: dict[str, Any] | None