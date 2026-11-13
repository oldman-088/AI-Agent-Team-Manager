import os
import asyncio
from unittest.mock import AsyncMock, Mock
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import make_engine
from app.main import create_app
from app.services.task_runs import prepare_run, resolve_run, heartbeat_run, RunRejected
from app.task_worker import run_once
from app.task_scheduler import select_candidates, run_batch
from app.providers.base import CompletionResult, TokenUsage

BACKEND = Path(__file__).resolve().parents[1]


def test_liveness_and_unconfigured_readiness():
    with TestClient(create_app(Settings(None)), base_url='http://localhost') as client:
        assert client.get('/health/live').json() == {'status': 'ok'}
        response = client.get('/health/ready')
        assert response.status_code == 503
        assert response.json()['database'] == 'not_configured'


def test_unavailable_database_does_not_leak_details():
    with TestClient(create_app(Settings('sqlite:///missing-directory/no.db')), base_url='http://localhost') as client:
        response = client.get('/health/ready')
        assert response.status_code == 503
        assert response.json() == {'status': 'not_ready', 'database': 'unavailable'}


def test_migration_and_readiness(tmp_path, monkeypatch, capsys):
    # A dedicated PostgreSQL CI service is used when configured. SQLite is a local smoke test only.
    url = os.environ.get('AATM_TEST_DATABASE_URL') or f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    monkeypatch.setenv('AATM_DATABASE_URL', url)
    config = Config(str(BACKEND / 'alembic.ini'))
    engine = create_engine(url)
    try:
        command.upgrade(config, '0001')
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO projects (name) VALUES ('Existing')"))
        command.upgrade(config, 'head')
        with engine.begin() as connection:
            row = connection.execute(text('SELECT name, status FROM projects')).one()
            assert row == ('Existing', 'planned')
        # Upgrade must refuse pre-existing simultaneous runs for one agent without deleting history.
        command.downgrade(config, '0010')
        with engine.begin() as connection:
            p = connection.execute(text("INSERT INTO projects (name) VALUES ('Old runs') RETURNING id")).scalar_one()
            a = connection.execute(text("INSERT INTO agents (name, role, project_id) VALUES ('Old', 'QA', :p) RETURNING id"), {'p': p}).scalar_one()
            t1 = connection.execute(text("INSERT INTO tasks (project_id, title) VALUES (:p, 'Old 1') RETURNING id"), {'p': p}).scalar_one()
            t2 = connection.execute(text("INSERT INTO tasks (project_id, title) VALUES (:p, 'Old 2') RETURNING id"), {'p': p}).scalar_one()
            connection.execute(text("INSERT INTO task_runs (task_id, agent_id, status, model) VALUES (:t1, :a, 'running', 'mock'), (:t2, :a, 'uncertain', 'mock')"), {'t1': t1, 't2': t2, 'a': a})
        with pytest.raises(RuntimeError, match='multiple unresolved runs'):
            command.upgrade(config, 'head')
        with engine.begin() as connection:
            assert connection.execute(text('SELECT COUNT(*) FROM task_runs')).scalar_one() == 2
            connection.execute(text("UPDATE task_runs SET status = 'resolved' WHERE task_id = :t"), {'t': t2})
        command.upgrade(config, 'head')
        with engine.begin() as connection:
            connection.execute(text('DELETE FROM task_runs'))
            connection.execute(text('DELETE FROM tasks WHERE project_id = :p'), {'p': p})
            connection.execute(text('DELETE FROM agents WHERE project_id = :p'), {'p': p})
            connection.execute(text('DELETE FROM projects WHERE id = :p'), {'p': p})
        # Exercise the 0005 -> 0006 upgrade with pre-existing tasks and edges.
        command.downgrade(config, '0005')
        with engine.begin() as connection:
            existing_project = connection.execute(text('SELECT id FROM projects')).scalar_one()
            first_id = connection.execute(text("INSERT INTO tasks (project_id, title) VALUES (:p, 'existing A') RETURNING id"), {'p': existing_project}).scalar_one()
            second_id = connection.execute(text("INSERT INTO tasks (project_id, title) VALUES (:p, 'existing B') RETURNING id"), {'p': existing_project}).scalar_one()
            connection.execute(text('INSERT INTO task_dependencies (task_id, depends_on_id, project_id) VALUES (:a, :b, :p)'), {'a': first_id, 'b': second_id, 'p': existing_project})
        command.upgrade(config, 'head')
        with engine.begin() as connection:
            assert connection.execute(text('SELECT COUNT(*) FROM task_dependencies')).scalar_one() == 1
            connection.execute(text("UPDATE tasks SET status = 'completed' WHERE id = :id"), {'id': second_id})
        with pytest.raises(RuntimeError, match='Cannot downgrade'):
            command.downgrade(config, '0005')
        with engine.begin() as connection:
            assert connection.execute(text('SELECT COUNT(*) FROM task_dependencies')).scalar_one() == 1
            connection.execute(text('DELETE FROM task_dependencies'))
            connection.execute(text('DELETE FROM tasks'))
        command.downgrade(config, '0001')
        with engine.begin() as connection:
            assert connection.execute(text('SELECT name FROM projects')).scalar_one() == 'Existing'
        command.upgrade(config, 'head')
        with engine.begin() as connection:
            connection.execute(text('DELETE FROM projects'))
        assert 'projects' in inspect(engine).get_table_names()
        with TestClient(create_app(Settings(url)), base_url='http://localhost') as client:
            assert client.get('/health/ready').json() == {'status': 'ok', 'database': 'reachable'}
            assert client.post('/api/projects', json={'name': '  Demo  ', 'description': 'Test'}).status_code == 201
            projects = client.get('/api/projects').json()
            assert len(projects) == 1 and projects[0]['name'] == 'Demo'
            project_id = projects[0]['id']
            assert client.patch(f'/api/projects/{project_id}', json={'status': 'active'}).json()['status'] == 'active'
            assert client.get(f'/api/projects/{project_id}').json()['description'] == 'Test'
            assert client.post('/api/projects', json={'name': '  '}).status_code == 422
            assert client.patch(f'/api/projects/{project_id}', json={'status': 'bogus'}).status_code == 422
            assert client.patch(f'/api/projects/{project_id}', json={'name': None}).status_code == 422
            assert client.get('/api/projects?limit=101').status_code == 422
            assert client.post('/api/projects', json={'name': 'evil'}, headers={'origin': 'https://evil.example'}).status_code == 403
            assert client.post('/api/projects', json={'name': 'evil'}, headers={'host': 'evil.example'}).status_code == 403
            assert client.get('/api/projects', headers={'host': 'evil.example'}).status_code == 403
            assert client.post('/api/projects', content='name=x', headers={'content-type': 'application/x-www-form-urlencoded'}).status_code == 415
            assert client.delete(f'/api/projects/{project_id}', headers={'sec-fetch-site': 'cross-site'}).status_code == 403
            assert client.get('/api/projects/999999999999999999999').status_code == 422
            assert client.post('/api/agents', json={'name': 'x', 'role': 'qa', 'project_id': 2147483647}).status_code == 422
            assert client.post('/api/agents', json={'name': ' ', 'role': 'qa'}).status_code == 422
            result = client.post('/api/agents', json={'name': ' Ada ', 'role': 'Developer', 'project_id': project_id, 'provider': 'example', 'model': 'configured only'})
            assert result.status_code == 201
            agent = result.json()
            assert agent['name'] == 'Ada' and agent['execution_status'] == 'not_implemented'
            agent_id = agent['id']
            assert client.get('/api/agents').json()[0]['id'] == agent_id
            assert client.get(f'/api/agents/{agent_id}').json()['project_id'] == project_id
            assert client.patch(f'/api/agents/{agent_id}', json={'instructions': 'Review carefully'}).json()['instructions'] == 'Review carefully'
            assert client.patch(f'/api/agents/{agent_id}', json={'name': None}).status_code == 422
            assert client.patch(f'/api/agents/{agent_id}', json={'project_id': None}).json()['project_id'] is None
            assert client.patch(f'/api/agents/{agent_id}', json={'project_id': project_id}).json()['project_id'] == project_id
            assert client.post(f'/api/agents/{agent_id}/start', json={}).status_code == 404
            assert client.get('/api/agents?limit=101').status_code == 422
            assert client.patch(f'/api/agents/{agent_id}', json={'execution_status': 'running'}).status_code == 422
            # An event persistence failure must also roll back the task mutation.
            def fail_event(*args, **kwargs):
                raise SQLAlchemyError('simulated failure')
            with monkeypatch.context() as patch:
                patch.setattr('app.api.tasks.record_event', fail_event)
                assert client.post('/api/tasks', json={'project_id': project_id, 'title': 'Rollback'}).status_code == 503
            assert client.get(f'/api/tasks?project_id={project_id}').json() == []
            assert client.get(f'/api/events?project_id={project_id}').json() == []
            assert client.post('/api/tasks', json={'project_id': 2147483647, 'title': 'Missing'}).status_code == 422
            assert client.post('/api/tasks', json={'project_id': project_id, 'title': '   '}).status_code == 422
            response = client.post('/api/tasks', json={'project_id': project_id, 'title': '  Plan  ', 'description': 'Details'})
            assert response.status_code == 201
            task = response.json()
            assert task['title'] == 'Plan' and task['status'] == 'pending'
            task_id = task['id']
            events = client.get(f'/api/events?project_id={project_id}').json()
            assert events[0]['event_type'] == 'task.created' and events[0]['task_id'] == task_id
            assert 'Plan' not in str(events) and 'Details' not in str(events)
            assert client.get('/api/events?limit=101').status_code == 422
            assert client.get(f'/api/tasks?project_id={project_id}').json()[0]['id'] == task_id
            assert client.get('/api/tasks?project_id=2147483647').json() == []
            assert client.get('/api/tasks?limit=101').status_code == 422
            assignment_url = f'/api/tasks/{task_id}/assignment'
            assert client.get(assignment_url).json() == {'task_id': task_id, 'agent_id': None}
            assert client.put(assignment_url, json={}).status_code == 422
            assert client.put(assignment_url, json={'agent_id': 2147483647}).status_code == 404
            other_agent = client.post('/api/agents', json={'name': 'Unassigned', 'role': 'QA'}).json()['id']
            assert client.put(assignment_url, json={'agent_id': other_agent}).status_code == 422
            assert client.delete(f'/api/agents/{other_agent}').status_code == 204
            assert client.put(assignment_url, json={'agent_id': agent_id}).json()['agent_id'] == agent_id
            ready = client.get(f'/api/tasks/ready?project_id={project_id}&assigned_only=true').json()
            assert [item['id'] for item in ready] == [task_id]
            assert client.get('/api/tasks/ready?limit=101').status_code == 422
            assert client.get('/api/tasks/ready?offset=-1').status_code == 422
            assert client.put(assignment_url, json={'agent_id': agent_id}).status_code == 200
            assert client.patch(f'/api/agents/{agent_id}', json={'project_id': None}).status_code == 409
            assert client.delete(f'/api/agents/{agent_id}').status_code == 409
            history = client.get(f'/api/events?project_id={project_id}').json()
            assert sum(e['event_type'] == 'task.assigned' and e['task_id'] == task_id for e in history) == 1
            with pytest.raises(RuntimeError, match='task assignments exist'):
                command.downgrade(config, '0007')
            # SQLite may commit earlier DDL before the guard raises. Restore head.
            command.upgrade(config, 'head')
            assert client.put(assignment_url, json={'agent_id': None}).json()['agent_id'] is None
            assert client.put(assignment_url, json={'agent_id': agent_id}).status_code == 200
            # Durable claim serializes competing workers; no real provider requests occur.
            assert client.patch(f'/api/agents/{agent_id}', json={'provider': 'openai', 'model': 'mock-model', 'instructions': 'Private instruction'}).status_code == 200
            worker_engine = make_engine(url)
            try:
                barrier = Barrier(2)
                def claim():
                    barrier.wait(timeout=5)
                    with Session(worker_engine) as session:
                        try:
                            return prepare_run(session, task_id).run_id
                        except RunRejected:
                            return None
                with ThreadPoolExecutor(max_workers=2) as pool:
                    a, b = pool.submit(claim), pool.submit(claim)
                    results = [a.result(timeout=20), b.result(timeout=20)]
                assert sum(item is not None for item in results) == 1
                run_id = next(item for item in results if item is not None)
                running = client.get(f'/api/tasks/{task_id}/runs').json()[0]
                assert running['status'] == 'running' and running['heartbeat_state'] == 'fresh'
                with pytest.raises(RuntimeError, match='unresolved worker runs'):
                    command.downgrade(config, '0010')
                with worker_engine.begin() as connection:
                    connection.execute(text('UPDATE task_runs SET heartbeat_at = :ts WHERE id = :id'), {'id': run_id, 'ts': datetime.now(timezone.utc) - timedelta(minutes=3)})
                assert client.get(f'/api/tasks/{task_id}/runs').json()[0]['heartbeat_state'] == 'stale'
                with Session(worker_engine) as session:
                    assert heartbeat_run(session, run_id)
                assert client.get(f'/api/tasks/{task_id}/runs').json()[0]['heartbeat_state'] == 'fresh'
                with Session(worker_engine) as session:
                    assert resolve_run(session, run_id)
                    assert not heartbeat_run(session, run_id)
                with pytest.raises(RuntimeError, match='heartbeat data exists'):
                    command.downgrade(config, '0009')
                # SQLite can commit earlier downgrade DDL; restore head before continuing.
                command.upgrade(config, 'head')
                # Disposable test database: clear heartbeats to exercise the older history guard.
                with worker_engine.begin() as connection:
                    connection.execute(text('UPDATE task_runs SET heartbeat_at = NULL WHERE id = :id'), {'id': run_id})
                assert client.get(f'/api/tasks/{task_id}/runs').json()[0]['heartbeat_state'] == 'not_running'
                with pytest.raises(RuntimeError, match='task run history'):
                    command.downgrade(config, '0008')
                command.upgrade(config, 'head')
                monkeypatch.setattr('app.task_worker.HEARTBEAT_INTERVAL_SECONDS', 0.01)
                heartbeat_writer = Mock(wraps=__import__('app.task_worker', fromlist=['_write_heartbeat'])._write_heartbeat)
                monkeypatch.setattr('app.task_worker._write_heartbeat', heartbeat_writer)
                async def slow_success(_request):
                    await asyncio.sleep(0.08)
                    return CompletionResult('draft output', TokenUsage(7, 2))
                provider = Mock(complete=AsyncMock(side_effect=slow_success), close=AsyncMock())
                assert asyncio.run(run_once(worker_engine, task_id, 'test-key', lambda _: provider)) == 0
                assert heartbeat_writer.call_count > 0
                assert 'Private instruction' in provider.complete.await_args.args[0].prompt
                assert client.get(f'/api/tasks/{task_id}').json()['status'] == 'pending'
                runs = client.get(f'/api/tasks/{task_id}/runs').json()
                assert [r['status'] for r in runs] == ['succeeded', 'resolved']
                assert all(r['heartbeat_state'] == 'not_running' for r in runs)
                assert runs[0]['input_tokens'] == 7 and runs[0]['output_tokens'] == 2
                assert 'Private instruction' not in str(runs) and 'draft output' not in str(runs)
                assert 'draft output' in capsys.readouterr().out
                failed = Mock(complete=AsyncMock(side_effect=RuntimeError('secret')), close=AsyncMock())
                assert asyncio.run(run_once(worker_engine, task_id, 'key', lambda _: failed)) == 1
                uncertain = client.get(f'/api/tasks/{task_id}/runs').json()[0]
                assert uncertain['status'] == 'uncertain'
                assert 'secret' not in capsys.readouterr().err
                assert asyncio.run(run_once(worker_engine, task_id, 'key', lambda _: provider)) == 2
                assert client.delete(f'/api/tasks/{task_id}').status_code == 409
                with Session(worker_engine) as session:
                    assert resolve_run(session, uncertain['id'])
                    assert not resolve_run(session, uncertain['id'])
                # Disposable database only: history must be explicitly handled before downgrade/deletion.
                with worker_engine.begin() as connection:
                    connection.execute(text('DELETE FROM task_runs'))
            finally:
                worker_engine.dispose()
            second = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Second'}).json()['id']
            third = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Third'}).json()['id']
            other_project = client.post('/api/projects', json={'name': 'Separate'}).json()['id']
            other_task = client.post('/api/tasks', json={'project_id': other_project, 'title': 'Other'}).json()['id']
            edge = f'/api/tasks/{task_id}/dependencies/{second}'
            assert client.put(edge, json={}).status_code == 204
            assert client.put(edge, json={}).status_code == 204
            edge_events = client.get(f'/api/events?project_id={project_id}').json()
            assert sum(e['event_type'] == 'dependency.added' and e['task_id'] == task_id and e['related_task_id'] == second for e in edge_events) == 1
            assert client.get(f'/api/tasks/{task_id}/dependencies').json() == [second]
            assert client.put(f'/api/tasks/{second}/dependencies/{third}', json={}).status_code == 204
            assert client.put(f'/api/tasks/{third}/dependencies/{task_id}', json={}).status_code == 409
            assert client.put(f'/api/tasks/{task_id}/dependencies/{task_id}', json={}).status_code == 422
            assert client.put(f'/api/tasks/{task_id}/dependencies/{other_task}', json={}).status_code == 422
            # The database also prevents cross-project edges, independently of API checks.
            strict_engine = make_engine(url)
            try:
                with pytest.raises(IntegrityError):
                    with strict_engine.begin() as connection:
                        connection.execute(text('INSERT INTO task_dependencies (task_id, depends_on_id, project_id) VALUES (:a, :b, :p)'), {'a': task_id, 'b': other_task, 'p': project_id})
            finally:
                strict_engine.dispose()
            assert client.put(f'/api/tasks/{task_id}/dependencies/2147483647', json={}).status_code == 404
            assert client.delete(f'/api/tasks/{second}').status_code == 409
            assert not any(e['event_type'] == 'task.deleted' and e['task_id'] == second for e in client.get(f'/api/events?project_id={project_id}').json())
            assert client.delete(edge).status_code == 204
            assert client.delete(edge).status_code == 404
            assert client.delete(f'/api/tasks/{second}/dependencies/{third}').status_code == 204
            # Simultaneous opposing edges must not both commit and create a cycle.
            barrier = Barrier(2)
            def add_edge(source, target):
                barrier.wait(timeout=5)
                with TestClient(create_app(Settings(url)), base_url='http://localhost') as parallel_client:
                    return parallel_client.put(f'/api/tasks/{source}/dependencies/{target}', json={}).status_code
            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(add_edge, task_id, second)
                reverse = pool.submit(add_edge, second, task_id)
                outcomes = sorted([first.result(timeout=20), reverse.result(timeout=20)])
            assert outcomes == [204, 409]
            for source, target in [(task_id, second), (second, task_id)]:
                if client.get(f'/api/tasks/{source}/dependencies').json():
                    assert client.delete(f'/api/tasks/{source}/dependencies/{target}').status_code == 204
            assert client.delete(f'/api/tasks/{second}').status_code == 204
            assert client.delete(f'/api/tasks/{third}').status_code == 204
            # A pending prerequisite blocks manual completion until explicitly completed.
            lead = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Lead'}).json()['id']
            prerequisite = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Prerequisite'}).json()['id']
            assert client.put(f'/api/tasks/{lead}/dependencies/{prerequisite}', json={}).status_code == 204
            ready_ids = [item['id'] for item in client.get(f'/api/tasks/ready?project_id={project_id}').json()]
            assert lead not in ready_ids and prerequisite in ready_ids and ready_ids == sorted(ready_ids)
            assert client.get('/api/tasks/ready?project_id=2147483647').json() == []
            assert len(client.get(f'/api/tasks/ready?project_id={project_id}&limit=1').json()) == 1
            first_page = client.get(f'/api/tasks/ready?project_id={project_id}&limit=1').json()
            second_page = client.get(f'/api/tasks/ready?project_id={project_id}&limit=1&offset=1').json()
            assert second_page and first_page[0]['id'] != second_page[0]['id']
            assert client.get(f'/api/tasks/{lead}/readiness').json() == {'task_id': lead, 'ready': False, 'status': 'pending', 'blocking_dependencies': [prerequisite]}
            worker_engine = make_engine(url)
            try:
                with Session(worker_engine) as session:
                    with pytest.raises(RunRejected, match='completed prerequisites'):
                        prepare_run(session, lead)
            finally:
                worker_engine.dispose()
            assert client.post(f'/api/tasks/{lead}/complete', json={}).status_code == 409
            assert client.post(f'/api/tasks/{prerequisite}/complete', json={}).json()['status'] == 'completed'
            assert client.post(f'/api/tasks/{prerequisite}/cancel', json={}).status_code == 409
            assert client.get(f'/api/tasks/{lead}/readiness').json()['ready'] is True
            ready_ids = [item['id'] for item in client.get(f'/api/tasks/ready?project_id={project_id}').json()]
            assert lead in ready_ids and prerequisite not in ready_ids
            assert client.post(f'/api/tasks/{lead}/complete', json={}).json()['status'] == 'completed'
            assert client.post(f'/api/tasks/{lead}/complete', json={}).status_code == 200
            assert client.get(f'/api/tasks/{lead}/readiness').json()['ready'] is False
            assert client.put(f'/api/tasks/{lead}/dependencies/{task_id}', json={}).status_code == 409
            assert client.delete(f'/api/tasks/{lead}/dependencies/{prerequisite}').status_code == 204
            assert client.delete(f'/api/tasks/{lead}').status_code == 204
            assert client.delete(f'/api/tasks/{prerequisite}').status_code == 204
            blocked = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Blocked'}).json()['id']
            cancelled = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Cancelled'}).json()['id']
            assert client.put(f'/api/tasks/{blocked}/dependencies/{cancelled}', json={}).status_code == 204
            assert client.post(f'/api/tasks/{cancelled}/cancel', json={}).status_code == 200
            assert client.post(f'/api/tasks/{cancelled}/complete', json={}).status_code == 409
            assert client.get(f'/api/tasks/{blocked}/readiness').json()['blocking_dependencies'] == [cancelled]
            ready_ids = [item['id'] for item in client.get(f'/api/tasks/ready?project_id={project_id}').json()]
            assert blocked not in ready_ids and cancelled not in ready_ids
            assert client.post(f'/api/tasks/{blocked}/complete', json={}).status_code == 409
            assert client.delete(f'/api/tasks/{blocked}/dependencies/{cancelled}').status_code == 204
            assert client.delete(f'/api/tasks/{blocked}').status_code == 204
            assert client.delete(f'/api/tasks/{cancelled}').status_code == 204
            # Completion and dependency insertion must be serialized.
            race = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Race'}).json()['id']
            blocker = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Blocker'}).json()['id']
            barrier = Barrier(2)
            def race_action(complete):
                barrier.wait(timeout=5)
                with TestClient(create_app(Settings(url)), base_url='http://localhost') as parallel_client:
                    if complete:
                        return parallel_client.post(f'/api/tasks/{race}/complete', json={}).status_code
                    return parallel_client.put(f'/api/tasks/{race}/dependencies/{blocker}', json={}).status_code
            with ThreadPoolExecutor(max_workers=2) as pool:
                completion = pool.submit(race_action, True)
                insertion = pool.submit(race_action, False)
                completion_code, insertion_code = completion.result(timeout=20), insertion.result(timeout=20)
            assert (completion_code, insertion_code) in [(200, 409), (409, 204)]
            if insertion_code == 204:
                assert client.delete(f'/api/tasks/{race}/dependencies/{blocker}').status_code == 204
            assert client.delete(f'/api/tasks/{race}').status_code == 204
            assert client.delete(f'/api/tasks/{blocker}').status_code == 204
            # Agent move and assignment may race, but a mismatched committed association is forbidden.
            race_agent = client.post('/api/agents', json={'name': 'Race agent', 'role': 'QA', 'project_id': project_id}).json()['id']
            race_task = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Assignment race'}).json()['id']
            barrier = Barrier(2)
            def race_assignment(assign):
                barrier.wait(timeout=5)
                with TestClient(create_app(Settings(url)), base_url='http://localhost') as parallel_client:
                    if assign:
                        return parallel_client.put(f'/api/tasks/{race_task}/assignment', json={'agent_id': race_agent}).status_code
                    return parallel_client.patch(f'/api/agents/{race_agent}', json={'project_id': other_project}).status_code
            with ThreadPoolExecutor(max_workers=2) as pool:
                assigning = pool.submit(race_assignment, True)
                moving = pool.submit(race_assignment, False)
                assignment_code, move_code = assigning.result(timeout=20), moving.result(timeout=20)
            assert (assignment_code, move_code) in [(200, 409), (422, 200), (409, 200)]
            current = client.get(f'/api/tasks/{race_task}/assignment').json()['agent_id']
            agent_project = client.get(f'/api/agents/{race_agent}').json()['project_id']
            assert current is None or agent_project == project_id
            assert client.put(f'/api/tasks/{race_task}/assignment', json={'agent_id': None}).status_code == 200
            assert client.delete(f'/api/tasks/{race_task}').status_code == 204
            assert client.delete(f'/api/agents/{race_agent}').status_code == 204
            # One-shot scheduler is project scoped, sequential, bounded, and never retries history.
            batch_project = client.post('/api/projects', json={'name': 'Batch', 'status': 'active'}).json()['id']
            batch_agent = client.post('/api/agents', json={'name': 'Batch worker', 'role': 'QA', 'project_id': batch_project, 'provider': 'openai', 'model': 'mock-model'}).json()['id']
            batch_tasks = [client.post('/api/tasks', json={'project_id': batch_project, 'title': title}).json()['id'] for title in ['First', 'Second', 'Third', 'Blocked']]
            for item in batch_tasks:
                assert client.put(f'/api/tasks/{item}/assignment', json={'agent_id': batch_agent}).status_code == 200
            assert client.put(f'/api/tasks/{batch_tasks[3]}/dependencies/{batch_tasks[2]}', json={}).status_code == 204
            batch_engine = make_engine(url)
            try:
                with Session(batch_engine) as session:
                    assert select_candidates(session, batch_project, 2) == batch_tasks[:2]
                    assert select_candidates(session, batch_project, 20) == batch_tasks[:3]
                    assert select_candidates(session, other_project, 20) == []
                assert client.patch(f'/api/projects/{batch_project}', json={'status': 'paused'}).status_code == 200
                with Session(batch_engine) as session:
                    assert select_candidates(session, batch_project, 20) == []
                    with pytest.raises(RunRejected, match='active'):
                        prepare_run(session, batch_tasks[0], first_run_only=True, project_id=batch_project)
                assert client.patch(f'/api/projects/{batch_project}', json={'status': 'active'}).status_code == 200
                success = CompletionResult('draft', TokenUsage(1, 1))
                provider = Mock(complete=AsyncMock(side_effect=[success, RuntimeError('private secret'), success]), close=AsyncMock())
                assert asyncio.run(run_batch(batch_engine, batch_project, 3, 'key', lambda _: provider)) == 1
                assert provider.complete.await_count == 2
                assert client.get(f'/api/tasks/{batch_tasks[0]}/runs').json()[0]['status'] == 'succeeded'
                assert client.get(f'/api/tasks/{batch_tasks[1]}/runs').json()[0]['status'] == 'uncertain'
                assert client.get(f'/api/tasks/{batch_tasks[2]}/runs').json() == []
                assert client.get(f'/api/tasks/{batch_tasks[0]}').json()['status'] == 'pending'
                assert 'private secret' not in capsys.readouterr().err
                with Session(batch_engine) as session:
                    assert select_candidates(session, batch_project, 20) == [batch_tasks[2]]
                assert asyncio.run(run_once(batch_engine, batch_tasks[0], 'key', lambda _: provider, first_run_only=True, project_id=batch_project)) == 2
                assert provider.complete.await_count == 2
                # The uncertain run holds the agent slot even for a different task.
                assert asyncio.run(run_batch(batch_engine, batch_project, 20, 'key', lambda _: provider)) == 2
                assert provider.complete.await_count == 2
                uncertain_id = client.get(f'/api/tasks/{batch_tasks[1]}/runs').json()[0]['id']
                with Session(batch_engine) as session:
                    assert resolve_run(session, uncertain_id)
                assert asyncio.run(run_batch(batch_engine, batch_project, 20, 'key', lambda _: provider)) == 0
                assert provider.complete.await_count == 3
                with batch_engine.begin() as connection:
                    connection.execute(text('DELETE FROM task_runs WHERE task_id IN (SELECT id FROM tasks WHERE project_id = :project_id)'), {'project_id': batch_project})
            finally:
                batch_engine.dispose()
            assert client.delete(f'/api/tasks/{batch_tasks[3]}/dependencies/{batch_tasks[2]}').status_code == 204
            for item in batch_tasks:
                assert client.delete(f'/api/tasks/{item}').status_code == 204
            assert client.delete(f'/api/agents/{batch_agent}').status_code == 204
            assert client.delete(f'/api/projects/{batch_project}').status_code == 204
            # Global capacity serializes claims across projects/agents; uncertain runs retain a slot.
            capacity_project = client.post('/api/projects', json={'name': 'Capacity', 'status': 'active'}).json()['id']
            capacity_engine = make_engine(url)
            try:
                agents, task_ids, run_ids = [], [], []
                with capacity_engine.begin() as connection:
                    for index in range(21):
                        aid = connection.execute(text("INSERT INTO agents (name, role, project_id, provider, model) VALUES (:n, 'worker', :p, 'openai', 'mock') RETURNING id"), {'n': f'Agent {index}', 'p': capacity_project}).scalar_one()
                        tid = connection.execute(text("INSERT INTO tasks (project_id, title) VALUES (:p, :t) RETURNING id"), {'p': capacity_project, 't': f'Task {index}'}).scalar_one()
                        connection.execute(text('INSERT INTO task_assignments (task_id, agent_id, project_id) VALUES (:t, :a, :p)'), {'t': tid, 'a': aid, 'p': capacity_project})
                        agents.append(aid); task_ids.append(tid)
                        if index < 19:
                            rid = connection.execute(text("INSERT INTO task_runs (task_id, agent_id, status, model) VALUES (:t, :a, 'uncertain', 'mock') RETURNING id"), {'t': tid, 'a': aid}).scalar_one()
                            run_ids.append(rid)
                barrier = Barrier(2)
                def capacity_claim(tid):
                    barrier.wait(timeout=5)
                    with Session(capacity_engine) as session:
                        try:
                            return prepare_run(session, tid).run_id
                        except RunRejected:
                            return None
                with ThreadPoolExecutor(max_workers=2) as pool:
                    one = pool.submit(capacity_claim, task_ids[19]); two = pool.submit(capacity_claim, task_ids[20])
                    claims = [one.result(timeout=20), two.result(timeout=20)]
                assert sum(value is not None for value in claims) == 1
                with capacity_engine.begin() as connection:
                    assert connection.execute(text("SELECT COUNT(*) FROM task_runs WHERE status IN ('running', 'uncertain')")).scalar_one() == 20
                    extra = connection.execute(text("INSERT INTO tasks (project_id, title) VALUES (:p, 'Same agent') RETURNING id"), {'p': capacity_project}).scalar_one()
                    connection.execute(text('INSERT INTO task_assignments (task_id, agent_id, project_id) VALUES (:t, :a, :p)'), {'t': extra, 'a': agents[0], 'p': capacity_project})
                with Session(capacity_engine) as session:
                    assert resolve_run(session, run_ids[1])
                with Session(capacity_engine) as session:
                    with pytest.raises(RunRejected, match='agent has an unresolved run'):
                        prepare_run(session, extra)
                with pytest.raises(IntegrityError):
                    with capacity_engine.begin() as connection:
                        connection.execute(text("INSERT INTO task_runs (task_id, agent_id, status, model) VALUES (:t, :a, 'running', 'mock')"), {'t': extra, 'a': agents[0]})
                with capacity_engine.begin() as connection:
                    connection.execute(text('DELETE FROM task_runs WHERE task_id IN (SELECT id FROM tasks WHERE project_id = :p)'), {'p': capacity_project})
                    connection.execute(text('DELETE FROM task_assignments WHERE project_id = :p'), {'p': capacity_project})
                    connection.execute(text('DELETE FROM tasks WHERE project_id = :p'), {'p': capacity_project})
                    connection.execute(text('DELETE FROM agents WHERE project_id = :p'), {'p': capacity_project})
            finally:
                capacity_engine.dispose()
            assert client.delete(f'/api/projects/{capacity_project}').status_code == 204
            assert client.delete(f'/api/tasks/{other_task}').status_code == 204
            assert client.delete(f'/api/projects/{other_project}').status_code == 204
            assert client.patch(f'/api/tasks/{task_id}', json={'title': 'Updated'}).json()['title'] == 'Updated'
            assert client.patch(f'/api/tasks/{task_id}', json={'status': 'running'}).status_code == 422
            assert client.post(f'/api/tasks/{task_id}/cancel', json={}).json()['status'] == 'cancelled'
            assert client.put(assignment_url, json={'agent_id': None}).status_code == 200
            assert client.put(assignment_url, json={'agent_id': agent_id}).status_code == 409
            assert client.post(f'/api/tasks/{task_id}/cancel', json={}).json()['status'] == 'cancelled'
            history = client.get(f'/api/events?project_id={project_id}').json()
            assert sum(e['event_type'] == 'task.cancelled' and e['task_id'] == task_id for e in history) == 1
            assert client.post('/api/tasks/2147483647/cancel', json={}).status_code == 404
            assert client.delete(f'/api/projects/{project_id}').status_code == 409
            assert client.get(f'/api/tasks/{task_id}').status_code == 200
            assert client.delete(f'/api/tasks/{task_id}').status_code == 204
            assert client.get(f'/api/tasks/{task_id}').status_code == 404
            deleted_events = client.get(f'/api/events?project_id={project_id}').json()
            assert any(e['event_type'] == 'task.deleted' and e['task_id'] is None for e in deleted_events)
            assert client.delete(f'/api/projects/{project_id}').status_code == 204
            assert client.get(f'/api/events?project_id={project_id}').json() == []
            assert any(e['project_id'] is None for e in client.get('/api/events').json())
            assert client.get(f'/api/agents/{agent_id}').json()['project_id'] is None
            assert client.delete(f'/api/agents/{agent_id}').status_code == 204
            assert client.get(f'/api/agents/{agent_id}').status_code == 404
            assert client.get(f'/api/projects/{project_id}').status_code == 404
        with pytest.raises(RuntimeError, match='activity events exist'):
            command.downgrade(config, 'base')
        # Disposable test DB only: explicitly remove history to test the reverse migration.
        with engine.begin() as connection:
            connection.execute(text('DELETE FROM activity_events'))
        command.downgrade(config, 'base')
        assert 'projects' not in inspect(engine).get_table_names()
    finally:
        engine.dispose()
