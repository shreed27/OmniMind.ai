from __future__ import annotations

from logging.config import dictConfig
from pathlib import Path

from app.core.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = REPO_ROOT / "alembic.ini"
VERSIONS_DIR = REPO_ROOT / "alembic" / "versions"


def setup_logging(level: str | None = None) -> None:
    level = level or get_settings().log_level
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structured": {
                    "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "structured",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"level": level, "handlers": ["console"]},
        }
    )
