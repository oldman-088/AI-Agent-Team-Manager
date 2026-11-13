import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.config import Settings
from app.main import create_app

BACKEND = Path(__file__).resolve().parents[1]


def test_liveness_and_unconfigured_readiness():
    with TestClient(create_app(Settings(None))) as client:
        assert client.get('/health/live').json() == {'status': 'ok'}
        response = client.get('/health/ready')
        assert response.status_code == 503
        assert response.json()['database'] == 'not_configured'


def test_unavailable_database_does_not_leak_details():
    with TestClient(create_app(Settings('sqlite:///missing-directory/no.db'))) as client:
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
        command.upgrade(config, 'head')
        assert 'projects' in inspect(engine).get_table_names()
        with TestClient(create_app(Settings(url))) as client:
            assert client.get('/health/ready').json() == {'status': 'ok', 'database': 'reachable'}
        command.downgrade(config, 'base')
        assert 'projects' not in inspect(engine).get_table_names()
    finally:
        engine.dispose()
