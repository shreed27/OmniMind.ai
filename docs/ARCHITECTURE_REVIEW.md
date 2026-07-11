# OmniMind.ai Architecture Review

Assumed frozen architecture per CLAUDE.md + docs. All findings below are evidence-based contradictions, omissions, and risks across the repository's markdown corpus. Built for a staff-level Systems review: no simplification, no engineeringus-utf8.

---

## 1) Overall Architecture Score: 68 / 100

Why this score: The architecture covers an unusually complete stack for an autonomous-organization OS, but it is materially underspecified in critical paths, with overlapping/duplicated documents, a few outright contradictions, and large gaps in runtime contracts, security state machines, observability, database schema, and edge-state behavior.

Key contributing factors:
- Ambition/scope coverage: 90/100
- Internal coherence: 55/100
- Executable specificity: 60/100
- Security/risk posture: 55/100
- Operational/observability detail: 60/100

---

## 2) Missing Components

- **Constitution Engine / SOP Store**: Spec mentions organization SOPs and "Constitution", but no schema, no immutable revisioning contract, no Governance API for rule CRUD + provenance, and no explained ownership boundary between Kernel vs Reflection outputs.
- **Synchronization Conflict Resolution Component**: edge_runtime.md mentions merge/replay/replace/branch, but no CRDT/Causality model, no Version Vector/Lamport-clock document, no split-brain policy, and no final-state model spec for hybrid online/offline merges.
- **Audit/Approval Pipeline**: Anti-repudiation is implied by "immutable", "explainable", but no Audit Log schema, no Human Approval Service lifecycle, no Approval Workflow State Machine, and no retention/policy engine.
- **Plugin Manifest/Sandbox Contract**: Plugin concepts exist in docs, but no manifest schema: permissions matrix, sandbox policy, runtime harness, hot-load semantics, plugin dependency/resolution model, failure isolation rules.
- **Organization Federation Schema**: Organization-to-organization messaging is mentioned, but shared-identity/cross-org trust/boundary/database partition strategy is absent.
- **Prompt/MIR Execution Layer**: TASKS.md references Mission IR / Execution DAG / Department Assignment Compiler / Worker Task Graph Compiler, but no document defines MIR AST nodes, validation semantics, or compiler passes.
- **Resource Economy Ledger**: E.g., GPU/time/budget as first-class resources is repeated, but no ledger/receipt schema, no double-entry or credit/debit event contract, and no eventual consistency model.
- **Edge-to-Cloud Artifact Reconciliation**: Sync lists artifacts, but not how large binary conflicts are handled, nor a content-addressed store or deduplication contract across Cloud Run + Edge.
- **Mission Time Machine Replay Harness**: Replay is described as user-facing; no capture/replay harness, no deterministic replay requirements, no non-determinism policy, nor seeding behavior for randomness/scheduling.
- **Edge Security Boundary**: edge_runtime.md references local filesystem/sqlite/browser cache, but no sandbox/permissions model for local Managed Agent execution, child-process limits, or local network egress policy.

---

## 3) Duplicate Components

- Kernel module lists are repeated across enterprise_kernel.md, system_architecture.md, and architecture.md with consistent but slightly divergent member lists. These should be extracted into a single Kernel Catalog registry.
- Event lists are duplicated, expanded, and occasionally inconsistently named across enterprise_kernel.md, api_contracts.md, org_protocol.md, TASKS.md, execution_model.md. There is no canonical Event Registry.
- Digital Twin is described in ~7 docs with overlapping but not identical state fields/views.
- Mission Graph node/edge type lists appear in multiple docs with variations (e.g., `Vote` vs `VoteStarted`/`VoteCompleted` as nodes vs events).
- Organization IQ and Plasticity metrics are restated in slightly varying shapes across IDEA, enterprise_kernel, organization_learning, and agents.
- Memory hierarchy appears in multiple docs, sometimes with `Skill Store` or `Skill Memory` inserted mid-stack; no canonical layering.

Duplication creates drift risk; every divergent list should be centralized.

---

## 4) Contradicting Documents

