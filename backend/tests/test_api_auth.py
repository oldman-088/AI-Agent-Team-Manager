import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app

TOKEN = 'test_' + 'a' * 40


def test_optional_bearer_gate_and_health_are_separate():
    with TestClient(create_app(Settings(None, api_token=TOKEN)), base_url='http://localhost') as client:
        assert client.get('/health/live').status_code == 200
        for headers in [{}, {'Authorization': 'Bearer incorrect'}, {'Authorization': 'Basic ' + TOKEN}, {'Authorization': 'Bearer ' + TOKEN + 'x'}]:
            response = client.get('/api/tasks', headers=headers)
            assert response.status_code == 401
            assert response.headers['cache-control'] == 'no-store'
            assert TOKEN not in response.text
        # Correct credentials reach the service (which has no DB in this test).
        assert client.get('/api/tasks', headers={'Authorization': 'Bearer ' + TOKEN}).status_code == 503
        assert client.get('/api/tasks', headers={'Authorization': 'bearer ' + TOKEN, 'host': 'evil.example'}).status_code == 403
        assert client.post('/api/tasks', headers={'Authorization': 'Bearer ' + TOKEN, 'origin': 'https://evil.example'}, json={}).status_code == 403
        assert client.get('/openapi.json').status_code == 200


def test_invalid_tokens_fail_without_echoing_secret():
    for token in ('short', 'x' * 31, 'x' * 257, '💥' * 32, 'with spaces' * 4):
        with pytest.raises(ValueError) as exc:
            Settings(None, api_token=token)
        assert token not in str(exc.value)
    assert TOKEN not in repr(Settings(None, api_token=TOKEN))


def test_empty_configured_environment_token_is_not_silently_disabled(monkeypatch):
    monkeypatch.setenv('AATM_API_TOKEN', '')
    with pytest.raises(ValueError):
        Settings.from_environment()


def test_default_remains_unauthenticated_and_requires_explicit_configuration(monkeypatch):
    monkeypatch.delenv('AATM_API_TOKEN', raising=False)
    assert Settings.from_environment().api_token is None
    with TestClient(create_app(Settings(None)), base_url='http://localhost') as client:
        assert client.get('/api/tasks').status_code == 503
