from __future__ import annotations

from typing import Any

from app.core.exceptions import ForbiddenError


class RBACEnforcer:
    @staticmethod
    def enforce(role: str | None, action: str, target_type: str, target_id: str) -> None:
        if role == "Anonymous":
            raise ForbiddenError("Anonymous role is not allowed to perform any action.")
        allowed = _PERMISSIONS.get(role, {}).get(action, set())
        if target_type not in allowed:
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
    "CEO": {"*"},
    "CTO": {"read", "write", "execute", "structure", "security"},
    "COO": {"read", "write", "execute"},
    "CFO": {"read", "write", "execute", "structure", "security"},
    "CMO": {"read", "write", "execute", "structure", "security"},
    "CRO": {"read", "write", "execute", "structure", "security"},
    "CSO": {"read", "write", "execute", "structure", "security"},
    "CLO": {"read", "write", "execute", "structure", "security"},
    "CIO": {"read", "write", "execute", "structure", "security"},
    "Manager": {"read", "write", "execute", "structure"},
    "Worker": {"read", "execute"},
    "Specialist": {"read", "execute"},
    "User": {"read"},
}
