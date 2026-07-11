# OmniMind.ai Master Engineering Backlog

Version: 1.0

Status: ACTIVE

---

# RULES

Hermes MUST

- Complete ONE task at a time
- Never skip dependencies
- Update IMPLEMENTATION_PROGRESS.md
- Update Mission Graph
- Write tests
- Never break architecture
- Follow CLAUDE.md

---

# PROJECT COMPLETION

Overall Progress: 0%

---

# PHASE 0 — FOUNDATION

## TASK-001

Title: Create monorepo structure
Priority: Critical
Status: Complete
Dependencies: None
Goal: Initialize repository folders

Folders

- frontend/
- backend/
- docs/
- kernel/
- agents/
- memory/
- mission_graph/
- edge/
- plugins/
- database/
- tests/

Delivered
- Scaffold + dev tooling in place.
- Backend FastAPI shell starts; health endpoint returns 200.
- Frontend Next.js shell renders homepage.
- Unit tests pass for backend shell.
- Documentation updated.

Acceptance: All folders exist.

---

## TASK-002

Title: Initialize FastAPI backend.
Status: Complete
Acceptance: Server starts. Health endpoint works.

---

## TASK-003

Title: Initialize Next.js frontend.
Status: Pending
Acceptance: Homepage renders.

---

## TASK-004

Title: Configure Docker.
Acceptance: Frontend + Backend run using Docker Compose.

---

## TASK-005

Title: Configure GitHub Actions CI.
Acceptance: Lint, Build, Tests pass automatically.

---

## TASK-006

Title: Setup PostgreSQL.
Acceptance: Connection established.

---

## TASK-007

Title: Setup Neo4j.
Acceptance: Mission Graph DB connected.

---

## TASK-008

Title: Setup Redis.
Acceptance: Cache working.

---

## TASK-009

Title: Setup Vector DB (Qdrant).
Acceptance: Embeddings stored.

---

## TASK-010

Title: Setup environment system.
Support: .env, .dev, .prod
Secrets: Google APIs, OpenAI, Anthropic, Gemini

Acceptance: Environments load correctly.

---

# PHASE 1 — GOOGLE CLOUD

## TASK-011

Title: Connect Google Vertex AI.
Acceptance: Gemini responds.

---

## TASK-012

Title: Integrate Gemini 2.5.
Acceptance: CEO uses Gemini.

---

## TASK-013

Title: Integrate Managed Agents.
Capabilities: Python, Browser, Terminal, Filesystem, Package install, Scheduling
Acceptance: Managed Agent executes Python.

---

## TASK-014

Title: Integrate iAPI.
Acceptance: Kernel orchestrates Managed Agents.

---

## TASK-015

Title: Integrate Gemma Edge Runtime.
Acceptance: Offline inference works.

---

## TASK-016

Title: Integrate Google Search.
Acceptance: Research department performs grounded search.

---

## TASK-017

Title: Integrate NB2 Lite.
Acceptance: Marketing creates images.

---

## TASK-018

Title: Cloud Run deployment.
Acceptance: Backend deploys.

---

## TASK-019

Title: Cloud Storage.
Acceptance: Artifacts stored.

---

## TASK-020

Title: Secret Manager.
Acceptance: Keys loaded securely.

---

# PHASE 2 — KERNEL

## TASK-021

Title: Event Envelope & Registry Loader
Status: In Progress
Dependencies: TASK-002, docs/registry/EVENTS.md
Goal: Define EventEnvelope in `kernel/core/event.py`, introduce signing-keyed `event_id`, SHA-256 `payload_hash` from sorted payload, and registry-backed validation.
Delivered
- `EventEnvelope` uses `payload_hash`.
- `EventEnvelope.event_id` derives from `name`, `payload_hash`, sorted context hash, and a signing key.
- `EventRegistry.validate()` enforces payload hash length and source service presence.
Acceptance: Invalid event schema raises `InvalidEventError`. Registry loader returns canonical event definitions for v1. Payload hash matches SHA-256 of sorted JSON.

## TASK-022

