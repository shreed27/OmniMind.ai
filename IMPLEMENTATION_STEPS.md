# OmniMind.ai Implementation Steps

Version: 1.0
Status: ACTIVE
Owner: Principal Engineer

This document breaks EnterpriseOS into executable engineering tasks.
Each task is sized to fit a 30–90 minute engineering block and can be independently reviewed, estimated, and assigned.

Hard constraints from CLAUDE.md:
- No chat APIs.
- No prompt APIs.
- No prompt history exposure.
- Every command emits Events.
- Every event updates Mission Graph.
- Documentation in /docs is single source of truth.

---

# Phase 0 — Repo & Dev Environment

## TASK-0.1 Monorepo Scaffold

- Goal: Establish canonical top-level folders and shared tooling baseline.
- Files:
  - `backend/`
  - `frontend/`
  - `kernel/`
  - `agents/`
  - `memory/`
  - `mission_graph/`
  - `edge/`
  - `plugins/`
  - `tests/`
  - `docs/`
  - `scripts/`
  - `.gitignore`
  - `Makefile`
  - `tox.ini`
  - `.pre-commit-config.yaml`
- Dependencies: None
- Acceptance Criteria:
  - All directories exist.
  - `make bootstrap` installs Python and Node dependencies from empty manifests.
  - `make lint` runs without error on empty source trees.
- Tests Required:
  - N/A
- Estimated Time: 45 minutes
- Risk Level: Low

## TASK-0.2 Python Service Template

- Goal: Create shared FastAPI app structure, logging, health checks, and docker target for backend services.
- Files:
  - `backend/app/main.py`
  - `backend/app/core/config.py`
  - `backend/app/core/events.py`
  - `backend/app/core/logging.py`
  - `backend/tests/test_health.py`
  - `backend/pyproject.toml`
  - `backend/Dockerfile`
  - `backend/.env.example`
- Dependencies: TASK-0.1
- Acceptance Criteria:
  - `uvicorn app.main:app` starts.
  - `GET /healthz` returns 200 with JSON.
  - Structured logs include `trace_id` when present.
- Tests Required:
  - Health endpoint test.
  - Config loading test.
  - Logging enrichment test.
- Estimated Time: 60 minutes
- Risk Level: Low

## TASK-0.3 Node TypeScript Template

- Goal: Initialize Next.js app shell with shared lint/format/test and CI target.
- Files:
  - `frontend/package.json`
  - `frontend/tsconfig.json`
  - `frontend/src/app/layout.tsx`
  - `frontend/src/app/page.tsx`
  - `frontend/src/lib/api-client.ts`
  - `frontend/.env.example`
- Dependencies: TASK-0.1
- Acceptance Criteria:
  - `pnpm dev` renders homepage.
  - `pnpm lint`, `pnpm typecheck`, `pnpm test` pass.
- Tests Required:
  - Smoke render test.
- Estimated Time: 45 minutes
- Risk Level: Low

## TASK-0.4 Docker Compose for Local Dev

- Goal: Bring up Postgres, Neo4j, Redis, Qdrant, and backend/frontend via one command.
- Files:
  - `docker-compose.yml`
  - `compose.override.yml`
  - `scripts/wait-for-services.sh`
  - `docs/local-development.md`
- Dependencies: TASK-0.2, TASK-0.3
- Acceptance Criteria:
  - `docker compose up -d` starts all services.
  - Backend connects to all databases.
  - Frontend proxies API correctly.
- Tests Required:
  - Smoke script verifying health endpoints.
- Estimated Time: 60 minutes
- Risk Level: Medium

---

# Phase 1 — Kernel Foundation

## TASK-1.1 Event Envelope & Registry Loader

- Goal: Define frozen event envelope model and registry loader for canonical events/v1.
- Files:
  - `kernel/core/event.py`
  - `kernel/core/event_registry.py`
  - `kernel/core/exceptions.py`
  - `kernel/tests/test_event_envelope.py`
  - `kernel/tests/test_event_registry.py`
- Dependencies: TASK-0.2, `docs/registry/EVENTS.md`
- Acceptance Criteria:
  - Invalid event schema raises `InvalidEventError`.
  - Registry loader returns canonical event definitions for v1.
  - Payload hash matches SHA-256 of sorted JSON.
- Tests Required:
  - Envelope validation tests.
  - Registry round-trip tests.
- Estimated Time: 60 minutes
- Risk Level: Medium

## TASK-1.2 Kernel Event Bus Interface

- Goal: Define event bus contract and in-memory implementation for development.
- Files:
  - `kernel/core/ports.py`
  - `kernel/core/event_bus.py`
  - `kernel/tests/test_event_bus.py`
- Dependencies: TASK-1.1
- Acceptance Criteria:
  - `publish` returns `event_id`.
  - Subscribers receive published events in order.
  - Dead-letter queue captures malformed handlers.
- Tests Required:
  - Publish/subscribe integration tests.
  - DLQ behavior tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-1.3 Kernel Configuration & Secrets Loader

- Goal: Centralize config, env layering, and secret retrieval contract.
- Files:
  - `kernel/core/config.py`
  - `kernel/core/secrets.py`
  - `kernel/tests/test_config.py`
  - `kernel/tests/test_secrets.py`
- Dependencies: TASK-0.2
- Acceptance Criteria:
  - `.dev`, `.prod`, and runtime overrides load correctly.
  - Missing required secrets raise `MissingSecretError` on startup.
  - No secret value ever returned in logs or serialized config dumps.
- Tests Required:
  - Config layering tests.
  - Secret masking tests.
- Estimated Time: 60 minutes
- Risk Level: Medium

---

# Phase 2 — Persistence & Graph

## TASK-2.1 SQLAlchemy Base Models

