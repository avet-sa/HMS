from datetime import date, timedelta


def test_full_booking_flow(client, admin_headers):
    # 1. Create Room Type
    room_type_data = {
        "name": "Deluxe Suite",
        "base_price": 200.0,
        "capacity": 2,
        "description": "A luxurious suite with a view",
    }
    response = client.post("/room-types/", json=room_type_data, headers=admin_headers)
    assert response.status_code == 200, response.text
    room_type = response.json()
    assert room_type["name"] == room_type_data["name"]
    room_type_id = room_type["id"]

    # 2. Create Room
    room_data = {
        "number": "101",
        "room_type_id": room_type_id,
        "price_per_night": 200.0,
        "floor": 1,
        "square_meters": 30,
        "maintenance_status": "available",
        "has_view": True,
        "is_smoking": False,
    }
    response = client.post("/rooms/", json=room_data, headers=admin_headers)
    assert response.status_code == 200, response.text
    room = response.json()
    assert room["number"] == room_data["number"]
    room_id = room["id"]

    # 3. Create Guest
    guest_data = {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "nationality": "US",
        "document_type": "passport",
        "document_id": "A12345678",
    }
    response = client.post("/guests/", json=guest_data, headers=admin_headers)
    assert response.status_code == 200, response.text
    guest = response.json()
    assert guest["email"] == guest_data["email"]
    guest_id = guest["id"]

    # 4. Create Booking
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    booking_data = {
        "guest_id": guest_id,
        "room_id": room_id,
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "number_of_guests": 2,
        "price_per_night": 200.0,
        "total_price": 400.0,
        "status": "pending",
    }
    response = client.post("/bookings/", json=booking_data, headers=admin_headers)
    assert response.status_code == 200, response.text
    booking = response.json()
    assert booking["guest"]["id"] == guest_id
    assert booking["room_id"] == room_id
    assert float(booking["total_price"]) == 400.0