Title: Kernel Event Bus Interface
Status: In Progress
Dependencies: TASK-021
Goal: Define `EventBus` protocol in `kernel/core/ports.py`, implement `InMemoryEventBus` in `kernel/core/event_bus.py`, add publish/subscribe DLQ placeholder, start/stop lifecycle, and tests in `kernel/tests/test_event_bus.py`.
Delivered
- `EventBus` protocol captures `publish`, `subscribe`, `start`, `stop`, `replay`, `dead_letter`.
- `InMemoryEventBus.publish` validates through `EventRegistry` and returns event reference string.
- Updated tests validate registration/deregistration flow.
Acceptance: `publish` returns `event_id`-ending reference. Subscribers receive published events in order. Dead-letter queue captures malformed handlers.

## TASK-023

Title: Kernel Configuration & Secrets Loader
Status: Pending
Dependencies: TASK-002
Goal: Centralize config, env layering, and secret retrieval contract.
Delivered

Acceptance: `.dev`, `.prod`, and runtime overrides load correctly. Missing required secrets raise `MissingSecretError` on startup. No secret value ever returned in logs or serialized config dumps.

## TASK-024

Title: Event Append Store
Status: Pending
Dependencies: TASK-021, TASK-002
Goal: Persist event envelope to Postgres before bus dispatch with idempotency on retry.
Delivered

Acceptance: Duplicate `event_id` insert raises constraint error. Causal version monotonicity enforced. Events queryable by `(mission_id, timestamp DESC)`.

## TASK-025

Title: Mission Graph Engine
Status: Pending
Dependencies: TASK-021, TASK-024
Goal: Canonical append-only mission graph store with branch, merge, rollback.
Delivered

Acceptance: Immutable append with required field validation. Rollback returns to target node without deleting history.

## TASK-026

Title: Memory Manager
Status: Pending
Dependencies: TASK-021, TASK-023
Goal: Hierarchical memory with working/mission/department/org awareness.
Delivered

Acceptance: Scoped memory access. Night cycle compression.

## TASK-027

Title: Knowledge Graph
Status: Pending
Dependencies: TASK-024, TASK-025
Goal: Embedding-backed Knowledge Graph for lessons/artifacts.
Delivered

Acceptance: Semantic discovery works. Embeddings invalidated on update.

## TASK-028

Title: Skill Registry
Status: Pending
Dependencies: TASK-025, TASK-027
Goal: Versioned skills lifecycle with benchmark and ratings.
Delivered

Acceptance: Fork retains provenance. Publish creates new version without losing old versions.

## TASK-029

Title: Reflection Engine
Status: Pending
Dependencies: TASK-023
Goal: Mandatory post-task/mission reflection.
Delivered

Acceptance: Reflection cannot be skipped. Outputs lessons, knowledge, skills, recommendations.

## TASK-030

Title: Evolution Engine
Status: Pending
Dependencies: TASK-029
Goal: Propose structural changes; require executive approval before applying.
Delivered

Acceptance: Proposals only. Revert emits rollback events.

## TASK-031

Title: Analytics Engine
Status: Pending
Dependencies: TASK-027
Goal: Time-series metrics for Organization IQ, Plasticity, success rates.
Delivered

Acceptance: Metrics derived from events. Historical queries bounded.

## TASK-032

Title: Security Engine
Status: Pending
Dependencies: TASK-021, TASK-030
Goal: RBAC, secrets, encryption, audit, approval.
Delivered

Acceptance: End-to-end security policies enforced.

## TASK-033

Title: Synchronization Engine
Status: Pending
Dependencies: TASK-021, TASK-025
Goal: Cloud↔edge reconciliation with causal version tracking.
Delivered

Acceptance: Conflicts flagged with entity hashes. Merge/replace/branch policies emit resolution events.

## TASK-034

Title: Digital Twin Engine
Status: Pending
Dependencies: TASK-022, TASK-027
Goal: Live organization state cache with scoped WebSocket updates.
Delivered

Acceptance: WebSocket channels can subscribe to subscopes.

Acceptance: EnterpriseOS boots.

---

# PHASE 3 — ORGANIZATION

