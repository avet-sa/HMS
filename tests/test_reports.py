from datetime import date, timedelta
from decimal import Decimal

from backend.app.db import models


def make_room_and_roomtype(db, number, price=Decimal('100')):
    rt = models.RoomType(name=f"RT-{number}", base_price=price, capacity=2)
    db.add(rt)
    db.flush()
    room = models.Room(number=str(number), room_type_id=rt.id, price_per_night=price)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room, rt


def make_guest(db, idx):
    g = models.Guest(name=f"G{idx}", surname="Test", email=f"guest{idx}@example.com")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def make_booking(db, guest, room, check_in, check_out, created_by=None, status=models.BookingStatus.CONFIRMED.value, total_price=None):
    nights = (check_out - check_in).days
    price = room.price_per_night
    total = total_price if total_price is not None else (nights * price)
    booking = models.Booking(
        booking_number=f"BK-{guest.id}-{room.id}-{check_in}",
        guest_id=guest.id,
        room_id=room.id,
        created_by=created_by,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=price,
        total_price=total,
        status=status,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def test_occupancy_report(db, client, admin_headers):
    # create rooms
    room1, rt1 = make_room_and_roomtype(db, 101, Decimal('100'))
    room2, rt2 = make_room_and_roomtype(db, 102, Decimal('100'))

    # create guests
    g1 = make_guest(db, 1)
    g2 = make_guest(db, 2)

    # create bookings overlapping dates
    start = date.today()
    end = start + timedelta(days=3)

    # booking 1 occupies room1 for start..start+2
    b1 = make_booking(db, g1, room1, start, start + timedelta(days=2))
    # booking 2 occupies room2 for start+1..start+3
    b2 = make_booking(db, g2, room2, start + timedelta(days=1), start + timedelta(days=3))

    resp = client.get(f"/reports/occupancy?start_date={start.isoformat()}&end_date={end.isoformat()}", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data['start_date'] == start.isoformat()
    assert data['end_date'] == end.isoformat()
    # daily length should be 4 days (start..end inclusive)
    assert len(data['daily']) == 4


def test_revenue_report_and_invoice_flow(db, client, admin_headers):
    # create room and guest
    room, rt = make_room_and_roomtype(db, 201, Decimal('120'))
    g = make_guest(db, 3)

    # booking and mark checked-out and set final_bill
    check_in = date.today() - timedelta(days=3)
    check_out = date.today() - timedelta(days=1)
    booking = make_booking(db, g, room, check_in, check_out, status=models.BookingStatus.CHECKED_OUT.value)
    booking.final_bill = Decimal('240')
    db.commit()
    db.refresh(booking)

    # create a PAID payment for booking
    payment = models.Payment(
        booking_id=booking.id,
        amount=Decimal('240'),
        currency='USD',
        method='card',
        status=models.Payment.PaymentStatus.PAID.value,
        processed_at=None,
    )
    # set processed_at to today so revenue report picks it up
    payment.processed_at = date.today()
    db.add(payment)
    db.commit()

    start = date.today() - timedelta(days=5)
    end = date.today()
    resp = client.get(f"/reports/revenue?start_date={start.isoformat()}&end_date={end.isoformat()}", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data['total_revenue'] == '240.00' or float(data['total_revenue']) == 240.0


def test_trends_report(db, client, admin_headers):
    # create rooms and guest
    room, rt = make_room_and_roomtype(db, 301, Decimal('80'))
    g = make_guest(db, 4)

    start = date.today() - timedelta(days=7)
    end = date.today()

    # create bookings in range
    for i in range(3):
        ci = start + timedelta(days=i)
        co = ci + timedelta(days=1)
        make_booking(db, g, room, ci, co, status=models.BookingStatus.CONFIRMED.value)

    # create one cancellation
    b = make_booking(db, g, room, start + timedelta(days=4), start + timedelta(days=5))
    b.status = models.BookingStatus.CANCELLED.value
    b.cancelled_at = start + timedelta(days=4)
    db.commit()

    # create one no-show
    b2 = make_booking(db, g, room, start + timedelta(days=5), start + timedelta(days=6))
    b2.status = models.BookingStatus.NO_SHOW.value
    db.commit()

    resp = client.get(f"/reports/trends?start_date={start.isoformat()}&end_date={end.isoformat()}", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data['total_bookings'] >= 3
    assert data['cancellations'] >= 1
    assert data['no_shows'] >= 1
