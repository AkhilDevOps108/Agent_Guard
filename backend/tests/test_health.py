from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "agentguard"


def test_root_endpoint_returns_running_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "AgentGuard API is running."}
