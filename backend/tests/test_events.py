from __future__ import annotations


from app.core.config import get_settings
from app.core.events import emit


def test_emit_returns_envelope() -> None:
    envelope = emit("Tested", {"value": 1}, {"trace_id": "abc"})
    assert envelope.name == "Tested"
    assert envelope.payload == {"value": 1}
    assert envelope.context["trace_id"] == "abc"
    assert envelope.context["app"] == get_settings().app_name
    assert envelope.context["env"] == get_settings().app_env


def test_emit_enriches_context() -> None:
    envelope = emit("Enriched", {})
    assert envelope.context["app"] == get_settings().app_name
    assert envelope.context["env"] == get_settings().app_env
