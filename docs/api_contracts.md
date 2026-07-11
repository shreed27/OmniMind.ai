# OmniMind.ai
# API Contracts

Version: v1

---

# Philosophy

Everything revolves around Missions.

There are no chat APIs.
There are no prompt APIs.

Every request belongs to a Mission.
Every response updates the Mission Graph.
Every important action emits Events.

Everything is versioned.
Everything is replayable.

---

# Base URL

/api/v1

---

# Authentication

Authorization: Bearer JWT

Every request contains

- Authorization
- WorkspaceID
- MissionID (optional)
- OrganizationID (optional)
- UserID

---

# API Categories

- Mission APIs
- Organization APIs
- Executive APIs
- Department APIs
- Worker APIs
- Mission Graph APIs
- Memory APIs
- Knowledge Graph APIs
- Skill APIs
- Artifact APIs
- Reflection APIs
- Learning APIs
- Analytics APIs
- Edge APIs
- Synchronization APIs
- Event APIs

---

# Mission APIs

POST /api/v1/missions

Create Mission

Body

- name
- objective
- constraints
- budget
- deadline
- priority

Returns

- Mission
- Organization
- MissionGraph
- ExecutiveBoard
- Status

---

GET /api/v1/missions/{id}

Returns

- Mission
- Mission Graph
- Organization
- Departments
- Workers
- Artifacts
- Timeline
- Analytics
- Reflection

---

PATCH /api/v1/missions/{id}

Update

- Objective
- Budget
- Deadline
- Priority
- KPIs
- Stakeholders

---

DELETE /api/v1/missions/{id}

Archives mission.
Mission Graph remains immutable.

---

POST /api/v1/missions/{id}/pause

Pause execution.

---

POST /api/v1/missions/{id}/resume

Resume execution.

---

POST /api/v1/missions/{id}/cancel

Cancel Mission.
Reflection still executes.

---

POST /api/v1/missions/{id}/simulate

Counterfactual Simulation

Input: Alternative assumptions
Returns:

- Projected Timeline
- Projected Cost
- Projected Confidence
- Projected Organization

---

# Organization APIs

GET /api/v1/organization

Returns

- Digital Twin
- Departments
- Hierarchy
- Organization Health
- IQ
- Plasticity
- Resources

---

POST /api/v1/organization/restructure

Body

- Create Department
- Merge
- Split
- Remove

Returns: Updated Organization

---

GET /api/v1/organization/timeline

Returns complete replay history.

---

GET /api/v1/organization/history

Returns

- Mission history
- Learning history
- Reflection history

---

GET /api/v1/organization/dna

Returns

- Mission Patterns
- Success Patterns
- Failure Patterns
- Organization Evolution

---

# Executive APIs

POST /api/v1/executives/meeting

Starts

- Planning
- Conflict
- Budget
- Launch
- Emergency
- Reflection
- Meeting

---

GET /api/v1/executives/board

Returns

- Executive Board
- Votes
- Meetings
- Current Decisions

---

POST /api/v1/executives/vote

Input

- Decision
- Confidence
- Evidence
- Alternatives
- Risk

Returns: Vote Node, Mission Graph Updated

---

POST /api/v1/executives/escalate

Escalates

- Human Review
- Legal Review
- Security Review
- Finance Review
- Medical Review

---

# Department APIs

GET /api/v1/departments

Returns all departments.

---

GET /api/v1/departments/{id}

Returns

- Workers
- Memory
- KPIs
- Artifacts
- Skills
- Resources
- Tasks

---

POST /api/v1/departments

Create temporary department.

---

DELETE /api/v1/departments/{id}

Destroy department.
Knowledge persists.

---

POST /api/v1/departments/{id}/split

Returns new departments.

---

POST /api/v1/departments/{id}/merge

Merge departments.

---

PATCH /api/v1/departments/{id}/objective

Update department objective.

---

# Worker APIs

GET /api/v1/workers

List workers.

---

GET /api/v1/workers/{id}

Returns

- Memory
- Current Task
- Artifacts
- Skills
- KPIs
- Confidence
- Dependencies
- Lineage
- DNA

---

POST /api/v1/workers/{id}/spawn

Creates temporary specialist.

---

POST /api/v1/workers/{id}/retire

Archives worker.
Knowledge retained.

---

PATCH /api/v1/workers/{id}/promote

Updates hierarchy.

---

