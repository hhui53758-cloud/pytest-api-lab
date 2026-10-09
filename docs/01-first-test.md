# 第一章：从一次请求到一条自动化测试

本章原始测试见 examples/chapter01/test_health.py。当前 tests 目录已升级为完整框架，此文用于回看基础概念。

目标：看懂并运行一个 HTTP 接口测试，能区分请求成功与业务结果符合预期。

## 1. 两个程序各自做什么

`app/main.py` 是被测服务。启动后，它监听本机 8000 端口，收到 `GET /health` 就返回约定的内容。

`tests/test_health.py` 是测试程序。它向服务发送请求，把实际响应与预期比较。

服务要先运行。运行测试不会自动启动服务；我们后续会讨论环境准备。

编辑器运行时，请将项目解释器设为项目内的 `.venv\Scripts\python.exe`。依赖安装在哪个 Python 环境，运行就要使用哪个环境。`另一个系统 Python` 是另一个解释器，不会自动共享本项目虚拟环境中的依赖。

现在 `main.py` 包含 `if __name__ == "__main__":` 启动入口：直接运行这个文件时启动 Uvicorn 服务；通过 `uvicorn app.main:app` 导入时，这段入口不执行，避免重复启动。

`127.0.0.1` 表示本机，`8000` 是端口，`/health` 是路径。HTTP GET 通常用于获取资源或状态。

## 2. 请求与响应

```python
response = requests.get("http://127.0.0.1:8000/health", timeout=3)
```

Requests 是 Python 的 HTTP 客户端库。`get()` 发起 GET 请求，返回响应对象。`timeout=3` 为连接和读取等待设置超时，防止一直卡住；它不等于整次请求的严格三秒总时限。

响应包括状态码、响应头和正文：

- `response.status_code`：HTTP 状态码。本接口约定成功时为 200。
- `response.headers`：响应头，描述返回数据的类型等信息。
- `response.text`：正文的文本形式。
- `response.json()`：把 JSON 正文解析为 Python 对象；本例为字典。正文不是合法 JSON 时解析会失败。

本接口的约定是：

```json
{"status": "ok", "service": "task-api"}
```

HTTP 200 表示这一层请求按服务定义成功处理；测试仍需检查正文中的业务结果。

## 3. Pytest 怎样找到测试

Pytest 是测试框架，负责发现用例、执行、记录失败并汇总结果。

本项目约定文件以 `test_` 开头，测试函数也以 `test_` 开头。`pytest.ini` 中的 `testpaths = tests` 指定默认从 `tests` 目录寻找用例。

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

`-m pytest` 使用当前这个 Python 环境运行 Pytest；`-v` 显示每条用例的详细结果。`collected 1 item` 表示收集到一条用例，`PASSED` 表示断言都满足。

## 4. 断言与 Arrange / Act / Assert

断言是测试的判定条件：

```python
assert response.status_code == 200
```

比较为真时继续；为假时抛出 AssertionError，Pytest 把用例记为失败，并显示实际比较信息。请求拿到了响应并不自动说明测试通过。

常用组织方法是 Arrange / Act / Assert：

1. Arrange：准备地址、数据和前置条件。
2. Act：执行被测操作。
3. Assert：验证结果。

本章依次检查状态码、JSON 类型和正文中的 `status`。只检查状态码会漏掉“返回 200，但字段内容错误”的情况。

## 5. 你来完成的小练习

打开 `tests/test_health.py`，在最后增加一条断言，验证返回的 `service` 等于 `task-api`。再次运行测试。

接着把你新增断言的预期值临时改为 `wrong-service`，观察 FAILED 输出中实际值与预期值的差异，再改回正确值并复测。不要修改服务来迎合错误预期。

完成后请反馈：

1. 你新增的断言。
2. 通过与失败时的输出。
3. 为什么已经检查 HTTP 200，还要检查正文？

## 6. 常见问题

- `ConnectionError`：先检查服务是否运行、端口和地址是否一致。
- `ModuleNotFoundError`：检查是否使用项目 `.venv` 中的 Python，依赖是否安装。
- `collected 0 items`：检查运行目录、文件名和函数名。
- `AssertionError`：阅读失败行和实际响应，先确认需求与预期，再判断是服务或测试的问题。

当前是基础接口测试。Fixture、数据库和请求封装将在后续章节逐步加入。
