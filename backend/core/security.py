from __future__ import annotations

from typing import Any

from app.core.exceptions import ForbiddenError


class RBACEnforcer:
    @staticmethod
    def enforce(role: str | None, action: str, target_type: str, target_id: str) -> None:
        if role == "Anonymous" or not role:
            raise ForbiddenError("Anonymous role is not allowed to perform any action.")
        role_actions = _PERMISSIONS.get(role, {})
        if "*" in role_actions or "*" in role_actions.get("*", set()):
            return
        allowed = role_actions.get(action, set())
        if "*" in allowed or target_type in allowed:
            return
        raise ForbiddenError(
            f"{role} is not allowed to perform {action} on {target_type}",
            context={
                "role": role,
                "action": action,
                "target_type": target_type,
                "target_id": target_id,
            },
        )


_PERMISSIONS: dict[str, dict[str, set[str]]] = {
    "CEO": {"*": {"*"}},
    "CTO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
        "security": {"*"},
    },
    "COO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
    },
    "CFO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
        "security": {"*"},
    },
    "CMO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
        "security": {"*"},
    },
    "CRO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
        "security": {"*"},
    },
    "CSO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
        "security": {"*"},
    },
    "CLO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
        "security": {"*"},
    },
    "CIO": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
        "security": {"*"},
    },
    "Manager": {
        "read": {"*"},
        "write": {"*"},
        "execute": {"*"},
        "structure": {"*"},
    },
    "Worker": {
        "read": {"*"},
        "execute": {"*"},
    },
    "Specialist": {
        "read": {"*"},
        "execute": {"*"},
    },
    "User": {
        "read": {"Mission", "Department", "Worker", "Task", "Artifact", "Memory"},
    },
}
