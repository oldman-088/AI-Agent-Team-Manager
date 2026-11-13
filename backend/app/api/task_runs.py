"""Read-only metadata; no remote requests or automatic worker start."""
from datetime import datetime, timezone
from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from app.api.projects import Db
from app.models import Task, TaskRun
from app.services.run_inspection import heartbeat_state, unresolved_runs

router = APIRouter(prefix='/api/tasks', tags=['task runs'])
inspection_router = APIRouter(prefix='/api/runs', tags=['task runs'])


class RunView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_id: int
    agent_id: int
    status: Literal['running', 'succeeded', 'uncertain', 'resolved']
    model: str
    started_at: datetime
    heartbeat_at: datetime | None
    heartbeat_state: Literal['fresh', 'stale', 'unknown', 'not_running']
    finished_at: datetime | None
    input_tokens: int | None
    output_tokens: int | None


@router.get('/{task_id}/runs', response_model=list[RunView])
def list_runs(task_id: Annotated[int, Path(ge=1, le=2147483647)], db: Db, limit: int = 100, offset: int = 0) -> list[RunView]:
    if not 1 <= limit <= 100 or not 0 <= offset <= 1000000:
        raise HTTPException(status_code=422, detail='Invalid pagination')
    if db.get(Task, task_id) is None:
        raise HTTPException(status_code=404, detail='Task not found')
    runs = list(db.scalars(select(TaskRun).where(TaskRun.task_id == task_id).order_by(TaskRun.id.desc()).limit(limit).offset(offset)))
    now = datetime.now(timezone.utc)
    views = []
    for run in runs:
        state = heartbeat_state(run, now)
        data = {name: getattr(run, name) for name in RunView.model_fields if name != 'heartbeat_state'}
        views.append(RunView(**data, heartbeat_state=state))
    return views


class UnresolvedRunView(BaseModel):
    id: int
    project_id: int
    task_id: int
    agent_id: int
    status: Literal['running', 'uncertain']
    started_at: datetime
    heartbeat_at: datetime | None
    heartbeat_state: Literal['fresh', 'stale', 'unknown', 'not_running']


@inspection_router.get('/unresolved', response_model=list[UnresolvedRunView])
def list_unresolved(db: Db, limit: int = 100, after_id: int = 0, project_id: int | None = None) -> list[UnresolvedRunView]:
    try:
        runs = unresolved_runs(db, limit=limit, after_id=after_id, project_id=project_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail='Invalid inspection bounds') from exc
    now = datetime.now(timezone.utc)
    return [UnresolvedRunView(id=run.id, project_id=pid, task_id=run.task_id, agent_id=run.agent_id,
                              status=run.status, started_at=run.started_at, heartbeat_at=run.heartbeat_at,
                              heartbeat_state=heartbeat_state(run, now)) for run, pid in runs]
