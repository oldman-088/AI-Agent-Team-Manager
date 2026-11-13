"""Migrations require an explicitly configured database URL."""
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models import Base

config = context.config
url = os.environ.get("AATM_DATABASE_URL")
if not url:
    raise RuntimeError("AATM_DATABASE_URL must be configured for migrations")
config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
