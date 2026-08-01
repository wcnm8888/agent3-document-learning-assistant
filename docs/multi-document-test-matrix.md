# 多文档与 Markdown 知识库管理测试矩阵

> Phase 1 设计产物。当前 Phase 2、Phase 3 和 Phase 4 已完成对应实现验证；Phase 5 独立 QA 尚未执行。

## 测试边界

- 默认 Embedding：`text-embedding-v4`；
- 向量维度：1024；
- Qdrant collection：`docqa_text-embedding-v4_dim1024`；
- 文档身份：原始文件字节 SHA-256；
- 文档隔离：`document_id`；
- 文档生命周期：不测试归档/删除；
- 真实数据：优先使用临时 SQLite/Qdrant，现有 v4 collection 只做只读回归。

## 测试矩阵

| 编号 | 风险/行为 | 层级 | 预期证据 |
| --- | --- | --- | --- |
| MD-001 | Markdown ATX/Setext 标题识别 | 单元 | 正确生成 section_path 和层级 |
| MD-002 | 中文标题、段落和标点 | 单元 | 内容非空，行号保持稳定 |
| MD-003 | 代码块 | 单元 | 代码作为文档数据，保留原始行范围，不执行 |
| MD-004 | 列表和嵌套列表 | 单元 | 内容完整，章节和行号可追溯 |
| MD-005 | 表格 | 单元 | 表格内容可检索，定位不丢失 |
| MD-006 | HTML/script/提示注入文本 | 单元/安全 | 原样作为不可信文档数据，不执行、不提升为系统指令 |
| MD-007 | 空 Markdown | 单元 | 明确 failed，不能写入空分块 |
| MD-008 | 无效 UTF-8 | 单元 | 明确解析错误，不伪造 indexed |
| MD-009 | 只有空白或 HTML 的文件 | 单元 | 无非空内容时 failed |
| MD-010 | 非 PDF/Markdown 扩展名 | 单元/UI | 明确格式校验错误，不调用 Embedding |
| MD-011 | PDF 回归 | 集成 | 171 页、262 分块、页码和现有 locator 不变 |
| MD-012 | document_id 生成 | 单元 | 相同字节得到相同 ID，不依赖文件名 |
| MD-013 | 同名不同内容 | 集成 | 得到不同 document_id，可并存 |
| MD-014 | 相同内容重复上传 | 集成 | duplicate 结果，points 不增加，canonical 文档不被覆盖 |
| MD-015 | 内容变化 | 集成 | 新 document_id，新 chunk ID，不删除旧文档 |
| MD-016 | chunk_id 稳定性 | 单元 | 相同内容、定位和 profile 得到相同 ID |
| MD-017 | Embedding profile 隔离 | 集成 | v3/其他维度不得写入 v4 collection |
| MD-018 | 多文档过滤 | 集成 | 指定 document_id 只返回目标文档 |
| MD-019 | 全部文档范围 | 集成 | 明确 all-documents scope，来源仍带 document_id |
| MD-020 | 文档切换 | 服务/UI | 回答、来源、待保存笔记和上下文清空，历史数据保留 |
| MD-021 | 来源元数据 | 集成 | 文档名、格式、document_id、chunk_id、章节、适用页码/行号、locator 完整 |
| MD-022 | Qdrant point 数量 | 集成 | point 数量与非空 chunk 数量一致 |
| MD-023 | Qdrant 失败恢复 | 集成 | 新文档失败不破坏既有文档和 points |
| MD-024 | 向量维度不匹配 | 集成 | 明确失败，不写入 points |
| MD-025 | SQLite 迁移兼容 | 数据库 | 备份、回填、integrity_check、既有会话/引用读取均通过 |
| MD-026 | SQLite 重复写入 | 数据库 | 唯一约束和事务不产生重复 canonical 文档 |
| MD-027 | 解析/索引状态机 | 服务 | pending、validating、parsing、indexing、indexed、failed 状态可追踪 |
| MD-028 | UI empty/loading/success/error | UI | 三种视口下状态文案和组件可用 |
| MD-029 | 长 locator 和长文件名 | UI | 换行/折叠，不横向溢出 |
| MD-030 | 密钥和文档指令泄露 | 静态/人工 | 日志、页面、数据库、评测结果不出现密钥；文档指令不成为系统指令 |

## 阶段执行顺序

1. Phase 2（已完成）：完成 MD-001～MD-017 的解析、目录和索引验证；
2. Phase 3（已完成）：完成 MD-018～MD-025 的检索、隔离和迁移验证；
3. Phase 4（已完成）：完成 MD-020、MD-028、MD-029 的文档库 UI 验收；补充 PDF/Markdown 上传、范围切换和 Markdown 行号来源测试；
4. Phase 5（后续）：使用真实 PDF、项目自有 Markdown 和故意损坏文件完成剩余质量复核，并由独立视角复核。

## 失败证明要求

每个失败用例必须记录：输入文件、预期状态、实际状态、失败阶段、错误摘要、是否写入 Qdrant、是否改变 SQLite、恢复步骤和可复现命令。不得把“API 调用成功”当作检索或回答质量通过。
