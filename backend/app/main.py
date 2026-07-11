from __future__ import annotations


from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.managed_agents import router as managed_agents_router
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
