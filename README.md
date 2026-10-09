# Pytest API Lab

[![API tests](https://github.com/hhui53758-cloud/pytest-api-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/hhui53758-cloud/pytest-api-lab/actions/workflows/tests.yml)

基于 **Pytest + Requests** 的接口自动化学习项目。以 FastAPI + SQLite 任务管理服务为测试对象，包含登录、任务 CRUD、权限、数据库核对、日志脱敏与 HTML 报告。

默认执行 **20 个独立测试场景**，数量按参数化展开后的 Pytest collected items 统计。

## 快速开始

需要 Python 3.12。克隆后进入仓库目录。

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe scripts/run_tests.py
.\.venv\Scripts\python.exe scripts/verify_redaction.py
```

macOS / Linux：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/run_tests.py
.venv/bin/python scripts/verify_redaction.py
```

测试会自动启动真实的本地 HTTP 服务，使用操作系统分配的空闲端口和临时 SQLite 数据库，结束后关闭服务。**无需手动启动 API，也不占用 8000 端口或修改演示数据库。**

报告：`reports/report.html`；日志：`logs/api-tests.log`。这两类运行产物不提交到 Git，GitHub Actions 中可从运行页面下载。

PyCharm 解释器请选择仓库内的 `.venv/Scripts/python.exe`。测试执行方式使用 Pytest，普通 Python 运行测试文件不会自动调用测试函数。

## 执行范围

以下命令在项目根目录执行，Python 需来自项目虚拟环境：

```bash
python -m pytest --collect-only -q
python -m pytest -v
python -m pytest -m smoke -v
python -m pytest -m regression -v
python -m pytest tests/test_tasks.py::test_update_task -v
python scripts/run_tests.py -m smoke
```

默认回归：20 个场景；冒烟：4 个场景。最后一个命令生成本次选择范围的报告，报告中的统计随执行范围变化。

## 框架结构

```text
app/                  FastAPI 业务接口、SQLite 存储
framework/            请求封装、配置、日志脱敏、数据库探针
config/settings.json  请求超时、两个公开演示账号
tests/conftest.py     临时服务、登录态、数据清理、日志 Fixture
tests/test_auth.py    登录用例
tests/test_health.py  健康检查
tests/test_tasks.py   CRUD、边界、权限、数据库一致性
scripts/              一键执行、脱敏检查、第一章请求脚本
docs/                 接口约定、20条清单、学习路线与简历模板
examples/             前两章的基础代码快照
.github/workflows/    GitHub Actions 自动测试
```

通信层返回原始 Response，业务断言留在测试层；数据库探针只读数据，测试准备和清理通过 API 完成。

Fixture 默认按函数隔离客户端，session 级别复用服务和演示登录令牌。每个用例创建的任务通过 task_factory 的 yield 清理。测试为串行模式，尚未适配 pytest-xdist 并行执行。

## 手动体验 API

```bash
python -m app.main
```

服务默认监听 `127.0.0.1:8000`。接口文档：<http://127.0.0.1:8000/docs>。

公开演示账号：

| 用户 | 密码 |
| --- | --- |
| alice | Alice123! |
| bob | Bob123! |

这些是本项目创建的演示数据。SQLite 存储密码哈希与令牌哈希，令牌有效期为 8 小时。任务接口需要 Bearer 认证。

手动运行使用 `data/demo.sqlite3`；可通过 `TASK_API_DB`指定本地演示数据库路径。测试请求超时默认 3 秒，可通过 `TASK_API_TIMEOUT` 覆盖。

本项目定位于本地学习和作品展示，未实现生产部署所需的注册、限流和会话管理。请求耗时日志用于定位，不等同于并发性能测试。

## 文档

- [接口约定](docs/api-contract.md)
- [20 个测试场景](docs/test-cases.md)
- [框架设计与排查](docs/architecture.md)
- [完整学习目录](docs/00-course-outline.md)
- [第三章：Fixture](docs/03-fixtures.md)
- [第四章：参数化与封装](docs/04-framework.md)
- [第五章：数据库与权限](docs/05-database-permissions.md)
- [第六章：日志与报告](docs/06-reporting.md)
- [第七章：独立验收](docs/07-delivery.md)
- [项目经历模板](docs/resume-project-template.md)

第一、二章讲义保留基础快照路径。完整框架已加入认证和自动环境管理，学习时按章节对应文件运行。

## CI

每次 push / pull request 在 Ubuntu + Python 3.12 上安装锁定依赖，执行测试、检查日志脱敏并保存报告。实际结果见顶部 Actions 徽章。

## License

MIT。
