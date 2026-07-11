from __future__ import annotations

import pytest

from backend.core.pii_scrub import PIIScrubber


def test_scrub_redacts_secret_strings() -> None:
    scrubber = PIIScrubber()
    result, detected = scrubber.scrub({"notes": "secret token: AIzaSyD00000000000000000000000"})
    assert detected is True
    assert "AIza" not in str(result)


def test_scrub_keeps_clean_payload() -> None:
    scrubber = PIIScrubber()
    result, detected = scrubber.scrub({"notes": "no secrets here"})
    assert detected is False
    assert result["notes"] == "no secrets here"


def test_scrub_records_batch() -> None:
    scrubber = PIIScrubber()
    records = [{"token": "sk-1234567890"}, {"summary": "ok"}]
    sanitized = scrubber.scrub_records(records)
    assert "REDACTED" in str(sanitized[0])
    assert sanitized[1]["summary"] == "ok"
