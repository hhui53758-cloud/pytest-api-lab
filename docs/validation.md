# 验证记录

日期：2026-10-09。

本地环境：Windows、Python 3.12.7，依赖版本见 requirements-lock.txt。

- 完整场景：20 passed。
- 冒烟选择：4 passed，16 deselected。
- 独立执行更新用例：1 passed。
- 再次全量执行：20 passed，临时数据库与自动服务重新创建。
- 日志与HTML报告检查：没有演示密码或原始令牌，包含脱敏占位符与耗时记录。
- pip check：无依赖冲突。

这些结果对应当前代码与本地环境，不代表并发性能或全量安全认证。GitHub Linux执行状态见Actions页面。

运行命令见README；报告与日志可在本地生成或下载CI产物。