- TASK-036 CEO
- TASK-037 CTO
- TASK-038 COO
- TASK-039 CFO
- TASK-040 CMO
- TASK-041 Research Officer
- TASK-042 Security Officer
- TASK-043 Legal Officer
- TASK-044 Infrastructure Officer
- TASK-045 Executive Board

Acceptance: Executives debate.

---

# PHASE 4 — DEPARTMENTS

- Engineering
- Research
- Marketing
- Finance
- Security
- Legal
- Infrastructure
- Operations
- Design
- Product
- Support
- Localization
- AI Safety
- Medical
- Compliance

Each department owns: Manager, Workers, Memory, Skills, KPIs, Artifacts, Reflection

---

# PHASE 5 — WORKERS

- Backend Engineer
- Frontend Engineer
- AI Engineer
- QA Engineer
- DevOps
- Designer
- Researcher
- Financial Analyst
- Legal Reviewer
- Security Analyst
- Documentation Writer
- Planner
- Scheduler

Acceptance: Workers execute independently.

---

# PHASE 6 — DYNAMIC SPECIALISTS

- OAuth Expert
- Stripe Expert
- Database Expert
- Docker Expert
- Redis Expert
- Performance Expert
- Vision Expert
- Prompt Expert
- Accessibility Expert
- Localization Expert
- Medical Reviewer
- Tax Specialist
- AI Safety Expert

Acceptance: Managers spawn specialists dynamically.

---

# PHASE 7 — MISSION GRAPH

- Immutable nodes
- Replay
- Rollback
- Merge
- Branch
- Diff
- Timeline
- Evidence
- Confidence
- Reasoning Summary
- Mission DNA

Acceptance: Git for Organizations operational.

---

# PHASE 8 — MEMORY / LEARNING / CONSTITUTION / EVOLUTION

Status: In Progress

Implemented
- `memory/service.py`, `memory/knowledge.py`, `memory/consolidation.py` establish scoped memory service, knowledge graph event emission, and duplicate/decay consolidation.
- `kernel/services/reflection.py` provides mandatory reflection pipeline with lessons/knowledge/skills/recommendations output and completion signature.
- `kernel/services/learning.py` absorbs reflection outputs into mission DNA, Organization IQ, and plasticity deltas.
- `kernel/services/constitution.py` supports effective-time rule selection and non-destructive rollback revisions.
- `kernel/services/evolution.py` supports proposal-only mutations, apply gating, and revert with rollback event emission.
- Tests added in `kernel/tests/test_reflection.py`, `kernel/tests/test_learning.py`, `kernel/tests/test_constitution.py`, `kernel/tests/test_evolution.py`.

Acceptance: Persistent learning works.

# PHASE 9 — SECURITY, APPROVAL, AUDIT

Status: In Progress

Implemented
- `backend/core/security.py` provides `RBACEnforcer` enforcing frozen permission matrix roles.
- `backend/core/dependencies.py` provides FastAPI permission dependency wiring for command endpoints.
- `backend/core/pii_scrub.py` prevents secret/prompt leakage before persistence or export.
- `backend/audit/logger.py` provides immutable append-only audit record log.
- `backend/audit/verify.py` checks audit order completeness with anti-tamper verification.
- Tests added in `backend/tests/test_rbac.py`, `backend/tests/test_pii_scrub.py`, `backend/tests/test_audit.py`.

Acceptance: End-to-end security policies enforced.

---

# PHASE 10 — FRONTEND

- Mission Dashboard
- Mission Graph
- Organization Graph
- Executive Board
- Mission Timeline
- Blackboard
- Digital Twin
- Organization Observatory
- Analytics
- Galaxy View

Acceptance: No chat UI exists. Everything is Mission-first.

---

# PHASE 11 — EDGE

- Gemma Runtime
- Offline Memory
- Offline Reflection
- Mission Continuity
- Synchronization
- Conflict Resolution

Acceptance: Mission continues offline.

---

# PHASE 12 — LEARNING

- Reflection
- Skill Generation
- Knowledge Graph
- Mission DNA
- Organization IQ
- Plasticity
- Constitution

Acceptance: Organization evolves after every mission.

---

# PHASE 13 — POLISH

