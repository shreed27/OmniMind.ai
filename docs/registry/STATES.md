# OmniMind Organization Protocol (OMP) State Machine Registry

Version: 1.0
Status: FROZEN

This registry is the single source of truth for all state machines in EnterpriseOS.

---

# General Rules

- State transitions are observable.
- State transitions are events.
- No component may skip states except emergency/forced transitions, which MUST still emit an event.
- State machines are deterministic given input events.
- Every transition MUST record a `reason`, `actor`, `confidence`, and `trace_id`.

---

# Mission Lifecycle

States:
- `Created`
- `Queued`
- `Planning`
- `OrganizationGeneration`
- `Execution`
- `Waiting`
- `Blocked`
- `Reviewing`
- `Reflecting`
- `Learning`
- `Evolving`
- `Completed`
- `Archived`
- `Cancelled`
- `Failed`

Transition summary:
- `Created` → `Queued` (`MissionCreated` event)
- `Queued` → `Planning` (Kernel dispatches)
- `Planning` → `OrganizationGeneration` (CEO approved plan)
- `OrganizationGeneration` → `Execution` (org ready)
- `Execution` → `Waiting` (task queue empty, pending deps)
- `Execution` → `Blocked` (hard dependency unresolved)
- `Blocked` → `Execution` (`MissionUnblocked`)
- `Waiting` → `Blocked` (dependency failed)
- `Execution` → `Reviewing` (artifact review phase)
- `Reviewing` → `Execution` (rework required)
- `Reviewing` → `Reflecting` (mission-level review complete)
- `Reflecting` → `Learning` (reflection complete)
- `Learning` → `Evolving` (learning complete)
- `Evolving` → `Completed` (evolution applied)
- `Completed` → `Archived` (Night Cycle)
- Any active → `Cancelled` (`MissionCancelled`)
- Any non-terminal → `Failed` (`MissionFailed`)
- `Cancelled`/`Failed` → `Reflecting` (reflection still executes)

Invalid transitions:
- `Completed` → `Execution` requires `MissionResumed` and new branch.
- `Cancelled` → `Execution` without human approval.

---

# Organization Lifecycle

States:
- `Registered`
- `Initializing`
- `Planning`
- `Executing`
- `Reflecting`
- `Learning`
- `Evolving`
- `Archived`
- `Destroyed`

Transition summary:
- `Registered` → `Initializing` (`OrganizationCreated`)
- `Initializing` → `Planning` (CEO plan emitted)
- `Planning` → `Executing` (executive vote passed)
- `Executing` → `Reflecting` (`MissionCompleted`/`Failed`/`Cancelled`)
- `Reflecting` → `Learning`
- `Learning` → `Evolving`
- `Evolving` → `Executing` (next wave resumed) OR `Archived`
- `Archived` → `Destroyed` (retention expired)
- `Executing` → `Archived` (mission cancelled and finalized)

---

# Department Lifecycle

States:
- `Sleeping`
- `Initializing`
- `Planning`
- `Waiting`
- `Executing`
- `Reviewing`
- `Reflecting`
- `Archived`
- `Merged`
- `Split`
- `Destroyed`

Transition summary:
- `Sleeping` → `Initializing` (`DepartmentCreated`)
- `Initializing` → `Planning` (context loaded)
- `Planning` → `Waiting` (tasks published)
- `Waiting` → `Executing` (`TaskStarted`)
- `Executing` → `Reviewing` (artifacts submitted)
- `Reviewing` → `Executing` (rework)
- `Reviewing` → `Reflecting` (tasks exhausted)
- `Reflecting` → `Sleeping` (post-reflection idle)
- `Sleeping` → `Merged` (`DepartmentMerged`)
- `Sleeping` → `Split` (`DepartmentSplit`)
- `Sleeping` → `Destroyed` (`DepartmentDestroyed`)

---

# Worker Lifecycle

States:
- `Created`
- `Sleeping`
- `Waiting`
- `Thinking`
- `Planning`
- `Executing`
- `Reviewing`
- `Blocked`
- `Escalated`
- `Reflecting`
- `Completed`
- `Archived`
- `Destroyed`