- Goal: Create base engine/session and canonical Postgres tables from frozen registry.
- Files:
  - `backend/db/base.py`
  - `backend/db/session.py`
  - `backend/db/models/event.py`
  - `backend/db/models/mission.py`
  - `backend/db/models/organization.py`
  - `backend/db/models/department.py`
  - `backend/db/models/worker.py`
  - `backend/db/models/task.py`
  - `backend/db/models/artifact.py`
  - `backend/db/models/memory.py`
  - `backend/db/alembic/env.py`
  - `backend/tests/test_session.py`
- Dependencies: TASK-0.2, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - `alembic upgrade head` creates tables.
  - Insert/query smoke tests pass.
  - All keyed columns have correct constraints and indexes.
- Tests Required:
  - Schema migration test.
  - Constraint violation tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-2.2 Redis Client & Key Policy

- Goal: Establish Redis connection, namespace helpers, TTL policy, and consumer-group compatibility.
- Files:
  - `backend/db/redis.py`
  - `backend/db/key_policy.py`
  - `backend/tests/test_redis.py`
- Dependencies: TASK-2.1, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - TTLs match registry policy.
  - Connection pool reuses across tests.
  - Consumer groups created idempotently.
- Tests Required:
  - TTL expiry tests.
  - Consumer group tests.
- Estimated Time: 60 minutes
- Risk Level: Medium

## TASK-2.3 Qdrant / Vector Client

- Goal: Initialize Qdrant client with embedding meta schema and collection migrations.
- Files:
  - `backend/db/qdrant.py`
  - `backend/db/embeddings.py`
  - `backend/tests/test_qdrant.py`
- Dependencies: TASK-2.1
- Acceptance Criteria:
  - Collections created with correct dimensions and HNSW defaults.
  - Meta filtering includes scope, entity_id, version.
  - Deprecated versions excluded by default filter.
- Tests Required:
  - Upsert/query test with version filter.
- Estimated Time: 60 minutes
- Risk Level: Medium

## TASK-2.4 Neo4j Session & Schema Baseline

- Goal: Create Neo4j driver wrapper, transaction helpers, and index setup.
- Files:
  - `backend/db/neo4j.py`
  - `backend/db/graph_schema.py`
  - `backend/tests/test_neo4j.py`
- Dependencies: TASK-2.1, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - Indexes created for all labels.
  - Transaction rollback on exception.
  - Driver settings tuned for connection pooling.
- Tests Required:
  - Transaction wrapper test.
  - Index creation idempotency test.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-2.5 Event Append Store

- Goal: Persist event envelope to Postgres before bus dispatch with idempotency on retry.
- Files:
  - `backend/events/store.py`
  - `backend/events/repository.py`
  - `backend/tests/test_event_store.py`
- Dependencies: TASK-2.1, TASK-1.1
- Acceptance Criteria:
  - Duplicate `event_id` insert raises constraint error.
  - Causal version monotonicity enforced.
  - Events queryable by `(mission_id, timestamp DESC)`.
- Tests Required:
  - Duplicate event rejection test.
  - Query ordering test.
- Estimated Time: 60 minutes
- Risk Level: High

---

# Phase 3 — Kernel Core Services

## TASK-3.1 Mission Scheduler Service

- Goal: Implement mission lifecycle transitions and validation against frozen state machine.
- Files:
  - `kernel/services/mission_scheduler.py`
  - `kernel/services/ports.py`
  - `kernel/tests/test_mission_scheduler.py`
- Dependencies: TASK-1.2, TASK-2.5, `docs/registry/STATES.md`
- Acceptance Criteria:
  - Valid transitions emit event and append node.
  - Invalid transitions raise `InvalidTransitionError`.
  - Cancelled missions still emit `ReflectionStarted`.
- Tests Required:
  - Transition matrix tests.
  - Invalid transition rejection tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-3.2 Organization Manager Service

- Goal: Create and evolve organizations with hierarchy and health metadata.
- Files:
  - `kernel/services/organization_manager.py`
  - `kernel/tests/test_organization_manager.py`
- Dependencies: TASK-3.1
- Acceptance Criteria:
  - Organization created with `Registered` state.
  - Hierarchy updates emit `OrganizationUpdated` events.
  - Orphan departments are rejected.
- Tests Required:
  - Lifecycle tests.
  - Hierarchy mutation tests.
- Estimated Time: 70 minutes
- Risk Level: Medium

## TASK-3.3 Department Manager Service

- Goal: Spawn, activate, merge, split, destroy departments with state validation.
- Files:
  - `kernel/services/department_manager.py`
  - `kernel/tests/test_department_manager.py`
- Dependencies: TASK-3.2, `docs/registry/STATES.md`
- Acceptance Criteria:
  - Merge/split validate source state.
  - Knowledge retained after destroy.
  - No department directly modifies another department.
- Tests Required:
  - State transition tests.
  - Merge/split boundary tests.
- Estimated Time: 80 minutes
- Risk Level: Medium

## TASK-3.4 Worker Scheduler Service

- Goal: Create, assign, suspend, resume, retire workers and specialists.
- Files:
  - `kernel/services/worker_scheduler.py`
  - `kernel/tests/test_worker_scheduler.py`
- Dependencies: TASK-3.3
- Acceptance Criteria:
  - Specialist lifecycle completes destroy in one path.
  - Retired workers retain genealogy.
  - Worker cannot modify another department.
- Tests Required:
  - Specialist lifecycle tests.
  - Promotion/retirement tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-3.5 Kernel Boot Sequence

- Goal: Assemble registry-based module loader, dependency wiring, and shutdown hooks.
- Files:
  - `kernel/bootstrap.py`
  - `kernel/app.py`
  - `kernel/tests/test_bootstrap.py`
- Dependencies: TASK-3.4
- Acceptance Criteria:
  - `python -m kernel.app` starts and registers all core services.
  - Missing required service raises `KernelBootError`.
  - SIGTERM triggers graceful shutdown sequence.
- Tests Required:
  - Startup/shutdown tests.
  - Missing dependency failure mode tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-3.6 HTTP Transport Layer