POST /api/v1/workers/{id}/reflect

Triggers reflection.

---

GET /api/v1/workers/{id}/genealogy

Returns complete delegation tree.

---

# Mission Graph APIs

Mission Graph is the immutable event history of every mission.
Every decision, artifact, review and reflection becomes a node.

GET /api/v1/mission-graph/{missionId}

Returns

- nodes
- edges
- timeline
- branches
- commits

---

GET /api/v1/mission-graph/{missionId}/timeline

Returns chronological replay.

---

GET /api/v1/mission-graph/{missionId}/node/{nodeId}

Returns

- Owner
- Department
- Confidence
- Evidence
- Dependencies
- Reasoning Summary
- Memory Used
- Artifacts
- Votes
- Execution Time
- Cost
- Version

---

POST /api/v1/mission-graph/{missionId}/branch

Creates execution branch.

Example

- Research Alternative
- Engineering Alternative
- Legal Alternative

---

POST /api/v1/mission-graph/{missionId}/merge

Merge branches.
CEO approval required.

---

POST /api/v1/mission-graph/{missionId}/rollback

Rollback Mission Graph to previous node.

---

GET /api/v1/mission-graph/{missionId}/diff

Compares two Mission Graph snapshots.

Returns

- Added Departments
- Removed Departments
- New Skills
- New Memories
- Decision Changes
- Budget Changes
- Timeline Differences

---

# Event Bus APIs

Every interaction is an Event.

GET /api/v1/events

Returns all live events.

---

POST /api/v1/events/publish

Body

- type
- source
- payload

---

POST /api/v1/events/subscribe

Body

- agentId
- eventTypes

---

Supported Events

- MissionCreated
- MissionUpdated
- MissionCompleted
- MissionFailed
- DepartmentCreated
- DepartmentDestroyed
- WorkerSpawned
- WorkerRetired
- SpecialistSpawned
- TaskCreated
- TaskCompleted
- TaskFailed
- ArtifactCreated
- ArtifactUpdated
- MemoryStored
- MemoryRetrieved
- ConflictRaised
- VoteStarted
- VoteCompleted
- ReflectionStarted
- ReflectionCompleted
- LearningCompleted
- SkillCreated
- SkillPublished
- SkillInstalled
- SynchronizationStarted
- SynchronizationCompleted
- EdgeActivated
- CloudActivated
- OrganizationUpdated

---

# Shared Blackboard APIs

GET /api/v1/blackboard/{missionId}

Returns

- Mission Board
- Research Progress
- Engineering Progress
- Finance Status
- Legal Status
- Confidence
- Dependencies
- Current Blockers

---

PATCH /api/v1/blackboard/{missionId}

Every modification is versioned.
Every change becomes a Mission Graph node.

---

GET /api/v1/blackboard/history

Replay every modification.

---

# Memory APIs

GET /api/v1/memory

Returns

- Working Memory
- Mission Memory
- Department Memory
- Organization Memory
- Knowledge Graph
- Skill Memory

---

POST /api/v1/memory/store

Store new memory.

---

POST /api/v1/memory/search

Hybrid search.

- Semantic
- Keyword
- Graph
- Embedding

---

POST /api/v1/memory/consolidate

Night Cycle trigger.

Compresses

- Duplicate memories
- Low-value memories
- Unused embeddings

---

POST /api/v1/memory/archive

Archives completed mission memories.

---

# Knowledge Graph APIs

GET /api/v1/knowledge

Returns graph.

---

POST /api/v1/knowledge/node

Create node.

---

POST /api/v1/knowledge/edge

Create relationship.

---

GET /api/v1/knowledge/search

Search

- Mission
- Skill
- Memory
- Artifact
- Department
- Worker
- Lesson
- Decision

---

# Skill Marketplace APIs

GET /api/v1/skills

Returns

- Published Skills
- Versions
- Ratings
- Benchmarks
- Downloads
- Dependencies

---

POST /api/v1/skills

Publish Skill.

---

POST /api/v1/skills/install

Install reusable skill.

---

POST /api/v1/skills/fork

Fork skill.

---

POST /api/v1/skills/benchmark

Benchmark skill.

---

POST /api/v1/skills/version

Publish new version.

---

POST /api/v1/skills/rate

Rate skill.

---

GET /api/v1/skills/history

Version history.

---

# Artifact APIs

GET /api/v1/artifacts

Returns