1. Event naming/layering:
   - enterprise_kernel.md calls events like `VoteStarted`, `VoteCompleted`, `ReviewStarted`, `ReviewCompleted`, `ArtifactUpdated`.
   - mission_graph.md lists `Vote`, `Conflict`, `Human Approval`, and events as node types, mixing concepts.
   - api_contracts.md has `TaskBlocked`, not present elsewhere.
   → Contradiction: no canonical set of "events vs graph node types"; mapping is undefined.

2. Mission Graph node types:
   - enterprise_kernel.md Node Types include `Decision`, `Department`, `Worker`, `Review`, `Synchronization`.
   - api_contracts.md mission-graph nodes implicitly includes `commits`, `branches` but not explicit node types.
   → Contradiction: no golden schema for Mission Graph.

3. Edge Runtime composition:
   - enterprise_kernel.md Edge Runtime section lists "Mini CEO, Mini Planner, Mini Engineer, Mini Memory".
   - agents.md lists "Mini CEO, Mini Planner, Mini Engineer, Mini Memory, Mini Skill Store, Mini Reflection, Mission Graph".
   - edge_runtime.md lists "Mini CEO, Mini Planner, Mini Engineer, Mini Memory, Mini Skill Store, Mission Graph".
   → Contradiction: composition is inconsistent; unclear whether reflection and skill store are mandatory.

4. Skill node placement in memory hierarchy:
   - memory.md inserts `Skill Store` above Archived Memory.
   - organization_learning.md and enterprise_kernel.md place skill lifecycle in the registry, not memory hierarchy.
   → Not a hard contradiction, but indicates lack of canonical schema.

5. Managed Agent capabilities:
   - Some docs include `Scheduling`, `Testing`, `Search`; others omit `Testing` from Managed Agents.
   - TASKS.md Controlled Agent capabilities mention variants across phases.
   → Risk of capability contract drift.

6. README.md is effectively boilerplate: "An autonomous organization that never stops operating." It does not reflect the actual architecture, and it contradicts/bypasses the convention that docs/ is the source of truth.

---

## 5) Missing APIs

- **Constitution / SOP APIs**: Create, read history, diff, rollback rule version, activate/deactivate rules, and query effective rules for mission/worker.
- **Resource Ledger APIs**: Charge/credit resource events, refunds, reservations, price/cost estimator, finance approval workflow endpoints.
- **Plugin Lifecycle APIs**: Upload manifest, validate, install/uninstall, permission grant, update manifest signatures, audit plugin events, health/diagnostics.
- **Counterfactual / Simulation Scheduler API**: Concretely define simulation isolation, result schema, rollback-after-simulation contract, and read-only replica enforcement.
- **Mission Graph Branching API semantics**: Branch/merge/rollback endpoints exist at REST level, but there is no documented rebase policy, merge driver strategy, or conflict resolution schema for branches.
- **Federation APIs**: Inter-organization message envelope addressing, auth token exchange, trust policies, topic namespacing, and quota enforcement.
- **Organization / Worker Promotion & Retirement APIs**: Explicit final state transitions, archival triggers, knowledge handoff behavior, and genealogy retention contract.
- **Notifications / Approval APIs**: Human approval queue submission, approval token model, expiration policy, escalation policy, and policy-as-config.
- **Skill Execution API**: How a skill is invoked, validated, sandboxed, and charged—currently only publish/install/rate/fork/benchmark operations.
- **Config/Secrets APIs**: Secret retrieval at runtime, rotation policy, Edge secret availability constraints, and mapping to GCP Secret Manager and local storage.
- **Edge Sync APIs**: Conflict listing, resolution semantics, resume path, partial sync resumability, and sync ordering guarantees.

---

## 6) Missing Database Tables

**PostgreSQL**
- `organization_constitutions` / `rules`: versioned SOPs tied to `organization_id`, with effective_from/effective_to + author + mission reference.
- `resource_ledger`: resource_id, organization_id, department_id, mission_id, resource_type, debit/credit, balance_after, approval_id.
- `event_envelopes`: immutable event stream table acting as durable log before/alongside Kafka-style bus, with `trace_id`, `mission_id`, `org_id`, `department_id`, `worker_id`, `confidence`, payload_hash.
- `approvals`: approval_id, policy_type, target_entity, required_by, approved_by, result, evidence_ref, ttl, escalation_path.
- `audit_logs`: append-only, includes every security-relevant mutation, immutable.
- `plugin_manifests`: plugin identifier, manifest JSON, permissions, versions, sandbox config.
- `skill_versions`: schema not defined precisely; currently only generic Skills table missing lifecycle columns.
- `worker_genealogy`, `specialist_events`: explicit lifecycle operations.
- `mission_branches`, `mission_merges`, `conflicts`, `review_committees`: currently zero schema for branch/merge/diff state.
- `edge_sync_state`: edge_id, last_sync_version, cloud_tail, sync_state, conflicts.
- `synchronization_conflicts`: conflict_id, entity_type, entity_id, edge_vs_cloud_hash, resolution, resolver.

