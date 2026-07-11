# Mission Graph

## Structure

Every action is a node with:
- who
- why
- confidence
- evidence
- alternatives
- memory used
- tools used
- artifacts
- time
- cost

## Operations

- create mission
- plan
- research
- detect conflict
- vote / debate
- approve / reject
- execute
- deploy
- reflect
- learn

## Versioning

Like Git:
- branches for risky experiments
- merge when experiment succeeds
- rollback on regression
- replay for debugging
- diff for change review
- time machine to inspect prior state

## Storage

Append-only event log by default.
Derived views for board, org chart, KPI dashboards.
