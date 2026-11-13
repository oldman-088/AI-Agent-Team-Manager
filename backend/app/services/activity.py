"""Write metadata-only operational events within the caller's transaction."""
from typing import Literal
from sqlalchemy.orm import Session
from app.models import ActivityEvent

EventType = Literal['task.created', 'task.updated', 'task.cancelled', 'task.completed_manual', 'task.deleted', 'dependency.added', 'dependency.removed', 'task.assigned', 'task.unassigned']


def record_event(db: Session, event_type: EventType, project_id: int, task_id: int, related_task_id: int | None = None) -> None:
    # Never copy user content, model prompts, credentials or request headers here.
    db.add(ActivityEvent(event_type=event_type, project_id=project_id, task_id=task_id, related_task_id=related_task_id))
