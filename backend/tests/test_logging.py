from __future__ import annotations

import logging

from fastapi.testclient import TestClient

from app.core.logging import StructuredFormatter, setup_logging


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_structured_formatter_adds_extra_when_present() -> None:
    handler = ListHandler()
    handler.setFormatter(StructuredFormatter())
    logger = logging.getLogger("test.formatter")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("hello %s", "world", extra={"trace_id": "xyz", "confidence": 0.9})

    assert len(handler.records) == 1
    record = handler.records[0]
    assert record.getMessage() == "hello world"
    assert record.trace_id == "xyz"
    assert record.confidence == 0.9


def test_setup_logging_does_not_crash() -> None:
    setup_logging(level="INFO")
    logger = logging.getLogger("test.setup")
    logger.info("ping")

    assert True


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
