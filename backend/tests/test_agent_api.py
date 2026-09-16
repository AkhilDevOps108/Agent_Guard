from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_invoke_endpoint_returns_trace():
    response = client.post(
        "/api/v1/agent/invoke",
        json={"message": "Where is order ORD-1001?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_calls"][0] == "get_order"
    assert body["trace"][0]["type"] == "tool"


def test_agent_invoke_endpoint_rejects_empty_message():
    response = client.post("/api/v1/agent/invoke", json={"message": ""})

    assert response.status_code == 422