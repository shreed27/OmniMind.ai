# Managed Agent Contract

Version: 1.0
Status: FROZEN

---

# Transport

Command endpoint:
POST /api/v1/managed-agents/execute

Authentication uses service-level bearer credentials.

---

# Request Schema

Fields:
- capability: str
- mission_id: str
- organization_id: str | null
- department_id: str | null
- worker_id: str | null
- input: dict[str, Any]
- timeout_seconds: int, 1..600
- retries: int, 0..5
- tags: list[str]
- metadata: dict[str, Any]

Capability aliases:
- python, node, terminal, browser
- fs/filesystem
- package/package_install
- search, schedule, parallel

---

# Response Schema

Fields:
- exit_status: int
- logs: str
- artifacts: list[ExecutionArtifact]
- mission_graph_node_ref: str | null
- emitted_events: list[str]
- attempts: int

---

# Status Codes

0: success
1: runtime failure
2: policy violation
3: manifest error
4: unsupported capability
1432: timeout
1433: runtime exception

---

# Timeout / Retry Policy

- Default timeout: 60s
- Default max retries: 2
- Retry only on timeout and transient error codes
- Jittered backoff recommended

---

# Event Emissions

- TaskSucceeded
- TaskFailed

Each event includes mission/org/department/worker/trace context and mission_graph_node_ref when available.
