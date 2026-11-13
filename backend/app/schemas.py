"""Validated API contracts for project management."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal['planned', 'active', 'paused', 'completed', 'archived']


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default='', max_length=4000)
    status: ProjectStatus = 'planned'

    @field_validator('name')
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('name must not be blank')
        return value


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    status: ProjectStatus | None = None

    @field_validator('name')
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError('name must not be blank')
        return value


class ProjectView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    status: ProjectStatus


class AgentCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=200)
    description: str = Field(default='', max_length=4000)
    instructions: str = Field(default='', max_length=10000)
    provider: str = Field(default='', max_length=100)
    model: str = Field(default='', max_length=200)
    project_id: int | None = Field(default=None, ge=1, le=2147483647)

    @field_validator('name', 'role')
    @classmethod
    def clean_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('must not be blank')
        return value


class AgentUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str | None = Field(default=None, min_length=1, max_length=100)
    role: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    instructions: str | None = Field(default=None, max_length=10000)
    provider: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=200)
    project_id: int | None = Field(default=None, ge=1, le=2147483647)

    @field_validator('name', 'role')
    @classmethod
    def clean_required(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError('must not be blank')
        return value


class AgentView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    role: str
    description: str
    instructions: str
    provider: str
    model: str
    project_id: int | None
    # Configuration records are not agent processes. No inferred runtime state.
    execution_status: Literal['not_implemented'] = 'not_implemented'


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    project_id: int = Field(ge=1, le=2147483647)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default='', max_length=4000)

    @field_validator('title')
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('title must not be blank')
        return value


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)

    @field_validator('title')
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError('title must not be blank')
        return value


class TaskView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    title: str
    description: str
    status: Literal['pending', 'cancelled', 'completed']


class TaskReadiness(BaseModel):
    task_id: int
    ready: bool
    status: Literal['pending', 'cancelled', 'completed']
    blocking_dependencies: list[int]