**Neo4j**
- Add explicit node labels and relationship types for [`Vote`, `Review`, `HumanApproval`, `ConstitutionRule`, `Plugin`, `Branch`, `Conflict`, `Specialist`, `ResourceAllocation`, `BudgetApproval`, `ApprovalQueue`, `EdgeSync`, `FederationTrustPolicy`].
- Relationship multiplicity rules for merge/branch/fork operations are not documented.

**Redis**
- Document TTL policy for cache vs queue vs session keys, especially for WebSocket channels and Digital Twin hot-state.

**Vector DB**
- Embedding meta-schema is not specified: versioned embedding policy, invalidation on update, embedding scope per memory/artifact/skill.

---

## 7) Missing Events

Canonical Event Registry is absent despite being required by the architecture. Gap examples:
- `BudgetExceeded`, `ResourceRequested`, `ApprovalRequired`, `ApprovalCompleted`, `ApprovalExpired` — mentioned in subscriptions, but no formal event definitions.
- `MagicStoreRebuilt`, `MemoryCompacted`, `NightCycleStarted`, `NightCycleCompleted` — referenced, but not formally defined.
- `SpecialistSpawned` exists both as an event and is implied as a Mission Graph node; boundary is unclear.
- `EdgeSyncConflictDetected`, `EdgeSyncResolved`, `SyncArtifactMerged` — implied but not defined.
- `Federation` events: `OrgInvited`, `OrgJoined`, `CrossOrgContractProposed`, `SharedMissionAssigned`, `FederationSync` — entirely missing.
- `SkillInstalled`, `SkillForked`, `SkillBenchmarked`, `SkillDeprecated`, `SkillRetired`.
- `DepartmentHealthChanged`, `WorkerPromotionCompleted`, `WorkerRetired`.
- `PluginInstalled`, `PluginFailed`, `PluginSandboxViolation`.
- `HumanFeedbackSubmitted` — referenced as a learning source, but not as an event.
- `MissionPreSimulated`, `SimulationCompleted` — diff between simulation input/output lifecycle events is missing.

---

## 8) Missing State Machines

- **Mission Lifecycle State Machine**: Documented loosely in several docs; no formal state diagram with transition pre/post conditions, invalid transitions, and idempotency guarantees for `Pause`/`Resume`/`Cancel`/`Archive`.
- **Department Lifecycle**: `Sleeping` → `Planning` → `Execution` → `Review` → `Sleep` → `Archive` but no defined failure transitions, no reconstitution semantics on Kernel restart, and no state persistence boundary.
- **Worker/Specialist Lifecycle**: Agent states exist (Sleeping/Waiting/Thinking/etc.), but no transition protocol, no machine-verifiable guards, and no state persistence contract across Kubernetes/Cloud Run restarts/edge transitions.
- **Executive Board Decision State Machine**: `VoteStarted` → submissions → missing/veto/override → `VoteCompleted` → appeal/reopen → CEO finalize. Not formally specified.
- **Conflict Resolution State Machine**: `ConflictRaised` → evidence gathering → review committee → re-vote → decision → appeal. No formal machine.
- **Reflection State Machine**: start/complete is too shallow; should interpolate between review, knowledge extraction, skill generation, constitution changes, and organization updates.
- **Resource Lifecycle**: Request → Finance Review → Allocate → Consume → Refund/Release → Audit.
- **Edge-to-Cloud Sync State Machine**: `Online` → `Degraded` → `Offline` → `EdgeActivated` → `SyncStarted` → `ConflictDetected` → `Merge/Replace/Branch` → `Resume`. Not formally defined.
- **Skill Lifecycle**: Create/Document/Benchmark/Version/Publish/Install/Fork/Update/Rollback/Retire. Partially present; not a machine.
- **Approval State Machine**: Requested → Human Action → Approved/Rejected → Escalated → Expired/Timeout.
- **Night Cycle State Machine**: Idle → Night Cycle Start → compress → merge → benchmark → archive → Ready.

