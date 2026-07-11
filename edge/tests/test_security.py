"""Tests for Edge Security - TASK-12.4"""

from __future__ import annotations

from edge.security import EdgeSecurityPolicy


def test_filesystem_access_whitelist() -> None:
    """Edge runtime allows only whitelisted filesystem paths."""
    policy = EdgeSecurityPolicy()

    policy.allow_filesystem_access("/tmp/mission-1")

    assert policy.check_filesystem_access("/tmp/mission-1/data.json") is True
    assert policy.check_filesystem_access("/etc/passwd") is False


def test_api_access_blocking() -> None:
    """Edge runtime blocks specified APIs during offline mode."""
    policy = EdgeSecurityPolicy()

    policy.block_api("secrets_service")

    assert policy.check_api_access("secrets_service") is False
    assert policy.check_api_access("memory_service") is True


def test_network_egress_blocked() -> None:
    """Network egress blocked during edge mode except localhost."""
    policy = EdgeSecurityPolicy()

    assert policy.check_network_egress("127.0.0.1") is True
    assert policy.check_network_egress("localhost") is True
    assert policy.check_network_egress("api.openai.com") is False


def test_audit_logging() -> None:
    """Edge operations are logged for security audit."""
    policy = EdgeSecurityPolicy()

    # Should not raise
    policy.audit_edge_operation("file_write", {"path": "/tmp/mission-1/artifact.json"})
