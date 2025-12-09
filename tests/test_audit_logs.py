"""
Tests for audit logging system
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.db.models import User, PermissionLevel, AuditLog, Booking, Guest, Room, RoomType, Payment
from backend.app.utils.audit import log_audit, log_booking_action, log_payment_action
from backend.app.core.security import get_password_hash


@pytest.fixture
def admin_user(db: Session):
    """Create an admin user for testing"""
    user = User(
        username="admin_test",
        password_hash=get_password_hash("admin123"),
        permission_level=PermissionLevel.ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db: Session):
    """Create a regular user for testing"""
    user = User(
        username="regular_test",
        password_hash=get_password_hash("user123"),
        permission_level=PermissionLevel.REGULAR,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def manager_user(db: Session):
    """Create a manager user for testing"""
    user = User(
        username="manager_test",
        password_hash=get_password_hash("manager123"),
        permission_level=PermissionLevel.MANAGER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_guest(db: Session):
    """Create a sample guest"""
    guest = Guest(
        name="John",
        surname="Doe",
        email="john.doe@example.com",
        phone_number="+1234567890"
    )
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest


@pytest.fixture
def sample_room(db: Session):
    """Create a sample room"""
    room_type = RoomType(
        name="Standard",
        description="Standard room",
        base_price=100.0,
        capacity=2
    )
    db.add(room_type)
    db.commit()
    
    room = Room(
        number="101",
        room_type_id=room_type.id,
        price_per_night=100.0
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


class TestAuditLogUtility:
    """Test the audit logging utility functions"""
    
    def test_log_audit_basic(self, db: Session, admin_user: User):
        """Test basic audit log creation"""
        log = log_audit(
            db=db,
            user=admin_user,
            action="CREATE",
            entity_type="test_entity",
            entity_id=123,
            description="Test log entry"
        )
        
        assert log.id is not None
        assert log.user_id == admin_user.id
        assert log.username == admin_user.username
        assert log.action == "CREATE"
        assert log.entity_type == "test_entity"
        assert log.entity_id == 123
        assert log.description == "Test log entry"
        assert log.created_at is not None
    
    def test_log_audit_with_values(self, db: Session, admin_user: User):
        """Test audit log with old and new values"""
        old_values = {"status": "pending", "amount": 100}
        new_values = {"status": "paid", "amount": 100}
        
        log = log_audit(
            db=db,
            user=admin_user,
            action="UPDATE",
            entity_type="payment",
            entity_id=456,
            description="Payment processed",
            old_values=old_values,
            new_values=new_values
        )
        
        assert log.old_values is not None
        assert log.new_values is not None
        assert "pending" in log.old_values
        assert "paid" in log.new_values
    
    def test_log_audit_without_user(self, db: Session):
        """Test audit log for system actions (no user)"""
        log = log_audit(
            db=db,
            user=None,
            action="SYSTEM_TASK",
            entity_type="booking",
            entity_id=789,
            description="Automated cleanup"
        )
        
        assert log.user_id is None
        assert log.username == "SYSTEM"
        assert log.action == "SYSTEM_TASK"
    
    def test_log_audit_truncates_long_values(self, db: Session, admin_user: User):
        """Test that long values are truncated to prevent errors"""
        # Create a very long string (>2000 chars)
        long_value = {"data": "x" * 3000}
        
        log = log_audit(
            db=db,
            user=admin_user,
            action="CREATE",
            entity_type="test",
            old_values=long_value
        )
        
        assert log.old_values is not None
        assert len(log.old_values) <= 2000
        assert log.old_values.endswith("...")
    
    def test_log_booking_action(self, db: Session, admin_user: User):
        """Test booking-specific audit logging"""
        log = log_booking_action(
            db=db,
            user=admin_user,
            action="CHECK_IN",
            booking_id=123,
            description="Guest checked in"
        )
        
        assert log.entity_type == "booking"
        assert log.entity_id == 123
        assert log.action == "CHECK_IN"
    
    def test_log_payment_action(self, db: Session, admin_user: User):
        """Test payment-specific audit logging"""
        log = log_payment_action(
            db=db,
            user=admin_user,
            action="PROCESS",
            payment_id=456,
            description="Payment processed"
        )
        
        assert log.entity_type == "payment"
        assert log.entity_id == 456
        assert log.action == "PROCESS"


class TestAuditLogAPI:
    """Test the audit log API endpoints"""
    
    def test_list_audit_logs_as_admin(self, client, db: Session, admin_user: User):
        """Test listing audit logs as admin"""
        # Create some audit logs
        for i in range(5):
            log_audit(
                db=db,
                user=admin_user,
                action="CREATE",
                entity_type="booking",
                entity_id=i,
                description=f"Test log {i}"
            )
        
        # Get admin token (this will create a LOGIN_SUCCESS audit log)
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # List audit logs
        response = client.get(
            "/audit-logs/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Should have 5 CREATE logs + 1 LOGIN_SUCCESS log
        assert len(data["items"]) == 6
        assert data["total"] == 6
        assert data["page"] == 1
        
        # Verify login log exists
        login_logs = [item for item in data["items"] if item["action"] == "LOGIN_SUCCESS"]
        assert len(login_logs) == 1
    
    def test_list_audit_logs_as_manager(self, client, db: Session, manager_user: User):
        """Test listing audit logs as manager"""
        # Create audit log
        log_audit(
            db=db,
            user=manager_user,
            action="UPDATE",
            entity_type="room",
            entity_id=1,
            description="Room updated"
        )
        
        # Get manager token
        response = client.post(
            "/auth/token",
            data={"username": "manager_test", "password": "manager123"}
        )
        token = response.json()["access_token"]
        
        # List audit logs
        response = client.get(
            "/audit-logs/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_list_audit_logs_as_regular_user_forbidden(self, client, db: Session, regular_user: User):
        """Test that regular users cannot access audit logs"""
        # Get regular user token
        response = client.post(
            "/auth/token",
            data={"username": "regular_test", "password": "user123"}
        )
        token = response.json()["access_token"]
        
        # Try to list audit logs
        response = client.get(
            "/audit-logs/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "access required" in response.json()["detail"].lower()
    
    def test_list_audit_logs_filter_by_action(self, client, db: Session, admin_user: User):
        """Test filtering audit logs by action"""
        # Create logs with different actions
        log_audit(db, admin_user, "CREATE", "booking", 1, "Created booking")
        log_audit(db, admin_user, "UPDATE", "booking", 1, "Updated booking")
        log_audit(db, admin_user, "DELETE", "booking", 1, "Deleted booking")
        
        # Get admin token
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Filter by CREATE action
        response = client.get(
            "/audit-logs/?action=CREATE",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["action"] == "CREATE"
    
    def test_list_audit_logs_filter_by_entity_type(self, client, db: Session, admin_user: User):
        """Test filtering audit logs by entity type"""
        # Create logs with different entity types
        log_audit(db, admin_user, "CREATE", "booking", 1, "Created booking")
        log_audit(db, admin_user, "CREATE", "payment", 1, "Created payment")
        log_audit(db, admin_user, "CREATE", "guest", 1, "Created guest")
        
        # Get admin token
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Filter by payment entity type
        response = client.get(
            "/audit-logs/?entity_type=payment",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["entity_type"] == "payment"
    
    def test_list_audit_logs_filter_by_user(self, client, db: Session, admin_user: User, manager_user: User):
        """Test filtering audit logs by user"""
        # Create logs from different users
        log_audit(db, admin_user, "CREATE", "booking", 1, "Admin action")
        log_audit(db, manager_user, "CREATE", "booking", 2, "Manager action")
        
        # Get admin token
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Filter by manager user
        response = client.get(
            f"/audit-logs/?user_id={manager_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["username"] == "manager_test"
    
    def test_list_audit_logs_filter_by_date_range(self, client, db: Session, admin_user: User):
        """Test filtering audit logs by date range"""
        # Create a log
        log_audit(db, admin_user, "CREATE", "booking", 1, "Test log")
        
        # Get admin token (this creates a LOGIN_SUCCESS log)
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Filter by date range
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        response = client.get(
            f"/audit-logs/?date_from={today.isoformat()}&date_to={tomorrow.isoformat()}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should have CREATE log + LOGIN_SUCCESS log
        assert len(data["items"]) == 2
    
    def test_list_audit_logs_pagination(self, client, db: Session, admin_user: User):
        """Test audit logs pagination"""
        # Create 60 logs
        for i in range(60):
            log_audit(db, admin_user, "CREATE", "booking", i, f"Log {i}")
        
        # Get admin token (this creates a LOGIN_SUCCESS log, total = 61)
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Get first page
        response = client.get(
            "/audit-logs/?page=1&page_size=50",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 50
        assert data["total"] == 61  # 60 CREATE logs + 1 LOGIN_SUCCESS
        assert data["total_pages"] == 2
        
        # Get second page
        response = client.get(
            "/audit-logs/?page=2&page_size=50",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 11  # Remaining 11 logs
    
    def test_get_audit_log_by_id(self, client, db: Session, admin_user: User):
        """Test getting a specific audit log by ID"""
        # Create a log
        log = log_audit(db, admin_user, "CREATE", "booking", 123, "Test log")
        
        # Get admin token
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Get the log
        response = client.get(
            f"/audit-logs/{log.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == log.id
        assert data["action"] == "CREATE"
        assert data["entity_id"] == 123
    
    def test_get_nonexistent_audit_log(self, client, db: Session, admin_user: User):
        """Test getting a nonexistent audit log"""
        # Get admin token
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Try to get nonexistent log
        response = client.get(
            "/audit-logs/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_list_audit_logs_sorting(self, client, db: Session, admin_user: User):
        """Test audit logs sorting"""
        # Create logs
        log_audit(db, admin_user, "CREATE", "booking", 1, "First")
        log_audit(db, admin_user, "UPDATE", "booking", 2, "Second")
        log_audit(db, admin_user, "DELETE", "booking", 3, "Third")
        
        # Get admin token (creates LOGIN_SUCCESS log)
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        token = response.json()["access_token"]
        
        # Sort by created_at ascending
        response = client.get(
            "/audit-logs/?sort_by=created_at&sort_order=asc",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["description"] == "First"
        assert data["items"][1]["description"] == "Second"
        assert data["items"][2]["description"] == "Third"
        
        # Sort by created_at descending (default)
        response = client.get(
            "/audit-logs/?sort_by=created_at&sort_order=desc",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # First item should be the LOGIN_SUCCESS (most recent)
        assert data["items"][0]["action"] == "LOGIN_SUCCESS"
        # Then the audit logs in reverse order
        assert data["items"][1]["description"] == "Third"
        assert data["items"][3]["description"] == "First"


class TestAuditLogIntegration:
    """Test audit logging integration with other features"""
    
    def test_audit_log_created_on_login(self, client, db: Session, admin_user: User):
        """Test that login creates an audit log"""
        # Perform login
        response = client.post(
            "/auth/token",
            data={"username": "admin_test", "password": "admin123"}
        )
        
        assert response.status_code == 200
        
        # Check that LOGIN_SUCCESS audit log was created
        audit_logs = db.query(AuditLog).filter(
            AuditLog.action == "LOGIN_SUCCESS",
            AuditLog.user_id == admin_user.id
        ).all()
        
        assert len(audit_logs) == 1
        assert audit_logs[0].entity_type == "user"
        assert audit_logs[0].entity_id == admin_user.id
        assert "logged in successfully" in audit_logs[0].description.lower()
    
    def test_audit_utility_functions_work(self, db: Session, admin_user: User):
        """Test that audit utility functions create proper logs"""
        # Test booking action logging
        log = log_booking_action(
            db=db,
            user=admin_user,
            action="CREATE",
            booking_id=999,
            description="Test booking log",
            new_values={"status": "pending"}
        )
        
        assert log.entity_type == "booking"
        assert log.entity_id == 999
        assert log.action == "CREATE"
        
        # Test payment action logging
        log2 = log_payment_action(
            db=db,
            user=admin_user,
            action="PROCESS",
            payment_id=888,
            description="Test payment log",
            old_values={"status": "pending"},
            new_values={"status": "paid"}
        )
        
        assert log2.entity_type == "payment"
        assert log2.entity_id == 888
        assert log2.action == "PROCESS"
        assert log2.old_values is not None
        assert log2.new_values is not None
