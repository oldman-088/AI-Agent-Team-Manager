"""Manual one-shot task text generation. Never starts tools or completes a task."""
import argparse
import asyncio
import os
import sys
from collections.abc import Callable, Sequence

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.database import make_engine
from app.provider_text import MAX_RESPONSE_CHARS, safe_terminal_text
from app.providers.base import Provider
from app.providers.openai_adapter import OpenAIProvider
from app.services.task_runs import RunRejected, finish_run, heartbeat_run, prepare_run, resolve_run


HEARTBEAT_INTERVAL_SECONDS = 5.0


def _write_heartbeat(engine: Engine, run_id: int) -> bool:
    with Session(engine) as db:
        return heartbeat_run(db, run_id)


async def _heartbeat_loop(engine: Engine, run_id: int, stop: asyncio.Event) -> None:
    while True:
        try:
            await asyncio.wait_for(stop.wait(), timeout=HEARTBEAT_INTERVAL_SECONDS)
            return
        except TimeoutError:
            try:
                if not await asyncio.to_thread(_write_heartbeat, engine, run_id):
                    return
            except Exception:
                print('Heartbeat update failed; run liveness may be unknown.', file=sys.stderr)
                return


async def run_once(engine: Engine, task_id: int, key: str, factory: Callable[[str], Provider], *, first_run_only: bool = False, project_id: int | None = None) -> int:
    try:
        with Session(engine) as db:
            prepared = prepare_run(db, task_id, first_run_only=first_run_only, project_id=project_id)
    except RunRejected as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception:
        print('Unable to claim task; check database and migrations.', file=sys.stderr)
        return 1
    print(f'Run #{prepared.run_id} claimed. Task data will be sent to OpenAI.', file=sys.stderr)
    provider = None
    result = None
    stop = asyncio.Event()
    heartbeat = asyncio.create_task(_heartbeat_loop(engine, prepared.run_id, stop))
    try:
        provider = factory(key)
        result = await provider.complete(prepared.request)
    except Exception:
        # A timeout or connection failure does not prove the remote call did not occur.
        print('Provider outcome uncertain; no automatic retry.', file=sys.stderr)
    finally:
        stop.set()
        await heartbeat
        if provider is not None:
            try:
                await provider.close()
            except Exception:
                print('Provider cleanup failed.', file=sys.stderr)
    try:
        with Session(engine) as db:
            if not finish_run(db, prepared.run_id, result):
                print('Run status changed externally; result suppressed.', file=sys.stderr)
                return 1
    except Exception:
        print('Unable to persist run outcome; result suppressed. Inspect the run before retrying.', file=sys.stderr)
        return 1
    if result is None:
        print(f'Run #{prepared.run_id} requires manual resolution.', file=sys.stderr)
        return 1
    print(safe_terminal_text(result.text[:MAX_RESPONSE_CHARS]))
    if len(result.text) > MAX_RESPONSE_CHARS:
        print('Response truncated locally.', file=sys.stderr)
    if result.usage:
        print(f'Input tokens: {result.usage.input_tokens}; output tokens: {result.usage.output_tokens}.', file=sys.stderr)
    print('Generation succeeded; task remains pending until manually completed.', file=sys.stderr)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Local manual task text worker; does not complete tasks or run tools.')
    sub = parser.add_subparsers(dest='action', required=True)
    run = sub.add_parser('run', help='Explicitly generate text for an assigned task')
    run.add_argument('--task-id', type=int, required=True)
    run.add_argument('--confirm-billable', action='store_true')
    run.add_argument('--confirm-data-transfer', action='store_true')
    resolve = sub.add_parser('resolve', help='Release an unresolved run after manual investigation')
    resolve.add_argument('--run-id', type=int, required=True)
    resolve.add_argument('--confirm-worker-stopped', action='store_true')
    args = parser.parse_args(argv)
    if args.action == 'run' and (not args.confirm_billable or not args.confirm_data_transfer or not 1 <= args.task_id <= 2147483647):
        print('Valid task ID and both billing and data-transfer confirmations required.', file=sys.stderr)
        return 2
    if args.action == 'resolve' and (not args.confirm_worker_stopped or not 1 <= args.run_id <= 2147483647):
        print('Valid run ID and --confirm-worker-stopped required.', file=sys.stderr)
        return 2
    key = os.environ.get('OPENAI_API_KEY', '') if args.action == 'run' else ''
    url = os.environ.get('AATM_DATABASE_URL', '')
    if not url or (args.action == 'run' and not key.strip()):
        print('Required database or provider configuration missing.', file=sys.stderr)
        return 2
    engine = None
    try:
        engine = make_engine(url)
        if args.action == 'run':
            return asyncio.run(run_once(engine, args.task_id, key, OpenAIProvider.from_api_key))
        with Session(engine) as db:
            if not resolve_run(db, args.run_id):
                print('Run not found or not unresolved.', file=sys.stderr)
                return 2
        print('Run resolved without asserting success; any remote outcome remains unknown.')
        return 0
    except Exception:
        print('Database operation failed; inspect state before retrying.', file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
