import pytest

pytestmark = pytest.mark.regression


@pytest.mark.parametrize("username,password,expected_status", [
    pytest.param("alice", "Alice123!", 200, id="valid", marks=pytest.mark.smoke),
    pytest.param("alice", "WrongPassword!", 401, id="wrong-password"),
    pytest.param("nobody", "AnyPassword!", 401, id="unknown-user"),
])
def test_login(api_client, username, password, expected_status):
    response = api_client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == expected_status
    if expected_status == 200:
        body = response.json()
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str) and len(body["access_token"]) >= 32
        api_client.set_token(body["access_token"])
        assert api_client.get("/tasks/0").status_code == 404
    else:
        assert response.json()["detail"] == "Invalid credentials"
