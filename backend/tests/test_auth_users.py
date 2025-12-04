import pytest


def test_register(client):
    data = {"username": "testuser", "password": "testpass"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["username"] == data["username"]
    assert "password" not in content


def test_login(client):
    # Register first
    client.post(
        "/auth/register", json={"username": "loginuser", "password": "loginpas"}
    )

    # Login
    response = client.post(
        "/auth/token", data={"username": "loginuser", "password": "loginpas"}
    )
    assert response.status_code == 200
    content = response.json()
    assert "access_token" in content
    assert content["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/token", data={"username": "nonexistent", "password": "wrongpass"}
    )
    assert response.status_code == 400


@pytest.fixture
def auth_token(client):
    # Register and login
    client.post("/auth/register", json={"username": "authuser", "password": "authpass"})
    response = client.post(
        "/auth/token", data={"username": "authuser", "password": "authpass"}
    )
    return response.json()["access_token"]


def test_get_current_user(client, auth_token):
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "authuser"


@pytest.fixture
def admin_token(client):
    # Register admin user
    response = client.post(
        "/auth/register",
        json={"username": "admin", "password": "adminpas", "permission_level": "ADMIN"},
    )
    # Login
    response = client.post(
        "/auth/token", data={"username": "admin", "password": "adminpas"}
    )
    return response.json()["access_token"]


def test_list_users_admin(client, admin_token):
    response = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_users_unauthorized(client, auth_token):
    response = client.get("/users/", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 403


def test_create_user_admin(client, admin_token):
    response = client.post(
        "/users/",
        json={"username": "newuser", "password": "newpassw"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_update_user_admin(client, admin_token):
    # Create user
    create_resp = client.post(
        "/users/",
        json={"username": "updateuser", "password": "updatepa"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_id = create_resp.json()["id"]

    # Update user
    response = client.patch(
        f"/users/{user_id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert not response.json()["is_active"]


def test_deactivate_user_admin(client, admin_token):
    # Create user
    create_resp = client.post(
        "/users/",
        json={"username": "deactivateuser", "password": "deactiva"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_id = create_resp.json()["id"]

    # Deactivate
    response = client.delete(
        f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert not response.json()["is_active"]