- Code
- Images
- Reports
- Presentations
- Videos
- Landing Pages
- Documentation

---

POST /api/v1/artifacts

Publish artifact.

---

GET /api/v1/artifacts/{id}/lineage

Returns provenance.

- Mission
- Department
- Worker
- Skill
- Memory
- Prompt
- Tool
- Artifact

---

# Reflection APIs

POST /api/v1/reflection/start

Starts organizational reflection.

---

GET /api/v1/reflection/{missionId}

Returns

- Lessons
- Mistakes
- Successes
- Skills
- Recommendations
- Constitution Updates
- Organization Changes

---

POST /api/v1/reflection/publish

Publishes organizational learning.

---

# Organizational Learning APIs

GET /api/v1/learning

Returns

- Learning History
- Knowledge Growth
- Skill Growth
- Mission DNA
- Organization IQ
- Plasticity

---

POST /api/v1/learning/update

Updates

- Knowledge Graph
- Skills
- Constitution
- Organization
- Mission DNA

---

GET /api/v1/learning/recommendations

Returns

- Recommended Skills
- Department Changes
- Architecture Improvements
- Research Suggestions

---

# WebSocket APIs

OmniMind is event-driven.
The frontend should never poll.
Every update is streamed.

Connection: GET /ws
Authentication: Bearer JWT, WorkspaceID, MissionID, OrganizationID

Subscriptions

- Mission Updates
- Organization Updates
- Department Updates
- Worker Updates
- Mission Graph Updates
- Memory Updates
- Knowledge Graph Updates
- Skill Updates
- Reflection Updates
- Analytics Updates
- Digital Twin Updates
- Edge Synchronization
- Conflict Updates
- Vote Updates
- Artifact Updates

---

# Real-time Event Types

- MissionCreated
- MissionUpdated
- MissionCompleted
- MissionPaused
- MissionCancelled
- MissionFailed
- OrganizationCreated
- OrganizationUpdated
- DepartmentCreated
- DepartmentMerged
- DepartmentSplit
- DepartmentDestroyed
- WorkerSpawned
- WorkerPromoted
- WorkerRetired
- WorkerDestroyed
- SpecialistSpawned
- TaskCreated
- TaskStarted
- TaskCompleted
- TaskBlocked
- TaskFailed
- ConflictRaised
- VoteStarted
- VoteCompleted
- ArtifactCreated
- ArtifactUpdated
- SkillPublished
- SkillInstalled
- SkillUpdated
- MemoryStored
- MemoryUpdated
- ReflectionStarted
- ReflectionCompleted
- LearningCompleted
- NightCycleStarted
- NightCycleCompleted
- OrganizationEvolved
- MissionGraphUpdated
- DigitalTwinUpdated
- EdgeActivated
- CloudActivated
- SynchronizationStarted
- SynchronizationCompleted
- HumanApprovalRequested
- HumanApprovalCompleted

---

# Digital Twin API

GET /api/v1/digital-twin

Returns

- Organization Graph
- Departments
- Workers
- Status
- Current Tasks
- KPIs
- Health
- Confidence
- Resources
- Dependencies

Digital Twin updates continuously through WebSockets.

---

GET /api/v1/digital-twin/{departmentId}

Returns

- Department
- Workers
- Managers
- Tasks
- Memory
- Artifacts
- Confidence
- Resources
- Health

---

GET /api/v1/digital-twin/{workerId}

Returns

- Current Task
- Current State
- Dependencies
- Memory
- Artifacts
- Confidence
- ETA
- Current Tool
- Current Skill
- Genealogy
- Mission Graph Node

---

# Mission Replay API

GET /api/v1/replay/{missionId}

Returns entire Mission Timeline

- Planning
- Delegation
- Research
- Conflicts
- Votes
- Artifacts
- Reflection
- Learning

Supports

- Play
- Pause
- Step
- Jump
- Replay Speed

---

# Counterfactual API

POST /api/v1/simulation

Body: Alternative Timeline

Example

- Research finishes early
- Budget doubles
- Legal approves

Returns

- Predicted Timeline
- Mission Success Probability
- Organization Changes
- Resource Changes
- Confidence
- Mission Graph Branch

---

# Organization Health API

GET /api/v1/analytics/organization

Returns

- Organization IQ
- Plasticity
- Mission Success Rate
- Learning Rate
- Knowledge Growth
- Skill Growth
- Department Health
- Average Confidence
- Average Recovery Time
- Resource Utilization
- Current Risk

