"""Tests for no-show penalties."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.app.db import models
from backend.app.services.booking_service import BookingService


def test_no_show_charges_full_bill(db):
    """Test that marking a booking as no-show charges the full final bill."""
    # Create guest and room
    guest = models.Guest(name="Test", surname="NoShow", email="noshow@example.com")
    room_type = models.RoomType(name="Test Room", base_price=Decimal("100"), capacity=2)
    
    db.add(guest)
    db.add(room_type)
    db.flush()
    
    room = models.Room(number="201", room_type_id=room_type.id, price_per_night=Decimal("100"))
    db.add(room)
    db.commit()

    # Create confirmed booking
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    booking = models.Booking(
        booking_number="NO-SHOW-001",
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

    # Mark as no-show (should auto-charge full bill)
    BookingService.mark_no_show(db, booking.id)

    # Verify booking is no-show
    booking = db.query(models.Booking).filter(models.Booking.id == booking.id).first()
    booking_status = booking.status.value if hasattr(booking.status, 'value') else booking.status
    assert booking_status == models.BookingStatus.NO_SHOW.value

    # Verify no-show charge was created
    no_show_payment = db.query(models.Payment).filter(
        models.Payment.booking_id == booking.id,
        models.Payment.status == models.Payment.PaymentStatus.PAID.value,
    ).first()
    assert no_show_payment is not None, "No-show charge not created"
    assert no_show_payment.amount == booking.total_price, f"Expected charge of {booking.total_price}, got {no_show_payment.amount}"
    assert "No-show charge" in no_show_payment.reference


def test_no_show_with_final_bill_set(db):
    """Test no-show charges the final_bill if it's already set."""
    # Create guest and room
    guest = models.Guest(name="Test", surname="NoShow2", email="noshow2@example.com")
    room_type = models.RoomType(name="Test Room", base_price=Decimal("100"), capacity=2)
    
    db.add(guest)
    db.add(room_type)
    db.flush()
    
    room = models.Room(number="202", room_type_id=room_type.id, price_per_night=Decimal("100"))
    db.add(room)
    db.commit()

    # Create confirmed booking with final_bill pre-set (e.g., 150 instead of 200)
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    booking = models.Booking(
        booking_number="NO-SHOW-002",
        guest_id=guest.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=Decimal("100"),
        total_price=Decimal("200"),
        final_bill=Decimal("150"),  # Adjusted final bill
        status=models.BookingStatus.CONFIRMED.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Mark as no-show
    BookingService.mark_no_show(db, booking.id)

    # Verify no-show charge uses final_bill, not total_price
    no_show_payment = db.query(models.Payment).filter(
        models.Payment.booking_id == booking.id,
        models.Payment.status == models.Payment.PaymentStatus.PAID.value,
    ).first()
    assert no_show_payment is not None
    assert no_show_payment.amount == Decimal("150"), f"Expected charge of 150 (final_bill), got {no_show_payment.amount}"


def test_no_show_no_charge_for_zero_bill(db):
    """Test that no-show with zero final bill doesn't create a charge."""
    # Create guest and room
    guest = models.Guest(name="Test", surname="NoShow3", email="noshow3@example.com")
    room_type = models.RoomType(name="Test Room", base_price=Decimal("100"), capacity=2)
    
    db.add(guest)
    db.add(room_type)
    db.flush()
    
    room = models.Room(number="203", room_type_id=room_type.id, price_per_night=Decimal("100"))
    db.add(room)
    db.commit()

    # Create confirmed booking with zero final_bill
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    booking = models.Booking(
        booking_number="NO-SHOW-003",
        guest_id=guest.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=Decimal("100"),
        total_price=Decimal("0"),  # Zero total price
        status=models.BookingStatus.CONFIRMED.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Mark as no-show
    BookingService.mark_no_show(db, booking.id)

    # Verify no charge was created (since bill is 0)
    no_show_payments = db.query(models.Payment).filter(
        models.Payment.booking_id == booking.id,
    ).all()
    assert len(no_show_payments) == 0, "No charge should be created for zero bill"
