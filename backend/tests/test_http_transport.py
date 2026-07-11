"""Tests for HTTP Transport Layer - TASK-3.6"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from backend.app.main import app

client = TestClient(app)


class TestMissionsAPI:
    """Test missions endpoints."""

    def test_create_mission(self) -> None:
        """POST /api/v1/missions creates a new mission."""
        response = client.post(
            "/api/v1/missions/",
            json={
                "name": "Test Mission",
                "objective": "Complete test objectives",
                "priority": 1,
                "created_by": str(uuid4()),
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Mission"
        assert data["status"] == "draft"
        assert data["current_phase"] == "initialization"
        assert "mission_id" in data
        assert "event_ref" in data

    def test_start_mission(self) -> None:
        """POST /api/v1/missions/{id}/start starts mission."""
        mission_id = uuid4()

        response = client.post(f"/api/v1/missions/{mission_id}/start")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "executing"
        assert data["mission_id"] == str(mission_id)

    def test_pause_mission(self) -> None:
        """POST /api/v1/missions/{id}/pause pauses mission."""
        mission_id = uuid4()

        response = client.post(
            f"/api/v1/missions/{mission_id}/pause",
            params={"reason": "Manual pause"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"

    def test_complete_mission(self) -> None:
        """POST /api/v1/missions/{id}/complete marks as completed."""
        mission_id = uuid4()

        response = client.post(
            f"/api/v1/missions/{mission_id}/complete",
            json={"confidence": 0.95},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"


class TestOrganizationsAPI:
    """Test organizations endpoints."""

    def test_create_organization(self) -> None:
        """POST /api/v1/organizations creates organization."""
        mission_id = uuid4()

        response = client.post(
            "/api/v1/organizations/",
            json={
                "mission_id": str(mission_id),
                "hierarchy": {"departments": []},
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["mission_id"] == str(mission_id)
        assert data["health"] == "healthy"
        assert data["state"] == "initializing"
        assert "organization_id" in data

    def test_evolve_organization(self) -> None:
        """POST /api/v1/organizations/{id}/evolve triggers evolution."""
        org_id = uuid4()

        response = client.post(
            f"/api/v1/organizations/{org_id}/evolve",
            json={"departments_added": ["engineering", "research"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "evolved"


class TestDepartmentsAPI:
    """Test departments endpoints."""

    def test_create_department(self) -> None:
        """POST /api/v1/departments creates department."""
        org_id = uuid4()
        mission_id = uuid4()

        response = client.post(
            "/api/v1/departments/",
            json={
                "organization_id": str(org_id),
                "mission_id": str(mission_id),
                "type": "engineering",
                "kpis": {"velocity": 0.8},
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "engineering"
        assert data["status"] == "initializing"
        assert "department_id" in data

    def test_assign_manager(self) -> None:
        """POST /api/v1/departments/{id}/assign-manager assigns manager."""
        dept_id = uuid4()
        manager_id = uuid4()

        response = client.post(
            f"/api/v1/departments/{dept_id}/assign-manager",
            params={"manager_id": str(manager_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["manager_id"] == str(manager_id)

    def test_merge_departments(self) -> None:
        """POST /api/v1/departments/{id}/merge merges departments."""
        dept_id = uuid4()
        target_id = uuid4()

        response = client.post(
            f"/api/v1/departments/{dept_id}/merge",
            params={"target_department_id": str(target_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["merged_from"] == str(dept_id)
        assert data["merged_into"] == str(target_id)


class TestWorkersAPI:
    """Test workers endpoints."""

    def test_create_worker(self) -> None:
        """POST /api/v1/workers creates worker."""
        dept_id = uuid4()
        org_id = uuid4()
        mission_id = uuid4()

        response = client.post(
            "/api/v1/workers/",
            json={
                "department_id": str(dept_id),
                "organization_id": str(org_id),
                "mission_id": str(mission_id),
                "role": "engineer",
                "dna": {"specialization": "backend"},
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "engineer"
        assert data["status"] == "idle"
        assert "worker_id" in data

    def test_assign_task(self) -> None:
        """POST /api/v1/workers/{id}/assign-task assigns task."""
        worker_id = uuid4()
        task_id = uuid4()

        response = client.post(
            f"/api/v1/workers/{worker_id}/assign-task",
            json={
                "task_id": str(task_id),
                "task_description": "Implement feature X",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == str(task_id)
        assert data["status"] == "assigned"

    def test_promote_worker(self) -> None:
        """POST /api/v1/workers/{id}/promote promotes worker."""
        worker_id = uuid4()

        response = client.post(
            f"/api/v1/workers/{worker_id}/promote",
            params={"new_role": "senior_engineer"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["new_role"] == "senior_engineer"

    def test_spawn_specialist(self) -> None:
        """POST /api/v1/workers/{id}/spawn-specialist spawns specialist."""
        worker_id = uuid4()

        response = client.post(
            f"/api/v1/workers/{worker_id}/spawn-specialist",
            params={"specialist_type": "security_auditor"},
            json={"audit_scope": "authentication"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["specialist_type"] == "security_auditor"
        assert "specialist_id" in data