- Goal: Expose FastAPI command endpoints that validate input, emit events, and never bypass Mission Graph.
- Files:
  - `backend/api/v1/router.py`
  - `backend/api/v1/missions.py`
  - `backend/api/v1/organizations.py`
  - `backend/api/v1/departments.py`
  - `backend/api/v1/workers.py`
  - `backend/tests/test_api.py`
- Dependencies: TASK-3.5, `docs/registry/PERMISSIONS.md`
- Acceptance Criteria:
  - Every command endpoint returns 202 with event reference.
  - AuthZ enforced using permissions registry.
  - No direct service calls outside Kernel Event Bus.
- Tests Required:
  - AuthZ matrix tests.
  - Event emission tests per endpoint.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-3.7 Error Contract Enforcer

- Goal: Standardize API error shape, trace inclusion, and mission graph node attachment.
- Files:
  - `backend/core/exceptions.py`
  - `backend/core/middleware.py`
  - `backend/tests/test_error_contract.py`
- Dependencies: TASK-3.6, `docs/api_contracts.md`
- Acceptance Criteria:
  - All 4xx/5xx match documented JSON schema.
  - `trace_id` present when available.
  - Mission Graph node linked when failure correlates to mission action.
- Tests Required:
  - Exception serialization tests.
  - Middleware propagation tests.
- Estimated Time: 60 minutes
- Risk Level: Medium

---

# Phase 4 — Mission Graph Engine

## TASK-4.1 Mission Graph Node Write Path

- Goal: Implement immutable append-only node writer with required field validation.
- Files:
  - `mission_graph/writer.py`
  - `mission_graph/schema.py`
  - `mission_graph/tests/test_writer.py`
- Dependencies: TASK-1.1, TASK-2.4, `docs/registry/NODES.md`
- Acceptance Criteria:
  - Missing required fields raises `InvalidNodeError`.
  - Duplicate `node_id` raises conflict.
  - Node append fires `MissionGraphUpdated` event.
- Tests Required:
  - Field validation tests.
  - Immutability tests.
- Estimated Time: 75 minutes
- Risk Level: High

## TASK-4.2 Mission Graph Edge Write Path

- Goal: Append immutable edges with cycle prevention per registry edge rules.
- Files:
  - `mission_graph/edges.py`
  - `mission_graph/tests/test_edges.py`
- Dependencies: TASK-4.1
- Acceptance Criteria:
  - `SUPERSEDES` cycle prevented.
  - `DEPENDS_ON` acyclic check enforced.
  - Edge append returns edge_id.
- Tests Required:
  - Cycle detection tests.
  - Relationship validation tests.
- Estimated Time: 75 minutes
- Risk Level: High

## TASK-4.3 Mission Graph Query Layer

- Goal: Implement read model queries for timeline, lineage, and branch head resolution.
- Files:
  - `mission_graph/reader.py`
  - `mission_graph/tests/test_reader.py`
- Dependencies: TASK-4.1, TASK-4.2
- Acceptance Criteria:
  - Timeline query returns nodes in causal order.
  - Lineage query bounded to max depth 12.
  - Branch head resolution returns latest approved node.
- Tests Required:
  - Query correctness tests.
  - Depth limit enforcement tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-4.4 Branch, Merge, Rollback Operations

- Goal: Implement graph mutations for branch/merge/rollback with event emission.
- Files:
  - `mission_graph/branching.py`
  - `mission_graph/tests/test_branching.py`
- Dependencies: TASK-4.3
- Acceptance Criteria:
  - Branch creates immutable fork record.
  - Merge creates merge node and emits merge event.
  - Rollback returns to target node without deleting history.
- Tests Required:
  - Branch/merge/rollback integration tests.
- Estimated Time: 90 minutes
- Risk Level: High

---

# Phase 5 — Agent Contracts & Manager Layer

## TASK-5.1 Base Agent Interface

- Goal: Define abstract agent contract with lifecycle hooks and event emission.
- Files:
  - `agents/base.py`
  - `agents/types.py`
  - `agents/tests/test_base.py`
- Dependencies: TASK-1.2, TASK-3.4, `docs/agents.md`
- Acceptance Criteria:
  - Agent state transitions emit lifecycle events.
  - Agent cannot write directly to another department without event bus.
  - Agent lifecycle respects state machine registry.
- Tests Required:
  - State transition tests.
  - Event emission tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-5.2 Executive Agent Implementations

- Goal: Stub CEO, CTO, CFO, COO, CMO, CRO, CSO, CLO, CIO with subscriptions and outputs.
- Files:
  - `agents/executive/ceo.py`
  - `agents/executive/cto.py`
  - `agents/executive/cfo.py`
  - `agents/executive/coo.py`
  - `agents/executive/cmo.py`
  - `agents/executive/cro.py`
  - `agents/executive/cso.py`
  - `agents/executive/clo.py`
  - `agents/executive/cio.py`
  - `agents/executive/board.py`
  - `agents/tests/test_executives.py`
- Dependencies: TASK-5.1, `docs/agents.md`
- Acceptance Criteria:
  - Each executive subscribes to documented event list.
  - Executives emit outputs as Mission Graph nodes.
  - No executive performs worker-level execution.
- Tests Required:
  - Subscription wiring tests.
  - Output node tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-5.3 Department Agent Implementations

- Goal: Stub Engineering, Research, Marketing, Finance, Legal, Security, Design, Operations, Infrastructure departments.
- Files:
  - `agents/departments/*.py`
  - `agents/tests/test_departments.py`
- Dependencies: TASK-5.2
- Acceptance Criteria:
  - Departments wake on mission/department events.
  - Departments never directly modify other departments.
  - Each department emits KPIs via events.
- Tests Required:
  - Wake/sleep lifecycle tests.
  - KPIs emission tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-5.4 Worker Agent Implementations

- Goal: Provide worker role stubs for Backend, Frontend, AI, QA, DevOps, Architect, Security, Documentation roles.
- Files:
  - `agents/workers/*.py`
  - `agents/tests/test_workers.py`
