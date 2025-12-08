"""Integration tests for payments (clean, consolidated).

These tests use the existing fixtures from `tests/conftest.py`:
- `client`, `admin_headers`, `regular_headers`, and `db`.

They purposefully fix `final_bill` in the DB when the lifecycle causes a zero
bill (same-day check-in/out) so payments can be exercised reliably.
"""

from datetime import date, timedelta, datetime
from decimal import Decimal

from backend.app.db import models


def make_room_type(client, admin_headers):
    resp = client.post(
        "/room-types/",
        json={"name": "Payments Test Room Type", "base_price": 100.0, "capacity": 2},
        headers=admin_headers,
    )
    return resp.json()


def make_room(client, admin_headers, room_type_id):
    resp = client.post(
        "/rooms/",
        json={
            "number": "301",
            "room_type_id": room_type_id,
            "price_per_night": 100.0,
            "square_meters": 20,
            "floor": 3,
        },
        headers=admin_headers,
    )
    return resp.json()


def make_guest(client, admin_headers, email="paytest.guest@example.com"):
    resp = client.post(
        "/guests/",
        json={"name": "Pay", "surname": "Guest", "email": email},
        headers=admin_headers,
    )
    return resp.json()


def make_booking(client, admin_headers, guest_id, room_id, price_per_night=100.0, total_price=100.0):
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


def _ensure_final_bill_nonzero(db, booking_id):
    booking_obj = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    booking_obj.actual_check_in = datetime.now() - timedelta(days=1)
    booking_obj.actual_check_out = datetime.now()
    booking_obj.final_bill = booking_obj.price_per_night * 1
    booking_obj.status = models.BookingStatus.CHECKED_OUT.value
    db.commit()
    return Decimal(str(booking_obj.final_bill))


def test_payment_integration_full_flow(client, admin_headers, regular_headers, db):
    """End-to-end: create booking, lifecycle -> create payment -> process -> refund"""
    rt = make_room_type(client, admin_headers)
    room = make_room(client, admin_headers, rt["id"])
    guest = make_guest(client, admin_headers, email="payflow.guest@example.com")

    booking = make_booking(client, admin_headers, guest["id"], room["id"], price_per_night=100.0, total_price=100.0)
    booking_id = booking["id"]

    # move through lifecycle
    r = client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    assert r.status_code == 200
    r = client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    assert r.status_code == 200
    r = client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)
    assert r.status_code == 200

    # fetch booking to get final_bill; if zero, fix it in DB
    g = client.get(f"/bookings/{booking_id}", headers=admin_headers)
    assert g.status_code == 200
    final_bill = Decimal(str(g.json().get("final_bill") or "0"))
    if final_bill == 0:
        final_bill = _ensure_final_bill_nonzero(db, booking_id)

    assert final_bill > 0

    # create payment as regular user
    pay = client.post(
        "/payments/create",
        json={"booking_id": booking_id, "amount": float(final_bill), "method": "card"},
        headers=regular_headers,
    )
    assert pay.status_code == 200, f"create payment failed: {pay.status_code} {pay.text}"
    p = pay.json()
    assert p["status"] in ("PENDING", "pending")

    # process payment as admin
    proc = client.post(f"/payments/{p['id']}/process", headers=admin_headers)
    assert proc.status_code == 200, f"process failed: {proc.status_code} {proc.text}"
    proc_json = proc.json()
    assert proc_json["status"] in ("PAID", "paid")

    # refund as admin
    ref = client.post(f"/payments/{p['id']}/refund", headers=admin_headers)
    assert ref.status_code == 200, f"refund failed: {ref.status_code} {ref.text}"
    ref_json = ref.json()
    assert ref_json["status"] in ("REFUNDED", "refunded")


def test_overpayment_rejected_via_api(client, admin_headers, regular_headers, db):
    rt = make_room_type(client, admin_headers)
    room = make_room(client, admin_headers, rt["id"])
    guest = make_guest(client, admin_headers, email="overpay.guest@example.com")

    booking = make_booking(client, admin_headers, guest["id"], room["id"], price_per_night=100.0, total_price=100.0)
    booking_id = booking["id"]

    client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)

    # Ensure final bill is non-zero
    _ensure_final_bill_nonzero(db, booking_id)

    # create two payments
    r1 = client.post(
        "/payments/create",
        json={"booking_id": booking_id, "amount": 90.0, "method": "card"},
        headers=regular_headers,
    )
    assert r1.status_code == 200
    p1 = r1.json()

    r2 = client.post(
        "/payments/create",
        json={"booking_id": booking_id, "amount": 20.0, "method": "card"},
        headers=regular_headers,
    )
    assert r2.status_code == 200
    p2 = r2.json()

    # process first -> should succeed
    pr1 = client.post(f"/payments/{p1['id']}/process", headers=admin_headers)
    assert pr1.status_code == 200

    # process second -> should be rejected (400)
    pr2 = client.post(f"/payments/{p2['id']}/process", headers=admin_headers)
    assert pr2.status_code == 400


def test_refund_flow(client, admin_headers, regular_headers, db):
    rt = make_room_type(client, admin_headers)
    room = make_room(client, admin_headers, rt["id"])
    guest = make_guest(client, admin_headers, email="refund.guest@example.com")

    booking = make_booking(client, admin_headers, guest["id"], room["id"], price_per_night=100.0, total_price=100.0)
    booking_id = booking["id"]

    # Lifecycle
    client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)

    # Fix DB for realistic final bill
    _ensure_final_bill_nonzero(db, booking_id)

    # Create & process payment via API
    p = client.post(
        "/payments/create",
        json={"booking_id": booking_id, "amount": 100.0, "method": "card"},
        headers=regular_headers,
    )
    assert p.status_code == 200
    p_json = p.json()

    proc = client.post(f"/payments/{p_json['id']}/process", headers=admin_headers)
    assert proc.status_code == 200

    # Refund
    ref = client.post(f"/payments/{p_json['id']}/refund", headers=admin_headers)
    assert ref.status_code == 200
    ref_json = ref.json()
    assert ref_json["status"] in ("REFUNDED", "refunded")

    # Cannot refund a non-PAID payment (API)
    p2 = client.post(
        "/payments/create",
        json={"booking_id": booking_id, "amount": 10.0, "method": "card"},
        headers=regular_headers,
    )
    assert p2.status_code == 200
    p2_json = p2.json()

    bad_ref = client.post(f"/payments/{p2_json['id']}/refund", headers=admin_headers)
    assert bad_ref.status_code == 400