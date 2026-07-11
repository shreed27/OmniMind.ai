# REST API Contracts

## Endpoints
- GET /healthz → 200 JSON
- POST /api/v1/managed-agents/execute → execute managed agent capability
- GET /api/v1/healthz → health check

## Events
- Every command emits event via EventBus.
- Response includes event reference string when available.

## Auth
- Role via X-Role header.
