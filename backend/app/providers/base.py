"""Minimal provider contract; additional capabilities require explicit support."""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CompletionRequest:
    model: str
    prompt: str
    max_output_tokens: int = 512

    def __post_init__(self) -> None:
        if not isinstance(self.model, str) or not self.model.strip() or len(self.model) > 200:
            raise ValueError('model must contain 1–200 characters')
        if not isinstance(self.prompt, str) or not self.prompt.strip() or len(self.prompt) > 100_000:
            raise ValueError('prompt must contain 1–100000 characters')
        if type(self.max_output_tokens) is not int or not 1 <= self.max_output_tokens <= 4096:
            raise ValueError('max_output_tokens must be an integer from 1 to 4096')


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class CompletionResult:
    text: str
    usage: TokenUsage | None


class ProviderError(Exception):
    """Sanitized provider failure safe to surface without upstream details."""


class Provider(Protocol):
    async def complete(self, request: CompletionRequest) -> CompletionResult: ...
    async def close(self) -> None: ...
