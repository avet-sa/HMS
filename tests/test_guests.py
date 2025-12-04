def test_create_guest(client):
    data = {
        "name": "John",
        "surname": "Smith",
        "email": "john.smith@example.com",
        "phone_number": "+1234567890",
        "nationality": "US",
    }
    response = client.post("/guests/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == data["email"]
    assert content["name"] == data["name"]


def test_list_guests(client):
    client.post(
        "/guests/",
        json={"name": "Jane", "surname": "Doe", "email": "jane.doe@example.com"},
    )
    response = client.get("/guests/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_guest(client):
    create_resp = client.post(
        "/guests/",
        json={"name": "Bob", "surname": "Johnson", "email": "bob.j@example.com"},
    )
    guest_id = create_resp.json()["id"]

    response = client.get(f"/guests/{guest_id}")
    assert response.status_code == 200
    assert response.json()["id"] == guest_id


def test_update_guest(client):
    create_resp = client.post(
        "/guests/",
        json={"name": "Alice", "surname": "Williams", "email": "alice.w@example.com"},
    )
    guest_id = create_resp.json()["id"]

    response = client.put(f"/guests/{guest_id}", json={"phone_number": "+9876543210"})
    assert response.status_code == 200
    assert response.json()["phone_number"] == "+9876543210"


def test_delete_guest(client):
    create_resp = client.post(
        "/guests/",
        json={"name": "Charlie", "surname": "Brown", "email": "charlie.b@example.com"},
    )
    guest_id = create_resp.json()["id"]

    response = client.delete(f"/guests/{guest_id}")
    assert response.status_code == 200

    get_resp = client.get(f"/guests/{guest_id}")
    assert get_resp.status_code == 404
