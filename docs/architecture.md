# Architecture

## Kernel

Event-driven kernel owns:
- Mission Scheduler
- Event Bus
- Knowledge Graph
- Conflict Engine
- Memory Manager
- Skill Registry
- Evolution Engine
- Organization Graph
- Mission Graph
- Security Manager
- Resource Manager
- Analytics Engine
- Reflection Engine
- Synchronization Engine

## Organization

Mission → CEO → Departments → Teams → Managers → Workers → Temporary Specialists

Departments own memory, skills, APIs, tools, knowledge, KPIs, artifacts, resources.

## Communication

Nothing directly calls another agent. Everything is an event.

Mission Created → Event Bus → Departments subscribe / wake / react / ignore

## Shared state

All work happens on the Mission Board.
Versioned, timestamped, attributed, observable, replayable.

## Execution

Mission Graph nodes: Created → Planning → Research → Conflict → Vote → Approval → Execution → Deployment → Reflection → Learning

Supports branches, merge, rollback, replay, diff, time machine.

## Conflict

Disagreement is expected.
Security rejects → CEO spawns Review Committee → temporary specialists → final vote.
Nothing is hidden.