- Animations
- Transitions
- Loading States
- Error Recovery
- Accessibility
- Dark Mode
- Performance
- Telemetry
- Benchmarking
- Security Audit
- Documentation
- Demo Script
- Presentation
- Hackathon Video
- Landing Page
- README
- Deployment

Acceptance: Hackathon-ready build.

---

# REQUIRED GOOGLE SERVICES

Use where appropriate:

- Gemini 2.5 Pro / Flash
- Gemma Edge
- Managed Agents (Antigravity)
- iAPI
- Vertex AI
- Cloud Run
- Cloud Storage
- Secret Manager
- Cloud Logging
- Cloud Monitoring
- Cloud Build
- Artifact Registry
- Identity Platform
- Google Search
- Maps API (optional)
- Places API (optional)
- Gmail API
- Calendar API
- Drive API
- Docs API
- Sheets API
- Firebase Auth (if appropriate)
- Firestore (for realtime features if chosen)

---

# Definition of Done

A task is complete only if:

- Architecture matches docs
- Tests pass
- APIs documented
- Events emitted
- Mission Graph updated
- Documentation updated
- IMPLEMENTATION_PROGRESS.md updated
- TASKS.md updated
- No regressions introduced

---

# PHASE 14 — ENTERPRISE KERNEL

- TASK-141 Kernel Boot Sequence
- TASK-142 Kernel Shutdown Sequence
- TASK-143 Kernel Health Monitor
- TASK-144 Kernel Scheduler
- TASK-145 Kernel Plugin Loader
- TASK-146 Kernel Event Dispatcher
- TASK-147 Kernel Crash Recovery
- TASK-148 Kernel Metrics Collector
- TASK-149 Kernel Configuration Manager
- TASK-150 Kernel Diagnostics Dashboard

Acceptance

- Kernel initializes all core services
- Health monitoring available
- Graceful shutdown supported
- Crash recovery tested

---

# PHASE 15 — PLUGIN SDK

- TASK-151 Plugin SDK Core
- TASK-152 Plugin Manifest Schema
- TASK-153 Plugin Loader
- TASK-154 Plugin Registry
- TASK-155 Plugin Marketplace UI
- TASK-156 Plugin Versioning
- TASK-157 Plugin Permission Model
- TASK-158 Plugin Sandbox
- TASK-159 Plugin Auto Update
- TASK-160 Plugin Documentation Generator

Plugins to support

- GitHub
- Slack
- Discord
- Notion
- Google Drive
- Google Docs
- Google Calendar
- Gmail
- Jira
- Linear
- Figma
- Vercel
- Docker
- Kubernetes
- Cloudflare
- Stripe
- Twilio

Acceptance

- Third-party plugins install without code changes

---

# PHASE 16 — ORGANIZATION TEMPLATES

- TASK-161 Template Engine
- TASK-162 Startup Template
- TASK-163 Research Lab Template
- TASK-164 Marketing Agency Template
- TASK-165 Law Firm Template
- TASK-166 Healthcare Template
- TASK-167 University Template
- TASK-168 Government Template
- TASK-169 Software Company Template
- TASK-170 Template Marketplace

Acceptance

- Mission chooses template automatically
- Users can create custom templates

---

# PHASE 17 — MULTI-ORGANIZATION

- TASK-171 Organization Federation
- TASK-172 Organization Discovery
- TASK-173 Inter-Organization Messaging
- TASK-174 Cross-Organization Contracts
- TASK-175 Shared Mission Support
- TASK-176 Cross-Organization Memory
- TASK-177 Federated Event Bus
- TASK-178 Federated Mission Graph
- TASK-179 Cross-Organization Analytics
- TASK-180 Federation Dashboard

Acceptance

- Multiple organizations collaborate on one mission

---

# PHASE 18 — PROMPT & MISSION COMPILER

- TASK-181 Mission Parser
- TASK-182 Mission Intermediate Representation (Mission IR)
- TASK-183 Mission Validator
- TASK-184 Mission Optimizer
- TASK-185 Mission Execution Planner
- TASK-186 Department Assignment Compiler
- TASK-187 Worker Task Graph Compiler
- TASK-188 Execution DAG Builder
- TASK-189 Mission Simulation Engine
- TASK-190 Mission Compiler Tests

