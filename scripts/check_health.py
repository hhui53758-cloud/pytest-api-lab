"""先用普通 Python 观察接口，再学习 Pytest。"""

import requests

response = requests.get("http://127.0.0.1:8000/health", timeout=3)

print("HTTP 状态码:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type"))
print("响应正文:", response.text)
print("解析后的 Python 对象:", response.json())
