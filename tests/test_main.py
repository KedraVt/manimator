from fastapi.testclient import TestClient

from manimator.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
