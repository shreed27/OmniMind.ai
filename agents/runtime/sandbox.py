from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeResult:
    exit_status: int
    stdout: str = ""
    stderr: str = ""
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: int = 0

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class Sandbox:
    def __init__(self, policy: Any) -> None:
        self.policy = policy

    def is_allowed(self, capability: str) -> bool:
        return capability in self.policy.allowlist
