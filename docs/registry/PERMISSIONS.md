# OmniMind Organization Protocol (OMP) Permission Registry

Version: 1.0
Status: FROZEN

This registry defines read/write/execute authority for every Kernel role.
The Security Service evaluates these policies at enforcement points.

---

# Baseline

| Entity | May |
|-------|-----|
| Anonymous | Nothing. |
| User | Create Missions, view own organization, submit approvals. |
| Kernel | Full authority over internal services. |
| Executive | Write within executive scope; require CEO confirmation for structural changes. |

---

# Executive Layer

| Role | Read | Write | Execute | Structure | Security |
|------|------|-------|---------|-----------|----------|
| CEO | All org/mission data | All org/mission mutations | Execute executive plan | Merge/split/create/archive depts and org | Can create review committees, escalate, publish constitution |
| CTO | Engineering outputs | Engineering artifacts | Approve code merges | Modify engineering org only | Can require security review |
| COO | Execution status | Reassign/pause/resume tasks | Manage scheduler | None | None |
| CFO | Budget/resources | Approve compute/allocate | None | None | Can block expensive plans |
| CMO | Marketing assets | Publish creative outputs | Launch campaigns | Marketing org only | Can require legal review |
| CRO | Research data | Publish research recommendations | Recommend changes | None | Cannot modify production |
| CSO | Security audit data | Publish audit reports | Scan code/infra | None | Can reject deployment |
| CLO | Legal/compliance data | Publish legal reviews | Approve compliance | None | Can reject launch/deployment |
| CIO | Infrastructure metrics | Scaling decisions | Infrastructure changes | Infrastructure org only | None |

Executive invariants:
- Executives never execute worker-level runtime.
- Every executive output is a Mission Graph node.
- All executive decisions are observable in the Event Bus and Mission Graph.

---

# Worker Layer

| Role | Read | Write | Execute | Structure | Security |
|------|------|-------|---------|-----------|----------|
| Base Worker | Mission, Department Memory, Skills, Blackboard | Publish artifacts, emit events, generate skills | Execute assigned task | Spawn specialists if manager allows | Cannot bypass organization policy |
| Specialist | Same as base worker for mission slice | Same | Same | Destroyed on completion | Same |
| Manager | Department Memory, workers, board | Assign tasks, pause/resume workers | Review artifacts | Spawn specialists, merge/promote workers within dept | Can request human approval |

Worker invariants:
- Workers cannot directly modify another department.
- All inter-department coordination occurs through events or shared board.
- Workers cannot bypass approval gates.
- Workers cannot produce execution outside assigned capability scope.

---

# Kernel Layer

| Service | Read | Write | Execute | Privileged |
|---------|------|-------|---------|-----------|
| Mission Scheduler | Mission metadata | Mission lifecycle transitions | Schedule missions | Pause/cancel missions without user confirmation |
| Organization Manager | Organization graph | Org lifecycle transitions | Spawn departments | Merge/split organization |
| Event Bus Service | All events | Replay, redrive | Route events | Dead-letter and retry for all publishers |
| Mission Graph Service | Graph views | Append-only nodes/edges | Query/Replay/Diff | Append-only enforcement |
| Memory Service | Memory by scope | Store/compress/archive | Retrieve/search | Dedupe/decay |
| Reflection Service | Task/mission history | Reflection outputs | Run reflection pipeline | Non-skippable at task/mission level |
| Evolution Service | KPIs, reflection | Propose changes | Analyze HQ | Cannot apply structural changes without executive approval |
| Security Service | Audit, permissions | Audit blocks, rejections | Authorize | Can force-cancel risky execution |
| Approval Engine Service | Approval queue | Record decisions | Escalate/timeout | None |
| Edge Runtime Service | Local state | Local writes | Local execution | Can resume offline mission if orphaned |
| Plugin Loader Service | Plugin registry | Install/uninstall/update | Load into sandbox | Cannot bypass kernel policy |

---

# Resource Access

| Resource | Viewer | Requester | Approver | Auditor |
|---------|--------|-----------|----------|---------|
| Budget | CEO, CFO, Org Owner | Department Manager | CFO, CEO | Kernel, Security |
| Compute | Department Manager | Worker | CFO | Kernel |
| GPU | Department Manager | Worker | CFO | Kernel, Security |
| API Quota | Department Manager | Worker | CFO | Kernel |
| Storage | Department Manager | Worker | CIO | Kernel |

---

# Approval Authority

| Decision Type | Required Authority | Expiry | Escalation |
|---------------|-------------------|--------|-----------|
| Financial > threshold | CFO | 24h | CEO |
| Legal/Compliance | CLO | 48h | CEO |
| Security Deployment | CSO | 24h | CEO |
| Architecture Change | CTO | 24h | CEO |
| Budget Exceeded > 20% | CFO | 24h | CEO |
| Repeated Failure > 3 | Manager | immediate | Executive Board |
| Low Confidence < 0.5 | Manager | immediate | Executive Board |

---

# Event Read Scope

Read access to live events:
- Kernel: all events.
- Security: all events.
- Executive Board: mission-scoped events only.
- Manager: department-scoped events only.
- Worker: mission-scoped events only.

Replay access:
- Users: missions they own.
- Executives: full mission graph for their organization.
- Kernel: all missions.

---

# Plugin Permissions Model

| Capability | Allowed | Requires Approval |
|-----------|---------|------------------|
| Read Events | Yes | No |
| Publish Events | Yes | No |
| Call Managed Agent | Yes | Yes |
| Access Filesystem | No | Yes |
| Access Network | No | Yes |
- Read/Write Memory | Yes | Department-scoped |
- Publish Artifacts | No | Yes |
- Modify Knowledge Graph | No | Yes |
- Invoke Research Service | Yes | No |
- Invoke Creative Service | No | Yes |

---

# Traceability Requirements

Every permission grant/revocation MUST:
- Create an immutable PermissionNode in Mission Graph.
- Emit a PermissionUpdated event.
- Be auditable via Security Audit API.
