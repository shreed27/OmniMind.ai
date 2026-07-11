from __future__ import annotations

import pytest

from backend.core.security import RBACEnforcer
from app.core.exceptions import ForbiddenError


def test_anonymous_is_forbidden() -> None:
    with pytest.raises(ForbiddenError):
        RBACEnforcer.enforce("Anonymous", "read", "Mission", "mission-1")


def test_user_can_read() -> None:
    RBACEnforcer.enforce("User", "read", "Mission", "mission-1")


def test_user_cannot_write() -> None:
    with pytest.raises(ForbiddenError):
        RBACEnforcer.enforce("User", "write", "Mission", "mission-1")


def test_ceo_can_do_anything() -> None:
    RBACEnforcer.enforce("CEO", "write", "Mission", "mission-1")
