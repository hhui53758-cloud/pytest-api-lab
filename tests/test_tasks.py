import pytest

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_create_then_get_task(api_alice, task_factory, db_probe):
    response = task_factory(title="学习 Pytest")
    assert response.status_code == 201
    task = response.json()
    assert isinstance(task["id"], int) and task["id"] > 0
    assert task["title"] == "学习 Pytest"
    assert task["status"] == "pending"
    queried = api_alice.get(f"/tasks/{task['id']}")
    assert queried.status_code == 200
    assert queried.json() == task
    assert db_probe.task(task["id"]) == task


def test_update_task(api_alice, task_factory, db_probe):
    response = task_factory(title="待修改")
    assert response.status_code == 201
    task_id = response.json()["id"]
    updated = api_alice.put(f"/tasks/{task_id}", json={"title": "已修改", "status": "done"})
    assert updated.status_code == 200
    body = updated.json()
    assert body["id"] == task_id
    assert body["title"] == "已修改"
    assert body["status"] == "done"
    queried = api_alice.get(f"/tasks/{task_id}")
    assert queried.status_code == 200
    assert queried.json() == body
    assert db_probe.task(task_id) == body


@pytest.mark.smoke
def test_delete_task(api_alice, task_factory, db_probe):
    response = task_factory(title="验证删除")
    assert response.status_code == 201
    task_id = response.json()["id"]
    deleted = api_alice.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    queried = api_alice.get(f"/tasks/{task_id}")
    assert queried.status_code == 404
    assert queried.json()["detail"] == "Task not found"
    assert db_probe.task(task_id) is None


@pytest.mark.parametrize("length,expected", [(0, 422), (1, 201), (50, 201), (51, 422)],
                         ids=["empty", "min", "max", "over-max"])
def test_title_boundaries(task_factory, db_probe, length, expected):
    count_before = db_probe.task_count()
    response = task_factory(title="a" * length)
    assert response.status_code == expected
    if expected == 201:
        task = response.json()
        assert task["title"] == "a" * length
        assert db_probe.task(task["id"]) == task
        assert db_probe.task_count() == count_before + 1
    else:
        assert any(error["loc"] == ["body", "title"] for error in response.json()["detail"])
        assert db_probe.task_count() == count_before


@pytest.mark.parametrize("status", ["pending", "running", "done"])
def test_allowed_status(task_factory, db_probe, status):
    response = task_factory(title="合法状态", status=status)
    assert response.status_code == 201
    task = response.json()
    assert task["status"] == status
    assert db_probe.task(task["id"]) == task


def test_unknown_status_is_rejected(task_factory, db_probe):
    count_before = db_probe.task_count()
    response = task_factory(title="非法状态", status="unknown")
    assert response.status_code == 422
    assert any(error["loc"] == ["body", "status"] for error in response.json()["detail"])
    assert db_probe.task_count() == count_before


def test_get_nonexistent_task_returns_404(api_alice):
    response = api_alice.get("/tasks/0")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_unauthenticated_create_is_rejected(api_client, db_probe):
    count_before = db_probe.task_count()
    response = api_client.post("/tasks", json={"title": "未登录"})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert db_probe.task_count() == count_before


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"], ids=["read", "update", "delete"])
def test_other_user_cannot_access_task(api_alice, api_bob, task_factory, db_probe, method):
    created = task_factory(title="Alice 的任务")
    assert created.status_code == 201
    task = created.json()
    kwargs = {"json": {"title": "越权修改", "status": "done"}} if method == "PUT" else {}
    response = api_bob.request(method, f"/tasks/{task['id']}", **kwargs)
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
    assert db_probe.task(task["id"]) == task
    owner_response = api_alice.get(f"/tasks/{task['id']}")
    assert owner_response.status_code == 200
    assert owner_response.json() == task
