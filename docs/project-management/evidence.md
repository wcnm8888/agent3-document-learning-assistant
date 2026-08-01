# 项目证据归档

> 文档说明：本文前部的原单 PDF Phase 0～8 和旧任务状态均为历史证据；当前多文档与 Markdown 任务卡状态以本文后面的 Phase 4 证据及 `current-task.md` 为准。

## 仓库

> 当前权威状态（2026-08-01）：多文档与 Markdown 任务卡 Phase 2、Phase 3、Phase 4、Phase 5、Phase 6 已完成。真实浏览器问答、来源展开、笔记创建/更新、文档切换、三种视口复验和全量质量门禁均已通过；Gradio 上传进度 404 记录为非阻塞依赖风险。本文前部“尚未进入业务实现”的描述属于 Phase 0/1 历史证据。

## Phase 5 独立 QA 最终证据（2026-08-01）

- 浏览器入口：`http://127.0.0.1:7861/`；Gradio 版本 5.50.0。
- PDF：重复上传并索引 `Happy-LLM-0727.pdf`，页面返回 duplicate，262 个分块、262 个 points；事实问题回答成功，来源页码为 6，locator 可追溯。
- Markdown：重复上传并索引 `phase3-multidocument-guide.md`，页面返回 duplicate，5 个分块、5 个 points；回答来源包含章节和 `lines=11-11`，页码字段为空。
- 文档切换：从 PDF 切换至 Markdown 时，当前回答、来源、待保存笔记和临时上下文清空；持久化会话和笔记仍保留。
- 笔记链路：浏览器完成一条笔记的创建和更新；切换到新会话后当前会话笔记列表为空，证明会话范围隔离。
- 缺陷修复：点击“新会话”后补充清空 `source_summary`，避免来源 JSON 已清空但摘要仍显示旧来源；`tests/test_phase5_ui.py` 新增回归测试。
- 截图：`output/playwright/phase5-qa-1440x900.png`、`phase5-qa-1024x768.png`、`phase5-qa-390x844.png`；三种尺寸均无横向溢出。
- 自动化门禁：全量 pytest 67 项通过；compileall、`git diff --check`、`doc_qa.cli health`、Qdrant healthz HTTP 200 和 SQLite integrity_check 通过。
- 非阻塞风险：浏览器控制台仍出现 Gradio `upload_progress?upload_id=undefined` 404，但文件上传、重复索引和页面状态均成功；不把该日志标记为“完全无风险”。

## DeepSeek 空响应修复证据（2026-08-01）

- 真实 API 配置：模型为 `deepseek-v4-flash`，有效思考模式为 `disabled`；不记录 API Key。
- 修复前：响应出现 `finish_reason=length`，`message.content` 为空而 `reasoning_content` 非空，适配器重试耗尽后报空响应。
- 修复后：真实适配器连续 3 次最小调用均返回非空内容；`doc_qa.cli ask "Happy-LLM 的内容分为哪两个部分？"` 返回 `answered`，引用第 6 页及对应 `source_locator`。
- 自动化：Phase 3/Phase 5 定向测试 23 项通过，新增默认关闭思考模式和截断空响应错误透明度测试。
- 已完成：浏览器中的真实 PDF/Markdown 问答、来源展开、笔记创建/更新和三种视口复验；Gradio 内部上传进度 404 仍需后续版本隔离升级验证。

## Phase 6 全量质量门禁与交付收口（已完成，2026-08-01）

- 任务卡旧的 Phase 5 阻塞状态已统一；独立 QA 已标记完成，Git 提交/PR/CI 保持未执行并等待负责人单独确认。
- 全量 pytest 67 项通过；compileall、`git diff --check`、敏感信息扫描通过。
- `doc_qa.cli health` 返回 `status=ok`；Qdrant healthz HTTP 200；SQLite `integrity_check=ok`。
- v4 collection `docqa_text-embedding-v4_dim1024` 为 267 points、1024 维，其中 PDF 262、Markdown 5；全部 point 使用 `text-embedding-v4:1024`，必需来源元数据完整。
- v3 collection `docqa_text-embedding-v3_dim1024_eval` 保持 262 points、1024 维且与 v4 隔离；本轮未修改 v3 或 v4 points。
- 本阶段不重新执行旧单 PDF v3/v4 评测，不切换 Embedding，不部署、不提交、不推送。

- 项目工作目录：`E:\Agent\开发实践\Agent3-智能文档问答助手`
- 上游源码目录：`E:\Agent\hello-agents-upstream`
- 获取方式：通过 Git 获取 Datawhale `hello-agents` 的 main 分支。
- 项目目录将建立独立的本地 Git 基线，不与上游仓库共享 Git 历史。

## 基准 PDF

- 文件：`data/reference/Happy-LLM-0727.pdf`
- 页数：171
- 文本提取：成功
- 质量观察：部分页面抽取文本出现重复字符，需要在文档转换阶段验证标题、代码和表格保真度。

