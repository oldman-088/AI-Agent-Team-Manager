"""Start a disposable SQLite-backed server for automated browser tests only.

This script deliberately ignores runtime database configuration and always creates
an isolated temporary database. Never point browser tests at user data.
"""
import os
import tempfile
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config

BACKEND = Path(__file__).resolve().parent


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='aatm-e2e-') as directory:
        os.environ['AATM_DATABASE_URL'] = f"sqlite:///{(Path(directory) / 'test.sqlite3').as_posix()}"
        # Always use a non-secret, test-only token; never inherit user credentials.
        os.environ['AATM_API_TOKEN'] = 'e2e_' + 'a' * 40
        command.upgrade(Config(str(BACKEND / 'alembic.ini')), 'head')
        uvicorn.run('app.main:app', host='127.0.0.1', port=8018, log_level='warning')


if __name__ == '__main__':
    main()
