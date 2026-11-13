"""Safe project-scoped dependency editing; scheduling is not implemented."""
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response
from sqlalchemy import select, text

from app.api.projects import Db
from app.models import Project, Task, TaskDependency

router = APIRouter(prefix='/api/tasks', tags=['task dependencies'])
TaskId = Annotated[int, Path(ge=1, le=2147483647)]
MAX_EDGES = 10000


def lock_project(db: Db, task_id: int) -> Task:
    # SQLite has database-level write locking; PostgreSQL serializes graph edits
    # via a row lock. Only these two database engines are supported here.
    dialect = db.get_bind().dialect.name
    if dialect == 'sqlite':
        db.execute(text('BEGIN IMMEDIATE'))
    elif dialect != 'postgresql':
        raise HTTPException(status_code=501, detail='Unsupported database for dependency changes')
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    project_id = task.project_id
    project = db.scalar(select(Project).where(Project.id == project_id).with_for_update())
    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    # Re-read after locking, as the task could have been removed while waiting.
    db.expire_all()
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    return task


@router.get('/{task_id}/dependencies', response_model=list[int])
def list_dependencies(task_id: TaskId, db: Db) -> list[int]:
    if db.get(Task, task_id) is None:
        raise HTTPException(status_code=404, detail='Task not found')
    return list(db.scalars(select(TaskDependency.depends_on_id).where(TaskDependency.task_id == task_id).order_by(TaskDependency.depends_on_id)))


@router.put('/{task_id}/dependencies/{dependency_id}', status_code=204)
def add_dependency(task_id: TaskId, dependency_id: TaskId, db: Db) -> Response:
    task = lock_project(db, task_id)
    if task_id == dependency_id:
        raise HTTPException(status_code=422, detail='A task cannot depend on itself')
    other = db.get(Task, dependency_id)
    if other is None:
        raise HTTPException(status_code=404, detail='Dependency task not found')
    if other.project_id != task.project_id:
        raise HTTPException(status_code=422, detail='Tasks must belong to the same project')
    if db.get(TaskDependency, (task_id, dependency_id)) is not None:
        return Response(status_code=204)
    if task.status == 'completed':
        raise HTTPException(status_code=409, detail='Completed task dependencies cannot be changed')
    edges = db.execute(select(TaskDependency.task_id, TaskDependency.depends_on_id)
                       .where(TaskDependency.project_id == task.project_id).limit(MAX_EDGES + 1)).all()
    if len(edges) >= MAX_EDGES:
        raise HTTPException(status_code=409, detail='Project dependency limit reached')
    graph: dict[int, list[int]] = defaultdict(list)
    for source, target in edges:
        graph[source].append(target)
    pending, visited = [dependency_id], set()
    while pending:
        current = pending.pop()
        if current == task_id:
            raise HTTPException(status_code=409, detail='Dependency would create a cycle')
        if current not in visited:
            visited.add(current)
            pending.extend(graph[current])
    db.add(TaskDependency(task_id=task_id, depends_on_id=dependency_id, project_id=task.project_id))
    db.commit()
    return Response(status_code=204)


@router.delete('/{task_id}/dependencies/{dependency_id}', status_code=204)
def remove_dependency(task_id: TaskId, dependency_id: TaskId, db: Db) -> Response:
    lock_project(db, task_id)
    edge = db.get(TaskDependency, (task_id, dependency_id))
    if edge is None:
        raise HTTPException(status_code=404, detail='Dependency not found')
    db.delete(edge)
    db.commit()
    return Response(status_code=204)
