# 初版架构

> 本文件前部的 Phase 2～8 模块说明来自原单 PDF 产品基线；当前多文档任务 Phase 2 的解析协议、Markdown parser、统一文档模型和文档目录实现补充见本文后部。当前阶段状态以 `docs/project-management/current-task.md`、`roadmap.md` 和 `implementation-plan.md` 为准。

```text
Gradio UI
  -> Application Services
     -> Document Ingestion Service
        -> MarkItDown / parser -> chunker -> Embedding -> Qdrant
     -> Q&A Service
        -> query embedding -> Qdrant -> context/citations -> DeepSeek
     -> Learning Service
        -> MemoryTool / SQLite -> notes, events, statistics
```

## 模块边界

- UI 只负责输入、展示和状态，不直接依赖 Qdrant、Neo4j 或底层 Tool。
- 文档摄入服务负责解析、分块、哈希、幂等和索引状态。
- 问答服务负责检索、来源、提示词和回答结构。
- 学习服务负责会话、事件、笔记和报告。
- Qdrant 保存文档片段向量和元数据。
- SQLite 保存文档、会话、问题、笔记和索引任务状态。
- Neo4j 暂不进入第一版核心路径。

## Phase 2 实际模块

- `src/doc_qa/pdf_parser.py`：pypdf 页级解析、文档哈希、章节线索和错误分类。
- `src/doc_qa/chunker.py`：页感知、字符上限、重叠和非空分块。
- `src/doc_qa/embedding.py`：复用 `hello-agents==0.2.0` 的 `DashScopeEmbedding`，显式固定模型、维度和批大小。
- `src/doc_qa/qdrant_index.py`：Qdrant URL/Docker 与本地持久化适配、collection 维度检查、稳定 point ID、元数据验证。
- `src/doc_qa/ingestion.py`：编排解析 → 分块 → Embedding → upsert → 状态验证。
- `src/doc_qa/cli.py`：单 PDF 索引命令，不承担问答或 UI 职责。

## Phase 3 实际模块

- `src/doc_qa/qdrant_index.py`：在不改变 Phase 2 索引流程的前提下提供 `query_points`、Top-K、分数阈值和 `document_id` 过滤。
- `src/doc_qa/deepseek.py`：DeepSeek OpenAI 兼容 Chat Completions 适配、JSON 输出、错误透明度和有限重试。
- `src/doc_qa/qa.py`：编排查询向量化、检索、上下文构建、回答解析和引用校验；许可证/授权/版权类问题使用受限术语扩展和关键词重排，仍只使用 Qdrant 实际返回分块作为证据。
- `src/doc_qa/models.py`：检索命中、引用和回答响应结构。
- `src/doc_qa/cli.py`：新增 `ask` 命令，暂不承担 UI 职责。

## Phase 4 实际模块

- `src/doc_qa/memory_store.py`：SQLite schema、事务、外键、WAL、会话、问答来源、笔记、事件和统计查询。
- `citations.page_start/page_end` 对 Markdown 允许为空；初始化时兼容迁移旧版 `NOT NULL` 引用表并保留既有数据。
- `src/doc_qa/learning.py`：编排会话上下文、Phase 3 问答、问答持久化、笔记和报告，不直接依赖 UI。
- `src/doc_qa/qa.py`：支持受限会话上下文；历史只用于指代消解，文档片段仍是事实来源。
- `src/doc_qa/cli.py`：新增 `session-create`、`ask-session`、`history`、`note-create`、`note-update`、`notes`、`stats` 和 `report` 命令。

SQLite 的详细表关系和数据边界见 `docs/database-design.md`。

## Phase 5 实际模块

- `src/doc_qa/ui.py`：Gradio 适配层，负责输入、展示、事件绑定和状态转换，不承载检索、索引、LLM 或 SQL 业务逻辑。
- `UIController.index_document` → `DocumentIngestionService`：上传 PDF、解析、分块、Embedding、Qdrant upsert 和文档目录状态。
- `UIController.ask` → `LearningService` → `QuestionAnswerService`：会话上下文、查询 Embedding、Qdrant 检索、DeepSeek 回答、来源持久化和学习事件。
- `UIController.save_note/update_note/refresh_stats` → `LearningService`/`SQLiteMemoryStore`：笔记、事件、统计和确定性报告。
- Gradio 状态通过 `gr.State` 维护 session、turn 和 source locator；移动端通过 CSS 将三栏布局折叠为纵向布局，并将来源区域放到内容末尾。
- 文档目录元数据持久化在 SQLite `documents` 表中，向量仍只存储在既有 Qdrant collection 中。

