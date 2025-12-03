import os
from dotenv import load_dotenv
import sys
# Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import RoomMaintenanceStatus, RoomType, Room, User
from app.db.models import PermissionLevel

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed_database():
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(RoomType).first():
            print("Database already seeded!")
            return
        
        # Add room types
        room_types = [
            RoomType(name="Single", base_price=100.00, capacity=1, 
                    description="Comfortable single room with one bed"),
            RoomType(name="Double", base_price=150.00, capacity=2, 
                    description="Spacious double room with queen bed"),
            RoomType(name="Suite", base_price=300.00, capacity=4, 
                    description="Luxurious suite with separate living area"),
            RoomType(name="Deluxe", base_price=200.00, capacity=2, 
                    description="Premium room with city view"),
        ]
        db.add_all(room_types)
        db.commit()
        
        # Get room type IDs
        single = db.query(RoomType).filter_by(name="Single").first()
        double = db.query(RoomType).filter_by(name="Double").first()
        suite = db.query(RoomType).filter_by(name="Suite").first()
        deluxe = db.query(RoomType).filter_by(name="Deluxe").first()
        
        # Add rooms - EXPLICITLY set maintenance_status
        rooms = [
            Room(
                number="101", 
                room_type_id=single.id, 
                price_per_night=100.00, 
                square_meters=20, 
                floor=1, 
                has_view=False,
                maintenance_status=RoomMaintenanceStatus.AVAILABLE  # Use enum
            ),
            Room(
                number="102", 
                room_type_id=single.id, 
                price_per_night=100.00, 
                square_meters=20, 
                floor=1, 
                has_view=False,
                maintenance_status=RoomMaintenanceStatus.AVAILABLE
            ),
            Room(
                number="201", 
                room_type_id=double.id, 
                price_per_night=150.00, 
                square_meters=30, 
                floor=2, 
                has_view=True,
                maintenance_status=RoomMaintenanceStatus.AVAILABLE
            ),
            Room(
                number="202", 
                room_type_id=double.id, 
                price_per_night=150.00, 
                square_meters=30, 
                floor=2, 
                has_view=True,
                maintenance_status=RoomMaintenanceStatus.AVAILABLE
            ),
            Room(
                number="301", 
                room_type_id=suite.id, 
                price_per_night=300.00, 
                square_meters=60, 
                floor=3, 
                has_view=True,
                maintenance_status=RoomMaintenanceStatus.AVAILABLE
            ),
            Room(
                number="401", 
                room_type_id=deluxe.id, 
                price_per_night=200.00, 
                square_meters=35, 
                floor=4, 
                has_view=True,
                maintenance_status=RoomMaintenanceStatus.AVAILABLE
            ),
        ]
        db.add_all(rooms)
        
        # Add sample users
        users = [
            User(
                username="admin", 
                password_hash="hashed_password_here", 
                permission_level=PermissionLevel.ADMIN
            ),
            User(
                username="manager", 
                password_hash="hashed_password_here", 
                permission_level=PermissionLevel.MANAGER
            ),
            User(
                username="receptionist", 
                password_hash="hashed_password_here", 
                permission_level=PermissionLevel.REGULAR
            ),
        ]
        db.add_all(users)
        
        db.commit()
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()