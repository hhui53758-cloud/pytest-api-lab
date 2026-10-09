# 第二章：任务接口的正常与异常测试

预计实操 25–30 分钟。目标：根据业务规则设计测试，学会 POST、JSON 请求体、资源 ID 和错误响应。

## 1. 本章接口约定

| 操作 | 请求 | 成功结果 | 异常结果 |
| --- | --- | --- | --- |
| 创建 | POST /tasks | 201，返回 id/title/status | 输入不符合规则时 422 |
| 查询 | GET /tasks/{task_id} | 200，返回任务 | 任务不存在时 404 |
| 删除 | DELETE /tasks/{task_id} | 204，没有正文 | 任务不存在时 404 |

- title 必填，字符串长度为 1–50 个字符，包含边界。这里按字符长度校验，不做首尾空格去除。
- status 只能是 pending、running、done；省略时默认为 pending。
- id 由服务生成，是从 1 开始递增的整数。测试必须使用创建响应返回的 ID，不能假定等于 1。
- 现在使用内存存储，重启服务后任务消失。登录、数据库将在后续加入。

这些状态码是本项目的接口约定，不表示所有系统必须使用相同状态码。

## 2. 重启服务

如果运行窗口里仍是旧的服务，先停止，重新运行 examples/chapter02/app.py。Python 服务未开启自动重载，保存文件不会让正在运行的旧进程自动更新。

在浏览器打开 http://127.0.0.1:8000/docs，应看到 POST、GET、DELETE 三个任务接口。

## 3. POST 与 JSON 请求体

GET 用来查询；本项目 POST 用来创建任务。创建需要把数据放入请求正文：

```python
payload = {"title": "学习 Pytest"}
response = requests.post(
    "http://127.0.0.1:8000/tasks", json=payload, timeout=3
)
```

payload 是 Python 字典。Requests 的 json 参数把它编码为 JSON，并设置 JSON Content-Type。不要把字典直接写进 URL。

成功响应的例子：

```json
{"id": 1, "title": "学习 Pytest", "status": "pending"}
```

id 是资源标识，用来定位刚创建的任务。每次测试的 ID 可以不同，因此读取 response.json()["id"]。

## 4. 状态码与业务断言

- 201 Created：创建了新资源。
- 200 OK：本项目查询成功。
- 204 No Content：操作成功，但没有正文。不要对 204 响应调用 .json()。
- 404 Not Found：本项目没有该任务。
- 422：本项目的请求输入未通过模型校验，例如空标题或非法状态。

除了状态码，正常测试还检查标题、默认状态和查询结果。异常测试还检查错误对应哪个字段。

```python
assert response.status_code == 201, response.text
```

逗号后的 response.text 是断言失败时的附加说明。成功时不报错；失败时显示响应正文，方便看出原因。

## 5. 测试设计方法

等价类：把预期行为相同的输入划为一组，例如允许的状态与不允许的状态。

边界值：检查规则边缘，例如标题长度 0、1、50、51。四个输入分别覆盖最小值外、最小值、最大值和最大值外。

业务链路：检查多个操作之间的关系。本章是创建→查询一致、删除→查询不存在。

代码先给出 5 条用例：创建查询、删除验证、空标题、非法状态、不存在任务。阅读时先找到输入、预期和断言，再看实现。

try/finally 用来清理测试创建的任务：try 中的断言失败，finally 仍会执行。下一章会用 Fixture 消除重复的准备与清理代码。

错误响应的 detail 是错误列表。其中 loc 表示错误位置，例如 ["body", "title"]。any(...) 表示列表里至少有一项满足条件。本章不强行断言整个错误文本，避免框架提示文案变化使测试无意义地失败。

## 6. 执行

在项目根目录的新终端执行：

```powershell
.\.venv\Scripts\python.exe -m pytest examples/chapter02/test_tasks.py -v
```

预期 5 passed。全部执行：

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

完整框架预期20 passed；本章快照独立执行预期5 passed。

## 7. 独立练习

新增 test_title_over_limit_is_rejected：

1. 用 "a" * 51 构造 51 字符标题。
2. 使用 POST /tasks 发出请求。
3. 按标题上限规则写状态码断言。
4. 运行这一条用例。

然后回答：为什么长度 50 和 51 都值得测？如果刚创建了任务，查询时能不能固定用 ID=1？

这是边界测试。这里的错误输入是需求明确禁止的输入，所以预期应该是接口正确拒绝它。
