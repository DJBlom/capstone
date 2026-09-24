"""Health and metrics endpoints (200 OK, JSON, request-rate instrumentation)."""


def test_health_returns_200_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"


def test_metrics_returns_200_json_with_requests_per_second(client):
    client.get("/health")
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    payload = response.get_json()
    assert "requests_per_second" in payload
    assert "requests_total" in payload
    assert payload["requests_total"] >= 2
    assert payload["requests_per_second"] >= 0
    assert "200" in payload["requests_by_status"]
