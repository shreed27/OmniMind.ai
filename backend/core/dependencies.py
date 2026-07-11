from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request

from app.core.exceptions import ForbiddenError
from backend.core.security import RBACEnforcer


class CurrentUser:
    def __init__(self, role: str = "User", user_id: str | None = None) -> None:
        self.role = role
        self.user_id = user_id


def get_current_user(request: Request) -> CurrentUser:
    role = request.headers.get("X-Role", "User")
    user_id = request.headers.get("X-User-Id")
    return CurrentUser(role=role, user_id=user_id)


def require_permission(action: str, target_type: str) -> Any:
    def checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        try:
            RBACEnforcer.enforce(current_user.role, action, target_type, target_type)
        except ForbiddenError as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail={"code": exc.code, "context": exc.context},
            ) from exc
        return current_user

    return checker