## 代码定位

- `code/chapter8/11_Q&A_Assistant.py`：示例助手和 Gradio UI。
- 示例通过 `MemoryTool.run` 和 `RAGTool.run` 调用能力。
- 文档说明中部分示例使用 `execute`，与当前代码存在接口表述差异，需以后以安装包实际 API 为准。

## 早期 Phase 0/1 规划记录（已被当前审计覆盖）

- Phase 0/1 没有连接真实 DeepSeek、百炼、Qdrant 或 Neo4j。
- Phase 0/1 没有运行第八章完整示例。
- 项目没有宣称真实问答或 UI 验收通过。

## 多文档与 Markdown 知识库管理：Phase 0 基线审计（2026-08-01）

- Git：当前分支为 `main`，基线提交为 `b121f09 chore: initialize intelligent document QA project`；工作区存在既有未提交修改，本阶段未覆盖、重置、提交或推送。
- 依赖：`hello-agents==0.2.0`、`qdrant-client==1.18.0`；安装包 API 为 `RAGTool(knowledge_base_path, qdrant_url, qdrant_api_key, collection_name, rag_namespace)`、`RAGTool.run(parameters)`、`MemoryTool(user_id, ...)` 和 `MemoryTool.run(parameters)`。
- 上游示例：`E:\Agent\hello-agents-upstream\code\chapter8\11_Q&A_Assistant.py` 是单 PDF 示例，使用 `MemoryTool`、`RAGTool` 和 Gradio，未提供本项目所需的文档目录、`document_id` 隔离、Markdown 来源定位和可验证多文档切换闭环。
- 基准 PDF：`data/reference/Happy-LLM-0727.pdf` 存在，171 页均有可提取文本，SHA-256 为 `1b96edb5cb7be57b14ceba1733f5f6a74c94c972769457c3f504952064034713`。
- Qdrant：`docqa-qdrant` 正常运行；healthz 返回 HTTP 200；`docqa_text-embedding-v4_dim1024` 为 green、262 points、1024 维。
- 配置：当前实际环境使用 `text-embedding-v4`、1024 维、`http://localhost:6333`；本地 `.env` 中配置项已存在，但本证据不记录任何密钥值；本地 Qdrant API Key 为空。
- 解析与索引差异：`PdfParser` 仅接受 `.pdf`，`PageAwareChunker` 只处理页号，`DocumentIngestionService` 只有 `index_pdf`，`DocumentChunk.payload()` 只生成 PDF 页码式 `source_locator`。
- 文档目录差异：SQLite `documents` 表已有 `document_id`、文档名、路径、页数、分块数、point 数、状态、错误和更新时间，但缺少格式、哈希、Embedding profile、章节/行号等跨格式字段。
- 隔离差异：`QdrantIndexer.search(..., document_id=...)` 和 `QuestionAnswerService.ask(..., document_id=...)` 已支持精确过滤；当前 UI 默认仍允许“全部文档”，Phase 1 需要定义全部知识库范围与指定文档范围的验收语义。
- UI 差异：`UIController.index_document` 和 Gradio `File` 当前只允许 PDF；不存在 Markdown 上传、Markdown 状态展示和章节/行号来源展示。
- 测试：`E:\Agent\docqa-venv311\Scripts\python.exe -m pytest tests -q` → 45 passed；现有 `test_ui_rejects_non_pdf_upload_without_calling_services` 明确记录当前 PDF-only 行为，后续规格确认后应替换为新的格式矩阵。

## Phase 0 审计结论

- Phase 0 完成定义满足：Git、依赖、运行环境、现有能力、差异和停止条件均有证据。
- Phase 0 未实现 Markdown、多文档索引或 UI 扩展；未修改 Schema、Qdrant collection、真实数据或业务代码。

## 多文档与 Markdown 知识库管理：Phase 1 规格证据（2026-08-01）

