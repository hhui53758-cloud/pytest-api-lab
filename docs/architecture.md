# 框架设计与故障排查

## 分层

1. app：被测业务。FastAPI 校验输入，SQLite 持久化并校验所有权。
2. framework：公共请求、环境配置、日志副本脱敏、SQL 只读核对。
3. tests：业务预期与断言。Fixture 管理环境、登录和资源生命周期。
4. scripts：一键运行和实际产物检查。
5. CI：在干净 Linux 环境复现执行。

测试使用 Requests 发出真实 HTTP 请求。Uvicorn 在线程中运行，绑定预先创建的空闲端口；不使用 FastAPI TestClient 绕过网络。

## 依赖顺序

test_environment(session) → 临时数据库和服务。

auth_tokens(session) → 两个测试账号的登录结果。

api_client(function) → 独立 Session；api_alice/api_bob 注入各自认证。

task_factory(function) → 创建任务并登记 ID → yield 后倒序清理。

db_probe(function) → 使用 SELECT 对比接口结果和业务持久化。

## 排查

- 401：确认登录状态、Authorization 头和令牌有效性。
- 403：确认请求用户与任务所有者，按需求判断是否正确拒绝。
- 422：检查 detail 中的 loc、输入规则及类型。
- 状态200但数据错误：对比业务字段与 SQLite，不仅检查状态码。
- 环境错误：确认编辑器使用 .venv，依赖版本与锁文件一致。
- collection error：检查导入、pytest.ini、函数与文件命名。
- teardown error：检查清理权限与状态；测试失败仍应尝试清理。

## 数据和日志

每轮使用新的临时数据库，保留演示数据与测试数据的边界。文件日志每轮覆盖；HTML报告随执行范围更新。

日志记录 case ID、路径、方法、状态、耗时和脱敏 JSON。原始请求不被脱敏函数修改，业务断言仍读取真实响应。非 JSON 正文仅记录类型说明。脱敏脚本检查当前报告和日志中没有演示密码或原始令牌。

暂未支持并行测试、外部生产地址或 CI 性能基线。
