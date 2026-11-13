import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.database import make_engine
from app.main import create_app

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


def test_migration_and_readiness(tmp_path, monkeypatch):
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
            assert client.post('/api/tasks', json={'project_id': 2147483647, 'title': 'Missing'}).status_code == 422
            assert client.post('/api/tasks', json={'project_id': project_id, 'title': '   '}).status_code == 422
            response = client.post('/api/tasks', json={'project_id': project_id, 'title': '  Plan  ', 'description': 'Details'})
            assert response.status_code == 201
            task = response.json()
            assert task['title'] == 'Plan' and task['status'] == 'pending'
            task_id = task['id']
            assert client.get(f'/api/tasks?project_id={project_id}').json()[0]['id'] == task_id
            assert client.get('/api/tasks?project_id=2147483647').json() == []
            assert client.get('/api/tasks?limit=101').status_code == 422
            second = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Second'}).json()['id']
            third = client.post('/api/tasks', json={'project_id': project_id, 'title': 'Third'}).json()['id']
            other_project = client.post('/api/projects', json={'name': 'Separate'}).json()['id']
            other_task = client.post('/api/tasks', json={'project_id': other_project, 'title': 'Other'}).json()['id']
            edge = f'/api/tasks/{task_id}/dependencies/{second}'
            assert client.put(edge, json={}).status_code == 204
            assert client.put(edge, json={}).status_code == 204
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
            assert client.delete(f'/api/tasks/{other_task}').status_code == 204
            assert client.delete(f'/api/projects/{other_project}').status_code == 204
            assert client.patch(f'/api/tasks/{task_id}', json={'title': 'Updated'}).json()['title'] == 'Updated'
            assert client.patch(f'/api/tasks/{task_id}', json={'status': 'running'}).status_code == 422
            assert client.post(f'/api/tasks/{task_id}/cancel', json={}).json()['status'] == 'cancelled'
            assert client.post(f'/api/tasks/{task_id}/cancel', json={}).json()['status'] == 'cancelled'
            assert client.post('/api/tasks/2147483647/cancel', json={}).status_code == 404
            assert client.delete(f'/api/projects/{project_id}').status_code == 409
            assert client.get(f'/api/tasks/{task_id}').status_code == 200
            assert client.delete(f'/api/tasks/{task_id}').status_code == 204
            assert client.get(f'/api/tasks/{task_id}').status_code == 404
            assert client.delete(f'/api/projects/{project_id}').status_code == 204
            assert client.get(f'/api/agents/{agent_id}').json()['project_id'] is None
            assert client.delete(f'/api/agents/{agent_id}').status_code == 204
            assert client.get(f'/api/agents/{agent_id}').status_code == 404
            assert client.get(f'/api/projects/{project_id}').status_code == 404
        command.downgrade(config, 'base')
        assert 'projects' not in inspect(engine).get_table_names()
    finally:
        engine.dispose()