---

# Department Analytics

GET /api/v1/analytics/departments

Returns

- Engineering
- Research
- Marketing
- Finance
- Security
- Legal
- Infrastructure
- Operations

Each returns

- Health
- Workers
- KPIs
- Artifacts
- Learning
- Budget
- Resources
- Confidence

---

# Organizational IQ API

GET /api/v1/analytics/iq

Returns

- Planning
- Execution
- Learning
- Communication
- Knowledge Reuse
- Conflict Resolution
- Reflection
- Plasticity
- Mission Success
- Overall IQ
- Historical Trend

---

# Plasticity API

GET /api/v1/analytics/plasticity

Returns

- Departments Created
- Departments Removed
- Hierarchy Changes
- Specialists Spawned
- Skills Reused
- Skills Generated
- Memory Reuse
- Adaptation Speed
- Plasticity Score

---

# Edge Runtime APIs

GET /api/v1/edge/status

Returns

- Online
- Offline
- Hybrid
- Current Device
- Current Mission
- Synchronization Status

---

POST /api/v1/edge/activate

Starts local organization.

- Mini CEO
- Mini Planner
- Mini Engineer
- Mini Memory
- Mini Skills

---

POST /api/v1/edge/sync

Synchronizes

- Mission Graph
- Artifacts
- Memory
- Knowledge Graph
- Skills
- Reflection
- Analytics

---

POST /api/v1/edge/conflicts

Returns synchronization conflicts.

Supports

- Merge
- Replace
- Branch
- Replay

---

# Managed Agent APIs

POST /api/v1/managed-agents/execute

Runs

- Python
- Node
- Terminal
- Browser
- Search
- Package Installation
- Scheduling
- Filesystem

Returns

- Logs
- Artifacts
- Execution Time
- Exit Status
- Mission Graph Node

---

# NB2 Creative APIs

POST /api/v1/creative/generate

Input

- Campaign
- Landing Page
- Banner
- LinkedIn
- Twitter
- Presentation
- Poster

Returns

- Artifacts
- Preview
- Versions
- Mission Graph Node

---

# Research APIs

POST /api/v1/research/query

Searches

- Web
- Papers
- Documentation
- Benchmarks

Returns

- Research Report
- Evidence
- Sources
- Recommendations
- Confidence

---

# Security APIs

GET /api/v1/security/audit

Returns

- Permissions
- Secrets
- Compliance
- Risks
- Sandbox Status
- Human Approval Queue

---

POST /api/v1/security/approve

Human approval endpoint.

---

# Organization Search

GET /api/v1/search

Searches everything.

- Mission
- Department
- Worker
- Skill
- Memory
- Artifact
- Knowledge
- Timeline
- Reflection
- Mission Graph
- DNA

---

# API Error Contract

Every error follows one format.

{
  "success": false,
  "code": "MISSION_NOT_FOUND",
  "message": "...",
  "suggestion": "...",
  "retryable": true,
  "missionGraphNode": "...",
  "timestamp": "...",
  "traceId": "..."
}

No opaque errors.
Every error is traceable.

---

# Versioning

Current: /api/v1
Future: /api/v2, /api/v3

Versioned

- Mission Graph version
- Skill version
- Organization version
- Constitution version
- Memory schema version

Every API is backward compatible.

---

# API Design Principles

- Mission-first
- Never chat-first
- Everything observable
- Everything replayable
- Everything explainable
- Everything versioned
- Everything event-driven
- Everything emits Mission Graph nodes
- Everything contributes to organizational learning

Every API should answer:

- What changed?
- Why?
- Who changed it?
- What evidence supported it?
- What confidence exists?
- What will happen next?

---

# Final Architecture

                    User
                      │
                 REST API
                      │
           EnterpriseOS API
                      │
     ┌───────────────────────────────────┐
     │                                   │
 Mission APIs                    Organization APIs
 Mission Graph                   Memory APIs
 Skills                          Analytics APIs
 Reflection                      Edge Runtime
 Digital Twin                    Research
 Security                        Managed Agents
 Event Bus                       Creative APIs
     │                                   │
     └───────────────────────────────────┘
                      │
                EnterpriseOS Kernel
                      │
                 Living Organization
                      │
            Mission Graph + Digital Twin
                      │
             Organizational Learning Loop
