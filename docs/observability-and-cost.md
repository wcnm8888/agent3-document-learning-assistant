# 可观测性与成本控制

## 最小事件字段

应用或外层运行器可记录：`timestamp`、`environment`、`operation`、`status`、`duration_ms`、`retry_count`、`session_id`、`turn_id`、`document_id`、`collection`、`model`、`dimension` 和 `error_type`。用户问题、回答全文、API Key、Authorization 和完整文档片段不得写入普通日志。

## 指标

- 可用性：Qdrant healthz、应用启动成功率、依赖连接失败数。
- 质量：检索命中率、来源准确率、无结果率、拒答准确率、引用完整率。
- 性能：Embedding/检索/DeepSeek 分阶段耗时、端到端耗时、超时数和重试数。
- 学习：会话数、问题数、回答数、无结果数、笔记数和文档数；统计事实继续以 SQLite 为准。
- 成本：Embedding 请求数和输入字符/Token 估算，DeepSeek usage、重试消耗和失败请求数。

## 脱敏与追踪

使用不可逆的 request/session/turn 标识关联一次请求，不记录密钥或完整请求头。第三方错误只保留状态码、错误类型、重试次数和脱敏后的短消息。

## 当前限制

项目当前没有集中式日志、指标后端和错误追踪服务，也没有成本告警。本文只定义字段和边界；在引入外部监控前，必须先确认数据保留、隐私和费用上限。
