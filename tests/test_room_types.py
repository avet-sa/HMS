def test_create_room_type(client, admin_headers):
    data = {
        "name": "Standard Room",
        "base_price": 100.0,
        "capacity": 2,
        "description": "A standard room",
    }
    response = client.post("/room-types/", json=data, headers=admin_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert float(content["base_price"]) == data["base_price"]
    assert "id" in content


def test_list_room_types(client, admin_headers):
    # Create a room type first
    client.post(
        "/room-types/", json={"name": "Single Room", "base_price": 80.0, "capacity": 1},
        headers=admin_headers,
    )

    response = client.get("/room-types/", headers=admin_headers)
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) >= 1


def test_get_room_type(client, admin_headers):
    # Create
    create_resp = client.post(
        "/room-types/", json={"name": "Double Room", "base_price": 120.0, "capacity": 2},
        headers=admin_headers,
    )
    room_type_id = create_resp.json()["id"]

    # Get
    response = client.get(f"/room-types/{room_type_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == room_type_id


def test_update_room_type(client, admin_headers):
    # Create
    create_resp = client.post(
        "/room-types/", json={"name": "Suite", "base_price": 200.0, "capacity": 4},
        headers=admin_headers,
    )
    room_type_id = create_resp.json()["id"]

    # Update
    update_data = {"base_price": 250.0}
    response = client.put(f"/room-types/{room_type_id}", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    assert float(response.json()["base_price"]) == 250.0


def test_delete_room_type(client, admin_headers):
    # Create
    create_resp = client.post(
        "/room-types/", json={"name": "Penthouse", "base_price": 500.0, "capacity": 6},
        headers=admin_headers,
    )
    room_type_id = create_resp.json()["id"]

    # Delete
    response = client.delete(f"/room-types/{room_type_id}", headers=admin_headers)
    assert response.status_code == 200

    # Verify deletion
    get_resp = client.get(f"/room-types/{room_type_id}", headers=admin_headers)
    assert get_resp.status_code == 404
