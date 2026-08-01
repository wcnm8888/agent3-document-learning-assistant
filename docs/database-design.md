# SQLite 数据设计

## 目标

SQLite 只保存本地学习闭环数据，不保存 API Key、Token 或外部服务凭据。Qdrant 继续负责文档向量和分块来源，SQLite 负责会话、问答、来源快照、笔记、事件和统计查询。

## 表关系

```text
sessions
  ├─ conversation_turns
  │    └─ citations
  ├─ notes
  └─ learning_events
```

- `sessions`：会话生命周期和最近更新时间。
- `conversation_turns`：问题、回答、状态、模型和会话内顺序；`(session_id, turn_index)` 唯一。
- `citations`：回答时从 Qdrant 返回的来源快照，保存文档名、document_id、chunk_id、页码、source_locator、分数和片段内容。
- `notes`：学习笔记，可关联 session、turn、document_id 和 source_locator。
- `learning_events`：学习行为事件；`(event_type, entity_id)` 唯一，重复写入使用 `INSERT OR IGNORE`，避免重复统计。

## 事务和隔离

- 初始化时启用 `PRAGMA foreign_keys = ON`、`busy_timeout` 和文件数据库 WAL。
- 会话、问答及其来源在一个事务中写入；失败时整体回滚。
- 笔记关联的 document_id/source_locator 必须存在于当前会话已保存的引用中。
- 统计只读取 SQLite，不调用 LLM，报告事实可重复计算。

## 记忆边界

- 记忆按 `session_id` 隔离，默认最多读取最近 6 轮。
- 上下文默认最多 4000 字符，优先保留最近轮次，再按时间顺序传给问答服务。
- 历史对话仅用于指代消解，不作为回答事实证据；事实仍必须来自 Qdrant 检索片段。

## 数据生命周期

- 默认路径：`data/docqa.sqlite3`，已被 `.gitignore` 忽略。
- 真实验证使用：`data/phase4-validation.sqlite3`，仅为本地验证数据，不应提交。
- 当前阶段不提供物理删除接口，避免误删学习记录；后续如需清理，应先设计归档或 soft delete 策略。

## 多文档与 Markdown：Phase 1 迁移审查

### 当前 `documents` 表差距

当前表已有：`document_id`、`document_name`、`source_path`、`pages_with_text`、`chunk_count`、`indexed_point_count`、`status`、`error_message` 和 `updated_at`。它可以支撑现有 PDF 目录，但不能完整表达跨格式文档。

### 建议的新增字段

| 字段 | 语义 | 兼容策略 |
| --- | --- | --- |
| `format` | `pdf` 或 `markdown` | 既有行回填 `pdf` |
| `content_hash` | 原始文件字节 SHA-256 | 既有行回填为 `document_id` |
| `embedding_model` | 实际 Embedding 模型 | 既有行回填 `text-embedding-v4` |
| `embedding_dimension` | 向量维度 | 既有行回填 `1024` |
| `source_locator_scheme` | `pdf-page-v1` 或 `markdown-heading-line-v1` | 既有行回填 `pdf-page-v1` |
| `source_unit_count` | PDF 页或 Markdown 章节/内容单元数量 | 既有行按现有页数初始化 |
| `created_at` | 文档首次进入目录的时间 | 既有行回填 `updated_at` |

`document_id` 继续作为主键；`content_hash` 建议增加唯一索引以防止同一内容在目录中出现多份 canonical 记录。`document_name` 不作为唯一键，同名不同内容必须允许并存。

### 状态和事务

- canonical 文档状态使用 `pending`、`validating`、`parsing`、`indexing`、`indexed`、`failed`；
- `duplicate` 是一次上传/摄入操作结果，不把已有 canonical 文档改成 duplicate；
- 文档目录状态更新与索引报告写入应使用事务；Qdrant upsert 成功后再标记 indexed；
- Qdrant 失败时保留 failed 和错误摘要，不删除既有文档；
- 所有查询继续使用参数化 SQL，保留 `status, updated_at`、`content_hash`、`format` 等必要索引。

