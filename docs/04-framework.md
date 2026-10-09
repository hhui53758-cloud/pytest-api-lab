# 第四章：参数化与请求封装

阅读 framework/client.py、framework/config.py、pytest.ini 和标题边界用例。

参数化复用测试逻辑，输入数据分别产生独立场景。ids 给场景稳定名称，避免密码等敏感输入出现在报告用例名中。

marker 是分类标签。smoke 选择核心链路，regression 选择完整回归；它不负责替换输入数据。使用 -m smoke 选择标签，用 -k 选择名字。

ApiClient 负责 Session、地址拼接、Bearer 认证、超时和脱敏日志，保留 Response 交给测试断言。业务规则仍位于用例，不在公共客户端中硬编码201或200。

练习：
1. 执行 -m smoke，预期4条。
2. 独立新增标题49字符场景，说明 collected 数量怎样改变。
3. 找出 timeout 配置和环境变量覆盖位置。
4. 解释客户端为什么不自动把401和422当作程序异常抛出。
