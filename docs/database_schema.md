# Database Schema

## PostgreSQL

### Users
- id
- email
- workspace
- settings

### Missions
- id
- objective
- status
- priority
- confidence
- budget
- created_at

### Organizations
- id
- mission_id
- health
- iq
- plasticity

### Departments
- id
- organization_id
- type
- manager_id

### Workers
- id
- department_id
- dna
- confidence
- status

### Skills
- id
- version
- author
- downloads
- benchmark

### Artifacts
- id
- mission_id
- type
- lineage

### Events
- id
- type
- payload
- timestamp

### Reflections
- id
- mission_id
- lessons
- improvements

### Constitution
- id
- version
- rule
- source

### Analytics
- mission_id
- iq
- learning_rate
- reuse_rate

---

## Neo4j

Nodes
- Mission
- Department
- Worker
- Task
- Decision
- Artifact
- Skill
- Memory
- Lesson

Relationships

- CREATED
- USES
- LEARNED
- GENERATED
- REVIEWED
- DEPENDS_ON
- BLOCKED_BY
- MERGED_INTO

---

## Redis

- Current Sessions
- Mission Cache
- Worker Cache
- Live Digital Twin
- WebSocket Channels
- Event Queue
- Task Queue

---

## Vector Database

- Mission Memory
- Organization Memory
- Department Memory
- Skills
- Research Reports
- Reflection
- Documentation