- 读取依据：Vibe Coding 操作协议、SDD、任务卡、架构、UI、数据库、质量门禁和风险方法论，以及项目当前任务、路线图、进度、架构、技术栈、设计规格、数据库设计、相关源码和 Phase 2～5 测试。
- 统一协议：确定 `DocumentSource → DocumentUnit → DocumentChunk` 三层模型，PDF 继续使用页码，Markdown 使用章节路径、段落序号和起止行号，Markdown 不伪造页码。
- Markdown locator：确定 `document_name#section=<encoded_section_path>&paragraph=<n>&lines=<start>-<end>&chunk=<chunk_id>`；无标题内容使用根文档；代码块、列表、表格和 HTML 保留为不可信文档数据。
- 身份和幂等：确定 `document_id/content_hash=SHA-256(原始文件字节)`；同内容重复上传返回 duplicate 操作结果，不增加 points；同名不同内容允许并存。
- chunk ID：确定由 document_id、稳定定位、规范化内容和 `embedding_profile=text-embedding-v4:1024` 生成；point ID 继续由 chunk_id 派生。
- Qdrant：确定所有 PDF/Markdown 共用 `docqa_text-embedding-v4_dim1024`，通过 document_id 和显式 all-documents scope 隔离；不创建文档级 collection，不混入其他模型/维度。
- 状态机：确定 canonical 文档状态为 pending、validating、parsing、indexing、indexed、failed；duplicate 只表示一次摄入结果，不覆盖已索引文档状态。
- SQLite 审查：确定新增 format、content_hash、embedding_model、embedding_dimension、source_locator_scheme、source_unit_count、created_at 的 additive migration 方向；迁移前备份、回填和完整性校验，Phase 1 不执行 Schema 变化。
- UI 影响：确定支持 PDF/Markdown 上传、格式/页数或章节行号展示、duplicate/failed 状态和范围切换；切换时清空当前回答、来源、待保存笔记和上下文，历史数据保留。
- 测试矩阵：新增 `docs/multi-document-test-matrix.md`，包含 30 个用例，覆盖解析、格式、身份、幂等、隔离、Qdrant、SQLite、UI 和安全风险。
- 文档状态：`current-task.md`、`roadmap.md`、`progress.md`、`architecture.md`、`design-spec.md`、`implementation-plan.md`、`database-design.md`、`decisions.md` 和任务卡已同步 Phase 1 设计状态。
- 本阶段未执行：业务代码、测试代码、SQLite Schema、真实数据库、Qdrant collection、真实配置、原始 PDF 和外部服务写入。

### Phase 1 质量门禁

- 全量回归：`E:\Agent\docqa-venv311\Scripts\python.exe -m pytest tests -q` → 45 passed；
- 文档差异：`git diff --check` → 通过；Git 仅报告工作区既有换行符提示；
- 文档完整性：任务卡、当前任务、路线图、进度、证据、架构、设计、实现计划、数据库设计、决策和测试矩阵文件均存在并已回读；
- 业务变更隔离：本阶段没有修改业务代码、测试、Schema、真实配置、Qdrant collection、原始 PDF 或真实 SQLite 数据。

## Phase 2 实施证据

- Python 环境：`E:\Agent\docqa-venv311`，`hello-agents==0.2.0`、`qdrant-client==1.18.0`、`pypdf==5.9.0`、`pytest==8.4.2`。
- API 审计：`hello_agents.memory.embedding.DashScopeEmbedding` 接受显式 `model_name`，默认值仍为 `text-embedding-v3`；项目适配器显式使用 v4，不做隐式回退。
- 代码检查：`pytest tests -q` → 12 passed；`python -m compileall src tests` → 通过；`git diff --check` → 通过。
- 真实 PDF 解析：`Happy-LLM-0727.pdf`，171 页有文本，262 个非空分块，文档 SHA-256 为 `1b96edb5cb7be57b14ceba1733f5f6a74c94c972769457c3f504952064034713`。
- 本地 Qdrant 闭环：使用真实 PDF 和本地持久化 Qdrant，首次 262 分块 → 262 points；重复执行 existing 262、最终仍 262 points；metadata_complete=true、idempotent_replay=true。
- 真实 Embedding 配置：`.env` 已配置 `EMBED_API_KEY`，实际模型为 `text-embedding-v4`，批大小为 10，向量维度为 1024；密钥未写入项目文档或日志。
- Docker Qdrant：容器 `docqa-qdrant` 运行正常，`http://localhost:6333/healthz` 返回 HTTP 200，collection 状态为 green。
- 真实 CLI 首次索引：171 页、262 个非空分块、262 个 points，`metadata_complete=true`。
- 真实 CLI 重复索引：同一 PDF 再次执行后仍为 262 个 points，`existing_chunk_count=262`、`idempotent_replay=true`。
- 真实索引命令：`$env:PYTHONPATH='E:\Agent\开发实践\Agent3-智能文档问答助手\src'; E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.cli index E:\Agent\开发实践\Agent3-智能文档问答助手\data\reference\Happy-LLM-0727.pdf`。
- 历史失败记录：在配置 API Key 前，CLI 曾因缺少凭据退出码 1；该记录用于证明缺少凭据时会明确失败，不代表当前状态。

## Phase 2 完成结论

- Phase 2 的真实 Embedding、Docker Qdrant、索引数量、来源元数据和重复索引幂等验收全部通过。
- v3/v4 召回质量、速度和成本对比尚未执行，属于路线图 Phase 6，不阻塞 Phase 2。
- 检索质量评测尚未执行，属于 Phase 3 及后续评测范围，不在 Phase 2 完成定义内。

## 多文档与 Markdown 任务卡 Phase 2 证据（2026-08-01）

