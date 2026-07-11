# OmniMind Organization Protocol (OMP) Event Registry

Version: 1.0
Status: FROZEN

This registry is the single source of truth for all event types in EnterpriseOS.
Duplicate/narrow lists in other docs are superseded by this file.

---

# Event Envelope

```yaml
event_id: UUID
causal_version: ULID
timestamp: ISO8601
source:
  service: string
  module: string
  component: string
mission_id: UUID | null
organization_id: UUID | null
department_id: UUID | null
worker_id: UUID | null
trace_id: UUID
confidence: float
payload: object
payload_hash: SHA-256
immutable: true
```

Rules:
- Events are immutable.
- Events are append-only.
- Every event updates the Mission Graph.
- Every event emits exactly one Mission Graph node.
- Events never reference mutable objects by pointer.
- Sender must populate all identity fields if known.

---

# Canonical Events

## Mission

| Event | Notes |
|------|-------|
| `MissionCreated` | Mission entering the system. |
| `MissionUpdated` | Non-destructive metadata update. |
| `MissionPaused` | Kernel pauses execution. |
| `MissionResumed` | Kernel resumes execution. |
| `MissionBlocked` | Mission cannot proceed without external input. |
| `MissionUnblocked` | Blocker removed. |
| `MissionCancelled` | Cancellation; reflection still executes. |

## Organization

| Event | Notes |
|------|-------|
| `OrganizationCreated` | Binding mission to new org. |
| `OrganizationUpdated` | Health/IQ/plasticity changes. |
| `OrganizationEvolved` | Structural changes already applied. |
| `OrganizationArchived` | Post-completion archival. |

## Department

| Event | Notes |
|------|-------|
| `DepartmentCreated` | Spawned by CEO or Executive action. |
| `DepartmentActivated` | Woke from Sleeping. |
| `DepartmentPaused` | Execution paused. |
| `DepartmentResumed` | Execution resumed. |
| `DepartmentMerged` | Two departments merged. |
| `DepartmentSplit` | One department split. |
| `DepartmentDestroyed` | Removed; knowledge retained. |
| `DepartmentArchived` | Moved to archive memory. |

## Worker

| Event | Notes |
|------|-------|
| `WorkerSpawned` | New worker created. |
| `WorkerActivated` | Woke from Sleeping/Waiting. |
| `WorkerPromoted` | Role/hierarchy change. |
| `WorkerRetired` | Archived; lineage retained. |
| `WorkerDestroyed` | Removed from active org. |

## Specialist

| Event | Notes |
|------|-------|
| `SpecialistSpawned` | Ephemeral worker spawned. |
| `SpecialistKnowledgeTransferred` | Knowledge moved to department. |
| `SpecialistDestroyed` | Ephemeral worker removed. |

## Task / Execution

| Event | Notes |
|------|-------|
| `TaskCreated` | Assigned to worker. |
| `TaskStarted` | Execution began. |
| `TaskCompleted` | Successful completion. |
| `TaskFailed` | Terminal failure. |
| `TaskRetried` | Retry attempted. |
| `TaskBlocked` | Dependency missing. |
| `TaskCancelled` | Ancestor cancelled. |

## Artifact

| Event | Notes |
|------|-------|
| `ArtifactCreated` | Published. |
| `ArtifactUpdated` | Patched/relinked. |
| `ArtifactReviewed` | Review decision attached. |
| `ArtifactPublished` | Approved and surfaced. |

## Memory / Knowledge / Skill

| Event | Notes |
|------|-------|
| `MemoryStored` | Written. |
| `MemoryCompacted` | Night Cycle compression. |
| `KnowledgeCreated` | New KG node. |
| `SkillCreated` | New skill version authored. |
| `SkillUpdated` | Existing skill updated. |
| `SkillPublished` | Published to marketplace. |
| `SkillInstalled` | Installed by consumer. |
| `SkillForked` | Forked. |
| `SkillBenchmarked` | Benchmark completed. |
| `SkillDeprecated` | Marked deprecated. |
| `SkillRetired` | Removed. |

