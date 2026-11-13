"""Database connection and connectivity probe."""
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine


def make_engine(url: str) -> Engine:
    engine = create_engine(url, pool_pre_ping=True, hide_parameters=True)
    if engine.dialect.name == 'sqlite':
        @event.listens_for(engine, 'connect')
        def enable_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute('PRAGMA foreign_keys=ON')
            finally:
                cursor.close()
    return engine


def check_database(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
