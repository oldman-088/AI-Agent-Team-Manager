"""Read-only inspection of unresolved worker runs. Never releases claims."""
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, TaskRun

HeartbeatState = Literal['fresh', 'stale', 'unknown', 'not_running']


def heartbeat_state(run: TaskRun, now: datetime) -> HeartbeatState:
    if run.status != 'running':
        return 'not_running'
    if run.heartbeat_at is None:
        return 'unknown'
    timestamp = run.heartbeat_at.replace(tzinfo=timezone.utc) if run.heartbeat_at.tzinfo is None else run.heartbeat_at
    age = (now - timestamp).total_seconds()
    return 'unknown' if age < -30 else 'fresh' if age <= 30 else 'stale'


def unresolved_runs(db: Session, *, limit: int = 100, after_id: int = 0, project_id: int | None = None):
    """Advisory keyset page; concurrent changes can remove records from later pages."""
    if not 1 <= limit <= 100 or not 0 <= after_id <= 2147483647 or (project_id is not None and not 1 <= project_id <= 2147483647):
        raise ValueError('Invalid inspection bounds')
    query = (select(TaskRun, Task.project_id).join(Task, Task.id == TaskRun.task_id)
             .where(TaskRun.status.in_(['running', 'uncertain']), TaskRun.id > after_id))
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    return db.execute(query.order_by(TaskRun.id).limit(limit)).all()