- Git：执行前确认 `main` 分支、基线 `b121f09`，保留工作区已有用户改动；未提交、未推送。
- Markdown：新增 `tests/test_phase2_multidocument.py`，覆盖标题层级、段落、代码块、列表、表格、中文、HTML/script 不执行、空内容、无效 UTF-8、稳定身份和行号定位。
- 统一协议：新增 `DocumentSource`、`DocumentUnit`、`ParsedDocument`，扩展 `DocumentChunk` 的格式、哈希、章节路径、行号、定位方案和 Embedding profile 元数据。
- PDF 回归：`Happy-LLM-0727.pdf` 仍解析为 171 个有文本页面和 262 个非空分块；既有 PDF locator 与 chunk ID 未改变。
- SQLite：旧 `documents` 表在临时数据库中完成可重复加法迁移，`PRAGMA integrity_check` 返回 `ok`；真实 `data/docqa.sqlite3` 未被修改。
- 目录：临时 SQLite 验证 `DocumentCatalogService` 的 created、duplicate、failed 状态和错误记录。
- 测试：本任务定向测试 9 项通过；全量 `pytest tests -q` 为 54 项通过；`compileall src tests` 已通过。
- 边界：本任务 Phase 2 未调用真实 Embedding、未写入 Qdrant，未进入多文档真实索引、检索隔离或 UI 扩展。

## 原单 PDF 项目 Phase 3 当前证据（历史基线）

- Qdrant 客户端：`qdrant-client==1.18.0`，使用 `query_points`，未使用不存在的旧式 `search` API。
- DeepSeek 适配：OpenAI 兼容接口，默认 `https://api.deepseek.com`，默认模型 `deepseek-v4-flash`。
- 代理复现修复：新增 `DEEPSEEK_TRUST_ENV`，默认值为 `false`；DeepSeek 使用显式 `httpx.Client(trust_env=False)`，标准命令不再依赖本机隐式 SOCKS/HTTP 代理。
- 真实查询检索：使用真实 `text-embedding-v4`/1024 查询向量访问 Docker Qdrant，命中 5 个真实来源片段。
- 来源字段验证：返回文档名、document_id、chunk_id、章节、页码和 source_locator。
- 自动化测试：`pytest tests -q` → 21 passed；`python -m compileall src tests` → 通过；`git diff --check` → 通过。
- 运行环境验证：Docker 容器 `docqa-qdrant` 状态为 `running`，`http://localhost:6333/healthz` 返回 HTTP 200。
- 真实 DeepSeek 验证：标准 `doc_qa.cli ask` 命令成功调用 `deepseek-v4-flash`，未输出或记录 API Key。
- q001 明确事实题：回答覆盖 Transformer、预训练、LLaMA2、微调、RAG/Agent；默认 Top-K=5 已返回第 1、6 页的有效证据，按评测标准使用 `--top-k 10` 复核后返回第 1、2 页，满足“引用第 2 页”的验收要求。
- q011 跨章节归纳题：回答覆盖 NLP → Transformer → 预训练模型 → LLM → 训练实践 → RAG/Agent，来源定位到第 2、3、6 页。
- q015 无答案拒答题：明确说明文档没有 DeepSeek API Key，未猜测真实密钥，引用第 165 页的占位符说明。
- q020 文档外问题：返回 `status=no_results`、`retrieved_count=0`、空引用，未调用 DeepSeek。
- 失败场景验证：自动化测试覆盖查询 Embedding 失败、Qdrant 不可用、DeepSeek 503/401、向量维度不匹配和 DeepSeek 失败时不生成伪答案。

## 原单 PDF 项目 Phase 3 完成结论（历史基线）

- Phase 3 完成定义满足：真实 v4 查询、Docker Qdrant 检索、真实 DeepSeek 回答、来源引用、文档外拒答和失败透明度均有证据。
- 真实基准只作为最小收口集，不等同于完整检索质量评测；30 条评测集、v3/v4 对比和人工规模化评估保留到后续质量阶段。
- MQE、HyDE、MemoryTool、笔记、统计、Neo4j 和 UI 均未实现，符合本阶段范围。

## Phase 4 实施证据

