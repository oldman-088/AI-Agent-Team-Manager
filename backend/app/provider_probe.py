"""Opt-in local OpenAI connectivity probe; no agent or task execution.

May transmit a fixed test prompt and incur charges; never invoked by the API.
"""
import argparse
import asyncio
import os
import sys
from collections.abc import Callable, Sequence

from app.providers.base import CompletionRequest, Provider
from app.providers.openai_adapter import OpenAIProvider

PROBE_PROMPT = 'Reply with the single word OK.'
MAX_OUTPUT_TOKENS = 32


async def run_probe(model: str, api_key: str, factory: Callable[[str], Provider]) -> int:
    """Never echo prompts, provider text, credentials or upstream exceptions."""
    try:
        request = CompletionRequest(model=model, prompt=PROBE_PROMPT, max_output_tokens=MAX_OUTPUT_TOKENS)
        provider = factory(api_key)
    except Exception:
        print('Unable to initialize provider probe.', file=sys.stderr)
        return 1
    try:
        result = await provider.complete(request)
    except Exception:
        print('Provider probe failed. Check local configuration and provider access.', file=sys.stderr)
        return 1
    finally:
        try:
            await provider.close()
        except Exception:
            # Cleanup error may contain private details; never echo it.
            print('Provider cleanup failed.', file=sys.stderr)
    print('Provider probe completed; response text is not displayed or stored.')
    if result.usage is None:
        print('Token usage unavailable.')
    else:
        print(f'Input tokens: {result.usage.input_tokens}; output tokens: {result.usage.output_tokens}.')
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Explicit local paid OpenAI text probe; never runs an agent.')
    parser.add_argument('--model', required=True, help='Explicit model ID available to your OpenAI account')
    parser.add_argument('--confirm-billable', action='store_true', help='Acknowledge remote data transfer and potential charges')
    args = parser.parse_args(argv)
    if not args.confirm_billable:
        print('Probe not run: pass --confirm-billable to acknowledge remote transfer and possible charges.', file=sys.stderr)
        return 2
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key.strip():
        print('Probe not run: OPENAI_API_KEY is not configured.', file=sys.stderr)
        return 2
    return asyncio.run(run_probe(args.model, api_key, OpenAIProvider.from_api_key))


if __name__ == '__main__':
    raise SystemExit(main())
