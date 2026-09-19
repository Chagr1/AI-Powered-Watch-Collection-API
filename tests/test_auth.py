def test_register_success(client):
    # Researched and adapted to remove email dependency
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": "strongpassword"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_register_duplicate_username(client, test_user):
    # Tests constraint violation using the existing test_user
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 400


def test_login_success(client, test_user):
    # Form data usually expects username/password fields
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401