from datetime import date, timedelta, datetime
from decimal import Decimal
from backend.app.db import models


def make_room_type(client, admin_headers):
    resp = client.post(
        "/room-types/",
        json={"name": "Invoices Test Room Type", "base_price": 120.0, "capacity": 2},
        headers=admin_headers,
    )
    return resp.json()


def make_room(client, admin_headers, room_type_id):
    resp = client.post(
        "/rooms/",
        json={
            "number": "302",
            "room_type_id": room_type_id,
            "price_per_night": 120.0,
            "square_meters": 22,
            "floor": 3,
        },
        headers=admin_headers,
    )
    return resp.json()


def make_guest(client, admin_headers, email="invtest.guest@example.com"):
    resp = client.post(
        "/guests/",
        json={"name": "Inv", "surname": "Guest", "email": email},
        headers=admin_headers,
    )
    return resp.json()


def make_booking(client, admin_headers, guest_id, room_id, price_per_night=120.0, total_price=120.0):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=2)
    data = {
        "guest_id": guest_id,
        "room_id": room_id,
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "number_of_guests": 1,
        "price_per_night": price_per_night,
        "total_price": total_price,
    }
    resp = client.post("/bookings/", json=data, headers=admin_headers)
    return resp.json()


def test_generate_invoice_success(client, admin_headers, db):
    rt = make_room_type(client, admin_headers)
    room = make_room(client, admin_headers, rt["id"])
    guest = make_guest(client, admin_headers, email="invsuccess.guest@example.com")

    booking = make_booking(client, admin_headers, guest["id"], room["id"], price_per_night=120.0, total_price=120.0)
    booking_id = booking["id"]

    # Move booking through lifecycle to set final_bill
    client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)

    # Fix DB so final_bill is non-zero
    booking_obj = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    booking_obj.actual_check_in = datetime.now() - timedelta(days=1)
    booking_obj.actual_check_out = datetime.now()
    booking_obj.final_bill = booking_obj.price_per_night * 1
    booking_obj.status = models.BookingStatus.CHECKED_OUT.value
    db.commit()

    # Generate invoice
    inv = client.post(f"/invoices/{booking_id}", headers=admin_headers)
    assert inv.status_code == 200
    inv_json = inv.json()
    assert inv_json["booking_id"] == booking_id
    assert Decimal(str(inv_json["subtotal"])) > 0
    assert Decimal(str(inv_json["tax"])) == (Decimal(str(inv_json["subtotal"])) * Decimal('0.10')).quantize(Decimal('0.01'))
    assert inv_json["invoice_number"].startswith("INV-")


def test_generate_invoice_rejected_without_final_bill(client, admin_headers, db):
    rt = make_room_type(client, admin_headers)
    room = make_room(client, admin_headers, rt["id"])
    guest = make_guest(client, admin_headers, email="invfail.guest@example.com")

    # Create booking but do NOT check out (final_bill will be None)
    booking = make_booking(client, admin_headers, guest["id"], room["id"], price_per_night=120.0, total_price=120.0)
    booking_id = booking["id"]

    inv = client.post(f"/invoices/{booking_id}", headers=admin_headers)
    assert inv.status_code == 400
