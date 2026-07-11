# API Contracts

## Principles

- event-first, not RPC-first
- typed events with schema registry
- backward-compatible event evolution
- no silent schema changes

## Core events

- `mission.created`
- `mission.updated`
- `plan.proposed`
- `research.completed`
- `conflict.detected`
- `vote.completed`
- `approval.granted`
- `approval.rejected`
- `execution.started`
- `execution.completed`
- `deployment.deployed`
- `reflection.completed`
- `learning.applied`

## Error model

- retry with exponential backoff
- dead-letter queue for poison events
- explicit failure events, not timeouts

## Auth

Agent identity required.
Skill execution requires capability token.
Cross-org access requires explicit grant.
