from unittest.mock import Mock
from app.task_scheduler import main


def test_batch_requires_both_confirmations_and_bounded_project_and_limit(monkeypatch):
    engine = Mock()
    monkeypatch.setattr('app.task_scheduler.make_engine', engine)
    monkeypatch.setenv('AATM_DATABASE_URL', 'sqlite:///unused')
    monkeypatch.setenv('OPENAI_API_KEY', 'secret')
    assert main(['--project-id', '1', '--max-tasks', '2', '--confirm-billable']) == 2
    assert main(['--project-id', '1', '--max-tasks', '21', '--confirm-billable', '--confirm-data-transfer']) == 2
    assert main(['--project-id', '0', '--max-tasks', '1', '--confirm-billable', '--confirm-data-transfer']) == 2
    engine.assert_not_called()
