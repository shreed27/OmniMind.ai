from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Any


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extras = {key: value for key, value in record.__dict__.items() if key not in logging.LogRecord(...) and not key.startswith("_")}
        extras.pop("message", None)
        extras.pop("msg", None)
        extras.pop("args", None)
        extras.pop("exc_info", None)
        extras.pop("exc_text", None)
        extras.pop("stack_info", None)
        extras = {str(key): value for key, value in extras.items() if value is not None}
        if extras:
            return f"{base} extras={extras}"
        return base


def setup_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"structured": {"()": StructuredFormatter}},
            "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "structured"}},
            "root": {"level": level, "handlers": ["console"]},
        }
    )
