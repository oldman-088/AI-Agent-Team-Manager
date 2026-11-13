"""Explicit local, single-shot text completion; no autonomous task execution."""
import argparse
import asyncio
import os
import sys
import unicodedata
from collections.abc import Callable, Sequence

from app.providers.base import CompletionRequest, Provider
from app.providers.openai_adapter import OpenAIProvider

MAX_PROMPT_CHARS = 20_000
MAX_OUTPUT_TOKENS = 512
MAX_RESPONSE_CHARS = 100_000


def safe_terminal_text(text: str) -> str:
    """Remove terminal control/format characters from untrusted provider output."""
    return ''.join(char for char in text if char in '\n\t' or not unicodedata.category(char).startswith('C'))


async def complete_text(model: str, prompt: str, api_key: str, factory: Callable[[str], Provider]) -> int:
    if len(prompt) > MAX_PROMPT_CHARS:
        print('Input too long; nothing sent.', file=sys.stderr)
        return 2
    try:
        request = CompletionRequest(model=model, prompt=prompt, max_output_tokens=MAX_OUTPUT_TOKENS)
        provider = factory(api_key)
    except Exception:
        print('Invalid input or provider initialization failed; nothing sent.', file=sys.stderr)
        return 2
    try:
        result = await provider.complete(request)
    except Exception:
        print('Provider request failed; check local configuration and provider access.', file=sys.stderr)
        return 1
    finally:
        try:
            await provider.close()
        except Exception:
            print('Provider cleanup failed.', file=sys.stderr)
    text = safe_terminal_text(result.text[:MAX_RESPONSE_CHARS])
    print(text)
    if len(result.text) > MAX_RESPONSE_CHARS:
        print('Response truncated locally.', file=sys.stderr)
    if result.usage is not None:
        print(f'Input tokens: {result.usage.input_tokens}; output tokens: {result.usage.output_tokens}.', file=sys.stderr)
    else:
        print('Token usage unavailable.', file=sys.stderr)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Explicit, billable one-shot remote text completion; no tools or agent execution.')
    parser.add_argument('--model', required=True, help='Model ID available to your OpenAI account')
    parser.add_argument('--confirm-billable', action='store_true', help='Acknowledge possible charges')
    parser.add_argument('--confirm-data-transfer', action='store_true', help='Acknowledge input will be transmitted to OpenAI')
    args = parser.parse_args(argv)
    if not args.confirm_billable or not args.confirm_data_transfer:
        print('Nothing sent: both --confirm-billable and --confirm-data-transfer are required.', file=sys.stderr)
        return 2
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key.strip():
        print('Nothing sent: OPENAI_API_KEY is not configured.', file=sys.stderr)
        return 2
    try:
        # Bounded read, including one extra character to detect oversized input.
        prompt = sys.stdin.read(MAX_PROMPT_CHARS + 1)
    except (OSError, UnicodeError):
        print('Could not read input; nothing sent.', file=sys.stderr)
        return 2
    return asyncio.run(complete_text(args.model, prompt, api_key, OpenAIProvider.from_api_key))


if __name__ == '__main__':
    raise SystemExit(main())
