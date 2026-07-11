# OmniMind Organization Protocol (OMP) Service Registry

Version: 1.0
Status: FROZEN

This registry defines the exact service boundaries for EnterpriseOS.
Docs that mention these concepts without boundaries are superseded by this file.

---

# Principles

- Every module communicates only through the Kernel Event Bus.
- Every external API is backed by a service boundary.
- Every service is independently testable, replaceable, and independently deployable.
- No service contains UI/transport concerns.
- No service directly calls another service outside the Kernel surface.

---

# Canonical Services

## Kernel Core

### Mission Scheduler
- Creates, queues, pauses, resumes, cancels, archives missions.
- Publishes Mission state transition events.
- Emits exactly one Mission node update per transition.

### Organization Manager
- Creates/destroys/splits/merges organizations.
- Maintains Organization Registry.
- Emits Organization lifecycle events.

### Department Manager
- Spawns, pauses, resumes, destroys, merges, splits departments.
- Emits Department lifecycle events.
- Maintains department hierarchy and reporting structure.

### Worker Scheduler
- Spawns, assigns, suspends, resumes, kills, promotes, retires workers/specialists.
- Maintains worker registry and genealogy.
- Emits Worker lifecycle events.

### Event Bus Service
- Canonical topic namespace + routing layer for all events.
- Provides at-least-once delivery to internal handlers.
- Supports replay via causal_version cursor.
- Supports dead-letter queue for poisoned events.
- Exposes subscription management and backpressure controls.

### Kernel Event Dispatcher
- Routes published events to subscribers.
- Wraps handler execution with trace propagation, audit logging, and panic compensation.

## Graph Services

### Mission Graph Service
- Immutable node/edge storage.
- Supports branch, merge, rollback, diff, timeline.
- Does not expose direct mutation outside new-node append semantics.
- Exposes query indices for head-branch, lineage, and time-window queries.

### Organization Graph Service
- Maintains current hierarchy.
- Tracks reporting lines, department membership, manager assignments.

### Knowledge Graph Service
- Stores lessons, skills, decisions, artifacts, missions as nodes.
- Supports semantic search, relationship traversal, reuse discovery.
- Manages embedding lifecycle, versioning, and invalidation.

## Memory Service

- Hierarchical memory: Worker → Department → Mission → Organization → Knowledge Graph → Archive.
- Handles semantic, keyword, and graph search.
- Performs compression, dedupe, decay.
- Enforces ownership and access control.

## Skill Registry Service

- Stores versioned skills.
- Supports publish, install, fork, update, benchmark, rollback, deprecate, retire.
- Tracks ratings, downloads, execution cost, average success.

## Reflection Service

- Bootstraps after every task/mission completion.
- Collects evidence, extracts lessons, generates knowledge.
- Emits ReflectionCompleted, skills, Constitution updates.
- Non-bypassable by design.

## Learning Service

- Consumes reflection outputs.
- Updates Knowledge Graph, Skill Registry, Constitution, Mission DNA.
- Updates Organization IQ and Plasticity metrics.

## Evolution Service

- Analyzes KPIs, reflection, mission DNA, analytics.
- Proposes merges, splits, promotions, retirements, new departments.
- Requires executive approval before applying structural changes.

## Resource Manager Service

- Tracks tenant/department/mission budgets, credits, compute, API quota.
- Enforces approval policy at allocation time.
- Maintains ledger records for every resource state change.

### Resource Ledger Service
- Immutable charge/credit/refund records.
- Supports audit reconciliation and finance reporting.

## Security Service

- Authenticates and authorizes requests.
- Manages RBAC permissions, tool/API access policies.
- Manages secrets rotation, encryption policies.
- Emits audit and sandbox-violation events.
- Enforces human approval policies.

### Approval Engine Service
- Request queue, delegation, escalation, timeout, expiry.
- Emits approval lifecycle events.
- Stores approval decision as immutable Mission Graph node.

### Policy Engine Service
- Stores verifiable policy rules.
- Evaluates allow/deny at runtime for actions and API calls.

## Analytics Service

- Ingests measurable signals from other services via events.
- Computes Organization IQ, Plasticity, efficiency, latency, confidence over time.
- Exposes time-series read APIs and anomaly detection.

## Digital Twin Service

- Maintains live organization state in Redis hot cache.
- Hydrates view models for WebSocket streaming.
- Supports multi-scale: org, department, worker.

## Edge Runtime Service

- Orchestrates local Mini Organization.
- Manages local SQLite mission queue and local filesystem boundary.
- Initiates Sync Service handshakes.

## Sync Service

- Cloud↔Edge reconciliation with causal version tracking.
- Detects divergences and emits EdgeSyncConflictDetected events.
- Supports merge/replace/branch/replay resolution policies.

## Research Service

- Performs web, paper, documentation, benchmark discovery.
- Never mutates production state directly.
- Emits research recommendations only.

## Creative Service

- Wraps NB2 Lite.
- Generates images, landing pages, campaigns.
- Each output becomes a versioned Artifact node.

## Managed Agent Service

- Executes runtime agent jobs with resource limits.
- Captures stdout/stderr, exit codes, durations, tool calls.
- Emits ManagedAgentExecution nodes.

## Notification Service

- Surfaces human-required signals: approvals, escalations, anomalies.
- Non-blocking for async consumers, blocking for human-in-the-loop queues.

## Observatory / Presentation Service

- Exposes read models for Mission Dashboard, Digital Twin, Executive Board views.
- Handles WebSocket stream selection and fan-out.
