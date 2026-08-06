# 当前数据库设计

## 1. 存储职责

系统使用两类存储：

- **SQLite**：文档目录、状态机、会话、回答、引用、笔记、学习事件和生命周期操作的业务权威；
- **Qdrant**：文档分块向量与来源 payload，用于语义检索。

默认路径为 `data/docqa.sqlite3` 和 `data/qdrant`。当前不使用 Neo4j、PostgreSQL、Redis 或对象存储。

## 2. SQLite 运行设置

- `PRAGMA foreign_keys = ON`；
- `PRAGMA busy_timeout = 10000`；
- 文件数据库在支持时使用 WAL；
- schema 初始化和迁移完成后显式提交；
- 应用通过 `SQLiteMemoryStore` 集中访问。

## 3. 数据表

### `sessions`

| 字段 | 说明 |
|---|---|
| `session_id` | 会话主键 |
| `created_at` / `updated_at` | 创建与更新时间 |

### `documents`

| 字段组 | 说明 |
|---|---|
| `document_id` | 稳定主键；文档、向量、引用和生命周期的隔离键 |
| `document_name` / `source_path` | 展示名称和本地来源路径 |
| `format` / `content_hash` | `pdf` 或 `markdown`；内容去重依据 |
| `pages_with_text` / `source_unit_count` | PDF 文本页数或格式相关来源单元数 |
| `chunk_count` / `indexed_point_count` | 分块数与预期 Qdrant point 数 |
| `status` / `error_message` | 当前状态与脱敏错误信息 |
| `embedding_model` / `embedding_dimension` | 索引使用的模型与维度 |
| `source_locator_scheme` | PDF 或 Markdown 的定位契约版本 |
| `created_at` / `updated_at` | 创建与更新时间 |

规范状态：`pending`、`validating`、`parsing`、`indexing`、`indexed`、`failed`、`archived`、`deleting`、`deleted`、`restoring`、`inconsistent`。

`duplicate` 是注册操作结果，不是持久状态。

### `conversation_turns`

| 字段 | 说明 |
|---|---|
| `turn_id` | 回合主键 |
| `session_id` | 所属会话，删除会话时级联删除 |
| `turn_index` | 会话内顺序，和 session 唯一 |
| `question` / `answer` | 问题与回答文本 |
| `status` | `answered` 或 `no_results` |
| `model` / `created_at` | 回答模型与时间 |

### `citations`

| 字段组 | 说明 |
|---|---|
| `turn_id` / `citation_id` | 所属回合和回合内唯一引用 |
| `document_id` / `document_name` / `chunk_id` | 文档和分块标识 |
| `section` / `source_locator` | 人类可读与机器可用定位 |
| `page_start` / `page_end` | PDF 页码；Markdown 时允许为空 |
| `score` / `content` | 相似度和来源片段 |

初始化 SQL 兼容旧 PDF schema；启动迁移会把页码字段重建为可空，避免为 Markdown 伪造页码。

### `notes`

| 字段 | 说明 |
|---|---|
| `note_id` | 笔记主键 |
| `session_id` | 所属会话，删除会话时级联删除 |
| `turn_id` | 可选回答关联，回合删除时置空 |
| `document_id` / `source_locator` | 可选文档和来源关联 |
| `content` | 笔记正文 |
| `created_at` / `updated_at` | 创建与更新时间 |

文档归档、删除不会直接删除笔记；UI 必须保留历史关联语义，并避免把已删除文档显示为仍可检索。

### `learning_events`

记录回答生成、无结果、笔记等学习事件。`event_type + entity_id` 唯一，用于统计和报告，不作为问答数据源。

### `document_operations`

记录删除等生命周期操作的前后状态、Qdrant point 数、错误和完成时间，用于审计和失败恢复判断。

## 4. 关系与索引

- session 1:N conversation turns；
- turn 1:N citations；
- session 1:N notes；note 可选关联 turn 和 document；
- session 1:N learning events；
- document 1:N citations / notes / operations（应用层关系，未全部建立外键）；
- 按 session 时间、document 状态时间、content hash、citation document、note session/document、event session/type 建立索引。

## 5. Qdrant 数据契约

当前 collection 为 `docqa_text-embedding-v4_dim1024`。每个 point 至少包含：

- `document_id`；
- 文档名、格式和 `chunk_id`；
- 内容与来源定位；
- PDF 页码或 Markdown 章节、段落、行号；
- Embedding profile 所需元数据。

删除条件必须是精确的 `document_id` filter。禁止按文件名或不完整 hash 批量删除。

## 6. 生命周期事务边界

SQLite 和 Qdrant 无法形成单一 ACID 事务，删除流程采用补偿协议：

1. 读取文档与删除前 point 数；
2. SQLite 写入 operation 并将状态设为 `deleting`；
3. 按 `document_id` 删除 Qdrant points；
4. 验证删除后数量；
5. SQLite 将文档写为 `deleted`，point 数归零并完成 operation；
6. 失败时记录错误，恢复原状态；无法确认一致性时标记 `inconsistent`。

删除保留 SQLite tombstone、会话、历史引用和笔记；重新导入相同内容通过恢复/重新索引路径处理，不能静默创建第二套业务身份。

## 7. 归档、删除与恢复

| 操作 | SQLite | Qdrant | 用户可见语义 |
|---|---|---|---|
| 归档 | `indexed → archived` | 保留 points | 从默认可用范围退出，可取消归档 |
| 删除 | 保留 `deleted` tombstone | 删除该 document points | 需明确确认，可在条件满足时恢复 |
| 重新索引 | 更新统计和索引状态 | 重建该 document points | 保持 `document_id` 和定位语义 |
| 恢复 | `deleted → restoring → indexed` | 从源文件重建 | 源文件和内容身份必须可验证 |

## 8. 备份与测试

- 使用 SQLite backup API 生成一致性备份；
- 恢复步骤见 [备份与恢复](backup-recovery.md)；
- 生命周期、失败回滚和一致性测试必须使用临时 SQLite / Qdrant 或安全替身；
- 不允许为测试删除真实文档、真实数据库或真实 Qdrant points。

## 9. 数据风险

- 跨库操作是补偿一致性，进程中断可能留下 `deleting` / `restoring` / `inconsistent`；
- `source_path` 指向本地文件，移动或删除源文件会影响恢复；
- 当前没有生产级多副本、加密密钥管理、在线迁移或灾备演练；
- 真实生产故障演练未执行。
