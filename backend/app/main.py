from __future__ import annotations

import logging
from typing import Generator

from fastapi import FastAPI

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

    @application.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

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
