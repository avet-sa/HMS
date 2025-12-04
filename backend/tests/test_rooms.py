import pytest


@pytest.fixture
def room_type(client):
    response = client.post(
        "/room-types/",
        json={"name": "Test Room Type", "base_price": 100.0, "capacity": 2},
    )
    return response.json()


def test_create_room(client, room_type):
    data = {
        "number": "101",
        "room_type_id": room_type["id"],
        "price_per_night": 100.0,
        "floor": 1,
        "square_meters": 25,
        "maintenance_status": "available",
    }
    response = client.post("/rooms/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["number"] == data["number"]
    assert content["room_type_id"] == room_type["id"]


def test_list_rooms(client, room_type):
    resp = client.post(
        "/rooms/",
        json={
            "number": "102",
            "room_type_id": room_type["id"],
            "price_per_night": 100.0,
            "square_meters": 25,
            "floor": 1,
        },
    )
    assert resp.status_code == 200, resp.text

    response = client.get("/rooms/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_room(client, room_type):
    create_resp = client.post(
        "/rooms/",
        json={
            "number": "103",
            "room_type_id": room_type["id"],
            "price_per_night": 100.0,
            "square_meters": 25,
            "floor": 1,
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    room_id = create_resp.json()["id"]

    response = client.get(f"/rooms/{room_id}")
    assert response.status_code == 200
    assert response.json()["id"] == room_id


def test_update_room(client, room_type):
    create_resp = client.post(
        "/rooms/",
        json={
            "number": "104",
            "room_type_id": room_type["id"],
            "price_per_night": 100.0,
            "square_meters": 25,
            "floor": 1,
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    room_id = create_resp.json()["id"]

    response = client.put(f"/rooms/{room_id}", json={"price_per_night": 150.0})
    assert response.status_code == 200
    assert float(response.json()["price_per_night"]) == 150.0


def test_delete_room(client, room_type):
    create_resp = client.post(
        "/rooms/",
        json={
            "number": "105",
            "room_type_id": room_type["id"],
            "price_per_night": 100.0,
            "square_meters": 25,
            "floor": 1,
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    room_id = create_resp.json()["id"]

    response = client.delete(f"/rooms/{room_id}")
    assert response.status_code == 200

    get_resp = client.get(f"/rooms/{room_id}")
    assert get_resp.status_code == 404
