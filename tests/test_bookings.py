from datetime import date, timedelta
import pytest


@pytest.fixture
def room_type(client, admin_headers):
    response = client.post(
        "/room-types/",
        json={"name": "Test Room Type", "base_price": 100.0, "capacity": 2},
        headers=admin_headers,
    )
    return response.json()


@pytest.fixture
def room(client, admin_headers, room_type):
    response = client.post(
        "/rooms/",
        json={
            "number": "201",
            "room_type_id": room_type["id"],
            "price_per_night": 150.0,
            "square_meters": 30,
            "floor": 2,
        },
        headers=admin_headers,
    )
    return response.json()


@pytest.fixture
def guest(client, admin_headers):
    response = client.post(
        "/guests/",
        json={"name": "Test", "surname": "Guest", "email": "test.guest@example.com"},
        headers=admin_headers,
    )
    return response.json()


def test_create_booking(client, admin_headers, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    data = {
        "guest_id": guest["id"],
        "room_id": room["id"],
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "number_of_guests": 2,
        "price_per_night": 150.0,
        "total_price": 300.0,
    }
    response = client.post("/bookings/", json=data, headers=admin_headers)
    assert response.status_code == 201
    content = response.json()
    assert content["guest"]["id"] == guest["id"]
    assert content["room_id"] == room["id"]


def test_list_bookings(client, admin_headers, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=2)
    client.post(
        "/bookings/",
        json={
            "guest_id": guest["id"],
            "room_id": room["id"],
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "number_of_guests": 1,
        },
        headers=admin_headers,
    )
    response = client.get("/bookings/", headers=admin_headers)
    assert response.status_code == 201
    assert len(response.json()) >= 1


def test_get_booking(client, admin_headers, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=2)
    create_resp = client.post(
        "/bookings/",
        json={
            "guest_id": guest["id"],
            "room_id": room["id"],
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "number_of_guests": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
        headers=admin_headers,
    )
    booking_id = create_resp.json()["id"]

    response = client.get(f"/bookings/{booking_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == booking_id


def test_update_booking(client, admin_headers, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=2)
    create_resp = client.post(
        "/bookings/",
        json={
            "guest_id": guest["id"],
            "room_id": room["id"],
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "number_of_guests": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
        headers=admin_headers,
    )
    booking_id = create_resp.json()["id"]

    response = client.put(f"/bookings/{booking_id}", json={"number_of_guests": 2}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["number_of_guests"] == 2


def test_checkin_booking(client, admin_headers, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=2)
    create_resp = client.post(
        "/bookings/",
        json={
            "guest_id": guest["id"],
            "room_id": room["id"],
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "number_of_guests": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
        headers=admin_headers,
    )
    booking_id = create_resp.json()["id"]

    # First confirm the booking
    confirm_resp = client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "confirmed"

    # Then check in
    response = client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "checked_in"


def test_checkout_booking(client, admin_headers, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=2)
    create_resp = client.post(
        "/bookings/",
        json={
            "guest_id": guest["id"],
            "room_id": room["id"],
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "number_of_guests": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
        headers=admin_headers,
    )
    booking_id = create_resp.json()["id"]

    # Confirm
    client.post(f"/bookings/{booking_id}/confirm", headers=admin_headers)

    # Check in
    client.post(f"/bookings/{booking_id}/check-in", headers=admin_headers)

    # Check out
    response = client.post(f"/bookings/{booking_id}/check-out", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "checked_out"


def test_cancel_booking(client, admin_headers, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=2)
    create_resp = client.post(
        "/bookings/",
        json={
            "guest_id": guest["id"],
            "room_id": room["id"],
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "number_of_guests": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
        headers=admin_headers,
    )
    booking_id = create_resp.json()["id"]

    response = client.post(f"/bookings/{booking_id}/cancel", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