---

## 9) Missing Services

Kernel is named, but exact service boundaries are not formally defined.
- **Constitution Service** — missing entirely in architecture docs.
- **Resource Ledger Service** — resource lifecycle missing.
- **Approval Engine / Human-in-the-Loop Service** — referred to but not specified.
- **Edge Runtime Manager Service** — underspecified; mentioned only in paragraph form.
- **Sync/Conflict Resolution Service** — no CRDT or merge-driver service.
- **Organization Registry Service** — activates as part of Organization Manager in docs, but no lifecycle-boundary spec.
- **Federation Service** — not built out at all.
- **Plugin Loader + Sandbox Service** — only named.
- **MIR / Mission Compiler Service** — only named in TASKS.
- **Model Router / Cost Engine** — TASKS phase 19; no architectural definition.
- **Observability / Telemetry Service** — not present in architecture doc.
- **Security Manager Service** — named but no security policy enforcer or policy decision point.
- **Human Approval Dashboard / Queue Service** — no service boundary.
- **Analytics Service** — ambiguous overlap with Analytics Engine in kernel; unclear ingestion/exposure boundaries.
- **Organization-to-Organization Messaging Service** — entirely absent.

---

## 10) Scalability Risks

- **Event Bus backpressure is undefined**: No retry semantics, dead-letter queue design, partition strategy, or consumer group model for departments/workers.
- **Mission Graph write amplification**: Every important action writes to Neo4j. At scale, neo4j write rate + relationship fan-out may be a bottleneck without batching, sharding, or episode aggregation.
- **Worker count explosion**: Design encourages arbitrarily large graph of workers/specialists. Need limits on concurrency, worker memory/lifetime caps, and destructive destruction semantics.
- **Digital Twin hot-state in Redis**: Real-time twin updates via WebSockets without subscriber partitioning or aggregation may collapse Redis throughput under orgs with thousands of workers.
- **No multi-tenancy / queue partitioning model**: Cloud Run scales via concurrency; per-organization/ per-mission bounded contexts are unspecified, risking noisy-neighbor issues and cross-org data leakage.
- **Embedding retrieval cost**: Every memory/skill/graph search is vectorized. No index freshness policy, no scalar quantization, no HNSW tuning guidance.
- **Branch/merge and simulation explosion**: Counterfactual simulator + branching implies exponential Mission Graph growth.
- **Cloud Storage for artifacts**: No content-addressed storage nor dedupe strategy; repeated artifacts due to reviewer rounds will balloon storage.
- **No rate limiting / admission control at Worker/Mission intake layer beyond 'Developer Experience Improvements'**.

---

## 11) Security Risks

- **RBAC is nominal**: CLAUDE.md mentions escalation categories, but no RBAC model for kernel modules, WebSocket channels, GraphQL reads, REST commands, or plugins. No least-privilege policy expressions.
- **Prompt-surface denial**: Multiple docs say "no chat", yet critical AI integrations run inside departments. Prompt inputs/outputs must be PII-scrubbed before entering Mission Graph.
- **Managed Agent sandboxing**: No process boundary, no filesystem jail, no network egress control, no resource limit for `Terminal`, `Browser`, `Package Installation`. Any worker could abuse shell execution.
- **Secret leakage via Mission Graph**: Graph node payload spec includes `APIs Used`, `Tool Calls`, `Memory Used`, `Artifacts`. Without scrubbing, secrets can be persisted to Mission Graph and Digital Twin.
- **Edge local storage**: Edge uses local SQLite + Gemma + local FS. Unless sealed with hardware-bound encryption and separate secret store, offline data is unprotected and local inference artifacts can be exfiltrated.
- **Human approval bypass**: Cannot be skipped per CLAUDE, but no enforcement boundary is documented at the transport/API layer.
- **Plugin trust model**: Permissions model exists only as a list; no signing/verification, no supply-chain attestation, no namespace isolation.
- **Audit integrity**: Append-only semantics are stated but no append-only enforcement mechanism at the database/key strategy is documented.
- **User identity and workspace isolation**: `Authorization` header + `WorkspaceID` is not itself a permission model. No audit of permission grants, revocations, or role changes.

