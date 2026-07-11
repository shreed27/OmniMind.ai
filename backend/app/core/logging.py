from __future__ import annotations

import logging
import sys
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            base["exception"] = self.formatException(record.exc_info)
        extra = {k: v for k, v in record.__dict__.items() if k not in logging.LogRecord("").__dict__}
        if extra:
            base["extra"] = extra
        payload = " ".join(f'{k}="{v}"' for k, v in {**base, "message": base["message"]}.items() if v is not None)
        return payload


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root.addHandler(handler)
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.error").handlers.clear()
    logging.getLogger("uvicorn").handlers.clear()
    logging.getLogger("uvicorn.access").addHandler(handler)
    logging.getLogger("uvicorn.error").addHandler(handler)
