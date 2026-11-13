import asyncio
import io
from unittest.mock import AsyncMock, Mock

from app.provider_text import MAX_OUTPUT_TOKENS, MAX_PROMPT_CHARS, complete_text, main
from app.providers.base import CompletionResult, TokenUsage


def test_explicit_flags_and_key_checked_before_read(monkeypatch, capsys):
    source = Mock()
    factory = Mock()
    monkeypatch.setattr('sys.stdin', source)
    monkeypatch.setattr('app.provider_text.OpenAIProvider.from_api_key', factory)
    monkeypatch.setenv('OPENAI_API_KEY', 'secret')
    assert main(['--model', 'model', '--confirm-billable']) == 2
    source.read.assert_not_called()
    monkeypatch.delenv('OPENAI_API_KEY')
    assert main(['--model', 'model', '--confirm-billable', '--confirm-data-transfer']) == 2
    source.read.assert_not_called()
    factory.assert_not_called()
    assert 'secret' not in capsys.readouterr().err


def test_valid_request_and_safe_output(capsys):
    provider = Mock(complete=AsyncMock(return_value=CompletionResult('Hello\x1b[31m\u202eWorld', TokenUsage(3, 4))), close=AsyncMock())
    assert asyncio.run(complete_text('model', 'user input', 'key', lambda _: provider)) == 0
    req = provider.complete.await_args.args[0]
    assert req.prompt == 'user input' and req.max_output_tokens == MAX_OUTPUT_TOKENS
    provider.close.assert_awaited_once()
    out = capsys.readouterr()
    assert '\x1b' not in out.out and '\u202e' not in out.out and 'World' in out.out
    assert 'Input tokens: 3; output tokens: 4' in out.err
    assert 'user input' not in out.err and 'key' not in out.err


def test_rejects_empty_or_oversize_without_client(capsys):
    factory = Mock()
    assert asyncio.run(complete_text('model', ' ', 'key', factory)) == 2
    assert asyncio.run(complete_text('model', 'x' * (MAX_PROMPT_CHARS + 1), 'key', factory)) == 2
    factory.assert_not_called()
    assert 'nothing sent' in capsys.readouterr().err.lower()


def test_sanitizes_provider_failure_and_closes(capsys):
    provider = Mock(complete=AsyncMock(side_effect=RuntimeError('key private prompt')), close=AsyncMock())
    assert asyncio.run(complete_text('model', 'private prompt', 'key', lambda _: provider)) == 1
    provider.close.assert_awaited_once()
    err = capsys.readouterr().err
    assert 'key' not in err and 'private prompt' not in err


def test_main_reads_bounded_input_and_calls_provider(monkeypatch, capsys):
    provider = Mock(complete=AsyncMock(return_value=CompletionResult('response', None)), close=AsyncMock())
    monkeypatch.setenv('OPENAI_API_KEY', 'key')
    monkeypatch.setattr('sys.stdin', io.StringIO('sample'))
    monkeypatch.setattr('app.provider_text.OpenAIProvider.from_api_key', lambda _: provider)
    assert main(['--model', 'model', '--confirm-billable', '--confirm-data-transfer']) == 0
    assert provider.complete.await_args.args[0].prompt == 'sample'
    assert capsys.readouterr().out == 'response\n'
