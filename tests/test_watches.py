def test_get_my_watches(authorized_client, test_watch):
    # Tests paginated GET endpoint for the authenticated user
    response = authorized_client.get("/api/v1/watches/")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["brand"] == "Seiko"


def test_get_watch_by_id(authorized_client, test_watch):
    # Tests fetching a specific watch by its ID
    response = authorized_client.get(f"/api/v1/watches/{test_watch.id}")

    assert response.status_code == 200
    assert response.json()["model_name"] == "5 Sports"


def test_delete_watch(authorized_client, test_watch):
    # Tests successful deletion and verifies it no longer exists
    response = authorized_client.delete(f"/api/v1/watches/{test_watch.id}")
    assert response.status_code == 200

    verify_response = authorized_client.get(f"/api/v1/watches/{test_watch.id}")
    assert verify_response.status_code == 404


def test_unauthorized_access(client, test_watch):
    """Tests that a user without a valid token cannot access or delete watches."""
    # Using 'client' (unauthenticated) instead of 'authorized_client'
    response = client.delete(f"/api/v1/watches/{test_watch.id}")
    assert response.status_code == 401