from __future__ import annotations

import json
import os
from typing import Any

import yaml


class RegistryError(Exception):
    """Raised when the registry file is invalid or missing."""


def load_registry(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        raise RegistryError(f"missing registry: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise RegistryError(f"invalid registry format: {path}")
    return data
