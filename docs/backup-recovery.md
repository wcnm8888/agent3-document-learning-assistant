# 备份与恢复方案

## 需要保护的数据

- SQLite：`data/docqa.sqlite3` 及其运行时 WAL 状态。
- Qdrant：Docker 持久化卷或 Qdrant snapshot；v4 collection 必须单独标识。
- 原始材料：`data/reference/` 中获得授权的 PDF。
- 评测材料：`eval/questions.jsonl`、`eval/rubric.md` 和 `eval/results/`。
- 配置模板：`.env.example`；真实 `.env` 不进入备份仓库，密钥由独立密码管理器保存。

## SQLite 备份

优先使用 SQLite 在线备份能力或 `VACUUM INTO` 生成临时备份，再校验备份文件；不要在数据库写入期间只复制主文件而忽略 `-wal`。示例命令仅供运维执行，当前阶段不自动运行：

```powershell
E:\Agent\docqa-venv311\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect(r'data/docqa.sqlite3'); c.execute(\"VACUUM INTO 'data/docqa.sqlite3.backup'\"); c.close()"
```

项目提供等价的可复现 CLI，默认不覆盖已有目标文件：

```powershell
cd "E:\Agent\开发实践\Agent3-智能文档问答助手"
$env:PYTHONPATH="$PWD\src"
E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.cli backup-sqlite data/backups/docqa.sqlite3
```

只有明确指定 `--overwrite` 才允许覆盖同名备份。备份命令使用 SQLite 原生 backup API，并在完成后执行 `PRAGMA integrity_check`。

恢复后执行 `PRAGMA integrity_check`，确认表数量、会话数量、引用数量和报告统计与备份前记录一致。

## Qdrant 备份

生产或重要测试数据应使用 Qdrant 官方 snapshot API 或 Docker 持久化卷的受控备份。备份名称必须包含 collection、模型和维度，例如 `docqa_text-embedding-v4_dim1024`。恢复到隔离实例后先检查 collection 维度、点数和来源元数据，再允许应用连接；不得用 v3 collection 覆盖 v4 collection。

## 恢复顺序

1. 锁定应用版本和 `.env.example` 版本。
2. 恢复 Qdrant 到隔离实例并检查 1024 维、262 points（以备份时证据为准）和元数据完整性。
3. 恢复 SQLite，并执行完整性检查。
4. 恢复授权文档和评测材料。
5. 执行全量测试、healthz、最小事实问答和来源核对。
6. 通过验收后再切换应用配置；失败则保留隔离恢复实例并回滚应用版本。

## 保留策略

至少保留最近 3 个可读的 SQLite 备份、最近 2 个 Qdrant snapshot 和每次评测的摘要/报告。备份中不得包含 API Key、token 或未授权文档。
