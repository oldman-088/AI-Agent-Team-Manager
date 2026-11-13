import asyncio
from unittest.mock import AsyncMock, Mock

from app.provider_probe import MAX_OUTPUT_TOKENS, PROBE_PROMPT, main, run_probe
from app.providers.base import CompletionResult, TokenUsage


def test_probe_requires_explicit_confirmation_and_key(monkeypatch, capsys):
    factory = Mock()
    monkeypatch.setattr('app.provider_probe.OpenAIProvider.from_api_key', factory)
    monkeypatch.setenv('OPENAI_API_KEY', 'secret-key')
    assert main(['--model', 'example']) == 2
    factory.assert_not_called()
    monkeypatch.delenv('OPENAI_API_KEY')
    assert main(['--model', 'example', '--confirm-billable']) == 2
    factory.assert_not_called()
    assert 'secret-key' not in capsys.readouterr().err


def test_probe_bounded_fixed_prompt_and_no_content_disclosure(capsys):
    provider = Mock(complete=AsyncMock(return_value=CompletionResult('private response', TokenUsage(5, 1))), close=AsyncMock())
    factory = Mock(return_value=provider)
    assert asyncio.run(run_probe('model', 'secret-key', factory)) == 0
    request = provider.complete.await_args.args[0]
    assert request.prompt == PROBE_PROMPT and request.max_output_tokens == MAX_OUTPUT_TOKENS
    assert request.model == 'model'
    factory.assert_called_once_with('secret-key')
    provider.close.assert_awaited_once()
    output = capsys.readouterr()
    assert 'Input tokens: 5; output tokens: 1' in output.out
    assert 'private response' not in output.out and 'secret-key' not in output.out + output.err


def test_probe_redacts_errors_and_closes(capsys):
    provider = Mock(complete=AsyncMock(side_effect=RuntimeError('private-key and prompt')), close=AsyncMock())
    assert asyncio.run(run_probe('model', 'private-key', lambda _: provider)) == 1
    provider.close.assert_awaited_once()
    output = capsys.readouterr()
    assert 'private-key' not in output.err and 'prompt' not in output.err
    assert 'Provider probe failed' in output.err


def test_probe_rejects_invalid_model_before_provider_creation(capsys):
    factory = Mock()
    assert asyncio.run(run_probe(' ', 'key', factory)) == 1
    factory.assert_not_called()
    assert 'Unable to initialize' in capsys.readouterr().err
