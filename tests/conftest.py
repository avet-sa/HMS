import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import sys
sys.path.append(".")

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.db import models
from backend.app.core.security import create_access_token

# Use an in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create the database tables
    models.Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the tables after the test
        models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db):
    """Create an admin user for testing."""
    from backend.app.services.user_service import UserService
    from backend.app.schemas.user import UserCreate
    
    user_data = UserCreate(username="admin", password="adminpass123")
    user = UserService.create_user(db, user_data)
    user.permission_level = models.PermissionLevel.ADMIN
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def manager_user(db):
    """Create a manager user for testing."""
    from backend.app.services.user_service import UserService
    from backend.app.schemas.user import UserCreate
    
    user_data = UserCreate(username="manager", password="managerpass123")
    user = UserService.create_user(db, user_data)
    user.permission_level = models.PermissionLevel.MANAGER
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def regular_user(db):
    """Create a regular user for testing."""
    from backend.app.services.user_service import UserService
    from backend.app.schemas.user import UserCreate
    
    user_data = UserCreate(username="regular", password="regularpass123")
    user = UserService.create_user(db, user_data)
    user.permission_level = models.PermissionLevel.REGULAR
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_headers(admin_user):
    """Get auth headers for admin user."""
    token = create_access_token(subject=admin_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def manager_headers(manager_user):
    """Get auth headers for manager user."""
    token = create_access_token(subject=manager_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def regular_headers(regular_user):
    """Get auth headers for regular user."""
    token = create_access_token(subject=regular_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def room_type(db):
    """Create a test room type"""
    from decimal import Decimal
    room_type = models.RoomType(
        name="Deluxe Suite",
        base_price=Decimal("100.00"),
        capacity=2,
        description="Luxury room"
    )
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


@pytest.fixture(scope="function")
def room(db, room_type):
    """Create a test room"""
    from decimal import Decimal
    room = models.Room(
        number="101",
        room_type_id=room_type.id,
        floor=1,
        price_per_night=Decimal("100.00"),
        maintenance_status="available"
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
