import pytest
from plugins.registry import PluginRegistry, Plugin


def test_plugin_registry_register_and_get() -> None:
    registry = PluginRegistry()
    registry.register(Plugin("github", "1.0.0"))
    plugin = registry.get("github")
    assert plugin is not None
    assert plugin.version == "1.0.0"