---

## 12) Performance Risks

- **WebSockets without granular subscriptions**: Broadcasting full Digital Twin updates to every session is O(subscribers × org size). No subscription scoping per department/mission or diff enqueue.
- **Kernel Tick is described as a synchronous loop**: `Observe → Dispatch Events → Schedule Missions → Allocate Resources → Execute Workers → ...`. This must be asynchronous event-driven with bounded queues, not a sync loop.
- **Neo4j traversal depth**: Without read-replica strategy and explicit traversal depth limits, deep org genealogy / mission delta queries can spike latency.
- **Reflection as mandatory synchronous path**: "Reflection always runs" needs to be performant; mandatory sync reflection will stall mission completion at scale unless it is background + eventual.
- **Artifact lineage resolution**: Provenance chains can be deep; without bounded graph traversal and caching, `/artifacts/{id}/lineage` is a recursion risk.
- **Edge sync bandwidth**: No delta-sync contract; full org replication after every offline session is untenable.

---

## 13) Developer Experience Improvements

- **Canonical Source-of-Truth Registry**: Introduce `registry/EVENTS.md`, `registry/NODES.md`, `registry/STATES.md`, `registry SERVICES.md`, `registry/PERMISSIONS.md`. All docs reference registry instead of copying lists.
- **Architecture Freeze Hook Automation**: CLAUDE.md mentions four docs; add a CI linting schema that denies architectural changes not reflected in registry/EVENTS.md or registry/NODES.md.
- **Mission IR / Executable Spec**: Unless Kotlin/Python/TypeScript IR schema is defined, backend implementers will invent their own formats and blockers. Provide a typed schema + validator.
- **Layered ADRs / RFCs**: Add RFCs for Event Bus contract, Digital Twin State Store, Sync Engine CRDT, GraphQL vs REST v1 ownership, and WebSocket subscription protocol.
- **Golden Path Repo Layout**: `implementation_plan.md` mentions backend tree, but it does not match the TASKS.md folder list; finalize a single tree.
- **API Testing Harness**: Mission Graph Replay, Event Bus Replay, and Digital Twin hydration should have test fixtures and replay tools.
- **Local Development Stack**: No docker-compose reference in repo docs; missing dev-environment instructions for Postgres/Neo4j/Redis/Qdrant/Cloud Run emulation.
- **Schema-as-Code**: Ship SQLAlchemy models + Neo4j schema + Redis TTL policy in code, not prose.

---

## 14) UI/UX Improvements

- **Mission Graph Operator UX**: Branch/merge/replay/simulate require non-trivial controls; provide a "Mission Diff", "Branch Selector", and "Replay Player" as first-class components.
- **Executive Debate UX**: Users need to read/compare evidence and votes. Provide structured evidence/reasoning view, not just text blocks.
- **Digital Twin at scale**: Large orgs will require lazy-load, clustering, minimap, search, and details-on-demand, not a single giant React Flow canvas.
- **Offline Mode UX**: Edge runtime needs a UI indicator of sync conflict backlog, merge decision queue, and Cloud-Edge reconciliation history.
- **Explainability views**: Every decision node already plans to expose reasoning summary + evidence, but no UI spec for "what if I change evidence" sensitivity analysis.
- **Role-scoped views**: Control room for humans vs AI-native managers should be explicitly defined, including what each actor sees vs what is hidden/sealed.

---

## 15) Google AI Integration Review

The architecture relies heavily on Google ecosystem services. Gaps:
- **Gemini capabilities contract**: Which models? What tool calling semantics? No policy on multi-modal Gemini 2.x across Research, Legal, CMO, and Edge runtime.
- **Gemma Edge packaging**: No documented quantization format (GGUF/MLX), model update path, artifact provenance at edge, or fallback behavior when Gemma cannot serve a request.
- **Vertex AI routing**: No model router contract in architecture (only TASKS phase 19); routing by "planning" vs "execution" is named but not defined.
- **Search grounding**: Google Search is referenced, but no grounding freshness policy, cache policy, or result attribution schema.
- **Gemini Safety**: No explicit safety filter policy between model provider output and Executive Board publications.
- **Latency SLOs**: Gemini Flash vs Pro routing should be specified in execution_model, but it is not.
- **Anti-prompt-leak**: GCP Identity/Auth is referenced, but no IAM boundary per mission/organization/worker is defined.

