# 部署方案

## 结论

当前版本定位为个人、本地优先的文档学习助手。推荐部署拓扑是：

```text
本机 Python 进程（Gradio + 应用服务）
        │
        ├── Docker Qdrant：localhost:6333
        ├── 本地 SQLite：data/docqa.sqlite3
        └── 本地文档与评测目录：data/reference/、eval/
```

本文只描述本地优先部署方案，不授权执行部署。当前版本没有认证、多租户、限流和独立应用健康端点，因此不建议直接暴露到公网或作为多人生产服务。

## 环境边界

| 环境 | LLM/Embedding | Qdrant | SQLite | 密钥来源 | 目标 |
| --- | --- | --- | --- | --- | --- |
| local | 真实 API，可人工验证 | Docker 本地实例 | 本地文件 | 未提交的 `.env` | 开发和手工验收 |
| test | mock/fake provider 或受控测试凭据 | 临时隔离实例 | 临时目录 | CI Secret | 自动化测试，不写生产数据 |
| production（未启用） | Secret Manager 注入 | 独立实例或托管服务 | 单实例持久卷；多实例前需换存储 | Secret Manager | 当前版本禁止直接启用 |

不同环境必须使用不同 collection、数据库文件和数据目录。v4 生产 collection `docqa_text-embedding-v4_dim1024` 不得被评测或其他模型写入。

## 容器化决策

- 当前推荐：应用继续在本机 Python 虚拟环境运行，仅使用 Docker 运行 Qdrant。
- 已提供 `docker-compose.local.yml` 管理隔离的 Qdrant 和持久化卷；真实 HTTP healthz 由项目 `health` CLI 检查，不改变应用配置和 collection 名称。
- 暂不容器化应用：当前没有认证、反向代理、生产日志、迁移和多实例 SQLite 方案，应用容器化会掩盖这些交付风险。
- 生产前置条件：补齐认证/访问控制、Secret Manager、独立数据卷、可恢复备份、应用健康端点和并发存储方案。

## 部署前检查与回滚

部署前必须确认 Docker Engine、Qdrant healthz、collection 维度/点数、API 配置、SQLite 完整性、备份可读性和全量测试均通过。失败时停止发布，保留现有 v4 collection 和 SQLite 文件；回滚只切换到上一个已验证的应用版本和对应配置，不覆盖数据。

具体操作顺序见 `docs/operations-runbook.md`、`docs/backup-recovery.md` 和 `docs/release-checklist.md`。
