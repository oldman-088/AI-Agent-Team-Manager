"""Application factory: liveness is independent from database readiness."""
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.api.projects import router as projects_router
from app.api.agents import router as agents_router
from app.api.tasks import router as tasks_router
from app.api.dependencies import router as dependencies_router
from app.api.events import router as events_router
from app.api.assignments import router as assignments_router
from app.security import LocalGuard
from app.config import Settings
from app.database import check_database, make_engine


def create_app(settings: Settings | None = None, engine_factory: Callable[[str], Engine] = make_engine) -> FastAPI:
    settings = settings or Settings.from_environment()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.engine = engine_factory(settings.database_url) if settings.database_url else None
        try:
            yield
        finally:
            if application.state.engine is not None:
                application.state.engine.dispose()

    application = FastAPI(title="AATM API", version="0.1.0", lifespan=lifespan)
    application.add_middleware(LocalGuard)
    application.include_router(projects_router)
    application.include_router(agents_router)
    application.include_router(tasks_router)
    application.include_router(dependencies_router)
    application.include_router(events_router)
    application.include_router(assignments_router)

    @application.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/ready")
    def ready() -> JSONResponse:
        engine = application.state.engine
        if engine is None:
            return JSONResponse({"status": "not_ready", "database": "not_configured"}, status_code=503)
        try:
            check_database(engine)
        except SQLAlchemyError:
            # Do not expose connection strings, credentials or database details.
            return JSONResponse({"status": "not_ready", "database": "unavailable"}, status_code=503)
        return JSONResponse({"status": "ok", "database": "reachable"})

    return application


app = create_app()
