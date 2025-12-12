"""Tests for housekeeping reporting endpoints"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi import status

from backend.app.db import models


def test_housekeeping_dashboard_empty(client: TestClient, admin_headers):
    """Test dashboard with no data"""
    response = client.get("/reports/housekeeping/dashboard", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["pending_tasks"] == 0
    assert data["rooms_available"] >= 0  # May have rooms from fixtures


def test_housekeeping_dashboard_with_tasks(client: TestClient, db: Session, admin_headers, room, guest):
    """Test dashboard with housekeeping tasks"""
    from backend.app.schemas.housekeeping import HousekeepingTaskCreate
    from backend.app.services.housekeeping_service import HousekeepingService
    
    service = HousekeepingService(db)
    
    # Create tasks with different statuses and priorities
    tasks = [
        HousekeepingTaskCreate(
            room_id=room.id,
            task_type="cleaning",
            priority="urgent",
            scheduled_date=date.today(),
            scheduled_time="10:00",
            notes="Test urgent task",
            estimated_duration_minutes=30
        ),
        HousekeepingTaskCreate(
            room_id=room.id,
            task_type="maintenance",
            priority="high",
            scheduled_date=date.today(),
            scheduled_time="14:00",
            notes="Test high priority task",
            estimated_duration_minutes=60
        ),
        HousekeepingTaskCreate(
            room_id=room.id,
            task_type="inspection",
            priority="normal",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time="09:00",
            notes="Test normal task",
            estimated_duration_minutes=15
        ),
    ]
    
    for task_data in tasks:
        service.create_task(task_data, created_by_id=1)
    
    # Get dashboard
    response = client.get("/reports/housekeeping/dashboard", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["pending_tasks"] == 3
    assert data["in_progress_tasks"] == 0
    assert data["urgent_tasks"] == 1
    assert data["high_priority_tasks"] == 1
    assert data["normal_priority_tasks"] == 1
    assert data["tasks_scheduled_today"] == 2


def test_housekeeping_dashboard_with_checkout_cleaning(client: TestClient, db: Session, admin_headers, room, guest):
    """Test dashboard shows checkout cleaning tasks"""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create and complete a booking to trigger checkout cleaning
    booking_response = client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": today,
            "check_out": tomorrow,
            "num_guests": 1
        }
    )
    booking_id = booking_response.json()["id"]
    
    # Confirm, check in, check out
    client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)
    
    # Check dashboard
    response = client.get("/reports/housekeeping/dashboard", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["checkout_cleanings_pending"] == 1
    assert data["rooms_in_maintenance"] >= 1  # Room should be in maintenance


def test_staff_performance_empty(client: TestClient, admin_headers):
    """Test staff performance with no data"""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    response = client.get(
        f"/reports/housekeeping/staff-performance?start_date={today}&end_date={tomorrow}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["staff_metrics"] == []
    assert data["total_tasks_completed"] == 0
    assert data["total_tasks_verified"] == 0


def test_staff_performance_with_completed_tasks(client: TestClient, db: Session, admin_headers, room):
    """Test staff performance metrics calculation"""
    from backend.app.schemas.housekeeping import HousekeepingTaskCreate
    from backend.app.services.housekeeping_service import HousekeepingService
    from backend.app.core.security import create_access_token
    
    # Create a staff user
    staff_response = client.post(
        "/users/",
        headers=admin_headers,
        json={"username": "cleaner_test", "password": "pass123"}
    )
    staff_id = staff_response.json()["id"]
    staff_token = create_access_token(subject="cleaner_test")
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    
    # Create and complete tasks
    service = HousekeepingService(db)
    
    for i in range(3):
        task_data = HousekeepingTaskCreate(
            room_id=room.id,
            task_type="cleaning",
            priority="normal",
            scheduled_date=date.today(),
            scheduled_time="10:00",
            notes=f"Test task {i+1}",
            estimated_duration_minutes=30,
            assigned_to=staff_id
        )
        task = service.create_task(task_data, created_by_id=1)
        
        # Start and complete the task
        client.post(f"/housekeeping/tasks/{task.id}/start", headers=staff_headers)
        client.post(
            f"/housekeeping/tasks/{task.id}/complete",
            headers=staff_headers,
            json={"completion_notes": "Done", "actual_duration_minutes": 25 + i * 5}
        )
    
    # Get performance report
    today = date.today().isoformat()
    response = client.get(
        f"/reports/housekeeping/staff-performance?start_date={today}&end_date={today}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data["staff_metrics"]) == 1
    assert data["staff_metrics"][0]["username"] == "cleaner_test"
    assert data["staff_metrics"][0]["tasks_completed"] == 3
    assert data["total_tasks_completed"] == 3
    assert float(data["average_completion_time_minutes"]) > 0


def test_staff_performance_invalid_date_range(client: TestClient, admin_headers):
    """Test staff performance with invalid date range"""
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    response = client.get(
        f"/reports/housekeeping/staff-performance?start_date={today}&end_date={yesterday}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_room_status_grid_basic(client: TestClient, admin_headers, room):
    """Test room status grid endpoint"""
    response = client.get("/reports/housekeeping/room-status-grid", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "rooms" in data
    assert "summary" in data
    assert "as_of_date" in data
    assert len(data["rooms"]) >= 1  # At least the fixture room
    
    # Check room info structure
    room_info = data["rooms"][0]
    assert "room_id" in room_info
    assert "room_number" in room_info
    assert "room_type" in room_info
    assert "maintenance_status" in room_info
    assert "has_pending_tasks" in room_info
    assert "has_in_progress_tasks" in room_info
    assert "next_booking_checkin" in room_info or room_info["next_booking_checkin"] is None


def test_room_status_grid_with_tasks_and_bookings(client: TestClient, db: Session, admin_headers, room, guest):
    """Test room status grid shows tasks and upcoming bookings"""
    from backend.app.schemas.housekeeping import HousekeepingTaskCreate
    from backend.app.services.housekeeping_service import HousekeepingService
    
    # Create a pending task
    service = HousekeepingService(db)
    task_data = HousekeepingTaskCreate(
        room_id=room.id,
        task_type="cleaning",
        priority="normal",
        scheduled_date=date.today(),
        scheduled_time="10:00",
        notes="Test task",
        estimated_duration_minutes=30
    )
    service.create_task(task_data, created_by_id=1)
    
    # Create a future booking
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    day_after = (date.today() + timedelta(days=2)).isoformat()
    
    client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": tomorrow,
            "check_out": day_after,
            "num_guests": 1
        }
    )
    
    # Get room status grid
    response = client.get("/reports/housekeeping/room-status-grid", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    
    # Find our test room
    test_room = next((r for r in data["rooms"] if r["room_id"] == room.id), None)
    assert test_room is not None
    assert test_room["has_pending_tasks"] is True
    assert test_room["next_booking_checkin"] == tomorrow


def test_room_status_grid_maintenance_status(client: TestClient, db: Session, admin_headers, room, guest):
    """Test room status grid reflects maintenance status"""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Checkout a booking to set room to maintenance
    booking_response = client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": today,
            "check_out": tomorrow,
            "num_guests": 1
        }
    )
    booking_id = booking_response.json()["id"]
    
    client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)
    
    # Get room status grid
    response = client.get("/reports/housekeeping/room-status-grid", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    
    # Find our test room
    test_room = next((r for r in data["rooms"] if r["room_id"] == room.id), None)
    assert test_room is not None
    assert test_room["maintenance_status"] == "maintenance"
    assert data["summary"]["maintenance"] >= 1


def test_housekeeping_dashboard_permissions(client: TestClient, db: Session):
    """Test that regular staff can access dashboard"""
    from backend.app.core.security import create_access_token, get_password_hash
    
    # Create a regular staff user
    staff_user = models.User(
        username="staff_test",
        password_hash=get_password_hash("password123"),
        permission_level=models.PermissionLevel.REGULAR
    )
    db.add(staff_user)
    db.commit()
    
    staff_token = create_access_token(subject="staff_test")
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    
    # Regular staff should access dashboard
    response = client.get("/reports/housekeeping/dashboard", headers=staff_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Regular staff should access room grid
    response = client.get("/reports/housekeeping/room-status-grid", headers=staff_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Regular staff should NOT access staff performance (manager only)
    today = date.today().isoformat()
    response = client.get(
        f"/reports/housekeeping/staff-performance?start_date={today}&end_date={today}",
        headers=staff_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
