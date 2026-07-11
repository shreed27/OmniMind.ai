from __future__ import annotations

import logging
from typing import Any

from kernel.core.config import get_kernel_settings

settings = get_kernel_settings()
logger = logging.getLogger("kernel")


def get_logger(component: str) -> logging.Logger:
    return logging.getLogger(f"kernel.{component}")


