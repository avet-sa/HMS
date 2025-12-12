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

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"

class TaskType(Enum):
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    INSPECTION = "inspection"
    DEEP_CLEANING = "deep_cleaning"
    TURNDOWN = "turndown"

class TaskPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


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
# Pricing Rule
# -----------------------------
class PricingRuleType(Enum):
    SEASONAL = "seasonal"  # e.g., summer, winter rates
    WEEKEND = "weekend"  # Friday-Saturday premium
    EARLY_BIRD = "early_bird"  # Discount for advance booking
    LAST_MINUTE = "last_minute"  # Discount for booking close to check-in
    LOYALTY = "loyalty"  # Discount based on loyalty tier
    LONG_STAY = "long_stay"  # Discount for extended stays
    CUSTOM = "custom"  # Custom rules


class PricingRule(Base):
    """Dynamic pricing rules to adjust room rates based on various factors"""
    __tablename__ = "pricing_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    # Rule type (stored as string for simplicity)
    rule_type = Column(String(20), nullable=False, index=True)  # seasonal, weekend, early_bird, etc.
    
    # Priority (higher priority rules are applied first)
    priority = Column(Integer, default=0, nullable=False, index=True)
    
    # Price adjustment
    adjustment_type = Column(String(20), nullable=False)  # "percentage", "fixed_amount"
    adjustment_value = Column(Numeric(10, 2), nullable=False)  # e.g., 20 for 20% or $20
    
    # Applicability filters (NULL means applies to all)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=True, index=True)
    
    # Date range (NULL means no date restriction)
    start_date = Column(Date, nullable=True, index=True)
    end_date = Column(Date, nullable=True, index=True)
    
    # Days of week (JSON array of day numbers: 0=Monday, 6=Sunday)
    # e.g., "[5, 6]" for weekends
    applicable_days = Column(String(50), nullable=True)  # JSON string
    
    # Booking conditions
    min_nights = Column(Integer, nullable=True)  # Minimum stay required
    min_advance_days = Column(Integer, nullable=True)  # Minimum days before check-in
    max_advance_days = Column(Integer, nullable=True)  # Maximum days before check-in
    
    # Loyalty tier (NULL means applies to all tiers)
    min_loyalty_tier = Column(Integer, nullable=True)
    
    # Active status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    room_type = relationship("RoomType")
    
    def __repr__(self):
        return f"<PricingRule {self.name} ({self.rule_type.value})>"


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
    housekeeping_tasks = relationship("HousekeepingTask", back_populates="room", cascade="all, delete-orphan")


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


# -----------------------------
# Cancellation Policy
# -----------------------------
class CancellationPolicy(Base):
    """Define refund percentages based on days before check-in."""
    __tablename__ = "cancellation_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Standard", "Flexible", "Non-Refundable"
    
    # Refund tiers: days_before_checkin -> refund_percentage
    # Example: full_refund_days=7 means 100% refund if cancelled 7+ days before check-in
    full_refund_days = Column(Integer, default=7, nullable=False)  # Days before check-in for 100% refund
    partial_refund_days = Column(Integer, default=2, nullable=False)  # Days before check-in for 50% refund
    partial_refund_percentage = Column(Numeric(5, 2), default=50, nullable=False)  # Refund % if within partial_refund_days
    # If cancelled within partial_refund_days, no refund
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CancellationPolicy {self.name}>"

# -----------------------------
# Housekeeping Task
# -----------------------------
class HousekeepingTask(Base):
    """Track cleaning, maintenance, and inspection tasks for rooms"""
    __tablename__ = "housekeeping_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Task details
    task_type = Column(String(20), nullable=False, index=True)  # cleaning, maintenance, etc.
    priority = Column(String(10), nullable=False, server_default="normal", index=True)
    status = Column(String(20), nullable=False, server_default="pending", index=True)
    
    # Scheduling
    scheduled_date = Column(Date, nullable=False, index=True)
    scheduled_time = Column(String(10), nullable=True)  # HH:MM format
    
    # Timing tracking
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes and details
    notes = Column(String(500), nullable=True)  # Initial instructions/notes
    completion_notes = Column(String(500), nullable=True)  # Notes added on completion
    verification_notes = Column(String(500), nullable=True)  # Notes added on verification
    
    # Duration tracking
    estimated_duration_minutes = Column(Integer, default=30)
    actual_duration_minutes = Column(Integer, nullable=True)
    
    # Special flags
    is_checkout_cleaning = Column(Boolean, default=False, index=True)  # Auto-created on checkout
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    room = relationship("Room", back_populates="housekeeping_tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    verifier = relationship("User", foreign_keys=[verified_by])
    booking = relationship("Booking")
    
    def __repr__(self):
        return f"<HousekeepingTask {self.task_type} for Room {self.room_id} - {self.status}>"

# -----------------------------
# Audit Log
# -----------------------------
class AuditLog(Base):
    """Track all critical operations for compliance and debugging"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(50), nullable=True)  # Denormalized for deleted users
    
    # What action was performed
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    entity_type = Column(String(50), nullable=False, index=True)  # booking, payment, room, user, etc.
    entity_id = Column(Integer, nullable=True, index=True)  # ID of the affected entity
    
    # Details about the change
    description = Column(String(500))  # Human-readable description
    old_values = Column(String(2000))  # JSON string of old values
    new_values = Column(String(2000))  # JSON string of new values
    
    # Request metadata
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type}#{self.entity_id} by {self.username}>"
