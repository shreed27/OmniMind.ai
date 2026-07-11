from __future__ import annotations

import logging
import re
from typing import Any, Sequence

logger = logging.getLogger("audit.pii")

_SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z\\-_]{35}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)secret"),
]


class PIIScrubber:
    def scrub(self, payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        serialized = _serialize(payload)
        detected = False
        for pattern in _SECRET_PATTERNS:
            if pattern.search(serialized):
                detected = True
                logger.warning("secret pattern detected")
                break
        if detected:
            return self._redact(payload), detected
        return payload, detected

    def scrub_records(self, records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        scrubbed = []
        for record in records:
            sanitized, _ = self.scrub(record)
            scrubbed.append(sanitized)
        return scrubbed

    def _redact(self, payload: dict[str, Any]) -> dict[str, Any]:
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, dict):
                redacted[key] = self._redact(value)
            elif isinstance(value, str):
                redacted[key] = _redact_string(value)
            else:
                redacted[key] = value
        return redacted


def _serialize(payload: dict[str, Any]) -> str:
    return str(payload)


def _redact_string(value: str) -> str:
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value
