from __future__ import annotations

class InvalidEventError(Exception):
    """Raised when an event violates schema or state rules."""
