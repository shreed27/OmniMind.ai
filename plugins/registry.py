from typing import Any


class Plugin:
    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)