Transition summary:
- `Created` → `Waiting` (`WorkerSpawned`)
- `Waiting` → `Thinking` (mission department woke)
- `Thinking` → `Planning` (context retrieved)
- `Planning` → `Executing` (`TaskStarted`)
- `Executing` → `Reviewing` (artifact published)
- `Executing` → `Blocked` (dependency unresolved)
- `Blocked` → `Executing` (`TaskUnblocked`)
- `Executing` → `Escalated` (approval required)
- `Escalated` → `Executing` (`ApprovalCompleted`)
- `Any active` → `Reflecting` (after task completion)
- `Reflecting` → `Sleeping` (reflection done)
- `Working` → `Completed` (department archived)
- `Sleeping` → `Archived` (`WorkerRetired`)
- `Archived` → `Destroyed` (retention expired)

---

# Specialist Lifecycle (Ephemeral)

States:
- `Requested`
- `Initializing`
- `Executing`
- `Reviewing`
- `KnowledgeTransferred`
- `Destroyed`

Transition summary:
- `Requested` → `Initializing` (`SpecialistSpawned`)
- `Initializing` → `Executing`
- `Executing` → `Reviewing`
- `Reviewing` → `KnowledgeTransferred` (`SpecialistKnowledgeTransferred`)
- `KnowledgeTransferred` → `Destroyed` (`SpecialistDestroyed`)

Invalid transitions:
- `Destroyed` → anything else; specialists are one-shot.

---

# Task Lifecycle

States:
- `Created`
- `Assigned`
- `Waiting`
- `Executing`
- `Reviewing`
- `Rework`
- `Completed`
- `Failed`
- `Cancelled`
- `Retried`

Transition summary:
- `Created` → `Assigned` (`TaskCreated`)
- `Assigned` → `Waiting` (resource blocked)
- `Waiting` → `Executing` (`TaskStarted`)
- `Executing` → `Reviewing` (artifact published)
- `Reviewing` → `Rework` (changes requested)
- `Rework` → `Executing` (re-execute)
- `Reviewing` → `Completed` (approved)
- `Any active` → `Failed` (`TaskFailed`)
- `Any` → `Cancelled` (`TaskCancelled`)
- `Failed` → `Retried` (`TaskRetried`)
- `Retried` → `Executing`

---

# Artifact Review Lifecycle

States:
- `Submitted`
- `EngineeringReview`
- `SecurityReview`
- `LegalReview`
- `MarketingReview`
- `ChangesRequested`
- `Approved`
- `Published`
- `Rejected`
- `Archived`

Transition summary:
- `Submitted` → `EngineeringReview` + `SecurityReview` + `LegalReview` + `MarketingReview` (parallel)
- Any review → `ChangesRequested`
- All reviews approved → `Approved`
- `Approved` → `Published` (only after executive finalize if required)
- Any review rejects with high severity → `Rejected`

---

# Executive Board Decision Lifecycle

States:
- `Proposal`
- `Debate`
- `VoteStarted`
- `VoteCollected`
- `Decision`
- `Appeal`
- `Finalized`
- `Superseded`

Transition summary:
- `Proposal` → `Debate`
- `Debate` → `VoteStarted`
- `VoteStarted` → `VoteCollected`
- `VoteCollected` → `Decision`
- `Decision` → `Appeal` (challenge raised)
- `Appeal` → `VoteStarted` (re-vote)
- `Decision` → `Finalized` (CEO finalize or timeout)
- `Finalized` → `Superseded` (new decision overrides)

---

# Conflict Resolution Lifecycle

States:
- `ConflictRaised`
- `EvidenceRequested`
- `ReviewCommitteeActive`
- `ReVoteStarted`
- `ReVoteCompleted`
- `Resolved`
- `Appealed`

Transition summary:
- `ConflictRaised` → `EvidenceRequested`
- `EvidenceRequested` → `ReviewCommitteeActive`
- `ReviewCommitteeActive` → `ReVoteStarted`
- `ReVoteStarted` → `ReVoteCompleted`
- `ReVoteCompleted` → `Resolved`
- `Resolved` → `Appealed` (extreme case)
- `Appealed` → `ReviewCommitteeActive` (reopen)

---

# Resource Lifecycle

States:
- `Requested`
- `FinanceReview`
- `Approved`
- `Allocated`
- `Consuming`
- `Released`
- `Rejected`
- `Refunded`

Transition summary:
- `Requested` → `FinanceReview`
- `FinanceReview` → `Approved`
- `FinanceReview` → `Rejected`
- `Approved` → `Allocated`
- `Allocated` → `Consuming`
- `Consuming` → `Released`
- `Consuming` → `Refunded` (overpayment or early release)

---

# Approval Lifecycle

States:
- `Requested`
- `Escalated`
- `Approved`
- `Rejected`
- `Expired`
- `Delegated`

