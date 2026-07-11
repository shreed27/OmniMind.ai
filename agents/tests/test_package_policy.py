from __future__ import annotations

import pytest

from app.runtime.package_policy import (
    PackagePolicyError,
    enforce_package_policy,
    install_packages,
    package_policy,
)


def test_approved_package_passes() -> None:
    enforce_package_policy(["requests", "pytest"])
    result = install_packages(["requests"])
    assert result.exit_status == 0
    assert "requests" in result.stdout


def test_unapproved_package_raises_policy_violation() -> None:
    with pytest.raises(PackagePolicyError):
        enforce_package_policy(["totally-fake-package"])


def test_install_timeout_aborts_after_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(package_policy, "timeout_seconds", 0)
    with pytest.raises(TimeoutError):
        install_packages(["pytest"])


def test_policy_allows_alias_forms() -> None:
    enforce_package_policy(["fs"])


def test_policy_rejects_mixed_packages() -> None:
    with pytest.raises(PackagePolicyError):
        enforce_package_policy(["requests", "evil"])
