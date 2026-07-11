# OmniMind Organization Protocol (OMP) Schema Registry

Version: 1.0
Status: FROZEN

This registry defines canonical schemas for persistence, sync, and API payload schemas referenced by other registry files.

---

# PostgreSQL Schemas (non-exhaustive)

## event_envelopes

- `event_id UUID PK`
- `causal_version ULID UK`
- `timestamp TIMESTAMPTZ NOT NULL`
- `source JSONB NOT NULL`
- `mission_id UUID NULL`
- `organization_id UUID NULL`
- `department_id UUID NULL`
- `worker_id UUID NULL`
- `trace_id UUID NOT NULL`
- `confidence FLOAT NOT NULL`
- `payload JSONB NOT NULL`
- `payload_hash SHA-256 NOT NULL`
- `immutable BOOLEAN NOT NULL DEFAULT TRUE`
Indexes:
- `(causal_version) ASC`
- `(mission_id, timestamp) DESC`
- `(organization_id, causal_version) DESC`
Partitioning: by month on `timestamp` if volume exceeds ~5M events/month.

## missions

- `mission_id UUID PK`
- `name TEXT NOT NULL`
- `objective TEXT NOT NULL`
- `status TEXT NOT NULL`
- `priority INT NOT NULL DEFAULT 0`
- `confidence FLOAT NOT NULL`
- `budget JSONB NULL`
- `stakeholders JSONB NULL`
- `risks JSONB NULL`
- `constraints JSONB NULL`
- `kpis JSONB NULL`
- `deadline TIMESTAMPTZ NULL`
- `current_phase TEXT NOT NULL`
- `current_state TEXT NOT NULL`
- `head_branch_id UUID NULL`
- `dna_version UUID NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `created_by UUID NOT NULL`

## organizations

- `organization_id UUID PK`
- `mission_id UUID FK`
- `health TEXT NOT NULL DEFAULT healthy`
- `iq FLOAT NULL`
- `plasticity FLOAT NULL`
- `state TEXT NOT NULL`
- `hierarchy JSONB NOT NULL`
- `current_event_cursor ULID NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `archived_at TIMESTAMPTZ NULL`

## departments

- `department_id UUID PK`
- `organization_id UUID FK`
- `mission_id UUID FK`
- `type TEXT NOT NULL`
- `status TEXT NOT NULL`
- `manager_id UUID NULL`
- `memory JSONB NULL`
- `resources JSONB NULL`
- `kpis JSONB NOT NULL`
- `dna JSONB NULL`
- `current_event_cursor ULID NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `archived_at TIMESTAMPTZ NULL`

## workers

- `worker_id UUID PK`
- `department_id UUID FK`
- `organization_id UUID FK`
- `mission_id UUID FK`
- `role TEXT NOT NULL`
- `status TEXT NOT NULL`
- `dna JSONB NOT NULL`
- `confidence FLOAT NOT NULL`
- `task_id UUID NULL`
- `resources JSONB NULL`
- `current_event_cursor ULID NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `archived_at TIMESTAMPTZ NULL`

## tasks

- `task_id UUID PK`
- `mission_id UUID FK`
- `organization_id UUID FK`
- `department_id UUID FK`
- `worker_id UUID NULL`
- `description TEXT NOT NULL`
- `status TEXT NOT NULL`
- `attempt INT NOT NULL DEFAULT 1`
- `dependencies JSONB NOT NULL DEFAULT '[]'::jsonb`
- `result JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `completed_at TIMESTAMPTZ NULL`

## artifacts

- `artifact_id UUID PK`
- `mission_id UUID FK`
- `organization_id UUID FK`
- `department_id UUID FK`
- `worker_id UUID NULL`
- `type TEXT NOT NULL`
- `content_ref TEXT NOT NULL`
- `content_hash SHA-256 NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'::jsonb`
- `lineage JSONB NOT NULL DEFAULT '[]'::jsonb`
- `version ULID NOT NULL`
- `review_status TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

## memories

- `memory_id UUID PK`
- `mission_id UUID FK`
- `organization_id UUID FK`
- `department_id UUID FK`
- `worker_id UUID NULL`
- `scope TEXT NOT NULL`
- `importance FLOAT NOT NULL`
- `confidence FLOAT NOT NULL`
- `recency FLOAT NOT NULL`
- `novelty FLOAT NOT NULL`
- `frequency INT NOT NULL DEFAULT 1`
- `embedding_id UUID NULL`
- `content JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `archived_at TIMESTAMPTZ NULL`

## skills

