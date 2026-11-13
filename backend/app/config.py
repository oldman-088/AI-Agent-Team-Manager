"""Explicit configuration. Credentials are supplied by the runtime, not the repository."""
import os
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    api_token: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.api_token is not None and not re.fullmatch(r'[A-Za-z0-9_-]{32,256}', self.api_token):
            raise ValueError('AATM_API_TOKEN must be a 32–256 character URL-safe token')

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(database_url=os.environ.get("AATM_DATABASE_URL") or None, api_token=os.environ.get("AATM_API_TOKEN"))