Acceptance

- Natural language converts into validated execution graph

---

# PHASE 19 — MODEL ROUTER & COST ENGINE

- TASK-191 AI Router
- TASK-192 Cost Optimizer
- TASK-193 Latency Optimizer
- TASK-194 Privacy Policy Router
- TASK-195 Offline Decision Engine
- TASK-196 Confidence Threshold Engine
- TASK-197 Fallback Strategy
- TASK-198 Provider Health Monitor
- TASK-199 Adaptive Routing
- TASK-200 Usage Analytics

Routing Examples

- Planning → Gemini
- Offline → Gemma
- Creative → NB2 Lite
- Execution → Managed Agents
- Search → Google Search

Acceptance

- Automatic routing based on task characteristics

---

# PHASE 20 — OBSERVABILITY

- TASK-201 OpenTelemetry
- TASK-202 Distributed Tracing
- TASK-203 Metrics Dashboard
- TASK-204 Structured Logging
- TASK-205 Mission Replay Logs
- TASK-206 Performance Dashboard
- TASK-207 Alerting
- TASK-208 Health Checks
- TASK-209 Incident Timeline
- TASK-210 Production Monitoring

Acceptance

- Entire organization observable in production

---

# PHASE 21 — SECURITY

- TASK-211 RBAC
- TASK-212 Secret Manager Integration
- TASK-213 Encryption
- TASK-214 API Rate Limiting
- TASK-215 Audit Trail
- TASK-216 Policy Engine
- TASK-217 Human Approval Engine
- TASK-218 Sandbox Hardening
- TASK-219 Dependency Scanner
- TASK-220 Security Dashboard

Acceptance

- End-to-end security policies enforced

---

# PHASE 22 — TESTING

- TASK-221 Unit Tests
- TASK-222 Integration Tests
- TASK-223 Mission Graph Tests
- TASK-224 Event Bus Tests
- TASK-225 Worker Lifecycle Tests
- TASK-226 Department Tests
- TASK-227 Executive Board Tests
- TASK-228 Edge Runtime Tests
- TASK-229 UI Tests
- TASK-230 End-to-End Tests

Acceptance

- CI passes with high coverage

---

# PHASE 23 — CHAOS ENGINEERING

- TASK-231 Kill Worker Simulation
- TASK-232 Kill Department Simulation
- TASK-233 Lose Internet Simulation
- TASK-234 Corrupt Memory Simulation
- TASK-235 Delay Events
- TASK-236 Fail Managed Agent
- TASK-237 Database Failure Recovery
- TASK-238 Redis Failure Recovery
- TASK-239 Mission Recovery
- TASK-240 Chaos Dashboard

Acceptance

- Organization recovers automatically from failures

---

# PHASE 24 — DEMO MODE

- TASK-241 Demo Mission Generator
- TASK-242 Scripted Executive Debate
- TASK-243 Auto Conflict Generator
- TASK-244 Mission Replay Script
- TASK-245 Digital Twin Showcase
- TASK-246 Observatory Demo
- TASK-247 Counterfactual Demo
- TASK-248 Offline Demo
- TASK-249 Live Metrics Demo
- TASK-250 Presentation Mode

Acceptance

- Reliable hackathon demo with no manual setup

---

# PHASE 25 — HACKATHON POLISH

- TASK-251 Landing Page
- TASK-252 Architecture Diagram
- TASK-253 Mission Flow Diagram
- TASK-254 Organization Diagram
- TASK-255 Mission Graph Visualization
- TASK-256 README
- TASK-257 Deployment Guide
- TASK-258 Demo Script
- TASK-259 Pitch Deck
- TASK-260 Final Video

Acceptance

- Submission package complete

---

# OPTIONAL FUTURE PHASES

- Phase 26 Voice-first Organizations
- Phase 27 AR/VR Organization Observatory
- Phase 28 Robot Fleet Organizations
- Phase 29 Autonomous Enterprise Marketplace
- Phase 30 Organization-as-a-Service (OaaS)
