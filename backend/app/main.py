from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.v1.departments import router as departments_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.managed_agents import router as managed_agents_router
from backend.app.api.v1.missions import router as missions_router
from backend.app.api.v1.organizations import router as organizations_router
from backend.app.api.v1.workers import router as workers_router
from app.core.config import get_settings
from app.core.events import emit


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    application.include_router(health_router)
    application.include_router(managed_agents_router)
    application.include_router(missions_router)
    application.include_router(organizations_router)
    application.include_router(departments_router)
    application.include_router(workers_router)

    @application.on_event("startup")
    async def _on_startup() -> None:
        emit(
            name="AppStarted",
            payload={"app": settings.app_name, "env": settings.app_env},
        )

    @application.on_event("shutdown")
    async def _on_shutdown() -> None:
        emit(
            name="AppStopped",
            payload={"app": settings.app_name, "env": settings.app_env},
        )

    return application


app = create_app()
