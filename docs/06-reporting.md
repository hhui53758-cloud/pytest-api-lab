# 第六章：日志与 HTML 报告

阅读 framework/redaction.py、framework/client.py 和 scripts/run_tests.py。

执行 python scripts/run_tests.py，打开 reports/report.html。执行 python scripts/verify_redaction.py 检查本次实际产物。

logging.INFO 记录执行过程，ERROR 记录请求异常。CASE_START/CASE_END 对应用例；REQUEST/RESPONSE 对应方法、路径、状态和耗时。

脱敏针对日志副本，不能修改发送给接口的数据。password、Authorization、access_token等字段替换成[REDACTED]，嵌套结构也递归处理。原始令牌不写入日志。

通过、断言失败、Fixture或环境错误、跳过分别表示不同执行情况。报告中的通过率只针对本次执行范围，不代表需求覆盖率。请求耗时日志不是压力测试结果。

练习：
1. 在报告中找到一个参数化边界场景。
2. 从日志定位一次请求及返回。
3. 确认认证头已脱敏。
4. 说明日志文件被下一轮覆盖后，怎样保留一次重要排查证据。
