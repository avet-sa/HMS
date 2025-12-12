"""
Tests for Housekeeping Automation Features
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta
from fastapi import status

from backend.app.db.models import RoomMaintenanceStatus, BookingStatus


def test_checkout_auto_creates_housekeeping_task(client: TestClient, db: Session, admin_headers, room, guest):
    """Test that checking out automatically creates a housekeeping task"""
    # Create a booking
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    today = date.today().isoformat()
    
    booking_response = client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": today,
            "check_out": tomorrow,
            "num_guests": 1,
            "special_requests": "Test booking"
        }
    )
    assert booking_response.status_code == status.HTTP_201_CREATED
    booking_id = booking_response.json()["id"]

    # Confirm, then check in the guest
    client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    checkin_response = client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    assert checkin_response.status_code == status.HTTP_200_OK    # Check out the guest
    checkout_response = client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)
    assert checkout_response.status_code == status.HTTP_200_OK
    
    # Verify housekeeping task was created
    tasks_response = client.get("/housekeeping/tasks/", headers=admin_headers)
    assert tasks_response.status_code == status.HTTP_200_OK
    tasks = tasks_response.json()
    
    # Should have at least one task
    assert len(tasks) > 0
    
    # Find the checkout cleaning task
    checkout_task = next((t for t in tasks if t["is_checkout_cleaning"]), None)
    assert checkout_task is not None
    assert checkout_task["room_id"] == room.id
    assert checkout_task["task_type"] == "cleaning"
    assert checkout_task["booking_id"] == booking_id


def test_checkout_sets_room_to_maintenance(client: TestClient, db: Session, admin_headers, room, guest):
    """Test that checking out sets room to maintenance status"""
    from backend.app.db.models import Room
    
    # Verify room starts as available
    db_room = db.query(Room).filter(Room.id == room.id).first()
    assert db_room.maintenance_status == RoomMaintenanceStatus.AVAILABLE
    
    # Create and check in booking
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    today = date.today().isoformat()
    
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
    client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)    # Check out
    client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)
    
    # Verify room is now in maintenance
    db.refresh(db_room)
    assert db_room.maintenance_status == RoomMaintenanceStatus.MAINTENANCE


def test_urgent_priority_for_same_day_checkin(client: TestClient, db: Session, admin_headers, room, guest):
    """Test that tasks get urgent priority if next check-in is today"""
    from backend.app.db.models import Booking
    
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create first booking (check out today)
    booking1_response = client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": today,
            "check_out": today,
            "num_guests": 1
        }
    )
    booking1_id = booking1_response.json()["id"]
    
    # Create second booking (check in today)
    booking2_response = client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": today,
            "check_out": tomorrow,
            "num_guests": 1,
            "status": "confirmed"
        }
    )
    
    # Check in and check out first booking
    client.post(f"/bookings/{booking1_id}/confirm", headers=admin_headers)
    client.post(f"/bookings/{booking1_id}/check-in", headers=admin_headers)
    client.post(f"/bookings/{booking1_id}/check-out", headers=admin_headers)
    
    # Verify housekeeping task has urgent priority
    tasks_response = client.get("/housekeeping/tasks/", headers=admin_headers)
    tasks = tasks_response.json()
    
    checkout_task = next((t for t in tasks if t["is_checkout_cleaning"]), None)
    assert checkout_task is not None
    assert checkout_task["priority"] == "urgent"


def test_verify_task_sets_room_available(client: TestClient, db: Session, admin_headers, room, guest):
    """Test that verifying a checkout cleaning task sets room back to available"""
    from backend.app.db.models import Room
    
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create, check in, and check out booking
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
    
    # Room should be in maintenance
    db_room = db.query(Room).filter(Room.id == room.id).first()
    db.refresh(db_room)
    assert db_room.maintenance_status == RoomMaintenanceStatus.MAINTENANCE
    
    # Get the housekeeping task
    tasks_response = client.get("/housekeeping/tasks/", headers=admin_headers)
    tasks = tasks_response.json()
    checkout_task = next((t for t in tasks if t["is_checkout_cleaning"]), None)
    task_id = checkout_task["id"]
    
    # Start and complete the task (need to assign first)
    # Note: We'll create a staff user for this
    staff_response = client.post(
        "/users/",
        headers=admin_headers,
        json={"username": "cleaner1", "password": "pass123"}
    )
    staff_id = staff_response.json()["id"]
    
    # Assign task
    client.post(
        f"/housekeeping/tasks/{task_id}/assign",
        headers=admin_headers,
        json={"assigned_to": staff_id}
    )
    
    # Create staff headers
    from backend.app.core.security import create_access_token
    staff_token = create_access_token(subject="cleaner1")
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    
    # Start task
    client.post(f"/housekeeping/tasks/{task_id}/start", headers=staff_headers)
    
    # Complete task
    client.post(
        f"/housekeeping/tasks/{task_id}/complete",
        headers=staff_headers,
        json={"completion_notes": "Room cleaned"}
    )
    
    # Verify task
    verify_response = client.post(
        f"/housekeeping/tasks/{task_id}/verify",
        headers=admin_headers,
        json={"verification_notes": "Quality check passed"}
    )
    assert verify_response.status_code == status.HTTP_200_OK
    
    # Room should now be available
    db.refresh(db_room)
    assert db_room.maintenance_status == RoomMaintenanceStatus.AVAILABLE


def test_high_priority_for_next_day_checkin(client: TestClient, db: Session, admin_headers, room, guest):
    """Test that tasks get high priority if next check-in is tomorrow"""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    day_after = (date.today() + timedelta(days=2)).isoformat()
    
    # Create first booking (check out today)
    booking1_response = client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": today,
            "check_out": today,
            "num_guests": 1
        }
    )
    booking1_id = booking1_response.json()["id"]
    
    # Create second booking (check in tomorrow)
    client.post(
        "/bookings/",
        headers=admin_headers,
        json={
            "guest_id": guest.id,
            "room_id": room.id,
            "check_in": tomorrow,
            "check_out": day_after,
            "num_guests": 1,
            "status": "confirmed"
        }
    )
    
    # Check in and check out first booking
    client.post(f"/bookings/{booking1_id}/confirm", headers=admin_headers)
    client.post(f"/bookings/{booking1_id}/check-in", headers=admin_headers)
    client.post(f"/bookings/{booking1_id}/check-out", headers=admin_headers)
    
    # Verify housekeeping task has high priority
    tasks_response = client.get("/housekeeping/tasks/", headers=admin_headers)
    tasks = tasks_response.json()
    
    checkout_task = next((t for t in tasks if t["is_checkout_cleaning"]), None)
    assert checkout_task is not None
    assert checkout_task["priority"] == "high"