- Dependencies: TASK-5.3
- Acceptance Criteria:
  - Workers execute assigned tasks and publish artifacts.
  - Workers reflect after task completion.
  - Workers respect permission registry.
- Tests Required:
  - Execution flow tests.
  - Reflection hook tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-5.5 Specialist Spawner

- Goal: Implement manager-side specialist spawning with auto-destroy after knowledge transfer.
- Files:
  - `agents/specialists/manager.py`
  - `agents/specialists/runtime.py`
  - `agents/tests/test_specialists.py`
- Dependencies: TASK-5.4
- Acceptance Criteria:
  - Specialist inherits mission context.
  - Knowledge transfer emits events.
  - Specialist destroyed after review; knowledge retained.
- Tests Required:
  - Spawn/destroy lifecycle tests.
  - Knowledge transfer tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

---

# Phase 6 — Managed Agents & Execution

## TASK-6.1 Managed Agent Service Contract

- Goal: Define execution request schema and output schema for Python/Node/Terminal/Browser/FS/Package/Search/Schedule/Parallel.
- Files:
  - `kernel/services/managed_agent_service.py`
  - `kernel/tests/test_managed_agent_service.py`
  - `docs/registry/MANAGED_AGENT_CONTRACT.md`
- Dependencies: TASK-1.2
- Acceptance Criteria:
  - Request validated against capability matrix.
  - Outputs include logs, artifacts, exit status, mission graph node ref.
  - Timeout/retry policy documented and enforced.
- Tests Required:
  - Capability matrix validation tests.
  - Timeout/retry tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-6.2 Python Execution Runtime

- Goal: Exec Python code inside container/sandbox boundary with resource limits.
- Files:
  - `agents/runtime/python_runtime.py`
  - `agents/runtime/sandbox.py`
  - `agents/tests/test_python_runtime.py`
- Dependencies: TASK-6.1
- Acceptance Criteria:
  - Timeout, memory, network egress limits enforced.
  - Stdout/stderr captured and attached as Artifact metadata.
  - Failed runs emit `TaskFailed` event.
- Tests Required:
  - Resource limit tests.
  - Capture/artifact attachment tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-6.3 Node/Terminal/Browser Runtime Stubs

- Goal: Provide bounded runtime contracts for remaining managed agents.
- Files:
  - `agents/runtime/node_runtime.py`
  - `agents/runtime/terminal_runtime.py`
  - `agents/runtime/browser_runtime.py`
  - `agents/tests/test_runtime_stubs.py`
- Dependencies: TASK-6.1
- Acceptance Criteria:
  - Browser has explicit cookie isolation.
  - Terminal has no interactive TTY unless explicitly requested.
  - Node runtime captures exit code similarly to Python runtime.
- Tests Required:
  - Contract adherence tests.
  - Security boundary smoke tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-6.4 Package Installation Policy

- Goal: Enforce install allowlist, lockfile behavior, and timeout for package installation.
- Files:
  - `agents/runtime/package_policy.py`
  - `agents/tests/test_package_policy.py`
- Dependencies: TASK-6.1
- Acceptance Criteria:
  - Installing unapproved package raises `PolicyViolationError`.
  - Install timeout aborts and emits `SandboxViolation` if retries exceed limit.
  - Installed artifacts recorded in registry.
- Tests Required:
  - Allowlist tests.
  - Timeout tests.
- Estimated Time: 60 minutes
- Risk Level: Medium

---

# Phase 7 — Memory, Knowledge, Skills

## TASK-7.1 Memory Service Core

- Goal: Implement hierarchical memory store with ownership and access boundaries.
- Files:
  - `memory/service.py`
  - `memory/ports.py`
  - `memory/tests/test_memory_service.py`
- Dependencies: TASK-2.1, TASK-2.3, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - Memory scopes enforced at write time.
  - Working memory separated from mission/department/org memory.
  - Search supports semantic, keyword, and graph queries.
- Tests Required:
  - Scope enforcement tests.
  - Search hybrid tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-7.2 Memory Consolidation / Decay

- Goal: Implement importance scoring, decay, and duplicate removal for Night Cycle.
- Files:
  - `memory/consolidation.py`
  - `memory/tests/test_consolidation.py`
- Dependencies: TASK-7.1
- Acceptance Criteria:
  - Consolidation is idempotent.
  - Duplicate detection uses content hash + similarity threshold.
  - Archived memory remains queryable.
- Tests Required:
  - Idempotency tests.
  - Decay behavior tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-7.3 Knowledge Graph Service

- Goal: Implement KG node/edge writer and search with embedding-backed discovery.
- Files:
  - `memory/knowledge.py`
  - `memory/tests/test_knowledge.py`
- Dependencies: TASK-7.1, TASK-2.4
- Acceptance Criteria:
  - Nodes and edges conform to registry.
  - Reuse discovery returns highest-relevant candidates.
  - Embeddings invalidated on knowledge update per schema.
- Tests Required:
  - KG write/search tests.
  - Embedding invalidation tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-7.4 Skill Registry Service

- Goal: Implement lifecycle CRUD, versioning, benchmark storage, and rating/model.
- Files:
  - `kernel/services/skill_registry.py`
  - `kernel/tests/test_skill_registry.py`
- Dependencies: TASK-7.3, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - Publish creates new version; old versions remain accessible.
  - Fork retains provenance to parent skill_id.
  - Benchmark schema enforced on write.
- Tests Required:
  - Versioning/fork tests.
  - Benchmark schema tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

---

# Phase 8 — Reflection, Learning, Evolution

## TASK-8.1 Reflection Service Core

- Goal: Run mandatory reflection pipeline after task/mission completion.
- Files:
  - `kernel/services/reflection.py`
  - `kernel/tests/test_reflection.py`
