from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_EVENTS_PATH = REPO_ROOT / "docs" / "registry" / "EVENTS.md"


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing registry: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    entries: dict[str, Any] = {"version": 1, "events": []}
    for line in lines:
        line = line.strip()
        if not line.startswith("-"):
            continue
        value = line.lstrip("- ").split(":")[0].strip()
        if value:
            entries["events"].append(value)
    return entries


def get_registry_path() -> Path:
    return REGISTRY_EVENTS_PATH


def normalize_event(envelope: dict[str, Any]) -> dict[str, Any]:
    payload = envelope.get("payload")
    context = envelope.get("context")
    return {
        "id": envelope.get("id"),
        "name": envelope.get("name"),
        "payload_hash": _stable_json_hash(payload),
        "context_hash": _stable_json_hash(context),
        "mission_id": envelope.get("mission_id"),
        "created_at": envelope.get("created_at"),
    }


def replay_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_event(event) for event in events]


def _stable_json_hash(data: Any) -> str:
    return json.dumps(data, sort_keys=True, default=str)
