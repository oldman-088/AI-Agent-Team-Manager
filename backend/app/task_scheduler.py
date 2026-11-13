"""Explicit one-shot sequential scheduler, not a background service or retry queue."""
import argparse
import asyncio
import os
import sys
from collections.abc import Callable, Sequence

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, aliased

from app.database import make_engine
from app.models import Agent, Project, Task, TaskAssignment, TaskDependency, TaskRun
from app.providers.base import Provider
from app.providers.openai_adapter import OpenAIProvider
from app.task_worker import run_once

MAX_BATCH = 20


def select_candidates(db: Session, project_id: int, limit: int) -> list[int]:
    """Advisory selection only: prepare_run rechecks under the project lock."""
    if not 1 <= limit <= MAX_BATCH or not 1 <= project_id <= 2147483647:
        raise ValueError('Invalid batch bounds')
    prerequisite = aliased(Task)
    blocked = (select(TaskDependency.task_id).join(prerequisite, prerequisite.id == TaskDependency.depends_on_id)
               .where(TaskDependency.task_id == Task.id, prerequisite.status != 'completed').exists())
    has_history = select(TaskRun.id).where(TaskRun.task_id == Task.id).exists()
    query = (select(Task.id).join(Project, Project.id == Task.project_id)
             .join(TaskAssignment, TaskAssignment.task_id == Task.id)
             .join(Agent, Agent.id == TaskAssignment.agent_id)
             .where(Task.project_id == project_id, Project.status == 'active', Task.status == 'pending',
                    Agent.project_id == Task.project_id, func.lower(func.trim(Agent.provider)) == 'openai',
                    func.length(func.trim(Agent.model)) > 0, ~blocked, ~has_history)
             .order_by(Task.id).limit(limit))
    return list(db.scalars(query))


async def run_batch(engine: Engine, project_id: int, limit: int, key: str, factory: Callable[[str], Provider]) -> int:
    try:
        with Session(engine) as db:
            ids = select_candidates(db, project_id, limit)
    except Exception:
        print('Unable to select tasks; check database and migrations.', file=sys.stderr)
        return 1
    if not ids:
        print('No eligible tasks; no provider calls made.', file=sys.stderr)
        return 0
    print(f'Selected {len(ids)} tasks; at most {limit} requests. Each claim will be rechecked.', file=sys.stderr)
    for task_id in ids:
        # The first-run check is repeated inside the same locked transaction as the claim.
        # Stopping on all failures avoids silently moving on after an uncertain billed call.
        print(f'Task #{task_id}:', file=sys.stderr)
        code = await run_once(engine, task_id, key, factory, first_run_only=True, project_id=project_id)
        if code != 0:
            print('Batch stopped; inspect task and run state before continuing.', file=sys.stderr)
            return code
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='One-shot sequential, project-scoped text batch; can incur charges.')
    parser.add_argument('--project-id', type=int, required=True)
    parser.add_argument('--max-tasks', type=int, required=True, help='Maximum provider requests in this batch (1–20)')
    parser.add_argument('--dry-run', action='store_true', help='Read-only candidate preview; no provider calls or claims')
    parser.add_argument('--confirm-billable', action='store_true')
    parser.add_argument('--confirm-data-transfer', action='store_true')
    args = parser.parse_args(argv)
    if (not 1 <= args.project_id <= 2147483647 or not 1 <= args.max_tasks <= MAX_BATCH
            or (not args.dry_run and (not args.confirm_billable or not args.confirm_data_transfer))):
        print('Valid project and batch bounds and both confirmations are required.', file=sys.stderr)
        return 2
    key = os.environ.get('OPENAI_API_KEY', '')
    url = os.environ.get('AATM_DATABASE_URL', '')
    if not url or (not args.dry_run and not key.strip()):
        print('Required database or provider configuration missing.', file=sys.stderr)
        return 2
    engine = None
    try:
        engine = make_engine(url)
        if args.dry_run:
            with Session(engine) as db:
                ids = select_candidates(db, args.project_id, args.max_tasks)
            print('Preview only; no claims or provider calls. Candidates are snapshots and may change.')
            for task_id in ids:
                print(f'Task #{task_id}')
            if not ids:
                print('No eligible tasks in this snapshot.')
            return 0
        return asyncio.run(run_batch(engine, args.project_id, args.max_tasks, key, OpenAIProvider.from_api_key))
    except Exception:
        print('Batch failed; inspect state before retrying.', file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
