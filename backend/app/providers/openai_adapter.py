"""Official OpenAI SDK adapter for non-streaming, text-only Responses calls.

No tools, automatic execution, pricing, model discovery or credential storage.
"""
from typing import Any

from openai import AsyncOpenAI
from app.providers.base import CompletionRequest, CompletionResult, ProviderError, TokenUsage


class OpenAIProvider:
    def __init__(self, client: Any):
        self._client = client

    @classmethod
    def from_api_key(cls, api_key: str) -> 'OpenAIProvider':
        if not api_key or not api_key.strip():
            raise ValueError('OpenAI API key is required')
        # No implicit retry: a retry can incur duplicate cost. Never log credentials.
        return cls(AsyncOpenAI(api_key=api_key, base_url='https://api.openai.com/v1', timeout=30.0, max_retries=0))

    async def complete(self, request: CompletionRequest) -> CompletionResult:
        try:
            response = await self._client.responses.create(
                model=request.model, input=request.prompt, max_output_tokens=request.max_output_tokens,
                store=False,
            )
            # Do not treat partial/incomplete or failed output as a successful result.
            if response.status != 'completed':
                raise ProviderError('Provider response was not completed')
            text = response.output_text
            if not isinstance(text, str) or not text:
                raise ProviderError('Provider returned no text')
            usage = response.usage
            tokens = None
            if usage is not None:
                input_tokens, output_tokens = usage.input_tokens, usage.output_tokens
                if type(input_tokens) is not int or type(output_tokens) is not int or input_tokens < 0 or output_tokens < 0:
                    raise ProviderError('Provider returned invalid usage')
                tokens = TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens)
            return CompletionResult(text=text, usage=tokens)
        except ProviderError:
            raise
        except Exception:
            # Upstream errors can include secrets or request content; do not propagate them.
            raise ProviderError('Provider request failed') from None

    async def close(self) -> None:
        await self._client.close()
