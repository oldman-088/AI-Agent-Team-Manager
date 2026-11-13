"""Read-only local operational history, not an authenticated audit log."""
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.api.projects import Db
from app.models import ActivityEvent

router = APIRouter(prefix='/api/events', tags=['events'])


class EventView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int | None
    task_id: int | None
    related_task_id: int | None
    event_type: str
    created_at: datetime


@router.get('', response_model=list[EventView])
def list_events(db: Db, project_id: Annotated[int | None, Query(ge=1, le=2147483647)] = None,
                limit: int = 100, offset: int = 0) -> list[ActivityEvent]:
    if not 1 <= limit <= 100 or not 0 <= offset <= 1000000:
        raise HTTPException(status_code=422, detail='Invalid pagination')
    query = select(ActivityEvent).order_by(ActivityEvent.id.desc()).limit(limit).offset(offset)
    if project_id is not None:
        query = query.where(ActivityEvent.project_id == project_id)
    return list(db.scalars(query))
