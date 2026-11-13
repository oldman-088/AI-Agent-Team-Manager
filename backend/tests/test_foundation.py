import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from app.config import Settings
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
            assert client.delete(f'/api/projects/{project_id}').status_code == 204
            assert client.get(f'/api/projects/{project_id}').status_code == 404
        command.downgrade(config, 'base')
        assert 'projects' not in inspect(engine).get_table_names()
    finally:
        engine.dispose()
