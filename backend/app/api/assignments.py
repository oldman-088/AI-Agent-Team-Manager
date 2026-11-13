"""Manual planning assignments; no execution, scheduling or agent lifecycle."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError

from app.api.projects import Db
from app.api.dependencies import lock_project
from app.models import Agent, Task, TaskAssignment
from app.services.activity import record_event

router = APIRouter(prefix='/api/tasks', tags=['task assignments'])
TaskId = Annotated[int, Path(ge=1, le=2147483647)]


class AssignmentInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    agent_id: int | None = Field(ge=1, le=2147483647)


class AssignmentView(BaseModel):
    task_id: int
    agent_id: int | None


@router.get('/{task_id}/assignment', response_model=AssignmentView)
def get_assignment(task_id: TaskId, db: Db) -> AssignmentView:
    if db.get(Task, task_id) is None:
        raise HTTPException(status_code=404, detail='Task not found')
    assignment = db.get(TaskAssignment, task_id)
    return AssignmentView(task_id=task_id, agent_id=assignment.agent_id if assignment else None)


@router.put('/{task_id}/assignment', response_model=AssignmentView)
def set_assignment(task_id: TaskId, data: AssignmentInput, db: Db) -> AssignmentView:
    task = lock_project(db, task_id)
    assignment = db.get(TaskAssignment, task_id)
    if data.agent_id is not None:
        agent = db.get(Agent, data.agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail='Agent not found')
        if agent.project_id != task.project_id:
            raise HTTPException(status_code=422, detail='Agent must belong to the task project')
    previous = assignment.agent_id if assignment else None
    if previous == data.agent_id:
        return AssignmentView(task_id=task_id, agent_id=previous)
    if task.status != 'pending' and data.agent_id is not None:
        raise HTTPException(status_code=409, detail='Only pending tasks can receive an assignment')
    if data.agent_id is None:
        if assignment is not None:
            db.delete(assignment)
        event_type = 'task.unassigned'
    else:
        if assignment is None:
            db.add(TaskAssignment(task_id=task_id, project_id=task.project_id, agent_id=data.agent_id))
        else:
            assignment.agent_id = data.agent_id
        event_type = 'task.assigned'
    record_event(db, event_type, task.project_id, task_id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Agent or task changed; refresh and retry') from None
    return AssignmentView(task_id=task_id, agent_id=data.agent_id)
