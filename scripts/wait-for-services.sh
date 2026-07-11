#!/usr/bin/env bash
set -euo pipefail

wait_for() {
  local url="$1"
  local timeout="${2:-60}"
  local elapsed=0
  until curl -fsS "$url" >/dev/null 2>&1; do
    sleep 2
    elapsed=$((elapsed + 2))
    if [ "$elapsed" -ge "$timeout" ]; then
      echo "Timeout waiting for $url"
      exit 1
    fi
  done
  echo "Ready: $url"
}

wait_for "http://localhost:8000/healthz" 120
wait_for "http://localhost:6333/healthz" 120
