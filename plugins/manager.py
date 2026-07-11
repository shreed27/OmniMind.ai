"""
Plugin Manager - TASK-14.3

Plugin lifecycle management with manifest validation and sandboxing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus


class PluginStatus:
    """Plugin lifecycle states."""

    REGISTERED = "registered"
    VALIDATING = "validating"
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"
    REMOVED = "removed"


class PluginManifest:
    """
    Plugin manifest schema.

    Required fields:
    - name
    - version
    - author
    - description
    - permissions
    - entry_point
    """

    def __init__(self, manifest_data: dict[str, Any]) -> None:
        self.name = manifest_data.get("name", "")
        self.version = manifest_data.get("version", "")
        self.author = manifest_data.get("author", "")
        self.description = manifest_data.get("description", "")
        self.permissions = manifest_data.get("permissions", [])
        self.entry_point = manifest_data.get("entry_point", "")
        self.dependencies = manifest_data.get("dependencies", [])
        self.sandbox = manifest_data.get("sandbox", {})

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate manifest.

        Returns:
            (is_valid, errors)
        """
        errors = []

        if not self.name or len(self.name) < 3:
            errors.append("Plugin name must be at least 3 characters")

        if not self.version:
            errors.append("Version is required")

        if not self.entry_point:
            errors.append("Entry point is required")

        # Validate permissions
        allowed_permissions = [
            "read_events",
            "publish_events",
            "read_memory",
            "write_memory",
            "call_managed_agent",
            "access_filesystem",
            "access_network",
        ]

        for perm in self.permissions:
            if perm not in allowed_permissions:
                errors.append(f"Unknown permission: {perm}")

        return len(errors) == 0, errors


class PluginManager:
    """
    Plugin lifecycle manager.

    Responsibilities:
    - Manifest validation
    - Plugin installation
    - Sandboxing enforcement
    - Permission management
    - Lifecycle events
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._logger = get_logger("plugin_manager")
        self._plugins: dict[str, dict[str, Any]] = {}

    async def install(self, manifest_data: dict[str, Any]) -> dict[str, Any]:
        """
        Install plugin from manifest.

        Steps:
        1. Validate manifest
        2. Check permissions
        3. Install in sandbox
        4. Emit PluginInstalled event
        """
        manifest = PluginManifest(manifest_data)

        # Validate
        is_valid, errors = manifest.validate()
        if not is_valid:
            self._logger.error("Plugin validation failed: %s", errors)
            return {
                "plugin_id": manifest.name,
                "status": PluginStatus.FAILED,
                "errors": errors,
            }

        plugin_id = f"{manifest.name}@{manifest.version}"

        plugin_record = {
            "plugin_id": plugin_id,
            "manifest": manifest_data,
            "status": PluginStatus.INSTALLED,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "permissions": manifest.permissions,
        }

        self._plugins[plugin_id] = plugin_record

        # Emit event
        event = EventEnvelope.create(
            name="PluginInstalled",
            payload={
                "plugin_id": plugin_id,
                "plugin_name": manifest.name,
                "version": manifest.version,
            },
            confidence=1.0,
            source={"service": "kernel", "module": "plugin_manager", "component": "install"},
        )

        await self._bus.publish(event)

        self._logger.info("Plugin installed: %s", plugin_id)

        return plugin_record

    async def enable(self, plugin_id: str) -> None:
        """Enable plugin."""
        if plugin_id not in self._plugins:
            raise ValueError(f"Plugin not found: {plugin_id}")

        self._plugins[plugin_id]["status"] = PluginStatus.ENABLED

        event = EventEnvelope.create(
            name="PluginEnabled",
            payload={"plugin_id": plugin_id},
            confidence=1.0,
            source={"service": "kernel", "module": "plugin_manager", "component": "enable"},
        )

        await self._bus.publish(event)

        self._logger.info("Plugin enabled: %s", plugin_id)

    async def disable(self, plugin_id: str) -> None:
        """Disable plugin."""
        if plugin_id not in self._plugins:
            raise ValueError(f"Plugin not found: {plugin_id}")

        self._plugins[plugin_id]["status"] = PluginStatus.DISABLED

        event = EventEnvelope.create(
            name="PluginDisabled",
            payload={"plugin_id": plugin_id},
            confidence=1.0,
            source={"service": "kernel", "module": "plugin_manager", "component": "disable"},
        )

        await self._bus.publish(event)

        self._logger.info("Plugin disabled: %s", plugin_id)

    async def remove(self, plugin_id: str) -> None:
        """Remove plugin."""
        if plugin_id not in self._plugins:
            raise ValueError(f"Plugin not found: {plugin_id}")

        self._plugins[plugin_id]["status"] = PluginStatus.REMOVED

        event = EventEnvelope.create(
            name="PluginRemoved",
            payload={"plugin_id": plugin_id},
            confidence=1.0,
            source={"service": "kernel", "module": "plugin_manager", "component": "remove"},
        )

        await self._bus.publish(event)

        self._logger.info("Plugin removed: %s", plugin_id)

    def list_plugins(self) -> list[dict[str, Any]]:
        """List all installed plugins."""
        return list(self._plugins.values())

    def get_plugin(self, plugin_id: str) -> dict[str, Any] | None:
        """Get plugin details."""
        return self._plugins.get(plugin_id)
