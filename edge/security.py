"""
Edge Runtime Security - TASK-12.4

Sandbox enforcement for offline execution.
Prevents unauthorized access during edge mode.
"""

from __future__ import annotations

from typing import Any

from kernel.core.logging import get_logger


class EdgeSecurityPolicy:
    """
    Security policies for edge runtime.

    Rules:
    - Network egress blocked by default
    - Filesystem access sandboxed to mission directory
    - No secret rotation during offline mode
    - All API calls logged for audit
    """

    def __init__(self) -> None:
        self._logger = get_logger("edge_security")
        self._allowed_paths: set[str] = set()
        self._blocked_apis: set[str] = set()

    def allow_filesystem_access(self, path: str) -> None:
        """Whitelist filesystem path for edge access."""
        self._allowed_paths.add(path)
        self._logger.info("Allowed filesystem path: %s", path)

    def block_api(self, api_name: str) -> None:
        """Block API endpoint during edge mode."""
        self._blocked_apis.add(api_name)
        self._logger.info("Blocked API: %s", api_name)

    def check_filesystem_access(self, path: str) -> bool:
        """Verify if path access is allowed."""
        for allowed_path in self._allowed_paths:
            if path.startswith(allowed_path):
                return True

        self._logger.warning("Filesystem access denied: %s", path)
        return False

    def check_api_access(self, api_name: str) -> bool:
        """Verify if API access is allowed."""
        if api_name in self._blocked_apis:
            self._logger.warning("API access denied: %s", api_name)
            return False

        return True

    def check_network_egress(self, destination: str) -> bool:
        """
        Verify if network egress is allowed.

        During edge mode, all network egress is blocked except localhost.
        """
        if destination.startswith("127.0.0.1") or destination.startswith("localhost"):
            return True

        self._logger.warning("Network egress denied: %s", destination)
        return False

    def audit_edge_operation(self, operation: str, details: dict[str, Any]) -> None:
        """Log edge operation for security audit."""
        self._logger.info("Edge operation audit: %s - %s", operation, details)
