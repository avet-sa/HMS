from datetime import date, timedelta, datetime, timezone
from decimal import Decimal
import pytest

from backend.app.db import models
from backend.app.services.payment_service import PaymentService


def create_room_and_guest(db):
    rt = models.RoomType(name="Unit Payment RT", base_price=100.0, capacity=2)
    db.add(rt)
    db.commit()
    db.refresh(rt)

    room = models.Room(number="401", room_type_id=rt.id, price_per_night=100.0)
    db.add(room)
    db.commit()
    db.refresh(room)

    guest = models.Guest(name="Unit", surname="Guest", email=f"unit.guest.{rt.id}@example.com")
    db.add(guest)
    db.commit()
    db.refresh(guest)

    return rt, room, guest


def create_checked_out_booking(db, guest, room, nights=1):
    booking_number = f"UT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    check_in = date.today()
    check_out = date.today() + timedelta(days=nights)
    booking = models.Booking(
        booking_number=booking_number,
        room_id=room.id,
        guest_id=guest.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=room.price_per_night,
        total_price=room.price_per_night * nights,
        status=models.BookingStatus.CHECKED_OUT.value,
        actual_check_in=datetime.now() - timedelta(days=nights),
        actual_check_out=datetime.now(),
        final_bill=room.price_per_night * nights,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def test_create_and_process_payment(db):
    rt, room, guest = create_room_and_guest(db)
    booking = create_checked_out_booking(db, guest, room, nights=1)

    # Create payment
    # debug: inspect stored booking.status
    print("booking.status repr:", repr(booking.status), "type:", type(booking.status))
    assert (booking.status.value if hasattr(booking.status, "value") else booking.status) == models.BookingStatus.CHECKED_OUT.value

    payment = PaymentService.create_payment(db, booking.id, Decimal("100.00"), method="card")
    assert (payment.status.value if hasattr(payment.status, "value") else payment.status) == models.Payment.PaymentStatus.PENDING.value

    # Process payment
    processed = PaymentService.process_payment(db, payment.id)
    assert (processed.status.value if hasattr(processed.status, "value") else processed.status) == models.Payment.PaymentStatus.PAID.value
    assert processed.processed_at is not None


def test_overpayment_prevention(db):
    rt, room, guest = create_room_and_guest(db)
    booking = create_checked_out_booking(db, guest, room, nights=1)

    p1 = PaymentService.create_payment(db, booking.id, Decimal("90.00"), method="card")
    p2 = PaymentService.create_payment(db, booking.id, Decimal("20.00"), method="card")

    # Process first payment
    PaymentService.process_payment(db, p1.id)

    # Processing second should raise HTTPException (overpayment)
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        PaymentService.process_payment(db, p2.id)


def test_refund_rules(db):
    rt, room, guest = create_room_and_guest(db)
    booking = create_checked_out_booking(db, guest, room, nights=1)

    p = PaymentService.create_payment(db, booking.id, Decimal("100.00"), method="card")
    PaymentService.process_payment(db, p.id)

    # Refund should work for PAID payment
    refunded = PaymentService.refund_payment(db, p.id)
    assert (refunded.status.value if hasattr(refunded.status, "value") else refunded.status) == models.Payment.PaymentStatus.REFUNDED.value
    assert refunded.refunded_at is not None

    # Cannot refund non-PAID payment
    p2 = PaymentService.create_payment(db, booking.id, Decimal("10.00"), method="card")
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        PaymentService.refund_payment(db, p2.id)
