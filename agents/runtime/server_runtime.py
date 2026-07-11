from __future__ import annotations

import subprocess
import sys
from typing import Any


class TerminalRuntime:
    def run(self, command: str, timeout: int = 5) -> dict[str, Any]:
        completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"command": command, "stdout": completed.stdout, "stderr": completed.stderr, "returncode": completed.returncode}


class ServerRuntime:
    def __init__(self, url: str) -> None:
        self.url = url

    def health(self) -> dict[str, Any]:
        return {"url": self.url, "status": "unknown"}
