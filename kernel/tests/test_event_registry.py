from __future__ import annotations

import pytest

from kernel.core.event_registry import InvalidEventError, load_event_registry, validate_event


def test_validate_event_raises_on_missing_field() -> None:
    with pytest.raises(InvalidEventError):
        validate_event({"name": "x"})


def test_load_event_registry_returns_events() -> None:
    registry = load_event_registry("docs/registry/EVENTS.md")
    assert "events" in registry
    assert isinstance(registry["events"], list)
