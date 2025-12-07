from datetime import date, timedelta, datetime, timezone
from decimal import Decimal
import pytest

from backend.app.db import models
from backend.app.services.invoice_service import InvoiceService


def create_room_and_guest(db):
    rt = models.RoomType(name="Unit Invoice RT", base_price=120.0, capacity=2)
    db.add(rt)
    db.commit()
    db.refresh(rt)

    room = models.Room(number="402", room_type_id=rt.id, price_per_night=120.0)
    db.add(room)
    db.commit()
    db.refresh(room)

    guest = models.Guest(name="Inv", surname="Guest", email=f"inv.guest.{rt.id}@example.com")
    db.add(guest)
    db.commit()
    db.refresh(guest)

    return rt, room, guest


def create_checked_out_booking(db, guest, room, nights=1):
    booking_number = f"UTINV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
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


def test_generate_invoice_success(db):
    rt, room, guest = create_room_and_guest(db)
    booking = create_checked_out_booking(db, guest, room, nights=1)

    invoice = InvoiceService.generate_invoice(db, booking.id)
    assert invoice.booking_id == booking.id
    assert Decimal(str(invoice.subtotal)) == Decimal(str(booking.final_bill))
    assert Decimal(str(invoice.tax)) == (Decimal(str(invoice.subtotal)) * Decimal('0.10')).quantize(Decimal('0.01'))
    assert invoice.invoice_number.startswith("INV-")


def test_generate_invoice_rejected_without_final_bill(db):
    rt, room, guest = create_room_and_guest(db)
    # Create booking but without final_bill
    booking_number = f"UTINV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    check_in = date.today()
    check_out = date.today() + timedelta(days=1)
    booking = models.Booking(
        booking_number=booking_number,
        room_id=room.id,
        guest_id=guest.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=room.price_per_night,
        total_price=room.price_per_night,
        status=models.BookingStatus.CHECKED_OUT.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        InvoiceService.generate_invoice(db, booking.id)