- `skill_id UUID PK`
- `name TEXT NOT NULL`
- `description TEXT NULL`
- `version TEXT NOT NULL`
- `owner_department_id UUID NULL`
- `author UUID NOT NULL`
- `status TEXT NOT NULL`
- `rating FLOAT NULL`
- `downloads INT NOT NULL DEFAULT 0`
- `benchmark JSONB NULL`
- `tests JSONB NULL`
- `dependencies JSONB NOT NULL DEFAULT '[]'::jsonb`
- `execution_cost JSONB NULL`
- `average_success FLOAT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

## skill_versions

- `skill_version_id UUID PK`
- `skill_id UUID FK`
- `version TEXT NOT NULL`
- `manifest JSONB NOT NULL`
- `benchmark JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `created_by UUID NOT NULL`

## reflections

- `reflection_id UUID PK`
- `mission_id UUID FK`
- `department_id UUID FK`
- `worker_id UUID NULL`
- `input JSONB NOT NULL`
- `output JSONB NOT NULL`
- `lessons JSONB NOT NULL DEFAULT '[]'::jsonb`
- `skills_emitted JSONB NOT NULL DEFAULT '[]'::jsonb`
- `knowledge_emitted JSONB NOT NULL DEFAULT '[]'::jsonb`
- `constitution_changes JSONB NOT NULL DEFAULT '[]'::jsonb`
- `confidence FLOAT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## organization_constitutions

- `constitution_id UUID PK`
- `organization_id UUID FK`
- `version TEXT NOT NULL`
- `rule TEXT NOT NULL`
- `effective_from TIMESTAMPTZ NOT NULL`
- `effective_to TIMESTAMPTZ NULL`
- `source_ref UUID NULL`
- `author UUID NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

Unique: `(organization_id, version)`.

## approvals

- `approval_id UUID PK`
- `policy_type TEXT NOT NULL`
- `target_entity_type TEXT NOT NULL`
- `target_entity_id UUID NOT NULL`
- `required_by TEXT NOT NULL`
- `requested_by UUID NOT NULL`
- `approver_id UUID NULL`
- `status TEXT NOT NULL`
- `evidence JSONB NULL`
- `ttl INTERVAL NOT NULL`
- `escalation_path JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `expires_at TIMESTAMPTZ NOT NULL`

Status: `Requested`, `Escalated`, `Approved`, `Rejected`, `Expired`, `Delegated`.

## approvals_history

- `approval_history_id UUID PK`
- `approval_id UUID FK`
- `transition TEXT NOT NULL`
- `from_status TEXT NOT NULL`
- `to_status TEXT NOT NULL`
- `actor_id UUID NOT NULL`
- `trace_id UUID NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## resource_ledger

- `ledger_id UUID PK`
- `organization_id UUID FK NOT NULL`
- `department_id UUID FK NULL`
- `mission_id UUID FK NULL`
- `resource_type TEXT NOT NULL`
- `amount FLOAT NOT NULL`
- `balance_after FLOAT NOT NULL`
- `direction TEXT NOT NULL CHECK (direction IN ('debit','credit'))`
- `approval_id UUID NULL`
- `reason TEXT NULL`
- `trace_id UUID NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## organization_iq

- `iq_id UUID PK`
- `organization_id UUID FK`
- `snapshot JSONB NOT NULL`
- `overall FLOAT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## plasticity_snapshots

- `plasticity_id UUID PK`
- `organization_id UUID FK`
- `snapshot JSONB NOT NULL`
- `score FLOAT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## mission_branches

- `branch_id UUID PK`
- `mission_id UUID FK`
- `name TEXT NOT NULL`
- `head_node_id UUID NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `created_by UUID NOT NULL`

## mission_merges

- `merge_id UUID PK`
- `mission_id UUID FK`
- `source_branch_id UUID FK`
- `target_branch_id UUID FK`
- `commit_node_id UUID NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `created_by UUID NOT NULL`

## mission_rollbacks

- `rollback_id UUID PK`
- `mission_id UUID FK`
- `from_node_id UUID NOT NULL`
- `to_node_id UUID NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `created_by UUID NOT NULL`

## conflicts

- `conflict_id UUID PK`
- `mission_id UUID FK`
- `organization_id UUID FK`
- `node_id UUID FK`
- `status TEXT NOT NULL`
- `evidence JSONB NOT NULL DEFAULT '[]'::jsonb`
- `votes JSONB NOT NULL DEFAULT '[]'::jsonb`
- `resolution JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `resolved_at TIMESTAMPTZ NULL`

## review_committees

- `committee_id UUID PK`
- `mission_id UUID FK`
- `type TEXT NOT NULL`
- `members JSONB NOT NULL`
- `status TEXT NOT NULL`
- `finding JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `completed_at TIMESTAMPTZ NULL`