- Dependencies: TASK-7.3, `docs/registry/STATES.md`
- Acceptance Criteria:
  - Reflection cannot be skipped by configuration flag.
  - Outputs: lessons, knowledge, skills, recommendations.
  - Each output emits corresponding events and nodes.
- Tests Required:
  - Skip-prevention tests.
  - Output schema tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-8.2 Learning Service

- Goal: Consume reflection outputs and update Memory, KG, Skills, Constitution, DNA.
- Files:
  - `kernel/services/learning.py`
  - `kernel/tests/test_learning.py`
- Dependencies: TASK-8.1, TASK-7.4
- Acceptance Criteria:
  - Replay-safe: duplicate reflection output does not double-write skills.
  - Organization IQ and Plasticity updated.
  - Mission DNA generated on mission completion.
- Tests Required:
  - Idempotency tests.
  - IQ/plasticity metric tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-8.3 Constitution Service

- Goal: Versioned SOP store with effective-time boundaries and rollback.
- Files:
  - `kernel/services/constitution.py`
  - `kernel/tests/test_constitution.py`
- Dependencies: TASK-8.2, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - Effective rule selection respects effective_from/effective_to.
  - Rollback creates new revision; no mutation of prior row.
  - Missions query effective rules deterministically.
- Tests Required:
  - Effective-time boundary tests.
  - Rollback tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-8.4 Evolution Service

- Goal: Propose structural changes from KPIs/reflection with executive approval gating.
- Files:
  - `kernel/services/evolution.py`
  - `kernel/tests/test_evolution.py`
- Dependencies: TASK-8.3, TASK-5.2
- Acceptance Criteria:
  - Proposals only; no direct structural mutation.
  - Executive vote required before `Applying`.
  - Revert proposal emits rollback events.
- Tests Required:
  - Approval gating tests.
  - Revert behavior tests.
- Estimated Time: 80 minutes
- Risk Level: Medium

---

# Phase 9 — Security, Approval, Audit

## TASK-9.1 RBAC Enforcement

- Goal: Intercept API and internal actions using frozen permission registry.
- Files:
  - `backend/core/security.py`
  - `backend/core/dependencies.py`
  - `backend/tests/test_rbac.py`
- Dependencies: TASK-3.6, `docs/registry/PERMISSIONS.md`
- Acceptance Criteria:
  - Forbidden action returns 403 with standardized error.
  - Worker cannot modify another department namespace.
  - Approval gating respected.
- Tests Required:
  - Permission matrix tests.
  - Namespace isolation tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-9.2 Approval Engine Service

- Goal: Queue, delegate, escalate, timeout, and expire human approvals.
- Files:
  - `kernel/services/approval_engine.py`
  - `kernel/tests/test_approval_engine.py`
- Dependencies: TASK-3.3, TASK-9.1, `docs/registry/STATES.md`
- Acceptance Criteria:
  - Timeout transitions to `Expired`.
  - Escalation follows registry policy table.
  - Decision recorded as immutable node.
- Tests Required:
  - Timeout/escalation tests.
  - Node emission tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-9.3 Audit Log Enforcer

- Goal: Append security-relevant mutations to immutable audit log with anti-tamper checks.
- Files:
  - `backend/audit/logger.py`
  - `backend/audit/verify.py`
  - `backend/tests/test_audit.py`
- Dependencies: TASK-2.1, TASK-9.1, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - Every grant/revoke mutation creates audit record.
  - Verify path detects removed or out-of-order entries.
  - Log export supports integrity verification.
- Tests Required:
  - Tamper detection tests.
  - Completeness tests.
- Estimated Time: 75 minutes
- Risk Level: High

## TASK-9.4 PII Scrub Middleware

- Goal: Prevent secret/prompt leakage into Mission Graph, logs, and exports.
- Files:
  - `backend/core/pii_scrub.py`
  - `backend/tests/test_pii_scrub.py`
- Dependencies: TASK-2.5, TASK-9.3
- Acceptance Criteria:
  - Detected secrets removed before persistence.
  - scrubber configurable per entity type.
  - Stats emitted on detected secrets.
- Tests Required:
  - Pattern-based redaction tests.
  - Config-driven behavior tests.
- Estimated Time: 60 minutes
- Risk Level: Medium

---

# Phase 10 — Resource Economy

## TASK-10.1 Resource Ledger Service

- Goal: Immutable debit/credit records for compute, GPU, budget, API quota.
- Files:
  - `kernel/services/resource_ledger.py`
  - `kernel/tests/test_resource_ledger.py`
- Dependencies: TASK-2.1, TASK-9.1, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - Ledger append-only; no UPDATE/DELETE paths.
  - Balance computation correctness under concurrent allocations.
  - Reconciliation query matches expected totals.
- Tests Required:
  - Ledger consistency tests.
  - Concurrency tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-10.2 Resource Policy & Approval

- Goal: Threshold-driven approval enforcement for expensive plans and runtimes.
- Files:
  - `kernel/services/resource_policy.py`
  - `kernel/tests/test_resource_policy.py`
- Dependencies: TASK-9.2, TASK-10.1
- Acceptance Criteria:
  - Budget exceeded 20% requires CFO approval.
  - Repeated failures trigger auto-escalation.
  - Policy changes visible as Mission Graph nodes.
- Tests Required:
  - Threshold breach tests.
  - Escalation chain tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

---

# Phase 11 — Digital Twin & Live Updates

## TASK-11.1 Digital Twin Hot Cache

- Goal: Maintain Redis-backed live org/department/worker state.
- Files:
  - `kernel/services/digital_twin.py`
  - `kernel/tests/test_digital_twin.py`
- Dependencies: TASK-2.2, TASK-3.3, TASK-3.4
- Acceptance Criteria:
  - State updates emit within 50ms under light load.
  - Reads return consistent snapshot for scope.
  - WebSocket channels can subscribe to subscopes.
- Tests Required:
  - Update latency tests.
  - Subscription scope tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-11.2 WebSocket Gateway