- SQLite 模块：`src/doc_qa/memory_store.py`；学习编排：`src/doc_qa/learning.py`。
- 数据表：`sessions`、`conversation_turns`、`citations`、`notes`、`learning_events`。
- 数据库策略：外键开启、文件库使用 WAL、busy timeout 10 秒、问答和来源在事务中写入；事件使用 `(event_type, entity_id)` 唯一约束和 `INSERT OR IGNORE`。
- 记忆策略：按 session_id 隔离，默认最近 6 轮、最多 4000 字符，优先保留最近轮次；历史不作为事实证据。
- 笔记策略：笔记可关联 session、turn、document_id 和 source_locator；文档和来源必须存在于当前会话的真实引用快照中。
- CLI 入口：`session-create`、`ask-session`、`history`、`note-create`、`note-update`、`notes`、`stats`、`report`。
- 自动化测试：`pytest tests -q` → 26 passed；`python -m compileall src tests` → 通过；`git diff --check` → 通过。
- 真实验证库：`data/phase4-validation.sqlite3`，未写入 API Key，已被 `.gitignore` 忽略。
- 真实问答：使用 Happy-LLM PDF、真实 `text-embedding-v4`/1024、Docker Qdrant 和 `deepseek-v4-flash` 完成 `ask-session`，返回 `answered`、4 条来源引用和页码/source_locator。
- 真实持久化：重新打开 SQLite 后恢复 1 条会话问答、4 条引用和 1 条笔记；`PRAGMA integrity_check` 返回 `ok`。
- 真实笔记：创建并更新 1 条笔记，关联基准 PDF 的 document_id 和第 2 页 source_locator。
- 真实统计：session_count=1、question_count=1、answered_count=1、note_count=1、document_count=1；报告统计字段与直接统计结果一致。
- 事件验证：真实报告包含 `session_created`、`question_asked`、`answer_generated`、`note_created`、`note_updated` 事件类型。

## Phase 4 完成结论

- Phase 4 完成定义满足：会话记忆、问答持久化、来源保存、笔记、学习事件、统计报告和数据库重开验证均完成。
- Phase 4 未实现 UI、Neo4j、MQE、HyDE 和多模态能力，符合阶段范围。
- `data/phase4-validation.sqlite3` 是本地验证产物，不应提交；如后续不再需要，删除前需单独确认。

## Phase 5 实施证据（历史阶段）

- 环境：Gradio `5.50.0`；启动命令：`E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.ui`，并设置项目 `src` 为 `PYTHONPATH`。
- 构建证据：`tests/test_phase5_ui.py` 5 项通过，Gradio Blocks 构建包含文档库、会话、问答、来源、笔记和统计组件；`compileall` 和 `git diff --check` 通过。
- 全量回归：`E:\Agent\docqa-venv311\Scripts\python.exe -m pytest tests -q`，31 项通过。
- 页面可达：`http://127.0.0.1:7860` 返回 HTTP 200，页面标题为“文档学习助手”。
- 真实 PDF 页面操作：上传 `Happy-LLM-0727.pdf` 后显示 processing 状态；完成后显示 171 页、262 个分块、262 个 points，文档目录状态为 `indexed`。
- 真实问答页面操作：问题“Happy-LLM 的内容分为哪两个部分？”返回“基础知识与实战应用”，引用 `Happy-LLM-0727.pdf` 第 6 页，`source_locator` 为 `Happy-LLM-0727.pdf#page=6&chunk=46beb5c86a3a1d98c3cde3a2d24549576a6c99a4d964dd0bed96254e807ef178`。
- 真实笔记页面操作：创建并更新同一条笔记；统计刷新后显示 `session_count=2`、`question_count=1`、`answered_count=1`、`note_count=1`、`document_count=1`，报告中的统计一致。
- 会话隔离：点击“新会话”后显示新的 session_id，问答记录、来源和笔记列表为空，旧会话内容未串入。
- 响应式截图：`output/playwright/phase5-empty-1440x900.png`、`phase5-empty-1024x768.png`、`phase5-empty-390x844.png`、`phase5-indexed-stats-1440x900.png`。
- 浏览器控制台观察：Playwright 文件选择流程记录 `upload_progress?upload_id=undefined` HTTP 404；不影响文件上传、索引完成、问答和笔记流程，列为 Gradio 版本风险。

## Phase 5 完成结论（历史阶段）

- Phase 5 完成定义满足：Gradio UI、业务服务调用边界、状态覆盖、真实 PDF 操作、响应式视口检查和回归测试均有证据。
- 历史记录：在 Phase 5 收口时，Phase 6 的 v3/v4 质量评测尚未执行；后续 Phase 6 已完成技术执行，最新结论见本文末尾。
## Phase 6 初次质量评测证据（历史记录，已被最新结果覆盖）

- 评测入口：`eval/run_embedding_comparison.py`。
- 原始结果：`eval/results/embedding-v3-v4-summary.json`。
- 报告：`eval/results/embedding-v3-v4-report.md`。
- PDF：171 页、262 个非空分块，SHA-256 为 `1b96edb5cb7be57b14ceba1733f5f6a74c94c972769457c3f504952064034713`。
- v3：`text-embedding-v3`、1024 维、`docqa_text-embedding-v3_dim1024_eval`、262 points。
- v4：`text-embedding-v4`、1024 维、`docqa_text-embedding-v4_dim1024`、评测前后均为 262 points，元数据完整。
- v3 自动结果：检索命中率 100.0%、来源自动准确率 80.0%、答案自动正确率 30.0%、拒答自动准确率 66.7%、平均 4048ms、失败 0。
- v4 自动结果：检索命中率 90.0%、来源自动准确率 76.7%、答案自动正确率 36.7%、拒答自动准确率 100.0%、平均 3594ms、失败 1（q011，DeepSeek 返回空内容）。
- 评测请求无 Embedding 重试；两套 v3/v4 向量未混用；结果和文档未包含 API Key。
- 质量结论：建议保留 v4 为默认模型，但 Phase 6 尚未满足全部完成定义，原因是远程回答失败和人工质量评分未完成。
## Phase 6 最新收口证据（2026-07-31）

