# 文档生命周期规格

## 状态机

```text
pending → validating → parsing → indexing → indexed
                                      └──────→ failed
indexed ↔ archived
indexed/archived → deleting → deleted
                    └──────→ inconsistent
deleted → restoring → indexing → indexed
```

- `indexed`：默认可检索、可作为新笔记来源。
- `archived`：保留 SQLite 和 Qdrant points，默认列表/检索排除；历史来源仍可展示。
- `deleting`：删除流程中的保护态，禁止问答、笔记关联和并发索引。
- `deleted`：SQLite tombstone；Qdrant 不应存在该 `document_id` points，历史数据只读。
- `inconsistent`：跨存储操作未完成，需要一致性检查或从源文件恢复，默认不可检索。
- `restoring`：从 tombstone 恢复的中间态，只有源文件存在且哈希匹配/重新索引成功后才回到 `indexed`。

`duplicate` 继续作为一次索引操作结果，不是 canonical 文档状态。

## 归档与删除

归档是可逆的业务可见性操作，不触碰 Qdrant；删除是受保护的数据清除操作，删除 points 但保留 SQLite tombstone。默认文档列表和检索只包含 `indexed`，详情页可查看 `archived`、`deleted` 和 `inconsistent`。

## Qdrant 删除条件

只允许使用当前 collection、当前 `document_id` payload filter：

```text
collection = docqa_text-embedding-v4_dim1024
must payload.document_id == requested_document_id
```

禁止按文档名、路径或模糊内容删除；删除前记录 point 数，删除后重新 count 并执行 payload 校验。collection/维度不匹配直接失败。

## SQLite 事务边界

1. 事务 A：锁定文档，校验状态和关联保护，写入 `deleting` 与操作日志并提交。
2. 外部步骤：调用 Qdrant 精确删除；失败则事务 B 将状态恢复为原状态并记录失败原因。
3. 事务 C：校验 points 为 0 后写入 `deleted`、清理可变索引计数并提交。
4. 若事务 C 提交失败，保留 `deleting`/`inconsistent`，不伪造 `deleted`；一致性检查负责发现，恢复流程从源文件重新索引。

SQLite 与 Qdrant 无法共享原子事务，因此不能承诺物理意义上的跨系统瞬时原子性；产品承诺的是：失败不静默丢状态、既有文档不会被误删、异常有可恢复标记和人工可验证路径。

## 笔记、引用和会话历史

- `conversation_turns`、`citations`、`notes` 和学习事件不级联删除；它们是历史证据。
- 删除后历史来源仍显示“文档已删除”，保留原始 locator 和内容快照。
- 删除后禁止新建指向该文档的笔记；已有笔记允许编辑正文，不允许改变其文档归属。
- 会话历史不跨文档迁移，恢复后仍使用原 `document_id`。

## 恢复、误删与重导入

- 删除必须由服务层要求 `confirm=True`，UI 还需二次确认文案。
- `deleted` 记录保留哈希和原路径；同内容重导入默认返回 tombstone/需要显式恢复，不新建重复 canonical 记录。
- 恢复要求源文件可读且内容哈希与 tombstone 一致；文件内容变化时走“新内容重新索引”审查，不覆盖旧 tombstone。
- 删除失败优先恢复原状态；无法恢复时进入 `inconsistent`，阻止检索并提示执行一致性检查/恢复。

## 一致性检查

对每条 `indexed`/`archived` 记录比较 SQLite `indexed_point_count` 与 Qdrant 按 `document_id` count，并检查 point payload 的 document/chunk 元数据；`deleted` 必须为 0 points；`deleting`/`inconsistent` 必须报告异常而不是自动隐藏。
