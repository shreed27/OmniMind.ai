from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Any


_SIGNING_KEY = "omnimiind-kernel-event-v1"


@dataclass(frozen=True)
class EventEnvelope:
    """Immutable canonical event envelope for EnterpriseOS."""
    name: str
    payload: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def event_id(self) -> str:
        payload_hash = self.payload_hash or ""
        ctx_hash = hashlib.sha256(
            str(sorted(self.context.items())).encode()
        ).hexdigest()[:12]
        raw = f"{self.name}:{payload_hash}:{ctx_hash}"
        return hmac.new(
            _SIGNING_KEY.encode(), raw.encode(), hashlib.sha256
        ).hexdigest()

    @property
    def payload_hash(self) -> str:
        try:
            material = str(sorted(self.payload.items())).encode()
        except TypeError as exc:  # pragma: no cover - defensive
            raise ValueError("Event payload must be JSON serializable") from exc
        return hashlib.sha256(material).hexdigest()
