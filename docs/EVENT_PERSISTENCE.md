## Phase 2 Event Persistence
- Event append: Postgres immutable append-only store
- Events table: events
- Indexes: mission_id, created_at
- Eligibility: causal version monotonicity enforced
- Backfill: none