- DeepSeek 空响应根因：空响应在原实现中直接抛出 `DeepSeekApiError`，未进入已有 HTTP/网络重试分支。
- 修复后：空响应按 `max_retries` 有限重试；重试耗尽返回 `DeepSeek API returned empty content after retries`；新增测试并通过。
- q011 真实验证：`answered`，引用页码 2、3、6，来源包含完整 `document_id`、`chunk_id` 和 `source_locator`。
- 最新完整评测 v3：30 题、失败 0、检索命中率 100.0%、来源自动准确率 83.3%、答案自动正确率 53.3%、拒答自动准确率 77.8%、Embedding 重试 0、DeepSeek 重试 0、平均 3487ms。
- 最新完整评测 v4：30 题、失败 0、检索命中率 96.7%、来源自动准确率 86.7%、答案自动正确率 60.0%、拒答自动准确率 100.0%、Embedding 重试 0、DeepSeek 重试 0、平均 3503ms。
- v4 collection 评测前后均为 262 points、1024 维、元数据完整；v3 collection 为 262 points、1024 维、元数据完整。
- 逐题证据复核文件：`eval/results/embedding-v3-v4-manual-review.md`。q016–q017 已通过第 4 页真实来源验证，q023–q028 的严格文档范围政策已确认。
- 当前质量结论：技术失败门禁、来源引用门禁和项目负责人人工确认均已通过；Phase 6 完成。

## Phase 7 交付准备证据（2026-08-01）

- Git 基线：当前分支为 `main`，基线提交为 `b121f09 chore: initialize intelligent document QA project`；工作区已有用户修改，本轮未覆盖、提交或推送。
- 运行入口：Gradio `5.50.0`，`python -m doc_qa.ui`，默认 `127.0.0.1:7860`；CLI 入口保持兼容。
- 依赖边界：Python 3.11.0rc2 虚拟环境、`hello-agents==0.2.0`、真实 v4 1024 维、Docker Qdrant、SQLite 本地文件。
- 配置边界：`.env.example` 不含真实密钥；真实密钥只允许存在本地未提交 `.env`，生产应迁移到 Secret Manager；日志规则禁止输出密钥、Authorization 和完整文档内容。
- 文档交付：新增部署、运行、备份恢复、可观测性/成本文档，更新 README、环境模板、架构、技术栈、决策和项目管理文档。
- 容器评估：推荐本地 Python 应用 + Docker Qdrant；暂不增加完整应用容器或公网部署。
- 运行状态更新：Docker Desktop 已恢复；`docqa-qdrant` 正常运行，`http://localhost:6333/healthz` 返回 HTTP 200；v3/v4 collection 均为 green、262 points、1024 维。
- 禁止项确认：未部署、未连接生产、未修改生产配置、未删除文件、未切换 v4、未提交、未推送。

## Phase 8 实施证据（已完成）

- 新增 `docker-compose.local.yml`：只定义 Qdrant、6333/6334 端口和持久化卷，不定义应用容器；真实 HTTP healthz 由 `health` CLI 验证。
- 新增 `doc_qa.cli health`：健康报告包含 `configuration`、`qdrant`、`qdrant_collection` 和 `sqlite` 检查；不输出 API Key 或 Token。
- 新增 `doc_qa.cli backup-sqlite`：使用 SQLite 原生 backup API，执行备份后 `PRAGMA integrity_check`。
- 新增测试：配置缺失、collection 缺失、Qdrant 不可用、SQLite 损坏、健康报告脱敏、备份恢复和防止意外覆盖，共 7 项。
- 真实 `.env` health CLI 已返回 `ok`；v3/v4 均为 green、262 points、1024 维，SQLite integrity check 为 `ok`。
- 真实 v4 smoke test 已通过：使用 `text-embedding-v4` 查询、现有 Docker Qdrant 和 DeepSeek 返回 `answered`，来源为 Happy-LLM 第 6 页。
- Phase 8 最终全量质量门禁和文档状态收口已完成。

## 多文档与 Markdown 任务：Phase 3 实施证据（2026-08-01）