---

## 16) Managed Agents Review

Gaps in execution semantics:
- **Process contract**: No exec model for `Python`, `Node`, `Terminal`, `Browser`. Need sandbox pods, timeout/retry policy, resource limits per run, stdout capture + streaming policy, exit-code schema.
- **Browser agent boundary**: Browser automation is high-risk. No cookie isolation, no credential handling, no originating mission context, and no recorded browser logs in Mission Graph.
- **Package installation**: No lockfile, install timeout, retry-after-failure, installed artifact registry, or revert behavior.
- **Scheduling**: "Scheduling" is listed but no scheduler; reuses Worker Scheduler in docs, but no preemptive/cancel semantics.
- **Parallel tasks**: No task DAG internal model; only external execution graph.
- **Code generation workers**: Generated code provenance must include source prompt/limitations/confidence; not documented.
- **Determinism**: Managed Agents will introduce non-determinism into replay; no guidance on recording external state to make replay meaningful.

---

## 17) Gemma Edge Runtime Review

Gaps in offline continuity:
- **Edge-specific Crash Recovery**: How does the mini organization recover from partial execution during abrupt power-off? No WAL/journal for local Mission Graph/Memory.
- **Edge Bandwidth Economics**: What is the minimum viable sync frequency? What is blocked during sync?
- **Edge Privacy/Security**: Local SQLite + Gemma inference suggests local prompts contain secrets; no guidance on zeroization on device wipe or physical access exposure.
- **Edge Test Matrix**: No edge-device coverage in testing requirements.
- **Mini Organization Capacity**: No documented maximums for local worker count, local memory size, or skill count on constrained devices.
- **Sync ordering**: How is eventual consistency resolved when local Mini CEO and Cloud CEO make conflicting decisions offline? No per-device causality.

---

## 18) Mission Graph Review

- **Immutability guarantee**: No documented storage enforcement strategy for immutability (append-only tables, Kafka topic retention, database-level policy). Immutability stated but not proved.
- **Graph Growth**: No compaction/aggregation/retention policy. At million-node scale, fetch-and-render is unsafe.
- **Graph Query patterns**: Missing query patterns for "what changed between two versions?", "which artifact depends on this decision?", "what is the latest approved branch state?".
- **Graph node schema standard**: Multiple variants exist across docs; a single JSON Schema/YAML schema for node payload should be frozen.
- **Patch semantics**: No `PATCH Mission Graph` operation; update paths all rely on new node creation.
- **Version identifier**: Notional `Mission Version` is mentioned but nothing defines how users/services resolve:
  - Head vs a given commit hash vs a branch name vs a simulation branch vs a merged branch.
- **Evidence store**: "Evidence" is conceptual, not typed—could mean logs, screenshots, structured findings, or MCP tool outputs. Each has different storage and PII requirements.

---

## 19) Organizational Learning Review

- **Learning pipeline is event-driven but not proven to be idempotent**: Replaying a reflection can create duplicate skills/memories unless dedup keys are known.
- **Skill generation validation**: Can any worker generate a published skill? Or only after benchmark? Learning review requires an explicit promotion gate with human or automated review.
- **Constitution update governance**: Reflection may update SOPs automatically. There is no policy limiting autonomic constitution drift, nor a rollback path for bad rules.
- **Organizational IQ**: It is a single aggregate metric with no per-KPI schema, no scoring scale, no decay, and no peer-reviewed benchmarks.
- **Night Cycle failure handling**: What happens if Night Cycle fails mid-compression? No checkpoint/restore semantics.

---

## 20) Suggestions That Materially Improve The Architecture

1. **Lock a Canonical Registry First**
   Introduce `docs/registry/` with frozen registries: Events.md, Nodes.md, StateMachines.md, Services.md, Permissions.md, Schemas.md. Every change triggers atomic registry updates. Otherwise coherence drifts forever.