- Goal: Stream scoped live updates to frontend with authentication and backpressure.
- Files:
  - `backend/ws/router.py`
  - `backend/ws/manager.py`
  - `backend/tests/test_ws.py`
- Dependencies: TASK-11.1, TASK-3.6, TASK-9.1
- Acceptance Criteria:
  - Subscriptions scoped by mission/department/worker.
  - Dropped connections cleanly handled without memory leak.
  - Auth rejected early during handshake.
- Tests Required:
  - Subscription tests.
  - Backpressure/reconnect tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-11.3 Observatory Read Models

- Goal: Query endpoints for Organization, Mission, Knowledge, Timeline, Resource views.
- Files:
  - `backend/api/v1/digital_twin.py`
  - `backend/api/v1/observatory.py`
  - `backend/tests/test_observatory.py`
- Dependencies: TASK-11.2
- Acceptance Criteria:
  - Read endpoints never write.
  - Read model freshness within 100ms of source event.
  - Field selection supports client-side rendering.
- Tests Required:
  - Read-model freshness tests.
  - Authorization boundary tests.
- Estimated Time: 80 minutes
- Risk Level: Medium

---

# Phase 12 — Edge Runtime

## TASK-12.1 Edge Runtime Server Contract

- Goal: Define local mode API with Mini CEO/Planner/Engineer/Memory boundaries.
- Files:
  - `edge/server.py`
  - `edge/config.py`
  - `edge/tests/test_server.py`
- Dependencies: TASK-1.1, TASK-2.3, TASK-8.1
- Acceptance Criteria:
  - Local exec runs with explicit mission context.
  - Local state persisted to local SQLite/FS only.
  - Online/offline transitions emit events.
- Tests Required:
  - Local mode smoke tests.
  - Event transition tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-12.2 Edge Local Storage & Recovery

- Goal: Implement local WAL/journal for crash recovery and sync resumption.
- Files:
  - `edge/wal.py`
  - `edge/recovery.py`
  - `edge/tests/test_wal.py`
- Dependencies: TASK-12.1
- Acceptance Criteria:
  - Abrupt shutdown resumes from last checkpoint.
  - Replay deterministic for same event stream.
  - WAL size limit triggers compaction.
- Tests Required:
  - Crash recovery tests.
  - Compaction tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-12.3 Cloud ↔ Edge Sync Service

- Goal: Delta sync, conflict detection, merge/replace/branch resolution policies.
- Files:
  - `kernel/services/sync_service.py`
  - `edge/sync_client.py`
  - `kernel/tests/test_sync_service.py`
- Dependencies: TASK-12.2, TASK-4.3, `docs/registry/SCHEMAS.md`
- Acceptance Criteria:
  - Sync uses causal version cursor, not full table scans.
  - Conflicts flagged with entity hashes.
  - Merge/replace/branch policies emit resolution events.
- Tests Required:
  - Conflict detection tests.
  - Resolution policy tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-12.4 Edge Security Boundary

- Goal: Lock local FS, SQLite, sandbox limits, secret handling, and wipe semantics.
- Files:
  - `edge/permissions.py`
  - `edge/wipe.py`
  - `edge/tests/test_security.py`
- Dependencies: TASK-9.1, TASK-12.1
- Acceptance Criteria:
  - Local filesystem access restricted to declared paths.
  - Secrets not persisted in local SQLite.
  - Wipe zeroizes local mission data on request.
- Tests Required:
  - Boundary tests.
  - Zeroization tests.
- Estimated Time: 60 minutes
- Risk Level: High

---

# Phase 13 — Frontend Shell & Kernel Integration

## TASK-13.1 API Client & Auth

- Goal: Implement typed API client with auth and trace propagation.
- Files:
  - `frontend/src/lib/api-client.ts`
  - `frontend/src/hooks/use-auth.ts`
  - `frontend/tests/api.test.ts`
- Dependencies: TASK-3.7
- Acceptance Criteria:
  - 401/403 handled with redirect/logout.
  - Every request includes `X-Trace-ID`.
  - Errors render standardized payloads.
- Tests Required:
  - Auth flow tests.
  - Error rendering tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-13.2 Mission Dashboard Shell

- Goal: Build Mission-first home view with status, timeline, and organization health summary.
- Files:
  - `frontend/src/app/missions/[id]/page.tsx`
  - `frontend/src/components/mission-card.tsx`
  - `frontend/src/components/timeline.tsx`
- Dependencies: TASK-13.1
- Acceptance Criteria:
  - Renders without showing chat UI.
  - Timeline updates via WebSocket.
  - Empty/error/loading states defined.
- Tests Required:
  - Render/snapshot tests.
  - WebSocket update tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-13.3 Digital Twin Viewer

- Goal: Render live org/department/worker graph with status and confidence.
- Files:
  - `frontend/src/components/digital-twin.tsx`
  - `frontend/src/components/org-graph.tsx`
  - `frontend/tests/digital-twin.test.tsx`
- Dependencies: TASK-11.2
- Acceptance Criteria:
  - Subscription supports org/dept/worker scoping.
  - Collapse/expand at department level.
  - Confidence color-coded.
- Tests Required:
  - Render tests.
  - Subscription cleanup tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-13.4 Executive Debate View

- Goal: Surface evidence, votes, and reasoning summaries without raw chain-of-thought.
- Files:
  - `frontend/src/components/executive-board.tsx`
  - `frontend/src/components/vote-card.tsx`
  - `frontend/tests/executive-board.test.tsx`
- Dependencies: TASK-13.3
- Acceptance Criteria:
  - Reasoning summaries display, not raw LLM output.
  - Vote timelines are replayable.
  - Empty states and loading states preserved.
- Tests Required:
  - Render and accessibility tests.
- Estimated Time: 80 minutes
- Risk Level: Medium

---

# Phase 14 — Research, Creative, Plugin, Model Router

## TASK-14.1 Research Service