- 执行前基线：Git 分支为 `main`，保留工作区既有修改；`docqa-qdrant` 运行中，`/healthz` 返回 HTTP 200；v4 collection 为 green、262 points、1024 维。
- 代码入口：`DocumentIngestionService.index_document()` 统一支持 PDF/Markdown；`index_pdf()` 保持兼容；CLI `index` 已支持两种扩展名。
- 目录状态：真实索引流程接入 `DocumentCatalogService`，状态依次经过 validating、parsing、indexing，成功写入 indexed，Embedding/Qdrant 失败记录 failed。
- 幂等策略：重复索引只 Embedding 缺失的 chunk；相同 Markdown 第二次执行返回 `status=duplicate`、`existing_chunk_count=5`、`idempotent_replay=true`。
- 真实 Markdown：`data/reference/phase3-multidocument-guide.md` 的 SHA-256/document_id 为 `0c5f775548e58615a6bd8dfb422f8370ffc3d00cf17c75c712ed7ba47bd54c74`；真实 `text-embedding-v4`、1024 维生成 5 个非空 chunk 并写入同一 v4 collection。
- 真实索引结果：首次 Markdown 索引前 collection 为 262 points，之后为 267 points；重复执行仍为 267 points；Markdown 文档目录状态为 indexed、point 元数据完整。
- 历史 PDF 兼容：原有 262 个 PDF points 未重建向量、未改变 point ID，仅通过 Qdrant payload 补齐 `format`、`content_hash`、`embedding_profile` 和 `source_locator_scheme`；补齐数量为 262，随后 PDF metadata_complete=true。
- 指定范围验证：PDF `document_id` 范围返回 20 个结果且全部属于 PDF；Markdown `document_id` 范围返回 5 个结果且全部属于 Markdown。
- Markdown 定位验证：Markdown 返回结果的 `page_start/page_end` 均为空，`source_locator` 均包含 `lines=`；PDF 继续保留页码 locator。
- 全部文档范围验证：limit=300 返回 267 个结果，包含 PDF 和 Markdown 两个 document_id，未发生串库。
- 自动化验证：Phase 2/3/4/5/6/8 全量测试共 59 项通过；`compileall src tests` 通过；`git diff --check` 通过（仅有既有换行符提示）。
- Phase 3 阶段未执行：Phase 4 UI 扩展、Markdown UI 上传、归档/删除、Neo4j 和生产部署；Phase 4 UI 已在后续阶段完成。

## 多文档与 Markdown 任务 Phase 3 完成结论

- Phase 3 的真实 PDF/Markdown 索引、同一 v4 collection、document_id 范围隔离、全部文档范围、幂等和元数据完整性已通过验证。
- 失败隔离和状态机已有自动化测试；真实外部服务失败不在本轮重复制造，保留测试注入验证。
- 该阶段完成后经负责人确认进入 Phase 4 UI；本节不代表当前阶段状态。

## 方向 A Gradio 版本隔离证据（2026-08-01）

- 5.50.0 与 5.49.1 的真实 Markdown 上传均记录 `GET /gradio_api/upload_progress?upload_id=undefined` 404；文件选择流程完成。
- 6.22.0 启动时在 `Chatbot(type="messages")` 抛出不兼容异常，构成回归；未进入稳定环境。
- 结论：未发现可安全切换的 v5 修复版本；该问题继续作为已复现的非阻塞依赖风险，不标记为已修复。

## 方向 B 设计证据（2026-08-01）

- 规格文件：`docs/document-lifecycle-task-card.md`、`document-lifecycle-spec.md`、`document-lifecycle-test-matrix.md`。
- 已明确 archived 不删 points、deleted 保留 SQLite tombstone、Qdrant 按 document_id 精确删除、历史关联保留、失败进入可恢复状态。
- 本阶段未删除真实文件、SQLite 记录或任何 Qdrant points。

## 方向 B/C 实现证据（2026-08-01）

- 方向 B：临时 Qdrant 验证归档保持 points、删除后 document_id points 为 0；SQLite 保留 deleted tombstone 和 document_operations；注入 Qdrant 失败后原 indexed 状态保持。UI 已提供归档、取消归档、删除确认和重新索引恢复入口。
- 方向 B：生命周期测试 5 项通过；测试路径均为临时 SQLite/Qdrant，未连接当前真实 v4 collection。
- 方向 C：document_rows 支持文档名/document_id 搜索、PDF/Markdown 和状态筛选、更新时间/名称排序；详情展示格式、hash、Embedding、定位方案、计数和脱敏错误。
- 真实 UI：新页面在 1440x900、1024x768、390x844 三种视口加载成功，未见横向溢出或新增控制台错误；PDF/Markdown 问答、来源、笔记和范围隔离沿用既有 Phase 5 证据，未因本轮查询层改动回归。

## 多文档与 Markdown 任务 Phase 4 UI 证据（2026-08-01）

