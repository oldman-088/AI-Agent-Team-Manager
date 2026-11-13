"""Explicit configuration. Credentials are supplied by the runtime, not the repository."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str | None

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(database_url=os.environ.get("AATM_DATABASE_URL") or None)