### 迁移方案（仅设计，不执行）

1. 备份当前 SQLite 文件并执行 `PRAGMA integrity_check`；
2. 新增可空或带默认值字段，避免破坏现有读取路径；
3. 按 document_id 回填既有 PDF 的格式、哈希、Embedding profile 和 locator scheme；
4. 校验非空、唯一性、外键、既有 sessions/citations/notes 读取；
5. 在新代码完全兼容后再收紧约束；
6. 失败时恢复备份，不执行 destructive down migration。

Phase 2 已完成迁移实现验证；Phase 3 复用现有加法迁移后的 `documents` 表更新文档索引状态和 point 数量，未执行新的 Schema 迁移。

### 来源快照兼容性

## Phase 2 迁移实现验证（2026-08-01）

- `SQLiteMemoryStore` 已实现对 `documents` 表的可重复加法迁移：`format`、`content_hash`、`embedding_model`、`embedding_dimension`、`source_locator_scheme`、`source_unit_count`、`created_at`。
- 旧 PDF 记录自动以 `document_id` 回填 `content_hash`，以原 `pages_with_text` 回填 `source_unit_count`，以 `updated_at` 回填 `created_at`。
- 已在临时 legacy SQLite 上验证迁移、重复打开和 `PRAGMA integrity_check=ok`；未对真实 `data/docqa.sqlite3` 执行迁移。
- 目录状态由 `DocumentCatalogService` 管理；`duplicate` 仅是操作结果，不写成 canonical 状态；本阶段不实现归档/删除。

现有 `citations.page_start/page_end` 需要在后续实现中改为可空，并增加 `format`、`section_path`、`paragraph_index`、`line_start` 和 `line_end`，以保存 Markdown 来源。迁移前必须保留既有 PDF 引用的可读性和恢复能力。

## Phase 3 数据目录使用说明

- 真实 PDF/Markdown 索引均写入 `documents` 目录；Markdown 的 `pages_with_text` 为 0，`source_unit_count` 记录解析单元数，格式和 locator scheme 分别保存为 `markdown` 与 `markdown-heading-line-v1`。
- 同内容重复索引不新增 canonical 文档，也不增加 Qdrant points；索引失败记录 `failed` 和脱敏错误摘要，不修改既有文档状态或向量。
- 本阶段未实现归档和删除，未修改真实学习会话、来源快照或生产数据。

## 文档生命周期管理设计（方向 B，规格阶段）

`documents.status` 扩展为 `archived`、`deleting`、`deleted`、`restoring`、`inconsistent`，保留既有状态；迁移必须是 additive。

新增 `document_operations` 记录 operation_id、document_id、operation_type、from_status、to_status、point_count_before、point_count_after、error_message、created_at、completed_at，作为恢复和审计依据，不保存文档正文、密钥或 token。

SQLite 事务只覆盖本地状态和操作日志；Qdrant 删除在事务间执行。删除前提交 `deleting`，Qdrant 成功并校验后提交 `deleted`；任一步失败都记录可恢复状态，不能把 SQLite/Qdrant 宣称为单一原子事务。turns/citations/notes/events 保留；新增关联必须拒绝 deleted/deleting/inconsistent 文档。

## Phase 4 UI 兼容补充（2026-08-01）

- Markdown 来源不具有 PDF 页码，因此 `citations.page_start` 和 `citations.page_end` 必须允许 `NULL`；PDF 引用仍保存实际页码。
- 初始化数据库时会检测旧版 `NOT NULL` 引用表，执行保留数据的兼容迁移后重建索引，并通过 `PRAGMA integrity_check` 验证。
- 引用读取逻辑对空页码保持 `None`，来源展示使用 Markdown 的章节、段落和行号 `source_locator`，不伪造页码。
