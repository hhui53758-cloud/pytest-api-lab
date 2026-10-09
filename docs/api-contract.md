# 接口约定

## 认证

POST /auth/login，JSON 请求体为 username/password。演示用户见 README。正确凭据返回 200、access_token、token_type=bearer；错误凭据返回 401。后续请求携带 Authorization: Bearer <token>。

## 任务

| 方法 | 路径 | 说明 | 成功 |
| --- | --- | --- | --- |
| POST | /tasks | 创建 | 201 |
| GET | /tasks/{id} | 查询 | 200 |
| PUT | /tasks/{id} | 替换标题与状态 | 200 |
| DELETE | /tasks/{id} | 删除 | 204，空正文 |

输入 title 必填，1–50 个字符，按原始字符长度校验；status 为 pending/running/done，省略时 pending。额外字段或不合法输入返回 422。PUT 使用完整写入语义，省略 status 会设为 pending。

成功的任务对象包含 id、user_id、title、status。未认证返回 401；任务不存在返回 404；操作其他用户任务返回 403。GET /health 不需要认证，返回 200、status=ok、service=task-api。

所有任务操作都检查所有权。测试不假定用户 ID 或任务 ID 固定为某值；ID=0 被用作保证不存在的资源。

## 数据一致性

分别验证 HTTP 状态、返回字段和数据库结果。前两者是接口行为检查，数据库结果用于验证持久化与副作用，不能统称为三重数据一致性。