## sync_state

- `edge_id TEXT PK`
- `mission_id UUID FK`
- `last_sync_version ULID NOT NULL`
- `cloud_tail ULID NOT NULL`
- `sync_state TEXT NOT NULL`
- `conflict_count INT NOT NULL DEFAULT 0`
- `updated_at TIMESTAMPTZ NOT NULL`

## sync_conflicts

- `conflict_id UUID PK`
- `edge_id TEXT FK`
- `entity_type TEXT NOT NULL`
- `entity_id UUID NOT NULL`
- `edge_hash SHA-256 NOT NULL`
- `cloud_hash SHA-256 NULL`
- `resolution TEXT NULL`
- `resolved_at TIMESTAMPTZ NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## plugin_manifests

- `plugin_id UUID PK`
- `name TEXT NOT NULL`
- `version TEXT NOT NULL`
- `manifest JSONB NOT NULL`
- `permissions JSONB NOT NULL DEFAULT '[]'::jsonb`
- `sandbox JSONB NOT NULL DEFAULT '{}'::jsonb`
- `status TEXT NOT NULL`
- `installed_by UUID NOT NULL`
- `installed_at TIMESTAMPTZ NOT NULL`

## audit_logs

- `audit_id UUID PK`
- `actor_id UUID NULL`
- `action TEXT NOT NULL`
- `target_type TEXT NOT NULL`
- `target_id UUID NOT NULL`
- `before JSONB NULL`
- `after JSONB NULL`
- `trace_id UUID NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `immutable BOOLEAN NOT NULL DEFAULT TRUE`

Indexes: `(target_type, target_id, created_at) DESC`.

---

# Neo4j Schema

## Node Labels

- `Mission`
- `Organization`
- `Department`
- `Worker`
- `Specialist`
- `Task`
- `Artifact`
- `Decision`
- `Vote`
- `Conflict`
- `Review`
- `ReviewCommittee`
- `Skill`
- `Memory`
- `Knowledge`
- `Lesson`
- `Reflection`
- `Learning`
- `ConstitutionUpdate`
- `Synchronization`
- `Simulation`
- `Branch`
- `Merge`
- `Rollback`
- `Approval`
- `HumanApproval`
- `ResourceAllocation`
- `BudgetApproval`
- `ApprovalQueue`
- `OrganizationIQSnapshot`
- `PlasticitySnapshot`
- `MissionDNA`
- `Plugin`

## Relationship Types

- `CREATED_BY`, `DEPENDS_ON`, `USES`, `BLOCKED_BY`, `REVIEWED_BY`, `GENERATED`, `LEARNT_FROM`, `SUPERSEDES`, `MERGED_INTO`, `FORKED_FROM`, `PART_OF`, `OWNED_BY`, `BLOCKED_ON`

## Indexes

- `:Mission(mission_id)`
- `:Organization(organization_id)`
- `:Department(department_id)`
- `:Worker(worker_id)`
- `:Task(task_id)`
- `:Artifact(artifact_id)`
- `:Skill(skill_id + version)`

Relationship multiplicity rules:
- No cycle on `SUPERSEDES`.
- `FORKED_FROM` and `MERGED_INTO` are branch-only.
- `DEPENDS_ON` must be acyclic.

---

# Redis Key Policy

## Key Namespace

```
omni:{scope}:{entity_id}:{field}
```

## TTL Policy

| Scope | TTL |
|-------|-----|
| Session | 24h |
| Mission Cache | Mission lifetime + 48h |
| Worker Cache | Worker lifetime + 24h |
| Live Digital Twin Hot-State | 60s sliding |
- WebSocket channels | connection lifetime
- Event queue consumer group | 7d
- Task queue consumer group | 3d

---

# Vector DB Contract

## Embedding Meta Schema

- `embedding_id UUID`
- `scope TEXT`  // `memory`, `artifact`, `skill`, `research_report`, `reflection`, `documentation`
- `entity_id UUID`
- `entity_type TEXT`
- `version TEXT`
- `created_at TIMESTAMPTZ`
- `updated_at TIMESTAMPTZ`
- `embedding_model TEXT`
- `embedding_dim INT`

Rules:
- Invalidation: writes create new version; prior version marked deprecated, not deleted.
- Retrieval MUST include `version` filter for scope.
- HNSW `ef_search` and `ef_construction` must be reviewed by Infrastructure/SEO/Performance.
