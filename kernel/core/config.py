from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings


@dataclass(slots=True, frozen=True)
class KernelSettings:
    app_env: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_kernel_settings() -> KernelSettings:
    s = get_settings()
    return KernelSettings(app_env=s.app_env, log_level=s.log_level)


def enrich_event_context(context: dict[str, Any]) -> dict[str, Any]:
    settings = get_kernel_settings()
    context.setdefault("app_env", settings.app_env)
    return context