Phase 2 使用 pypdf 直接读取 PDF，而不是直接调用 `RAGTool.add_document`：页码是本阶段的硬性来源字段，直接读取可以保留页级边界；后续仍可在适配层替换解析器。

## 关键数据隔离

至少使用 `user_id`、`knowledge_base_id`、`document_id`、`chunk_id` 和 `embedding_profile` 进行隔离和追踪。

## 重要决策

Embedding 不能混用。v3 与 v4 必须分别使用不同 collection 或完成明确迁移。回答必须保留引用所需的文档名、页码、章节和 chunk 元数据。
## Phase 6 评测隔离边界

v3/v4 评测在 collection 层完全隔离：v4 继续服务现有应用，v3 仅写入 `docqa_text-embedding-v3_dim1024_eval`。评测 runner 在执行前后检查 collection 维度、point 数量和来源元数据；模型名、维度和 collection 不匹配时直接失败，不自动迁移或删除数据。

## Phase 7 运行拓扑

交付准备阶段采用本地优先拓扑：Gradio 应用运行在 Python 进程，Qdrant 运行在 Docker `docqa-qdrant`，SQLite 和授权文档保存在本地持久化目录。应用不直接暴露数据库端口，默认只监听 `127.0.0.1`。

生产拓扑暂不启用。原因是当前版本没有认证、限流、独立应用健康端点和多实例 SQLite 存储方案；若未来部署，必须使用独立 Qdrant/SQLite 数据边界、Secret Manager 和可恢复备份。

## Phase 8 运维入口

- `doc_qa.cli health`：只读检查配置、Qdrant healthz、v3/v4 collection 和 SQLite 完整性，失败时返回非零退出码。
- `doc_qa.cli backup-sqlite`：使用 SQLite 原生 backup API 创建一致性备份，并校验备份文件。
- `docker-compose.local.yml`：只管理 Qdrant，不管理应用容器，不自动连接生产。

## 多文档与 Markdown 知识库管理：Phase 1 设计

### 统一数据协议

采用三层边界，避免 PDF 页模型直接污染 Markdown：

```text
DocumentSource
  -> DocumentUnit
     -> DocumentChunk
        -> Embedding -> Qdrant payload
```

`DocumentSource` 表示文件身份和索引配置：

- `document_id`：原始文件字节的 SHA-256；
- `document_name`、`format`、`source_path`、`content_hash`；
- `embedding_profile`：固定 `text-embedding-v4:1024`；
- `source_locator_scheme`：`pdf-page-v1` 或 `markdown-heading-line-v1`。

`DocumentUnit` 表示可定位的原始内容单元：

- `section_path`、`section`、`paragraph_index`；
- `line_start`、`line_end`；
- PDF 可填写 `page_start`、`page_end`，Markdown 保持为空；
- `content`。

`DocumentChunk` 表示用于向量化的稳定片段：

- 继承文档身份和来源定位；
- 增加 `chunk_id`；
- payload 必须包含 `format`、`embedding_profile`、`source_locator_scheme` 和适用的页码/行号字段。

### 解析适配器

- PDF adapter 复用现有 `pypdf` 页级解析和现有 PDF source_locator 兼容格式；
- Markdown adapter 采用保留原始行号的块解析策略，识别嵌套标题、段落、代码块、列表和表格；
- HTML/script 只作为文档数据保留或转义展示，不执行、不改变系统 Prompt；
- `DocumentParser` 统一返回 `DocumentSource` 和 `DocumentUnit`，不让 Qdrant 或 UI 依赖具体 parser。

### 摄入和索引边界

`DocumentIngestionService` 扩展为统一入口，负责：

```text
validate -> parse -> normalize -> chunk -> embed -> upsert -> verify -> catalog update
```

解析器、分块器和 Embedding provider 通过适配器注入；Qdrant upsert 只接受统一 `DocumentChunk`。同一 v4 collection 通过 `document_id` 和 `embedding_profile` 隔离，不按文档创建 collection。

### 问答和切换边界

