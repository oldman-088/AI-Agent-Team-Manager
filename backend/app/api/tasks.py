"""Project planning tasks; no agent execution or scheduling yet."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, Query, Response
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.api.projects import Db
from app.models import Project, Task
from app.schemas import TaskCreate, TaskUpdate, TaskView

router = APIRouter(prefix='/api/tasks', tags=['tasks'])
TaskId = Annotated[int, Path(ge=1, le=2147483647)]
ProjectQuery = Annotated[int | None, Query(ge=1, le=2147483647)]


def find_task(db: Db, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    return task


@router.get('', response_model=list[TaskView])
def list_tasks(db: Db, project_id: ProjectQuery = None, limit: int = 100, offset: int = 0) -> list[Task]:
    if not 1 <= limit <= 100 or not 0 <= offset <= 1000000:
        raise HTTPException(status_code=422, detail='Invalid pagination')
    statement = select(Task).order_by(Task.id).limit(limit).offset(offset)
    if project_id is not None:
        statement = statement.where(Task.project_id == project_id)
    return list(db.scalars(statement))


@router.post('', response_model=TaskView, status_code=201)
def create_task(data: TaskCreate, db: Db) -> Task:
    if db.get(Project, data.project_id) is None:
        raise HTTPException(status_code=422, detail='Project does not exist')
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get('/{task_id}', response_model=TaskView)
def get_task(task_id: TaskId, db: Db) -> Task:
    return find_task(db, task_id)


@router.patch('/{task_id}', response_model=TaskView)
def update_task(task_id: TaskId, data: TaskUpdate, db: Db) -> Task:
    changes = data.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail='Provide non-null fields to update')
    task = find_task(db, task_id)
    for field, value in changes.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.post('/{task_id}/cancel', response_model=TaskView)
def cancel_task(task_id: TaskId, db: Db) -> Task:
    # Idempotent state transition; no external execution is stopped by this operation.
    db.execute(update(Task).where(Task.id == task_id, Task.status == 'pending').values(status='cancelled'))
    db.commit()
    return find_task(db, task_id)


@router.delete('/{task_id}', status_code=204)
def delete_task(task_id: TaskId, db: Db) -> Response:
    task = find_task(db, task_id)
    db.delete(task)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Task has dependencies; remove them before deleting') from None
    return Response(status_code=204)
