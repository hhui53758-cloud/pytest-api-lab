"""第一章：真实 HTTP 请求和第一条自动化测试。"""

import requests


def test_health_returns_ok():
    # Arrange：准备请求地址。
    url = "http://127.0.0.1:8000/health"

    # Act：发送请求。timeout 防止无限等待。
    response = requests.get(url, timeout=3)

    # Assert：按接口约定判断实际结果。
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")

    body = response.json()
    assert body["status"] == "ok"
