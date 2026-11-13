from unittest.mock import Mock

from app.task_worker import main


def test_cli_rejects_without_both_acknowledgements_before_database(monkeypatch, capsys):
    factory = Mock()
    monkeypatch.setattr('app.task_worker.make_engine', factory)
    monkeypatch.setenv('AATM_DATABASE_URL', 'sqlite:///not-used')
    monkeypatch.setenv('OPENAI_API_KEY', 'secret')
    assert main(['run', '--task-id', '1', '--confirm-billable']) == 2
    assert main(['run', '--task-id', '1', '--confirm-data-transfer']) == 2
    assert main(['run', '--task-id', '0', '--confirm-billable', '--confirm-data-transfer']) == 2
    assert main(['resolve', '--run-id', '1']) == 2
    factory.assert_not_called()
    assert 'secret' not in capsys.readouterr().err
