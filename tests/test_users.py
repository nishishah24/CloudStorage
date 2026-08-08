def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "TestPass123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["is_active"] is True
    assert "id" in data

def test_duplicate_registration(client):
    payload = {
        "username": "duplicateuser",
        "email": "duplicate@example.com",
        "password": "TestPass123",
    }

    first_response = client.post(
        "/users/register",
        json=payload,
    )

    second_response = client.post(
        "/users/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json() == {
        "success": False,
        "error": "Username or email already exists",
    }


def test_login_success(client):
    client.post(
        "/users/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "TestPass123",
        },
    )

    response = client.post(
        "/users/login",
        json={
            "email": "login@example.com",
            "password": "TestPass123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/users/register",
        json={
            "username": "wrongpassuser",
            "email": "wrongpass@example.com",
            "password": "CorrectPass123",
        },
    )

    response = client.post(
        "/users/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPass123",
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "success": False,
        "error": "Invalid email or password",
    }

def test_get_me_without_token(client):
    response = client.get("/users/me")

    assert response.status_code in (401, 403)


def test_get_me_with_valid_token(client):
    # Create a user
    client.post(
        "/users/register",
        json={
            "username": "meuser",
            "email": "meuser@example.com",
            "password": "TestPass123",
        },
    )

    # Login and get JWT
    login_response = client.post(
        "/users/login",
        json={
            "email": "meuser@example.com",
            "password": "TestPass123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Send JWT with protected request
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "meuser"
    assert data["email"] == "meuser@example.com"
    assert data["is_active"] is True


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer this-is-not-a-valid-token",
        },
    )

    assert response.status_code == 401