- 代码范围：`src/doc_qa/ui.py`、`src/doc_qa/models.py`、`src/doc_qa/qa.py`、`src/doc_qa/learning.py`；测试范围：`tests/test_phase5_ui.py`。
- Gradio 版本：5.50.0；启动方式：`E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.ui`；本地页面返回 HTTP 200。
- 文档库真实页面显示已有 PDF 和 Markdown；上传 `data/reference/phase3-multidocument-guide.md` 后返回“重复文档，未新增向量”，Markdown 5 个分块、collection 267 points、`text-embedding-v4/1024`。
- 文档范围下拉真实显示“全部文档”、Happy-LLM PDF 和 Markdown 文档；切换 Markdown 范围后页面显示范围已切换，并清空当前回答、来源和临时上下文。
- UI 定向测试：7 项通过；相关 Phase 3/Phase 4 回归测试通过；完整测试结果以最终门禁命令为准。
- 响应式截图：`output/playwright/phase4-ui-1440x900.png`、`output/playwright/phase4-ui-1024x768.png`、`output/playwright/phase4-ui-390x844.png`。
- 人工验收观察：三种尺寸均无页面横向溢出；移动端按文档库、问答、来源/笔记纵向排列；长 document_id 在表格中缩略显示，完整值仍保留在范围选择和来源数据中。
- 浏览器控制台出现 Gradio 上传进度接口 `upload_progress?upload_id=undefined` 的 404 日志，但不影响文件上传、重复索引和页面状态更新；记录为 Gradio 版本级非阻塞风险。

## 多文档与 Markdown 任务 Phase 4 结论

Phase 4“文档库 UI 与问答切换”完成定义满足；下一步为 Phase 5 独立 QA，需负责人确认后执行。

### Phase 4 最终修复证据

- 根因：旧版 SQLite `citations.page_start/page_end` 使用 `NOT NULL`，Markdown 引用没有 PDF 页码，真实问答保存时失败。
- 修复：初始化时检测旧表约束，迁移为允许空页码的兼容表，保留既有 citation 行；读取引用时对空页码保持 `None`，不执行 `int(None)`。
- 自动化验证：旧 schema 迁移、Markdown 引用保存与重新读取测试通过；SQLite `PRAGMA integrity_check` 返回 `ok`。
- 真实浏览器验证：Markdown 问答成功，回答状态为 `answered`，来源包含章节、段落和 `lines=`，`page_start/page_end` 显示为 `null`；未伪造页码。
- 最终质量门禁：全量 `pytest` 64 项通过，`compileall`、`git diff --check`、Qdrant healthz 200、v3/v4 collection 健康检查和敏感信息扫描通过。

## Phase 5 独立 QA 最终证据（2026-08-01）

- Git：当前分支为 `main`，工作区存在既有修改；本轮未重置、删除、提交或推送。
- 本地服务：`docqa-qdrant` 正常运行，healthz 返回 HTTP 200；v4 collection 为 267 points、1024 维，PDF 262 points、Markdown 5 points，v4 payload 必需元数据完整。
- 自动化门禁：全量 pytest 67 项通过；compileall、`git diff --check`、敏感信息扫描和 `doc_qa.cli health` 通过。
- 真实 UI：文档库加载、Markdown 重复索引、空文件、损坏 PDF、文档范围切换和错误状态均已验证；重复 Markdown 未增加 points。
- 来源隔离：真实 v4 Embedding + Qdrant 检索验证 PDF 使用页码 locator，Markdown 使用 `lines=` locator 且页码为空；全部文档检索返回 PDF 与 Markdown 两类 document_id。
- 响应式：1440×900、1024×768、390×844 均无横向溢出；截图位于 `output/playwright/phase5-qa-*.png`。
- DeepSeek：连接恢复后，真实 PDF 和 Markdown 问答均返回 `answered`；来源展开、笔记创建/更新和会话隔离均已复验，页面未生成伪答案。
- UI 缺陷修复：点击“新会话”后补充清空 `source_summary`，修复来源 JSON 已清空但摘要仍显示旧来源的问题；新增回归测试并通过。
- 非阻塞风险：Gradio 5.50.0 的 `upload_progress?upload_id=undefined` 404 仍存在，但上传、索引和页面状态成功；后续升级 Gradio 时需再次观察。

## Phase 8 最终证据（2026-08-01）

- `python -m doc_qa.cli health`：返回 `status=ok`；配置完整、Qdrant healthz HTTP 200、v3/v4 均 green/262 points/1024 维、SQLite `integrity_check=ok`。
- `python -m doc_qa.cli backup-sqlite data/backups/phase8-validation.sqlite3`：备份返回 `status=ok`；恢复文件完整性为 `ok`，包含 2 个 sessions、1 个 conversation turn。
- 真实 v4 smoke test：`text-embedding-v4` 查询 → Docker Qdrant → DeepSeek，返回 `answered`，引用 Happy-LLM 第 6 页和对应 `source_locator`。
- 全量测试：45 项通过；compileall、Compose 配置解析和 `git diff --check` 通过。
- Phase 8 完成；未部署生产、未公网暴露、未提交、未推送。