- `QuestionAnswerService` 继续负责查询 Embedding、Qdrant 检索、来源和回答；
- 指定文档时必须使用 Qdrant `document_id` filter；全部文档时必须显式传入知识库范围语义；
- UI 切换文档范围时清空当前回答、来源、待保存笔记和会话上下文，历史记录仍由 SQLite 保留；
- 不直接采用 `hello-agents` 的 `RAGTool` 作为业务入口，因为其 advanced search 默认包含 MQE/HyDE、返回字符串且不满足当前结构化引用和严格范围契约；如复用，仅限适配器内部并需单独验证。

### 失败和回滚

- validating、parsing、indexing 任一阶段失败只标记当前文档失败，不删除或覆盖已有 points；
- 重复内容返回 duplicate 操作结果，canonical 文档保持 indexed；
- Qdrant 写入前必须完成维度、collection、metadata 和 document_id 校验；
- SQLite 迁移和真实多文档验证优先使用临时数据库/临时 collection，基准 v4 collection 只做只读回归。

### Phase 1 设计时的未实现项（历史记录）

## Phase 2 实现补充（历史完成记录，2026-08-01）

- 已落地 `DocumentSource -> DocumentUnit -> ParsedDocument -> DocumentChunk` 的解析侧协议。
- `DocumentParser` 按扩展名分派 `PdfParser` 和 `MarkdownParser`；PDF 继续使用原有页级解析与分块，Markdown 使用章节、段落和原始行号定位。
- `DocumentIngestionService.parse_document()` 与 `parse_and_chunk()` 只做解析/分块，不调用 Embedding 或 Qdrant；既有 `index_pdf()` 行为保持兼容。
- `DocumentCatalogService` 通过 SQLite 管理文档元数据和 canonical 状态；Phase 2 未执行真实 Schema 文件迁移，仅在初始化时对临时 SQLite 做可重复加法迁移验证。

本节保留 Phase 1 设计阶段的边界说明；Markdown parser、统一摄入入口和多文档 catalog 已在后续 Phase 2/3 落地，UI 扩展仍留待 Phase 4。

## 多文档与 Markdown 任务：Phase 3 实现补充（2026-08-01）

- `DocumentIngestionService.index_document()` 是 PDF/Markdown 统一真实索引入口；`index_pdf()` 作为兼容包装。
- 真实数据流为：`DocumentParser → PageAwareChunker → EmbeddingProvider(text-embedding-v4/1024) → QdrantIndexer → DocumentCatalogService`。
- `QdrantIndexer` 在同一 v4 collection 上提供按 `document_id` 的 point 计数和检索过滤；未为文档创建独立 collection。
- 重复索引通过稳定 `chunk_id` 识别已有 points，只对缺失 chunk 调用 Embedding；重复操作返回 duplicate。
- 历史 point 只允许通过 `set_payload` 补齐格式、哈希、Embedding profile 和 locator scheme，不重建向量、不改变 point ID。
- `DocumentScopeState` 是 UI 无关的范围状态边界；切换文档或全部文档范围时清空临时上下文、来源和待保存笔记，Phase 4 已接入 Gradio。

## 文档生命周期管理设计（方向 B，规格阶段）

- `DocumentLifecycleService` 负责归档、删除、恢复、重新索引和一致性检查；UI 只传递 document_id、确认标志和操作结果。
- SQLite 记录保留 tombstone；`archived` 不删除 Qdrant，`deleted` 要求 document_id 精确过滤后 points 为 0。
- 删除采用 `deleting` 中间态和操作日志，外部 Qdrant 操作失败恢复原状态；最终 SQLite 提交失败进入 `inconsistent`，不得伪造成功。
- 历史 turns、citations、notes 和 learning events 保留，删除后禁止新增该文档的来源关联。

## 多文档与 Markdown 任务：Phase 4 UI 实现补充（2026-08-01）

- `UIController.index_document()` 支持 `.pdf`、`.md` 和 `.markdown`，通过 `DocumentIngestionService` 和 `DocumentCatalogService` 完成索引与状态反馈。
- 文档库展示格式、短 document_id、状态、页数或 Markdown 单元数、分块、points、定位方案、更新时间和脱敏错误。
- 问答范围支持“全部文档”和指定 `document_id`；切换范围会清空当前回答、来源、待保存笔记和临时会话上下文，但保留 SQLite 中的历史数据。
- 来源展示保留 PDF 页码，Markdown 使用章节/段落/行号；`Citation.page_start/page_end` 允许为空，避免伪造 Markdown 页码。
- UI 只通过摄入、学习和问答服务访问数据；Gradio CSS 覆盖 1440×900、1024×768 和 390×844 的三栏/纵向布局。