- Goal: Implement read-only research worker with web/paper/doc discovery and recommendation emission.
- Files:
  - `kernel/services/research_service.py`
  - `kernel/tests/test_research_service.py`
- Dependencies: TASK-5.2, TASK-7.3
- Acceptance Criteria:
  - Never mutates mission/organization directly.
  - Emits recommendation node and evidence metadata.
  - Sources include freshness and confidence.
- Tests Required:
  - Non-mutation regression tests.
  - Recommendation schema tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-14.2 Creative Service

- Goal: Wrap NB2 Lite generation into versioned artifact creation with provenance node.
- Files:
  - `kernel/services/creative_service.py`
  - `kernel/tests/test_creative_service.py`
- Dependencies: TASK-7.4
- Acceptance Criteria:
  - Every asset includes lineage node.
  - Failure does not create empty artifact.
  - Image/campaign generation emits concrete artifact type.
- Tests Required:
  - Lineage emission tests.
  - Failure path tests.
- Estimated Time: 60 minutes
- Risk Level: Medium

## TASK-14.3 Plugin Loader & Sandbox

- Goal: Validate manifest, install/uninstall, enforce permissions, emit health/sandbox events.
- Files:
  - `kernel/services/plugin_loader.py`
  - `kernel/services/plugin_sandbox.py`
  - `kernel/tests/test_plugin_loader.py`
- Dependencies: TASK-9.1, `docs/registry/PERMISSIONS.md`
- Acceptance Criteria:
  - Invalid manifest rejected at install.
  - Sandbox violation emits event and disables plugin.
  - Filesystem and network require explicit manifest grants.
- Tests Required:
  - Manifest validation tests.
  - Policy enforcement tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-14.4 Model Router Contracts

- Goal: Route planning/execution/offline/creative/search to model targets without magic strings.
- Files:
  - `kernel/services/model_router.py`
  - `kernel/tests/test_model_router.py`
  - `docs/registry/MODEL_ROUTER.md`
- Dependencies: TASK-14.1, TASK-14.2, TASK-12.1
- Acceptance Criteria:
  - Router keyed on task characteristics, not prompt contents.
  - Offline route requires Edge Runtime confirmation.
  - Router decisions emitted as events.
- Tests Required:
  - Routing matrix tests.
  - Offline fallback tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

---

# Phase 15 — Observability, Testing, Chaos Baseline

## TASK-15.1 Telemetry & Distributed Traces

- Goal: Add OpenTelemetry instrumentation with mandatory context fields.
- Files:
  - `backend/telemetry/__init__.py`
  - `backend/telemetry/otel.py`
  - `kernel/telemetry/__init__.py`
  - `backend/tests/test_telemetry.py`
- Dependencies: TASK-3.5, TASK-3.6
- Acceptance Criteria:
  - Every span includes `mission_id`, `org_id`, `dept_id`, `worker_id`, `trace_id`, `confidence`.
  - Background tasks create new span but maintain same `trace_id`.
  - Exporter configurable for logs/traces.
- Tests Required:
  - Span attribute tests.
  - Exporter fallback tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-15.2 CI Pipeline Baseline

- Goal: Enable lint, typecheck, unit + integration tests, security scan in GitHub Actions.
- Files:
  - `.github/workflows/ci.yml`
  - `Makefile` targets: `lint`, `typecheck`, `test`, `security`
  - `backend/tests/conftest.py`
  - `frontend/tests/setup.ts`
- Dependencies: TASK-0.1, TASK-0.2, TASK-0.3
- Acceptance Criteria:
  - PR checks block merge on failure.
  - Cached Postgres/Neo4j/Redis containers for integration tests.
  - Security scan reports uploaded.
- Tests Required:
  - CI workflow smoke run.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-15.3 Test Harness & Fixtures

- Goal: Provide base fixtures for Kernel, Event Bus, DBs, and Mission Graph replay tests.
- Files:
  - `tests/fixtures/__init__.py`
  - `tests/fixtures/event_fixtures.py`
  - `tests/fixtures/mission_fixtures.py`
  - `tests/fixtures/agent_fixtures.py`
  - `tests/harness/replay.py`
- Dependencies: TASK-15.1, TASK-4.3
- Acceptance Criteria:
  - Reusable across backend/kernel/frontend tests.
  - Replay harness replays mission deterministically from events.
  - Fixtures wired into pytest automatically.
- Tests Required:
  - Fixture initialization tests.
  - Replay determinism tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-15.4 Chaos Scenarios — Worker/Department Kill

- Goal: Simulate worker and department failures with automatic recovery assertions.
- Files:
  - `tests/chaos/test_worker_kill.py`
  - `tests/chaos/test_department_kill.py`
  - `tests/chaos/recovery_assertions.py`
- Dependencies: TASK-15.3, TASK-3.4
- Acceptance Criteria:
  - Killed worker tasks reassigned within bounds.
  - Department destruction does not lose knowledge.
  - Mission resumes after recovery.
- Tests Required:
  - Chaos simulation tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

---

# Phase 16 — Mission Compiler & MIR

## TASK-16.1 Mission IR Schema

- Goal: Define typed AST schema for parsed missions with validation rules.
- Files:
  - `kernel/mir/schema.py`
  - `kernel/mir/types.py`
  - `kernel/tests/test_mir_schema.py`
  - `docs/registry/MISSION_IR.md`
- Dependencies: TASK-3.1
- Acceptance Criteria:
  - IR serializes to/from JSON deterministically.
  - Invalid mission input rejects before scheduler.
  - Schema versioned and documented.
- Tests Required:
  - Round-trip serialization tests.
  - Validation rejection tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-16.2 Mission Validator & Optimizer

- Goal: Validate objectives, risks, constraints, KPIs, and budgets; suggest optimizations.
- Files:
  - `kernel/mir/validator.py`
  - `kernel/mir/optimizer.py`
  - `kernel/tests/test_mir_validator.py`
