"""Tests for cancellation refund policy."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.app.db import models
from backend.app.services.booking_service import BookingService
from backend.app.services.refund_policy import RefundPolicyService


def test_full_refund_on_early_cancellation(db):
    """Test that cancelling 7+ days before check-in gives 100% refund."""
    # Setup policy
    policy = models.CancellationPolicy(
        name="Standard",
        full_refund_days=7,
        partial_refund_days=2,
        partial_refund_percentage=Decimal("50"),
        is_active=True,
    )
    db.add(policy)
    
    # Create guest and room
    guest = models.Guest(name="Test", surname="Guest", email="test@example.com")
    room_type = models.RoomType(name="Test Room", base_price=Decimal("100"), capacity=2)
    
    db.add(guest)
    db.add(room_type)
    db.flush()  # Flush to get room_type.id
    
    room = models.Room(number="101", room_type_id=room_type.id, price_per_night=Decimal("100"))
    db.add(room)
    db.commit()

    # Create booking with check-in 10 days from today
    check_in = date.today() + timedelta(days=10)
    check_out = check_in + timedelta(days=2)
    booking = models.Booking(
        booking_number="TEST-001",
        guest_id=guest.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=Decimal("100"),
        total_price=Decimal("200"),
        status=models.BookingStatus.CONFIRMED.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Create and process a payment
    payment = models.Payment(
        booking_id=booking.id,
        amount=Decimal("200"),
        currency="USD",
        method="card",
        status=models.Payment.PaymentStatus.PAID.value,
        processed_at=datetime.now(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Cancel 8 days before check-in (should be full refund)
    booking.cancelled_at = datetime.now()
    db.commit()

    refund_pct = RefundPolicyService.calculate_refund_percentage(booking, policy)
    assert refund_pct == Decimal("100"), f"Expected 100% refund, got {refund_pct}%"


def test_partial_refund_within_window(db):
    """Test that cancelling 2-7 days before check-in gives 50% refund."""
    policy = models.CancellationPolicy(
        name="Standard",
        full_refund_days=7,
        partial_refund_days=2,
        partial_refund_percentage=Decimal("50"),
        is_active=True,
    )
    db.add(policy)

    guest = models.Guest(name="Test", surname="Guest", email="test2@example.com")
    room_type = models.RoomType(name="Test Room", base_price=Decimal("100"), capacity=2)
    
    db.add(guest)
    db.add(room_type)
    db.flush()  # Flush to get room_type.id
    
    room = models.Room(number="102", room_type_id=room_type.id, price_per_night=Decimal("100"))
    db.add(room)
    db.commit()

    # Create booking with check-in 5 days from today
    check_in = date.today() + timedelta(days=5)
    check_out = check_in + timedelta(days=2)
    booking = models.Booking(
        booking_number="TEST-002",
        guest_id=guest.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=Decimal("100"),
        total_price=Decimal("200"),
        status=models.BookingStatus.CONFIRMED.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Cancel 4 days before check-in (within partial refund window)
    booking.cancelled_at = datetime.now()
    db.commit()

    refund_pct = RefundPolicyService.calculate_refund_percentage(booking, policy)
    assert refund_pct == Decimal("50"), f"Expected 50% refund, got {refund_pct}%"


def test_no_refund_on_late_cancellation(db):
    """Test that cancelling within 2 days gives 0% refund."""
    policy = models.CancellationPolicy(
        name="Standard",
        full_refund_days=7,
        partial_refund_days=2,
        partial_refund_percentage=Decimal("50"),
        is_active=True,
    )
    db.add(policy)

    guest = models.Guest(name="Test", surname="Guest", email="test3@example.com")
    room_type = models.RoomType(name="Test Room", base_price=Decimal("100"), capacity=2)
    
    db.add(guest)
    db.add(room_type)
    db.flush()  # Flush to get room_type.id
    
    room = models.Room(number="103", room_type_id=room_type.id, price_per_night=Decimal("100"))
    db.add(room)
    db.commit()

    # Create booking with check-in 1 day from today
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    booking = models.Booking(
        booking_number="TEST-003",
        guest_id=guest.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=Decimal("100"),
        total_price=Decimal("200"),
        status=models.BookingStatus.CONFIRMED.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Cancel today (1 day before check-in, within no-refund window)
    booking.cancelled_at = datetime.now()
    db.commit()

    refund_pct = RefundPolicyService.calculate_refund_percentage(booking, policy)
    assert refund_pct == Decimal("0"), f"Expected 0% refund, got {refund_pct}%"


def test_auto_refund_on_cancellation(db):
    """Test that cancelling a booking auto-refunds paid amounts."""
    policy = models.CancellationPolicy(
        name="Standard",
        full_refund_days=7,
        partial_refund_days=2,
        partial_refund_percentage=Decimal("50"),
        is_active=True,
    )
    db.add(policy)

    guest = models.Guest(name="Test", surname="Guest", email="test4@example.com")
    room_type = models.RoomType(name="Test Room", base_price=Decimal("100"), capacity=2)
    
    db.add(guest)
    db.add(room_type)
    db.flush()  # Flush to get room_type.id
    
    room = models.Room(number="104", room_type_id=room_type.id, price_per_night=Decimal("100"))
    db.add(room)
    db.commit()

    # Create booking with check-in 10 days from today (eligible for full refund)
    check_in = date.today() + timedelta(days=10)
    check_out = check_in + timedelta(days=2)
    booking = models.Booking(
        booking_number="TEST-004",
        guest_id=guest.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=Decimal("100"),
        total_price=Decimal("200"),
        status=models.BookingStatus.CONFIRMED.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Create and process a payment
    payment = models.Payment(
        booking_id=booking.id,
        amount=Decimal("200"),
        currency="USD",
        method="card",
        status=models.Payment.PaymentStatus.PAID.value,
        processed_at=datetime.now(),
    )
    db.add(payment)
    db.commit()

    # Cancel the booking (should auto-refund 100% of payment)
    BookingService.cancel_booking(db, booking.id)

    # Verify booking is cancelled
    booking = db.query(models.Booking).filter(models.Booking.id == booking.id).first()
    booking_status = booking.status.value if hasattr(booking.status, 'value') else booking.status
    assert booking_status == models.BookingStatus.CANCELLED.value

    # Verify refund was created
    refund = db.query(models.Payment).filter(
        models.Payment.booking_id == booking.id,
        models.Payment.status == models.Payment.PaymentStatus.REFUNDED.value,
    ).first()
    assert refund is not None, "Refund payment not created"
    assert refund.amount == Decimal("200"), f"Expected refund of 200, got {refund.amount}"
