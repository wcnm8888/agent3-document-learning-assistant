# 多文档与 Markdown 测试矩阵

本矩阵是 [测试策略](testing-strategy.md) 的领域附录。实现、独立 UI QA 和高保真视觉恢复均已完成；最近记录的全量基线为 95 项通过。

## 固定边界

- Embedding：`text-embedding-v4`；
- 维度：1024；
- collection：`docqa_text-embedding-v4_dim1024`；
- 文档身份：内容 hash 派生的稳定 `document_id`；
- 测试数据：临时 SQLite / Qdrant 或安全替身；真实 collection 只允许明确的只读检查。

## 解析与身份

| 编号 | 行为 | 预期 |
|---|---|---|
| MD-001 | Markdown ATX / Setext 标题 | section path 和层级正确 |
| MD-002 | 中文标题、段落和标点 | 内容非空，行号稳定 |
| MD-003 | 代码块、列表、表格 | 作为不可信文档数据保留，不执行 |
| MD-004 | HTML / script / 提示注入文本 | 不提升为系统指令 |
| MD-005 | 空 Markdown / 无效 UTF-8 | 明确失败，不写入空分块或 points |
| MD-006 | 不支持的扩展名 | 校验失败，不调用 Embedding |
| MD-007 | PDF 回归 | 文本页、分块、页码和 locator 语义不变 |
| MD-008 | document_id 稳定性 | 相同字节得到相同 ID，不依赖文件名 |
| MD-009 | 同名不同内容 | 不同 document_id，可并存 |
| MD-010 | 相同内容重复上传 | duplicate，不增加 points，不覆盖 canonical 文档 |
| MD-011 | 内容变化 | 新 document_id 和 chunk ID，不静默删除旧文档 |
| MD-012 | chunk_id 稳定性 | 相同内容、定位和 profile 得到相同 ID |

## 索引、检索与来源

| 编号 | 行为 | 预期 |
|---|---|---|
| MD-013 | Embedding profile 隔离 | 其他模型/维度不写入当前 collection |
| MD-014 | 指定文档范围 | 只返回目标 document_id |
| MD-015 | 全部文档范围 | 来源仍携带 document_id |
| MD-016 | 文档范围切换 | 清空当前回答、来源和待保存笔记；持久历史保留 |
| MD-017 | 来源元数据 | 文档、格式、chunk、locator 和适用定位完整 |
| MD-018 | Qdrant point 数 | 与非空 chunk 数一致 |
| MD-019 | Qdrant 写入失败 | 新文档失败不破坏既有文档和 points |
| MD-020 | 向量维度不匹配 | 明确失败，不写 points |
| MD-021 | PDF 来源 | 显示真实页码 |
| MD-022 | Markdown 来源 | 显示章节、段落和行号，不伪造页码 |
| MD-023 | 无检索结果 | 返回 no_results，不生成伪答案 |

## SQLite、会话和 UI

| 编号 | 行为 | 预期 |
|---|---|---|
| MD-024 | SQLite 加法迁移 | 旧会话/引用可读，integrity check 通过 |
| MD-025 | 重复目录写入 | 唯一约束和事务不产生重复 canonical 文档 |
| MD-026 | 解析/索引状态机 | 状态可追踪，失败信息可定位 |
| MD-027 | 搜索、筛选和排序 | 只改变文档列表，不改变问答范围 |
| MD-028 | 空、加载、成功、失败和禁用 | 三种视口有文字状态且可操作 |
| MD-029 | 长文件名、locator、document_id | 不产生页面级横向溢出；完整值可在详情访问 |
| MD-030 | 会话和笔记隔离 | 切换会话/文档不串用记录 |
| MD-031 | 桌面 1440×900 | 文档库、会话和检查器层级稳定 |
| MD-032 | 平板 1024×768 | 主工作区优先，导航/检查器可收缩 |
| MD-033 | 移动 390×844 | 单工作区、导航抽屉和上下文底部面板可用 |
| MD-034 | 密钥和文档指令泄漏 | 页面、日志、数据库、证据不暴露密钥；文档指令不成为系统指令 |

## 失败证据要求

每个失败用例应记录输入、预期状态、实际状态、失败阶段、脱敏错误摘要、SQLite/Qdrant 是否变化、恢复步骤和复现命令。API 调用成功不等于检索质量、回答质量或视觉验收通过。

生命周期归档、删除和恢复的详细用例见 [document-lifecycle-test-matrix.md](document-lifecycle-test-matrix.md)。