## Reflection / Learning

| Event | Notes |
|------|-------|
| `ReflectionStarted` | Mandatory reflection begins. |
| `ReflectionCompleted` | Lessons/knowledge/skills emitted. |
| `LearningCompleted` | Knowledge graph + constitution updated. |
| `ConstitutionUpdated` | Rule added/changed/retired. |
| `MissionDNAGenerated` | DNA emitted post-completion. |

## Governance / Security

| Event | Notes |
|------|-------|
| `ConflictRaised` | Disagreement detected. |
| `ReviewStarted` | Temporary committee created. |
| `ReviewCompleted` | Evidence and decision emitted. |
| `VoteStarted` | Executive vote started. |
| `VoteCompleted` | Immutable vote node recorded. |
| `ApprovalRequested` | Human approval required. |
| `ApprovalCompleted` | Human answered. |
| `ApprovalExpired` | Timeout reached. |
| `ApprovalEscalated` | Moved to higher authority. |
| `HumanFeedbackSubmitted` | Post-hoc learning signal. |
| `SecretRotated` | Credential rotation event. |
| `SecurityAuditCompleted` | Audit record emitted. |
| `SandboxViolation` | Policy violation detected. |
| `EgressBlocked` | Network egress denied by policy. |

## Resources / Finance

| Event | Notes |
|------|-------|
| `ResourceRequested` | Department request created. |
| `ResourceApproved` | Finance approved. |
| `ResourceRejected` | Finance denied. |
| `ResourceAllocated` | Ledger debited/credited. |
| `ResourceReleased` | Unused returned. |
| `BudgetExceeded` | Threshold breached. |

## Analytics / Observability

| Event | Notes |
|------|-------|
| `OrganizationIQUpdated` | Aggregate score changed. |
| `PlasticityUpdated` | Plasticity score changed. |
| `MissionReplayRequested` | Replay started. |
| `MissionReplayCompleted` | Replay completed. |

## Runtime / Scheduling

| Event | Notes |
|------|-------|
| `KernelTick` | Kernel loop completed. |
| `WorkerScheduled` | Kernel assigned worker to task. |
| `WorkerSuspended` | Preempted. |
| `WorkerResumed` | Preemption ended. |
| `WorkerKilled` | Hard termination. |
| `NightCycleStarted` | Idle maintenance started. |
| `NightCycleCompleted` | Maintenance finished. |

## Edge

| Event | Notes |
|------|-------|
| `EdgeActivated` | Local mode enabled. |
| `CloudActivated` | Cloud mode enabled. |
| `HybridModeActivated` | Hybrid mode enabled. |
| `SynchronizationStarted` | Sync process started. |
| `SynchronizationCompleted` | Sync process ended cleanly. |
| `EdgeSyncConflictDetected` | Cloud/Edge divergence found. |
| `EdgeSyncResolved` | Conflict resolved. |
| `EdgeDeviceWiped` | Local state cleared securely. |

## Plugins

| Event | Notes |
|------|-------|
| `PluginInstalled` | Manifest registered. |
| `PluginUpdated` | Manifest changed. |
| `PluginRemoved` | Manifest unregistered. |
| `PluginSandboxViolation` | Out-of-bounds access. |
| `PluginHealthChanged` | Status transition. |

## Federation

| Event | Notes |
|------|-------|
| `OrganizationFederationInvited` | Trust handshake offered. |
| `OrganizationFederationAccepted` | Trust established. |
| `CrossOrgContractProposed` | Shared mission contract. |
| `CrossOrgContractSigned` | Contract active. |
| `CrossOrgMessageSent` | Federation event transmitted. |
| `FederationSyncStarted` | Federated graph sync started. |
| `FederationSyncCompleted` | Federated graph sync finished. |

## Simulation

| Event | Notes |
|------|-------|
| `SimulationStarted` | Counterfactual run initiated. |
| `SimulationCompleted` | Counterfactual run completed. |
| `SimulationDiscarded` | Branch discarded; production untouched. |
