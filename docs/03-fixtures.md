# 第三章：Fixture 与登录状态

阅读 tests/conftest.py，再看 tests/test_tasks.py。

Fixture 是由 Pytest 管理生命周期的依赖。测试函数声明同名参数，Pytest 找到并执行 Fixture，将返回或 yield 的对象传入测试。

session 生命周期：一次 Pytest 执行复用，例如 test_environment 和 auth_tokens。function 生命周期：每个用例新建，例如 api_client 和 task_factory。

yield 前准备，yield 后清理。task_factory 返回可调用的创建函数；它登记成功创建的 ID，在用例结束后删除，即使断言失败也会进入清理。

登录态不是“登录一次就全局生效”，它通过 Bearer 请求头绑定到对应客户端。Alice 和 Bob 使用不同 Requests Session，避免认证信息串用。

练习：
1. 只执行 test_update_task，确认无需先执行创建用例。
2. 连续执行两次，说明 ID 为什么可以不同。
3. 解释删除用例的清理为何允许 404。
4. 说明把 api_client 改成 session scope 可能引入什么共享状态。
