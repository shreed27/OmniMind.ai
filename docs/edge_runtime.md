# Edge Runtime

## Purpose

Operate offline, recover fast, and sync later.

## Capabilities

- local mission execution
- local memory and state
- offline fallback for skills and runtimes
- conflict-free replicated data types for shared state
- resume from checkpoint after failure
- background sync when network returns

## Guarantees

- durability before acknowledgment
- idempotent event replay
- deterministic replay for debugging
- bounded resource usage on-device

## When to use

- deployed environments with intermittent connectivity
- privacy or compliance constraints
- cost-sensitive long-running missions
