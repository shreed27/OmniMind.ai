"""
WebSocket Gateway - TASK-11.2

Real-time event streaming to frontend clients.
Mission Graph updates, Digital Twin changes, Live execution status.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus


class WebSocketConnection:
    """Active WebSocket connection with subscription filters."""

    def __init__(self, websocket: WebSocket, connection_id: str) -> None:
        self.websocket = websocket
        self.connection_id = connection_id
        self.subscriptions: dict[str, Any] = {}
        self.authenticated = False
        self.user_id: str | None = None
        self.workspace_id: str | None = None

    async def send_event(self, event: EventEnvelope) -> None:
        """Send event to client if subscribed."""
        await self.websocket.send_json(
            {
                "type": "event",
                "event_id": event.event_id,
                "name": event.payload.get("name", ""),
                "mission_id": event.mission_id,
                "organization_id": event.organization_id,
                "department_id": event.department_id,
                "worker_id": event.worker_id,
                "payload": event.payload,
                "timestamp": event.timestamp,
            }
        )

    async def send_message(self, message_type: str, payload: dict[str, Any]) -> None:
        """Send control message to client."""
        await self.websocket.send_json({"type": message_type, "payload": payload})


class WebSocketGateway:
    """
    WebSocket gateway for real-time updates.

    Subscriptions:
    - Mission updates
    - Organization updates
    - Department updates
    - Worker updates
    - Mission Graph updates
    - Digital Twin updates
    - Artifact updates
    - Reflection updates
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._logger = get_logger("websocket_gateway")
        self._connections: dict[str, WebSocketConnection] = {}
        self._subscriptions: dict[str, set[str]] = {}  # event_type -> {connection_id}

    async def connect(self, websocket: WebSocket) -> str:
        """Accept WebSocket connection."""
        await websocket.accept()

        connection_id = str(uuid4())
        connection = WebSocketConnection(websocket, connection_id)
        self._connections[connection_id] = connection

        self._logger.info("WebSocket connected: %s", connection_id)

        # Send welcome message
        await connection.send_message("connected", {"connection_id": connection_id})

        return connection_id

    async def disconnect(self, connection_id: str) -> None:
        """Close WebSocket connection and cleanup subscriptions."""
        if connection_id in self._connections:
            connection = self._connections.pop(connection_id)

            # Remove from all subscriptions
            for subscribers in self._subscriptions.values():
                subscribers.discard(connection_id)

            self._logger.info("WebSocket disconnected: %s", connection_id)

    async def subscribe(
        self,
        connection_id: str,
        *,
        mission_id: str | None = None,
        organization_id: str | None = None,
        department_id: str | None = None,
        event_types: list[str] | None = None,
    ) -> None:
        """
        Subscribe connection to event stream.

        Filters:
        - mission_id: Only events for this mission
        - organization_id: Only events for this organization
        - event_types: Only specific event types
        """
        if connection_id not in self._connections:
            return

        connection = self._connections[connection_id]

        connection.subscriptions = {
            "mission_id": mission_id,
            "organization_id": organization_id,
            "department_id": department_id,
            "event_types": event_types or [],
        }

        # Register for event types
        for event_type in event_types or ["*"]:
            self._subscriptions.setdefault(event_type, set()).add(connection_id)

        await connection.send_message(
            "subscribed",
            {
                "mission_id": mission_id,
                "organization_id": organization_id,
                "event_types": event_types,
            },
        )

        self._logger.info("WebSocket %s subscribed: mission=%s, org=%s", connection_id, mission_id, organization_id)

    async def broadcast_event(self, event: EventEnvelope) -> None:
        """Broadcast event to all matching subscriptions."""
        event_name = event.payload.get("name", "")

        # Get all connections subscribed to this event type
        subscribers = self._subscriptions.get(event_name, set()) | self._subscriptions.get("*", set())

        for connection_id in list(subscribers):
            if connection_id not in self._connections:
                continue

            connection = self._connections[connection_id]

            # Apply filters
            if not self._matches_subscription(event, connection.subscriptions):
                continue

            try:
                await connection.send_event(event)
            except Exception as exc:
                self._logger.error("Failed to send event to %s: %s", connection_id, exc)
                await self.disconnect(connection_id)

    def _matches_subscription(self, event: EventEnvelope, subscription: dict[str, Any]) -> bool:
        """Check if event matches subscription filters."""
        # Mission filter
        if subscription.get("mission_id") and event.mission_id != subscription["mission_id"]:
            return False

        # Organization filter
        if subscription.get("organization_id") and event.organization_id != subscription["organization_id"]:
            return False

        # Department filter
        if subscription.get("department_id") and event.department_id != subscription["department_id"]:
            return False

        return True

    async def handle_client_message(self, connection_id: str, message: dict[str, Any]) -> None:
        """Handle incoming message from client."""
        if connection_id not in self._connections:
            return

        connection = self._connections[connection_id]
        message_type = message.get("type")

        if message_type == "subscribe":
            await self.subscribe(
                connection_id,
                mission_id=message.get("mission_id"),
                organization_id=message.get("organization_id"),
                department_id=message.get("department_id"),
                event_types=message.get("event_types", []),
            )

        elif message_type == "unsubscribe":
            connection.subscriptions = {}
            await connection.send_message("unsubscribed", {})

        elif message_type == "ping":
            await connection.send_message("pong", {"timestamp": EventEnvelope.now({})})

    def connection_count(self) -> int:
        """Get active connection count."""
        return len(self._connections)
