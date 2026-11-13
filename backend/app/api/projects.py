"""Project CRUD endpoints, scoped to the locally operated prototype API."""
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate, ProjectView

router = APIRouter(prefix='/api/projects', tags=['projects'])


def get_session(request: Request) -> Iterator[Session]:
    engine = request.app.state.engine
    if engine is None:
        raise HTTPException(status_code=503, detail='Database not configured')
    with Session(engine) as session:
        try:
            yield session
        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(status_code=503, detail='Database unavailable') from None


Db = Annotated[Session, Depends(get_session)]
ProjectId = Annotated[int, Path(ge=1, le=2147483647)]


def find_project(session: Session, project_id: int) -> Project:
    item = session.get(Project, project_id)
    if item is None:
        raise HTTPException(status_code=404, detail='Project not found')
    return item


@router.get('', response_model=list[ProjectView])
def list_projects(db: Db, limit: int = 100, offset: int = 0) -> list[Project]:
    if not 1 <= limit <= 100 or offset < 0 or offset > 1000000:
        raise HTTPException(status_code=422, detail='Invalid pagination')
    return list(db.scalars(select(Project).order_by(Project.id).limit(limit).offset(offset)))


@router.post('', response_model=ProjectView, status_code=201)
def create_project(data: ProjectCreate, db: Db) -> Project:
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get('/{project_id}', response_model=ProjectView)
def get_project(project_id: ProjectId, db: Db) -> Project:
    return find_project(db, project_id)


@router.patch('/{project_id}', response_model=ProjectView)
def update_project(project_id: ProjectId, data: ProjectUpdate, db: Db) -> Project:
    changes = data.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail='Provide non-null fields to update')
    project = find_project(db, project_id)
    for name, value in changes.items():
        setattr(project, name, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete('/{project_id}', status_code=204)
def delete_project(project_id: ProjectId, db: Db) -> Response:
    project = find_project(db, project_id)
    db.delete(project)
    db.commit()
    return Response(status_code=204)
