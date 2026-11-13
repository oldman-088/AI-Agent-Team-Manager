"""Read-only metadata; no remote requests or automatic worker start."""
from datetime import datetime, timezone
from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from app.api.projects import Db
from app.models import Task, TaskRun

router = APIRouter(prefix='/api/tasks', tags=['task runs'])


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
        state = 'not_running'
        if run.status == 'running':
            if run.heartbeat_at is None:
                state = 'unknown'
            else:
                timestamp = run.heartbeat_at.replace(tzinfo=timezone.utc) if run.heartbeat_at.tzinfo is None else run.heartbeat_at
                age = (now - timestamp).total_seconds()
                state = 'unknown' if age < -30 else 'fresh' if age <= 30 else 'stale'
        data = {name: getattr(run, name) for name in RunView.model_fields if name != 'heartbeat_state'}
        views.append(RunView(**data, heartbeat_state=state))
    return views
