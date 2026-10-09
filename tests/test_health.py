import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.regression]


def test_health_returns_ok(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    assert response.json() == {"status": "ok", "service": "task-api"}