2. **Define the Kernel Tick as an Asynchronous Loop with Backpressure/Dead-Letter**
   The current loop model suggests synchronous execution. Replace with event-and-task queue primitive: producer/consumer, DLQ, partitioning keys, and bounded worker pools per department.

3. **Event Bus Must Be a Product, Not a Metaphor**
   Add: Topic taxonomy, partition strategy, message envelope spec with `trace_id`, retention/SLA, replay API, and exactly-once delivery contract for Mission Graph writes.

4. **Security / Observability as First-Class Frameworks**
   Mandate OpenTelemetry for all modules; embed `mission_id`, `org_id`, `department_id`, `worker_id`, `trace_id`, `confidence` in every log line. Add PII-scrub middleware before logging or persisting.

5. **Introduce a Bounded Kernel API Surface**
   Map every external API contract to an internal Kernel command + event. Every command emits exactly one or more events; no direct service-to-service calls outside the Kernel surface.

6. **Mission IR + Mission Compiler Should Be Defined Before Phase 18 Code**
   MIR is the only way to guarantee Mission quality before execution. Define the AST, validation passes, optimization passes, and DAG lowerings now.

7. **Edge Runtime Requires an Explicit Isolation Boundary**
   Gear: local sqlite should be the source-of-truth queue, local filesystem must be contained, and sync must optimize delta vectors keyed by `(mission_id, causal_version)`. Add edge-device test fixtures.

8. **Mission Graph Needs an Index/Query Layer**
   Add a read-model/index for the most common queries: latest approved head per branch, lineage, node-by-type filters, time-window slices. Otherwise the display layer will thrash Neo4j.

9. **Audit + Approval as Immutable State Machines**
   Formalize approvals as events + transitions + machine, backed by append-only tables.

10. **Skill/Marketplace Needs Execution Contract**
   Skills are described as reusable capabilities, but not a runtime contract. Define skill inputs, outputs, versioning policy, sandbox policy, and runtime identity to avoid re-implementing every capability.

11. **Resource Economy Needs a Ledger and a Finance Service**
   Without balances/reservations/invoices/approvals modeled as records, budget enforcement is unreachable.

12. **Strategy: Reduce Contradictions First**
   Prioritize canonical registries over new features. The architecture as-written is compelling but fragile to independent contributors because duplicate/incongruent source-of-truth lists will propagate bugs.

13. **Add Formal Liveness and Safety Properties**
   As a deep-Mind-style system, the architecture should include explicit invariants: no missing reflection, no hidden messages, no mutable Mission Graph, no decoupled approval bypass. Specify these as rules the Kernel can validate.

14. **UI Spec Should Match Execution Model**
   The current `ui.md` is only a set of short principles and a list of surfaces. It should extend to explicit connection to real-time APIs, subscription naming, offline queue, and accessibility targets so frontend can be staffed without guessing Kernel behavior.

15. **README.md Should Be Retired or Repositioned**
   It is not architecturally accurate, contradicts docs-as-source-of-truth, and provides no implementation guidance. Delete or rewrite to a minimal pointer: `/docs/index.md`, repo status, and contribution instructions.

---

## Evidence Extraction Notes

Cross-document review found:
- 24 markdown files scanned.
- Multiple divergent lists for Events, Node Types, Kernel Modules, Services, Memory Hierarchy, Agent States, Executive Sub/Output definitions, and Digital Twin state fields.
- Multiple references to the same capability without formalization: Plugin manifest, Constitution rule schema, Resource ledger, Audit log schema, Edge conflict model, MIR specification.
- README ignored docs-as-source-of-truth.
- Minimum reproducible capability gaps: Event envelope contract, Approval state machine, Resource ledger, Skill execution contract, Edge delta-sync algorithm.

---

## Final Assessment

This architecture is more complete than most open-source operating systems' v0 docs. However, its strength—ambition and breadth—is also its weakness: many concepts are repeated but not precisely defined. Before implementation, the single most valuable engineering investment is canonical registries and formally specified state machines. Everything else becomes easier once the contract layer is locked.

Recommended next action: freeze docs/registry/* and schema/*.md, then begin implementation against those registries as the single source of truth.