- Dependencies: TASK-16.1
- Acceptance Criteria:
  - Validation emits structured issues with severity.
  - Optimizer suggests department and worker allocation.
  - Optimizer is non-destructive; only suggestions.
- Tests Required:
  - Validation matrices tests.
  - Optimization suggestion regression tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-16.3 Execution DAG Builder

- Goal: Build task DAG from MIR with dependency analysis and scheduling hints.
- Files:
  - `kernel/mir/dag_builder.py`
  - `kernel/tests/test_dag_builder.py`
- Dependencies: TASK-16.2, TASK-3.4
- Acceptance Criteria:
  - DAG acyclic with explicit exception on cycle.
  - Parallel paths marked schedulable.
  - DAG emitted as Mission Graph nodes and events.
- Tests Required:
  - Cycle detection tests.
  - Parallelization tests.
- Estimated Time: 90 minutes
- Risk Level: High

---

# Phase 17 — Counterfactual, Time Machine, Analytics

## TASK-17.1 Mission Replay Engine

- Goal: Replay mission from event log with deterministic time control and WebSocket streaming.
- Files:
  - `mission_graph/replay.py`
  - `backend/api/v1/replay.py`
  - `kernel/tests/test_replay.py`
- Dependencies: TASK-4.3, TASK-11.2
- Acceptance Criteria:
  - Replay starts from causal version cursor.
  - Non-deterministic external calls blocked or seeded from recorded data.
  - Replay emits timeline events to subscribers.
- Tests Required:
  - Deterministic replay tests.
  - Cursor-based slice tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-17.2 Counterfactual Simulator

- Goal: Create isolated branch, run alternative timeline, and diff results.
- Files:
  - `kernel/services/simulation.py`
  - `backend/api/v1/simulation.py`
  - `kernel/tests/test_simulation.py`
- Dependencies: TASK-17.1, TASK-4.4
- Acceptance Criteria:
  - Production state never mutated.
  - Simulation branch closed/discarded after run.
  - Diff includes timeline, cost, confidence, organization changes.
- Tests Required:
  - Isolation tests.
  - Mutation regression tests.
- Estimated Time: 90 minutes
- Risk Level: High

## TASK-17.3 Analytics Service Core

- Goal: Emit, store, and query Organization IQ, Plasticity, Mission Success, and Resource Efficiency.
- Files:
  - `kernel/services/analytics.py`
  - `backend/api/v1/analytics.py`
  - `kernel/tests/test_analytics.py`
- Dependencies: TASK-8.2, TASK-10.1
- Acceptance Criteria:
  - Metrics derived from events, not direct service-to-service calls.
  - Historical trend queries bounded by time window.
  - No PII in aggregated metrics.
- Tests Required:
  - Metric accuracy tests.
  - Query latency tests.
- Estimated Time: 75 minutes
- Risk Level: Medium

## TASK-17.4 Organization Observatory UI

- Goal: Add Galaxy/Knowledge/Timeline/Resource views with performance-conscious rendering.
- Files:
  - `frontend/src/components/observatory/*.tsx`
  - `frontend/src/app/missions/[id]/observatory/page.tsx`
  - `frontend/tests/observatory.test.tsx`
- Dependencies: TASK-17.3, TASK-13.3
- Acceptance Criteria:
  - Views render within 200ms for 1k-node org graph.
  - Search filters graph nodes without full rerender.
  - Offline sync backlog visible.
- Tests Required:
  - Render performance tests.
  - Filter behavior tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

---

# Phase 18 — Frontend Polish, Demo Mode, Hackathon

## TASK-18.1 Mission Graph Operator UX

- Goal: Branch selector, diff viewer, replay player, simulation controls.
- Files:
  - `frontend/src/components/mission-graph/*.tsx`
  - `frontend/src/app/missions/[id]/graph/page.tsx`
- Dependencies: TASK-17.1, TASK-17.2
- Acceptance Criteria:
  - Diff highlights added/removed nodes.
  - Replay supports play/pause/step/speed.
  - Simulation results comparable to production path.
- Tests Required:
  - Diff algorithm tests.
  - Replay control tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-18.2 Demo Mode Scripting

- Goal: Scripted executive debate, auto conflict generator, offline demo, live metrics.
- Files:
  - `tests/demo/missions/*.py`
  - `tests/demo/fixtures/*.py`
  - `docs/demo-runbook.md`
- Dependencies: TASK-5.5, TASK-17.2
- Acceptance Criteria:
  - Demo mission runs without human approval.
  - Offline demo boots Edge Runtime and re-syncs.
  - Metrics dashboard shows live counters.
- Tests Required:
  - End-to-end demo smoke tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-18.3 Accessibility, Dark Mode, Performance

- Goal: Meet baseline a11y, dark mode parity, and performance budgets.
- Files:
  - `frontend/src/app/globals.css`
  - `frontend/src/components/*` theme updates
  - `frontend/tests/a11y.test.tsx`
  - `frontend/tests/performance.test.tsx`
- Dependencies: TASK-13.4, TASK-18.1
- Acceptance Criteria:
  - Keyboard navigation on primary surfaces.
  - Dark mode no FOUC on route change.
  - Lighthouse performance >= 85 on main pages.
- Tests Required:
  - Accessibility regression tests.
  - Performance snapshot tests.
- Estimated Time: 90 minutes
- Risk Level: Medium

## TASK-18.4 Documentation Sprint

- Goal: Update docs and diagrams to reflect frozen registry.
- Files:
  - `docs/implementation_plan.md`
  - `docs/architecture.md`
  - `docs/enterprise_kernel.md`
  - `docs/execution_model.md`
  - `docs/api_contracts.md`
  - `docs/IMPLEMENTATION_PROGRESS.md`
- Dependencies: All prior phases
- Acceptance Criteria:
  - Every doc links to registry docs.
  - No orphaned event/node lists outside registry.
  - README.md retired or rewritten to stable pointer.
- Tests Required:
  - Doc link validation script.
- Estimated Time: 50 minutes
- Risk Level: Low
