def test_create_room_type(client):
    data = {
        "name": "Standard Room",
        "base_price": 100.0,
        "capacity": 2,
        "description": "A standard room",
    }
    response = client.post("/room-types/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert float(content["base_price"]) == data["base_price"]
    assert "id" in content


def test_list_room_types(client):
    # Create a room type first
    client.post(
        "/room-types/", json={"name": "Single Room", "base_price": 80.0, "capacity": 1}
    )

    response = client.get("/room-types/")
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) >= 1


def test_get_room_type(client):
    # Create
    create_resp = client.post(
        "/room-types/", json={"name": "Double Room", "base_price": 120.0, "capacity": 2}
    )
    room_type_id = create_resp.json()["id"]

    # Get
    response = client.get(f"/room-types/{room_type_id}")
    assert response.status_code == 200
    assert response.json()["id"] == room_type_id


def test_update_room_type(client):
    # Create
    create_resp = client.post(
        "/room-types/", json={"name": "Suite", "base_price": 200.0, "capacity": 4}
    )
    room_type_id = create_resp.json()["id"]

    # Update
    update_data = {"base_price": 250.0}
    response = client.put(f"/room-types/{room_type_id}", json=update_data)
    assert response.status_code == 200
    assert float(response.json()["base_price"]) == 250.0


def test_delete_room_type(client):
    # Create
    create_resp = client.post(
        "/room-types/", json={"name": "Penthouse", "base_price": 500.0, "capacity": 6}
    )
    room_type_id = create_resp.json()["id"]

    # Delete
    response = client.delete(f"/room-types/{room_type_id}")
    assert response.status_code == 200

    # Verify deletion
    get_resp = client.get(f"/room-types/{room_type_id}")
    assert get_resp.status_code == 404
