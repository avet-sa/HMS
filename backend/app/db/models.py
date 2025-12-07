from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Numeric, Enum as SQLEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from enum import Enum
from datetime import date

Base = declarative_base()

# Enums for better type safety
class PermissionLevel(Enum):
    REGULAR = "REGULAR"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class RoomMaintenanceStatus(Enum):
    AVAILABLE = "available"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"

class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    ONLINE = "online"


# -----------------------------
# User
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    permission_level = Column(SQLEnum(PermissionLevel, name="permission_level", values_callable=lambda x: [e.value for e in x]), default=PermissionLevel.REGULAR.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# -----------------------------
# Guest
# -----------------------------
class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    phone_number = Column(String(30), index=True)
    email = Column(String(100), unique=True, index=True)
    nationality = Column(String(50))
    gender = Column(String(10))
    birth_date = Column(Date)
    
    document_type = Column(String(20))  # passport, ID card, driver's license
    document_id = Column(String(50))
    
    # Loyalty/VIP
    loyalty_points = Column(Integer, default=0)
    vip_tier = Column(Integer, default=0)  # 0: regular, 1-3: VIP levels
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="guest")
    
    @property
    def age(self):
        """Calculate age from birth_date"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


# -----------------------------
# Room Type
# -----------------------------
class RoomType(Base):
    __tablename__ = "room_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Single, Double, Suite, etc.
    base_price = Column(Numeric(10, 2), nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    rooms = relationship("Room", back_populates="room_type")


# -----------------------------
# Room
# -----------------------------
class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(10), unique=True, nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False)

    price_per_night = Column(Numeric(10, 2), nullable=False)
    square_meters = Column(Integer)
    floor = Column(Integer)
    
    # Maintenance status (separate from booking availability)
    maintenance_status = Column(
        SQLEnum(RoomMaintenanceStatus, name="room_maintenance_status", values_callable=lambda x: [e.value for e in x]), 
        default=RoomMaintenanceStatus.AVAILABLE.value,  # Use .value here!
        nullable=False
    )
    
    # Additional features
    has_view = Column(Boolean, default=False)
    is_smoking = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    room_type = relationship("RoomType", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")


# -----------------------------
# Booking
# -----------------------------
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_number = Column(String(20), unique=True, nullable=False, index=True)  # e.g., BK-2024-00001
    
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # User who created booking
    
    check_in = Column(Date, nullable=False, index=True)
    check_out = Column(Date, nullable=False, index=True)
    
    number_of_guests = Column(Integer, nullable=False, default=1)

    @hybrid_property
    def number_of_nights(self):
        return (self.check_out - self.check_in).days
    
    # Pricing
    price_per_night = Column(Numeric(10, 2), nullable=False)  # Lock in price at booking time
    total_price = Column(Numeric(10, 2), nullable=False)
    
    status = Column(SQLEnum(BookingStatus, name="booking_status", values_callable=lambda x: [e.value for e in x]), default=BookingStatus.PENDING.value, nullable=False, index=True)
    
    # Actual check-in/check-out timestamps
    actual_check_in = Column(DateTime(timezone=True), nullable=True)
    actual_check_out = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    final_bill = Column(Numeric(10, 2), nullable=True)
    
    # Special requests/notes
    special_requests = Column(String(500), nullable=True)
    internal_notes = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    guest = relationship("Guest", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
    created_by_user = relationship("User", foreign_keys=[created_by])


# -----------------------------
# Payment
# -----------------------------
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, server_default="USD")
    method = Column(String(50), nullable=False)

    class PaymentStatus(Enum):
        PENDING = "PENDING"
        PAID = "PAID"
        FAILED = "FAILED"
        REFUNDED = "REFUNDED"

    status = Column(SQLEnum(PaymentStatus, name="payment_status", values_callable=lambda x: [e.value for e in x]), default=PaymentStatus.PENDING.value, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)

    reference = Column(String(100), nullable=True)

    booking = relationship("Booking", back_populates="payments")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)

    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    booking = relationship("Booking")