from __future__ import annotations

import logging
import sys
from typing import Any


class StructuredFormatter(logging.Formatter):
    _BASE_KEYS = {
        "name",
        "msg",
        "args",
        "created",
        "relativeCreated",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "pathname",
        "filename",
        "module",
        "levelname",
        "levelno",
        "msecs",
        "thread",
        "threadName",
        "processName",
        "process",
    }

    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            base["exception"] = self.formatException(record.exc_info)
        extra = {k: v for k, v in record.__dict__.items() if k not in self._BASE_KEYS}
        if extra:
            base["extra"] = extra
        return " ".join(f'{k}="{v}"' for k, v in base.items() if v is not None)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root.addHandler(handler)
    for name in ("uvicorn.access", "uvicorn.error", "uvicorn"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False
