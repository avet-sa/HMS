"""
Tests for Housekeeping Management System
Tests CRUD operations, workflow actions, and permissions
"""
import pytest
from datetime import date, time, datetime, timedelta
from fastapi import status

from backend.app.db.models import TaskStatus, TaskType, TaskPriority


@pytest.fixture
def staff_user(db):
    """Create a staff user for testing"""
    from backend.app.db.models import User, PermissionLevel
    from backend.app.core.security import get_password_hash, create_access_token
    
    # Create user directly in database
    user = User(
        username="staff_user",
        password_hash=get_password_hash("staff123"),
        permission_level=PermissionLevel.REGULAR.value,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate auth token
    token = create_access_token(subject=user.username)
    
    return {"headers": {"Authorization": f"Bearer {token}"}, "user": user}


def test_create_housekeeping_task_as_admin(client, db, admin_headers, room):
    """Test creating a housekeeping task as admin"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
            "notes": "Standard checkout cleaning"
        }
    )
    
    if response.status_code != status.HTTP_201_CREATED:
        print(f"ERROR: {response.json()}")
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["room_id"] == room.id
    assert data["task_type"] == "cleaning"
    assert data["priority"] == "normal"
    assert data["status"] == "pending"
    assert data["scheduled_date"] == tomorrow
    assert data["scheduled_time"] in ["10:00:00", "10:00"]  # Accept both formats
    assert data["notes"] == "Standard checkout cleaning"


def test_create_housekeeping_task_as_staff_fails(client, db, staff_user, room):
    """Test that staff users cannot create tasks"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    response = client.post(
        "/housekeeping/tasks/",
        headers=staff_user["headers"],
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_task_with_invalid_room_fails(client, db, admin_headers):
    """Test creating task with non-existent room"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": 99999,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Room 99999 not found" in response.json()["detail"]


def test_list_housekeeping_tasks(client, db, admin_headers, room):
    """Test listing all housekeeping tasks"""
    # Create multiple tasks
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    for i in range(3):
        client.post(
            "/housekeeping/tasks/",
            headers=admin_headers,
            json={
                "room_id": room.id,
                "task_type": "cleaning",
                "priority": "high" if i == 0 else "normal",
                "scheduled_date": tomorrow,
                "scheduled_time": f"{10+i}:00",
            }
        )
    
    # List tasks
    response = client.get("/housekeeping/tasks/", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3
    # Verify ordering (high priority first)
    assert data[0]["priority"] == "high"


def test_list_tasks_with_filters(client, db, admin_headers, room):
    """Test listing tasks with various filters"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create tasks with different priorities
    client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "high",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "maintenance",
            "priority": "low",
            "scheduled_date": tomorrow,
            "scheduled_time": "14:00",
        }
    )
    
    # Filter by priority
    response = client.get(
        "/housekeeping/tasks/",
        headers=admin_headers,
        params={"priority": "high"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(task["priority"] == "high" for task in data)
    
    # Filter by task_type
    response = client.get(
        "/housekeeping/tasks/",
        headers=admin_headers,
        params={"task_type": "maintenance"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(task["task_type"] == "maintenance" for task in data)
    
    # Filter by room
    response = client.get(
        "/housekeeping/tasks/",
        headers=admin_headers,
        params={"room_id": room.id}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(task["room_id"] == room.id for task in data)


def test_get_housekeeping_task(client, db, admin_headers, room):
    """Test getting a specific task"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    task_id = create_response.json()["id"]
    
    # Get task
    response = client.get(f"/housekeeping/tasks/{task_id}", headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert data["room_id"] == room.id


def test_get_nonexistent_task_fails(client, db, admin_headers):
    """Test getting non-existent task"""
    response = client.get("/housekeeping/tasks/99999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_housekeeping_task(client, db, admin_headers, room):
    """Test updating a housekeeping task"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    task_id = create_response.json()["id"]
    
    # Update task
    response = client.patch(
        f"/housekeeping/tasks/{task_id}",
        headers=admin_headers,
        json={
            "priority": "high",
            "notes": "Urgent cleaning required"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["priority"] == "high"
    assert data["notes"] == "Urgent cleaning required"


def test_update_task_as_staff_fails(client, db, admin_headers, staff_user, room):
    """Test that staff cannot update tasks"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create task as admin
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    task_id = create_response.json()["id"]
    
    # Try to update as staff
    response = client.patch(
        f"/housekeeping/tasks/{task_id}",
        headers=staff_user["headers"],
        json={"priority": "high"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_housekeeping_task(client, db, admin_headers, room):
    """Test deleting a pending task"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    task_id = create_response.json()["id"]
    
    # Delete task
    response = client.delete(f"/housekeeping/tasks/{task_id}", headers=admin_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deletion
    get_response = client.get(f"/housekeeping/tasks/{task_id}", headers=admin_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_assign_task(client, db, admin_headers, staff_user, room):
    """Test assigning task to staff member"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Get staff user ID
    staff_response = client.get("/users/me", headers=staff_user["headers"])
    staff_id = staff_response.json()["id"]
    
    # Create task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    task_id = create_response.json()["id"]
    
    # Assign task
    response = client.post(
        f"/housekeeping/tasks/{task_id}/assign",
        headers=admin_headers,
        json={
            "assigned_to": staff_id,
            "notes": "Please clean thoroughly"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["assigned_to"] == staff_id
    assert "Please clean thoroughly" in data["notes"]


def test_start_task(client, db, admin_headers, staff_user, room):
    """Test staff member starting assigned task"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Get staff user ID
    staff_response = client.get("/users/me", headers=staff_user["headers"])
    staff_id = staff_response.json()["id"]
    
    # Create and assign task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
            "assigned_to": staff_id,
        }
    )
    task_id = create_response.json()["id"]
    
    # Start task
    response = client.post(
        f"/housekeeping/tasks/{task_id}/start",
        headers=staff_user["headers"]
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None


def test_start_unassigned_task_fails(client, db, admin_headers, staff_user, room):
    """Test that staff cannot start tasks not assigned to them"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create task without assignment
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    task_id = create_response.json()["id"]
    
    # Try to start task
    response = client.post(
        f"/housekeeping/tasks/{task_id}/start",
        headers=staff_user["headers"]
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_complete_task(client, db, admin_headers, staff_user, room):
    """Test staff member completing task"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Get staff user ID
    staff_response = client.get("/users/me", headers=staff_user["headers"])
    staff_id = staff_response.json()["id"]
    
    # Create and assign task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
            "assigned_to": staff_id,
        }
    )
    task_id = create_response.json()["id"]
    
    # Start task
    client.post(f"/housekeeping/tasks/{task_id}/start", headers=staff_user["headers"])
    
    # Complete task
    response = client.post(
        f"/housekeeping/tasks/{task_id}/complete",
        headers=staff_user["headers"],
        json={"completion_notes": "Room cleaned and ready"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None
    assert data["completion_notes"] == "Room cleaned and ready"


def test_verify_task(client, db, admin_headers, staff_user, room):
    """Test manager verifying completed task"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Get staff user ID
    staff_response = client.get("/users/me", headers=staff_user["headers"])
    staff_id = staff_response.json()["id"]
    
    # Create, assign, and complete task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
            "assigned_to": staff_id,
        }
    )
    task_id = create_response.json()["id"]
    
    client.post(f"/housekeeping/tasks/{task_id}/start", headers=staff_user["headers"])
    client.post(
        f"/housekeeping/tasks/{task_id}/complete",
        headers=staff_user["headers"],
        json={"completion_notes": "Completed"}
    )
    
    # Verify task
    response = client.post(
        f"/housekeeping/tasks/{task_id}/verify",
        headers=admin_headers,
        json={"verification_notes": "Quality check passed"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "verified"
    assert data["verified_at"] is not None
    assert data["verification_notes"] == "Quality check passed"


def test_verify_non_completed_task_fails(client, db, admin_headers, room):
    """Test that only completed tasks can be verified"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
        }
    )
    task_id = create_response.json()["id"]
    
    # Try to verify pending task
    response = client.post(
        f"/housekeeping/tasks/{task_id}/verify",
        headers=admin_headers,
        json={"verification_notes": "Test"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_staff_can_only_see_assigned_tasks(client, db, admin_headers, staff_user, room):
    """Test that staff users only see their assigned tasks"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Get staff user ID
    staff_response = client.get("/users/me", headers=staff_user["headers"])
    staff_id = staff_response.json()["id"]
    
    # Create task assigned to staff
    client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "normal",
            "scheduled_date": tomorrow,
            "scheduled_time": "10:00",
            "assigned_to": staff_id,
        }
    )
    
    # Create unassigned task
    client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "maintenance",
            "priority": "low",
            "scheduled_date": tomorrow,
            "scheduled_time": "14:00",
        }
    )
    
    # List tasks as staff
    response = client.get("/housekeeping/tasks/", headers=staff_user["headers"])
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Should only see assigned task
    assert all(task["assigned_to"] == staff_id for task in data)


def test_task_workflow_full_cycle(client, db, admin_headers, staff_user, room):
    """Test complete task lifecycle: create → assign → start → complete → verify"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Get staff user ID
    staff_response = client.get("/users/me", headers=staff_user["headers"])
    staff_id = staff_response.json()["id"]
    
    # 1. Create task
    create_response = client.post(
        "/housekeeping/tasks/",
        headers=admin_headers,
        json={
            "room_id": room.id,
            "task_type": "cleaning",
            "priority": "high",
            "scheduled_date": tomorrow,
            "scheduled_time": "09:00",
            "notes": "VIP checkout"
        }
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    task_id = create_response.json()["id"]
    
    # 2. Assign to staff
    assign_response = client.post(
        f"/housekeeping/tasks/{task_id}/assign",
        headers=admin_headers,
        json={"assigned_to": staff_id}
    )
    assert assign_response.status_code == status.HTTP_200_OK
    
    # 3. Start task
    start_response = client.post(
        f"/housekeeping/tasks/{task_id}/start",
        headers=staff_user["headers"]
    )
    assert start_response.status_code == status.HTTP_200_OK
    assert start_response.json()["status"] == "in_progress"
    
    # 4. Complete task
    complete_response = client.post(
        f"/housekeeping/tasks/{task_id}/complete",
        headers=staff_user["headers"],
        json={"completion_notes": "Room cleaned to VIP standards"}
    )
    assert complete_response.status_code == status.HTTP_200_OK
    assert complete_response.json()["status"] == "completed"
    
    # 5. Verify task
    verify_response = client.post(
        f"/housekeeping/tasks/{task_id}/verify",
        headers=admin_headers,
        json={"verification_notes": "Inspected - excellent work"}
    )
    assert verify_response.status_code == status.HTTP_200_OK
    assert verify_response.json()["status"] == "verified"
    
    # 6. Verify final state
    final_task = client.get(f"/housekeeping/tasks/{task_id}", headers=admin_headers).json()
    assert final_task["status"] == "verified"
    assert final_task["started_at"] is not None
    assert final_task["completed_at"] is not None
    assert final_task["verified_at"] is not None
    assert final_task["assigned_to"] == staff_id
    assert final_task["completion_notes"] == "Room cleaned to VIP standards"
    assert final_task["verification_notes"] == "Inspected - excellent work"
