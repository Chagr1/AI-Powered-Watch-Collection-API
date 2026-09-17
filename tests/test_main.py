from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_swagger_ui_is_running():
    """
    Test if the API documentation page is accessible.
    """
    response = client.get("/docs")
    assert response.status_code == 200