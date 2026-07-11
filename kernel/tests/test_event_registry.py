from __future__ import annotations

from kernel.core.event_registry import EventRegistry


def test_event_registry_known_names() -> None:
    assert "MissionCreated" in EventRegistry.defined_events()
    assert "ReflectionStarted" in EventRegistry.defined_events()


def test_event_registry_canonical_definition() -> None:
    definition = EventRegistry.canonical_definition("MissionCreated")
    assert definition["description"].startswith("Mission")
