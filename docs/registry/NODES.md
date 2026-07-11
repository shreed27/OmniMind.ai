# OmniMind Organization Protocol (OMP) Node Registry

Version: 1.0
Status: FROZEN

This registry is the single source of truth for Mission Graph node types.

---

# Canonical Node Types

## Core

| Node | Description |
|------|-------------|
| `Mission` | User-submitted objective. |
| `Organization` | Org tied to mission. |
| `Department` | Autonomous unit. |
| `Worker` | Execution entity. |
| `Specialist` | Ephemeral worker. |
| `ManagedAgentRun` | External execution record. |

## Planning & Governance

| Node | Description |
|------|-------------|
| `Plan` | Proposed execution strategy. |
| `Decision` | Approved strategy or choice. |
| `Vote` | Executive vote record. |
| `Review` | Review artifact. |
| `Meeting` | Executive meeting record. |
| `Conflict` | Disagreement record. |
| `ReviewCommittee` | Temporary committee instance. |
| `Approval` | Human approval decision. |

## Execution & Artifacts

| Node | Description |
|------|-------------|
| `Task` | Assigned work item. |
| `Artifact` | Produced deliverable. |
| `ToolCall` | Exact tool invocation. |
| `ManagedAgentExecution` | Exec run result. |

## Organizations & Lineage

| Node | Description |
|------|-------------|
| `DepartmentMerge` | Merge operation record. |
| `DepartmentSplit` | Split operation record. |
| `WorkerPromotion` | Promotion record. |
| `WorkerRetirement` | Retirement record. |

## Memory & Learning

| Node | Description |
|------|-------------|
| `Memory` | Memory write record. |
| `Knowledge` | Knowledge graph record. |
| `Lesson` | Reflection-derived lesson. |
| `Skill` | Reusable capability record. |
| `Reflection` | Reflection session. |
| `Learning` | Learning pipeline run. |
| `ConstitutionUpdate` | SOP change record. |
| `MissionDNA` | Post-mission DNA. |

## Sync & Simulation

| Node | Description |
|------|-------------|
| `Synchronization` | Cloud/Edge sync record. |
| `Simulation` | Counterfactual run record. |
| `Branch` | Mission branch record. |
| `Merge` | Branch merge record. |
| `Rollback` | Rollback operation record. |

## Analytics

| Node | Description |
|------|-------------|
| `OrganizationIQSnapshot` | IQ metric snapshot. |
| `PlasticitySnapshot` | Plasticity metric snapshot. |

---

# Required Fields Per Node

Every node MUST contain:
- `node_id`: UUID
- `type`: one of the canonical types above
- `mission_id`: UUID
- `organization_id`: UUID
- `department_id`: UUID | null
- `worker_id`: UUID | null
- `timestamp`: ISO8601
- `confidence`: float
- `reasoning_summary`: string
- `evidence`: list[object]
- `artifacts`: list[UUID]
- `memory_references`: list[UUID]
- `tool_calls`: list[UUID]
- `execution_cost`: object
- `duration_ms`: int | null
- `dependencies`: list[UUID]
- `alternatives`: list[object]
- `version`: string | null
- `payload_hash`: SHA-256

Rules:
- Nodes are immutable once written.
- Nodes are append-only.
- Nodes may reference other nodes only through edges.

---

# Canonical Edge Types

| Edge | From | To | Notes |
|------|------|----|-------|
| `CREATED_BY` | Entity | Mission/Org/Dept/Worker/etc. | Causal origin. |
| `DEPENDS_ON` | Task/Artifact | Task/Artifact/Decision | Dependency. |
| `USES` | Worker/Department | Skill/Tool/Memory | Usage record. |
| `BLOCKED_BY` | Task | Task/Decision/Resource | Blocker. |
| `REVIEWED_BY` | Artifact/Decision | Review/Vote | Reviewer graph. |
| `GENERATED` | Worker/Department | Artifact/Skill/Knowledge/K Lesson | Provenance. |
| `LEARNT_FROM` | Learning/Constitution/Improvement | Reflection | Parent reflection. |
| `SUPERSEDES` | Newer Node | Older Node | Replacement. |
| `MERGED_INTO` | Source branch | Target branch | Merge target. |
| `FORKED_FROM` | Branch | Mission/Original branch | Branch origin. |
| `PART_OF` | Worker/Task/Artifact | Department | Ownership. |
| `OWNED_BY` | Entity | Worker/Department/Manager | Ownership. |
| `BLOCKED_ON` | Entity | Resource/Approval | Resource gate. |

Rules:
- Edges are immutable.
- Edges must not form cycles that violate causal ordering.
- `MERGED_INTO` and `FORKED_FROM` are branch-only edges.
- Every edge implicitly stores `timestamp` and `evidence`.
