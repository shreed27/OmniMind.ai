"""Tests for Plugin Manager - TASK-14.3"""

from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from plugins.manager import PluginManifest, PluginManager, PluginStatus


@pytest.mark.asyncio
async def test_plugin_installation() -> None:
    """Plugin manager installs valid plugins."""
    bus = InMemoryEventBus()
    manager = PluginManager(event_bus=bus)

    manifest = {
        "name": "github-integration",
        "version": "1.0.0",
        "author": "OmniMind",
        "description": "GitHub API integration",
        "permissions": ["read_events", "publish_events"],
        "entry_point": "github_plugin.main",
    }

    result = await manager.install(manifest)

    assert result["status"] == PluginStatus.INSTALLED
    assert "plugin_id" in result


@pytest.mark.asyncio
async def test_plugin_validation_failure() -> None:
    """Invalid plugin manifests are rejected."""
    bus = InMemoryEventBus()
    manager = PluginManager(event_bus=bus)

    invalid_manifest = {
        "name": "a",  # Too short
        "version": "",  # Missing
        "author": "Test",
    }

    result = await manager.install(invalid_manifest)

    assert result["status"] == PluginStatus.FAILED
    assert len(result["errors"]) > 0


@pytest.mark.asyncio
async def test_plugin_lifecycle() -> None:
    """Plugin can be enabled, disabled, removed."""
    bus = InMemoryEventBus()
    manager = PluginManager(event_bus=bus)

    manifest = {
        "name": "test-plugin",
        "version": "1.0.0",
        "author": "Test",
        "permissions": [],
        "entry_point": "test.main",
    }

    result = await manager.install(manifest)
    plugin_id = result["plugin_id"]

    # Enable
    await manager.enable(plugin_id)
    plugin = manager.get_plugin(plugin_id)
    assert plugin["status"] == PluginStatus.ENABLED

    # Disable
    await manager.disable(plugin_id)
    plugin = manager.get_plugin(plugin_id)
    assert plugin["status"] == PluginStatus.DISABLED

    # Remove
    await manager.remove(plugin_id)
    plugin = manager.get_plugin(plugin_id)
    assert plugin["status"] == PluginStatus.REMOVED


def test_manifest_validation() -> None:
    """PluginManifest validates required fields."""
    valid_manifest = {
        "name": "valid-plugin",
        "version": "1.0.0",
        "author": "Test",
        "entry_point": "main.py",
        "permissions": ["read_events"],
    }

    manifest = PluginManifest(valid_manifest)
    is_valid, errors = manifest.validate()

    assert is_valid is True
    assert len(errors) == 0


def test_manifest_invalid_permissions() -> None:
    """Unknown permissions are rejected."""
    invalid_manifest = {
        "name": "test",
        "version": "1.0.0",
        "author": "Test",
        "entry_point": "main.py",
        "permissions": ["invalid_permission"],
    }

    manifest = PluginManifest(invalid_manifest)
    is_valid, errors = manifest.validate()

    assert is_valid is False
    assert any("Unknown permission" in err for err in errors)
