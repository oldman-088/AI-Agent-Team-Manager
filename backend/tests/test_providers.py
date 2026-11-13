import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.providers.base import CompletionRequest, ProviderError
from app.providers.openai_adapter import OpenAIProvider


def run(coro):
    return asyncio.run(coro)


def test_openai_adapter_text_usage_and_safe_options():
    response = SimpleNamespace(status='completed', output_text='Hello', usage=SimpleNamespace(input_tokens=4, output_tokens=2))
    client = SimpleNamespace(responses=SimpleNamespace(create=AsyncMock(return_value=response)), close=AsyncMock())
    provider = OpenAIProvider(client)
    result = run(provider.complete(CompletionRequest(model='example-model', prompt='hello', max_output_tokens=42)))
    assert result.text == 'Hello' and result.usage.input_tokens == 4 and result.usage.output_tokens == 2
    client.responses.create.assert_awaited_once_with(model='example-model', input='hello', max_output_tokens=42, store=False)
    run(provider.close())
    client.close.assert_awaited_once()


def test_optional_usage_and_failure_sanitization():
    client = SimpleNamespace(responses=SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(status='completed', output_text='ok', usage=None))))
    provider = OpenAIProvider(client)
    assert run(provider.complete(CompletionRequest('model', 'prompt'))).usage is None
    client.responses.create.side_effect = RuntimeError('secret or private request')
    with pytest.raises(ProviderError, match='Provider request failed') as exc:
        run(provider.complete(CompletionRequest('model', 'prompt')))
    assert 'secret' not in str(exc.value)


@pytest.mark.parametrize('status,text,usage', [
    ('incomplete', 'partial', None), ('failed', '', None), ('completed', '', None),
    ('completed', 'x', SimpleNamespace(input_tokens=-1, output_tokens=2)),
])
def test_invalid_provider_output_is_not_success(status, text, usage):
    client = SimpleNamespace(responses=SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(status=status, output_text=text, usage=usage))))
    with pytest.raises(ProviderError):
        run(OpenAIProvider(client).complete(CompletionRequest('model', 'prompt')))


def test_request_validation_and_client_configuration(monkeypatch):
    for args in [('', 'hi', 1), ('model', ' ', 1), ('model', 'hi', 0), ('model', 'hi', 4097), ('model', 'hi', True)]:
        with pytest.raises(ValueError):
            CompletionRequest(*args)
    factory = Mock()
    monkeypatch.setattr('app.providers.openai_adapter.AsyncOpenAI', factory)
    with pytest.raises(ValueError):
        OpenAIProvider.from_api_key(' ')
    OpenAIProvider.from_api_key('private-key')
    factory.assert_called_once_with(api_key='private-key', base_url='https://api.openai.com/v1', timeout=30.0, max_retries=0)


def test_official_sdk_request_with_mock_transport():
    import json
    import httpx
    from openai import AsyncOpenAI

    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={
            'id': 'resp_test', 'object': 'response', 'created_at': 1,
            'model': 'example-model', 'status': 'completed',
            'output': [{'id': 'msg_test', 'type': 'message', 'role': 'assistant', 'status': 'completed',
                        'content': [{'type': 'output_text', 'text': 'SDK works', 'annotations': []}]}],
            'usage': {'input_tokens': 3, 'output_tokens': 2, 'total_tokens': 5},
        })

    async def exercise():
        http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        sdk = AsyncOpenAI(api_key='test-only', http_client=http, max_retries=0)
        provider = OpenAIProvider(sdk)
        try:
            result = await provider.complete(CompletionRequest('example-model', 'Hello'))
            assert result.text == 'SDK works' and result.usage.output_tokens == 2
        finally:
            await provider.close()

    run(exercise())
    assert seen[0].url.path.endswith('/responses')
    assert json.loads(seen[0].content)['store'] is False
