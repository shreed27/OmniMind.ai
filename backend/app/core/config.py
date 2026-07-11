from __future__ import annotations

import logging
import os
from logging.config import dictConfig
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "omnimind-backend"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite+aiosqlite:///./dev.db"
    redis_url: str = "redis://localhost:6379/0"
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "omnimind"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60


def get_settings() -> Settings:
    return Settings()


def configure_logging(level: str | None = None) -> None:
    level = level or get_settings().log_level
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                },
                "structured": {
                    "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "structured",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {
                "level": level,
                "handlers": ["console"],
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def enrich_event_context(context: dict[str, Any]) -> dict[str, Any]:
    """Enrich event/trace context with application metadata."""
    enriched = dict(context)
    enriched.setdefault("app", get_settings().app_name)
    enriched.setdefault("env", get_settings().app_env)
    return enriched
