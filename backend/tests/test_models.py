import pytest

from app.db.models import Event, Mission


def test_mission_model_defaults() -> None:
    mission = Mission(id="mission-1", objective="demo")
    assert mission.status == "created"
    assert mission.priority == "normal"


def test_event_model_defaults() -> None:
    event = Event(id="evt-1", name="Tested")
    assert event.name == "Tested"
    assert event.payload is None
