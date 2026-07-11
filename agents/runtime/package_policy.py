from __future__ import annotations

from typing import Any

from app.runtime.python_runtime import RuntimeExecutionError
from app.runtime.sandbox import RuntimeResult


class PolicyViolationError(Exception):
    pass


class PackagePolicy:
    def __init__(self, allowlist: set[str] | None = None, timeout_seconds: int = 120) -> None:
        self.allowlist = allowlist or {
            "requests",
            "httpx",
            "pydantic",
            "sqlalchemy",
            "pandas",
            "pytest",
            "black",
            "ruff",
            "fastapi",
            "uvicorn",
        }
        self.timeout_seconds = timeout_seconds

    def enforce(self, packages: list[str]) -> None:
        unapproved = [package for package in packages if package not in self.allowlist]
        if unapproved:
            raise PolicyViolationError(f"Disallowed packages: {unapproved}")

    def should_abort_install(self, attempt: int, exit_status: int) -> bool:
        return attempt >= 3 or exit_status not in {0, 1}


package_policy = PackagePolicy()


def enforce_package_policy(packages: list[str]) -> None:
    package_policy.enforce(packages)


def install_packages(packages: list[str]) -> RuntimeResult:
    enforce_package_policy(packages)
    return RuntimeResult(exit_status=0, stdout=f"installed: {packages}", artifacts=[{"type": "package-lock", "content_ref": "packages"}])
