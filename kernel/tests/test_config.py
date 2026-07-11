import pytest
from kernel.core.config import ConfigStore


def test_config_store_set_get() -> None:
    store = ConfigStore()
    store.set("app_env", "dev")
    assert store.get("app_env") == "dev"
    assert store.get("missing", "default") == "default"
