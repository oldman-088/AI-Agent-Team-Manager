"""Durable manual text runs; no scheduler, tools or automatic task completion."""
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import lock_project
from app.api.tasks import blocking_dependencies
from app.models import Agent, Project, TaskAssignment, TaskRun
from app.providers.base import CompletionRequest, CompletionResult


class RunRejected(Exception):
    pass


@dataclass(frozen=True)
class PreparedRun:
    run_id: int
    request: CompletionRequest


def prepare_run(db: Session, task_id: int, *, first_run_only: bool = False, project_id: int | None = None) -> PreparedRun:
    """Claim a pending, ready, assigned task while holding the project lock."""
    try:
        task = lock_project(db, task_id)
    except HTTPException as exc:
        raise RunRejected('Task unavailable') from exc
    if project_id is not None and task.project_id != project_id:
        raise RunRejected('Task project changed')
    if first_run_only and db.get(Project, task.project_id).status != 'active':
        raise RunRejected('Project must be active for batch execution')
    if task.status != 'pending' or blocking_dependencies(db, task_id):
        raise RunRejected('Task must be pending and have completed prerequisites')
    if db.scalar(select(TaskRun.id).where(TaskRun.task_id == task_id, TaskRun.status.in_(['running', 'uncertain']))) is not None:
        raise RunRejected('Task has an unresolved run')
    if first_run_only and db.scalar(select(TaskRun.id).where(TaskRun.task_id == task_id).limit(1)) is not None:
        raise RunRejected('Task already has run history; batch never retries')
    assignment = db.get(TaskAssignment, task_id)
    agent = db.get(Agent, assignment.agent_id) if assignment else None
    if agent is None or agent.project_id != task.project_id:
        raise RunRejected('Task requires an agent assigned to the same project')
    if agent.provider.strip().lower() != 'openai':
        raise RunRejected('Assigned agent must explicitly use provider openai')
    # Snapshot database content before external call. No tools or privileged instructions.
    prompt = f'Role: {agent.role}\nInstructions:\n{agent.instructions}\n\nTask: {task.title}\nDetails:\n{task.description}'
    try:
        request = CompletionRequest(model=agent.model, prompt=prompt, max_output_tokens=512)
    except ValueError as exc:
        raise RunRejected('Assigned agent model or task input is invalid') from exc
    run = TaskRun(task_id=task.id, agent_id=agent.id, status='running', model=agent.model, heartbeat_at=func.now())
    db.add(run)
    try:
        db.flush()
        result = PreparedRun(run_id=run.id, request=request)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise RunRejected('Task already has an unresolved run or changed concurrently') from exc
    return result


def finish_run(db: Session, run_id: int, result: CompletionResult | None) -> bool:
    """A provider failure is uncertain: no retry until an operator resolves it."""
    values = {'status': 'succeeded' if result is not None else 'uncertain', 'finished_at': datetime.now(timezone.utc)}
    if result and result.usage:
        values.update(input_tokens=result.usage.input_tokens, output_tokens=result.usage.output_tokens)
    changed = db.execute(update(TaskRun).where(TaskRun.id == run_id, TaskRun.status == 'running').values(**values)).rowcount
    db.commit()
    return bool(changed)


def resolve_run(db: Session, run_id: int) -> bool:
    # Explicit human action only; never assert success or automatically retry.
    changed = db.execute(update(TaskRun).where(TaskRun.id == run_id, TaskRun.status.in_(['running', 'uncertain']))
                         .values(status='resolved', finished_at=datetime.now(timezone.utc))).rowcount
    db.commit()
    return bool(changed)


def heartbeat_run(db: Session, run_id: int) -> bool:
    """Record a best-effort worker heartbeat only while the claim is running."""
    changed = db.execute(update(TaskRun).where(TaskRun.id == run_id, TaskRun.status == 'running')
                         .values(heartbeat_at=func.now())).rowcount
    db.commit()
    return bool(changed)