Transition summary:
- `Requested` → `Escalated` (requires higher authority)
- `Requested` → `Approved`
- `Requested` → `Rejected`
- `Requested` → `Expired` (timeout)
- `Requested` → `Delegated` (forwarded)

---

# Edge Runtime Lifecycle

States:
- `Online`
- `Degraded`
- `Offline`
- `EdgeActivated`
- `Configuring`
- `Continuing`
- `SyncStarted`
- `ConflictDetected`
- `SyncResolved`
- `Resuming`

Transition summary:
- `Online` → `Degraded` (intermittent connectivity)
- `Online`/`Degraded` → `Offline` (connectivity lost)
- `Offline` → `EdgeActivated` (`EdgeActivated`)
- `EdgeActivated` → `Configuring`
- `Configuring` → `Continuing`
- `Continuing` → `SyncStarted` (connectivity returned)
- `SyncStarted` → `ConflictDetected` (divergence found)
- `ConflictDetected` → `SyncResolved`
- `SyncResolved` → `Resuming`
- `Resuming` → `Online`

---

# Night Cycle Lifecycle

States:
- `Idle`
- `Starting`
- `CompressingMemory`
- `MergingSkills`
- `Benchmarking`
- `Archiving`
- `UpdatingConstitution`
- `Ready`

Transition summary:
- `Idle` → `Starting` (`NightCycleStarted`)
- `Starting` → `CompressingMemory`
- `CompressingMemory` → `MergingSkills`
- `MergingSkills` → `Benchmarking`
- `Benchmarking` → `Archiving`
- `Archiving` → `UpdatingConstitution`
- `UpdatingConstitution` → `Ready` (`NightCycleCompleted`)
- `Any` → `Idle` (emergency abort)

---

# Plugin Lifecycle

States:
- `Registered`
- `Validating`
- `Installed`
- `Enabled`
- `Disabled`
- `Failed`
- `Removed`

Transition summary:
- `Registered` → `Validating` (`PluginInstalled`)
- `Validating` → `Installed` (manifest valid)
- `Validating` → `Failed` (manifest invalid)
- `Installed` → `Enabled`
- `Enabled` → `Disabled`
- `Enabled`/`Disabled` → `Removed` (`PluginRemoved`)
- `Enabled` → `Failed` (`PluginSandboxViolation`)

---

# Reflection Pipeline Lifecycle

States:
- `Waiting`
- `CollectingEvidence`
- `ExtractingLessons`
- `GeneratingKnowledge`
- `GeneratingSkills`
- `UpdatingConstitution`
- `Completing`

Transition summary:
- `Waiting` → `CollectingEvidence` (`ReflectionStarted`)
- `CollectingEvidence` → `ExtractingLessons`
- `ExtractingLessons` → `GeneratingKnowledge`
- `GeneratingKnowledge` → `GeneratingSkills`
- `GeneratingSkills` → `UpdatingConstitution`
- `UpdatingConstitution` → `Completing` (`ReflectionCompleted`)

---

# Organization IQ Evolution Lifecycle

States:
- `CollectingMetrics`
- `Scoring`
- `Persisting`
- `Emitting`

Transition summary:
- `Scoring` → `Persisting`
- `Persisting` → `Emitting` (`OrganizationIQUpdated`)

---

# Simulation Lifecycle

States:
- `CreatingBranch`
- `Running`
- `Comparing`
- `Discarding`
- `Promoting`

Transition summary:
- `SimulationStarted` → `CreatingBranch`
- `CreatingBranch` → `Running`
- `Running` → `Comparing`
- `Comparing` → `Discarding` (`SimulationDiscarded`)
- `Comparing` → `Promoting` (branch becomes head)

---

# Morphology Lifecycle

States:
- `Monitoring`
- `ProposingSplit`
- `ProposingMerge`
- `ProposingCreate`
- `ExecutiveVoting`
- `Applying`
- `Completed`
- `Reverted`

Transition summary:
- `Monitoring` → `ProposingSplit`/`ProposingMerge`/`ProposingCreate`
- Any proposal → `ExecutiveVoting`
- `ExecutiveVoting` → `Applying`
- `Applying` → `Completed`
- `Applying` → `Reverted` (failure)

Invalid transitions:
- Merge target may not be `Destroyed`.
- Split source may not be `Destroyed`.
- `Reverted` transitions must emit rollback events.

---

# Mandatory Invariants

- Every terminal state MUST emit exactly one terminal event.
- Every transition MUST update exactly one Mission Graph node.
- Every transition MAY publish zero or more additional events.
- No transition may bypass the Event Bus.
