from datetime import date, timedelta
import pytest


@pytest.fixture
def room_type(client):
    response = client.post(
        "/room-types/",
        json={"name": "Booking Test Room Type", "base_price": 150.0, "capacity": 2},
    )
    return response.json()


@pytest.fixture
def room(client, room_type):
    response = client.post(
        "/rooms/",
        json={
            "number": "201",
            "room_type_id": room_type["id"],
            "price_per_night": 150.0,
            "square_meters": 30,
            "floor": 2,
        },
    )
    return response.json()


@pytest.fixture
def guest(client):
    response = client.post(
        "/guests/",
        json={"name": "Test", "surname": "Guest", "email": "test.guest@example.com"},
    )
    return response.json()


def test_create_booking(client, room, guest):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    data = {
        "guest_id": guest["id"],
        "room_id": room["id"],
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "number_of_guests": 2,
        "number_of_nights": 2,
        "price_per_night": 150.0,
        "total_price": 300.0,
    }
    response = client.post("/bookings/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["guest_id"] == guest["id"]
    assert content["room_id"] == room["id"]


def test_list_bookings(client, room, guest):
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
            "number_of_nights": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
    )
    response = client.get("/bookings/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_booking(client, room, guest):
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
            "number_of_nights": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
    )
    booking_id = create_resp.json()["id"]

    response = client.get(f"/bookings/{booking_id}")
    assert response.status_code == 200
    assert response.json()["id"] == booking_id


def test_update_booking(client, room, guest):
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
            "number_of_nights": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
    )
    booking_id = create_resp.json()["id"]

    response = client.put(f"/bookings/{booking_id}", json={"number_of_guests": 2})
    assert response.status_code == 200
    assert response.json()["number_of_guests"] == 2


def test_checkin_booking(client, room, guest):
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
            "number_of_nights": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
    )
    booking_id = create_resp.json()["id"]

    response = client.post(f"/bookings/{booking_id}/checkin")
    assert response.status_code == 200
    assert response.json()["status"] == "checked_in"


def test_checkout_booking(client, room, guest):
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
            "number_of_nights": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
    )
    booking_id = create_resp.json()["id"]

    response = client.post(f"/bookings/{booking_id}/checkout")
    assert response.status_code == 200
    assert response.json()["status"] == "checked_out"


def test_cancel_booking(client, room, guest):
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
            "number_of_nights": 1,
            "price_per_night": 150.0,
            "total_price": 150.0,
        },
    )
    booking_id = create_resp.json()["id"]

    response = client.post(f"/bookings/{booking_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
