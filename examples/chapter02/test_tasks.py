"""第二章：从接口约定推导正常和异常测试。"""

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_create_then_get_task():
    payload = {"title": "学习 Pytest"}

    create_response = requests.post(
        f"{BASE_URL}/tasks", json=payload, timeout=3
    )
    assert create_response.status_code == 201, create_response.text

    created = create_response.json()
    task_id = created["id"]
    try:
        assert isinstance(task_id, int) and task_id > 0
        assert created["title"] == payload["title"]
        assert created["status"] == "pending"

        get_response = requests.get(f"{BASE_URL}/tasks/{task_id}", timeout=3)
        assert get_response.status_code == 200, get_response.text
        assert get_response.json() == created
    finally:
        # 本章先手动清理。下一章使用 Fixture 统一管理。
        requests.delete(f"{BASE_URL}/tasks/{task_id}", timeout=3)


def test_delete_task_makes_it_unavailable():
    create_response = requests.post(
        f"{BASE_URL}/tasks", json={"title": "验证删除"}, timeout=3
    )
    assert create_response.status_code == 201, create_response.text
    task_id = create_response.json()["id"]
    try:
        delete_response = requests.delete(
            f"{BASE_URL}/tasks/{task_id}", timeout=3
        )
        assert delete_response.status_code == 204, delete_response.text
        assert delete_response.content == b""

        get_response = requests.get(f"{BASE_URL}/tasks/{task_id}", timeout=3)
        assert get_response.status_code == 404, get_response.text
        assert get_response.json()["detail"] == "Task not found"
    finally:
        # 若前面已删除，此处返回 404；正常清理允许任务已经不存在。
        requests.delete(f"{BASE_URL}/tasks/{task_id}", timeout=3)


def test_empty_title_is_rejected():
    response = requests.post(
        f"{BASE_URL}/tasks", json={"title": ""}, timeout=3
    )
    assert response.status_code == 422, response.text
    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", "title"] for error in errors)


def test_unknown_status_is_rejected():
    response = requests.post(
        f"{BASE_URL}/tasks",
        json={"title": "状态测试", "status": "unknown"},
        timeout=3,
    )
    assert response.status_code == 422, response.text
    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", "status"] for error in errors)


def test_get_nonexistent_task_returns_404():
    # 本服务从 1 开始分配 ID，因此 0 必定不存在。
    response = requests.get(f"{BASE_URL}/tasks/0", timeout=3)
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Task not found"
