"""Agent configuration registry. It does not start or control agent processes."""
from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Path, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.projects import Db
from app.models import Agent, Project, TaskRun
from app.services.run_inspection import heartbeat_state
from app.schemas import AgentCreate, AgentUpdate, AgentView

router = APIRouter(prefix='/api/agents', tags=['agents'])
AgentId = Annotated[int, Path(ge=1, le=2147483647)]


def find_agent(db: Db, agent_id: int) -> Agent:
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail='Agent not found')
    return agent


def validate_project(db: Db, project_id: int | None) -> None:
    if project_id is not None and db.get(Project, project_id) is None:
        raise HTTPException(status_code=422, detail='Project does not exist')


@router.get('', response_model=list[AgentView])
def list_agents(db: Db, limit: int = 100, offset: int = 0) -> list[Agent]:
    if not 1 <= limit <= 100 or not 0 <= offset <= 1000000:
        raise HTTPException(status_code=422, detail='Invalid pagination')
    return list(db.scalars(select(Agent).order_by(Agent.id).limit(limit).offset(offset)))


@router.post('', response_model=AgentView, status_code=201)
def create_agent(data: AgentCreate, db: Db) -> Agent:
    validate_project(db, data.project_id)
    agent = Agent(**data.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get('/{agent_id}', response_model=AgentView)
def get_agent(agent_id: AgentId, db: Db) -> Agent:
    return find_agent(db, agent_id)


class AgentClaimView(BaseModel):
    agent_id: int
    claim_status: Literal['none', 'running', 'uncertain']
    run_id: int | None = None
    task_id: int | None = None
    heartbeat_at: datetime | None = None
    heartbeat_state: Literal['fresh', 'stale', 'unknown', 'not_running'] | None = None


@router.get('/{agent_id}/claim', response_model=AgentClaimView)
def get_agent_claim(agent_id: AgentId, db: Db) -> AgentClaimView:
    """Snapshot of recorded unresolved claim, not process or provider liveness."""
    find_agent(db, agent_id)
    run = db.scalar(select(TaskRun).where(TaskRun.agent_id == agent_id,
                    TaskRun.status.in_(['running', 'uncertain'])).order_by(TaskRun.id).limit(1))
    if run is None:
        return AgentClaimView(agent_id=agent_id, claim_status='none')
    return AgentClaimView(agent_id=agent_id, claim_status=run.status, run_id=run.id,
                          task_id=run.task_id, heartbeat_at=run.heartbeat_at,
                          heartbeat_state=heartbeat_state(run, datetime.now(timezone.utc)))


@router.patch('/{agent_id}', response_model=AgentView)
def update_agent(agent_id: AgentId, data: AgentUpdate, db: Db) -> Agent:
    changes = data.model_dump(exclude_unset=True)
    if not changes or any(value is None for key, value in changes.items() if key != 'project_id'):
        raise HTTPException(status_code=422, detail='Provide valid fields to update')
    if 'project_id' in changes:
        validate_project(db, changes['project_id'])
    agent = find_agent(db, agent_id)
    for field, value in changes.items():
        setattr(agent, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Agent has task assignments; remove them before changing project') from None
    db.refresh(agent)
    return agent


@router.delete('/{agent_id}', status_code=204)
def delete_agent(agent_id: AgentId, db: Db) -> Response:
    agent = find_agent(db, agent_id)
    db.delete(agent)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Agent has task assignments or run history; resolve references before deleting') from None
    return Response(status_code=204)
