# 项目进度

## 当前状态

> 当前权威状态（2026-08-01）：多文档与 Markdown 任务卡 Phase 2、Phase 3、Phase 4、Phase 5、Phase 6 已完成。真实浏览器问答、来源展开、笔记创建/更新、文档切换、三种视口复验和全量质量门禁均已通过；Gradio 上传进度 404 仍为非阻塞依赖风险。本节后方关于“等待进入 Phase 2”的内容属于历史基线记录。

## Phase 6 全量质量门禁与交付收口（已完成，2026-08-01）

- 任务卡状态已统一为 Phase 0～6 完成；独立 QA 已勾选，Git 提交/PR/CI 仍等待负责人单独确认。
- 全量 `pytest tests -q`：67 项通过；`compileall`、`git diff --check`、敏感信息扫描通过。
- `python -m doc_qa.cli health`：`status=ok`；Qdrant healthz HTTP 200；SQLite integrity check 为 `ok`。
- v4 collection：`docqa_text-embedding-v4_dim1024`，267 points、1024 维；PDF 262 points、Markdown 5 points；必需来源元数据完整，未混入 v3 或测试向量。
- v3 collection：`docqa_text-embedding-v3_dim1024_eval`，262 points、1024 维，保持独立且本轮未修改。
- Gradio `upload_progress?upload_id=undefined` 404 仍为非阻塞依赖风险；上传、索引、问答和页面状态未受影响。

## Phase 5 独立 QA 收口（2026-08-01）

- 真实浏览器验证：PDF 重复索引保持 262 points；Markdown 重复索引保持 5 points；v4 collection 总数保持 267 points。
- PDF 问答成功：`Happy-LLM 的内容分为哪两个部分？` 返回 `answered`，来源为第 6 页并包含 `source_locator`。
- Markdown 问答成功：来源包含章节、段落和 `lines=` 定位；`page_start/page_end` 保持为空，没有伪造 PDF 页码。
- 学习链路成功：真实浏览器完成笔记创建和更新；切换文档范围清空回答、来源和临时笔记上下文，同时保留持久化历史。
- 缺陷修复：修复点击“新会话”后来源摘要残留、但来源 JSON 已清空的 UI 状态不一致问题；新增回归测试。
- 响应式验证：1440×900、1024×768、390×844 均无横向溢出，截图见 `output/playwright/phase5-qa-*.png`。
- 最终门禁：全量 pytest 67 项通过，compileall、`git diff --check`、`doc_qa.cli health`、Qdrant healthz 和 SQLite integrity_check 通过。
- 风险：Gradio 5.50.0 仍记录 `upload_progress?upload_id=undefined` 404；上传、索引和页面状态均成功，不阻塞 Phase 5，但后续升级 Gradio 时需单独回归。

## DeepSeek 空响应修复（2026-08-01）

- 根因：DeepSeek V4 Flash 默认启用思考模式，`max_tokens` 同时计算 `reasoning_content`；在 JSON 输出和文档上下文较长时，响应可能以 `finish_reason=length` 结束而 `message.content` 为空。
- 修复：新增 `DEEPSEEK_THINKING` 配置，默认值为 `disabled`；CLI、UI 和评测入口统一传入显式思考模式。
- 错误透明度：空响应耗尽重试后报告 `finish_reason` 和推理长度，不记录回答正文、密钥或 Token；无伪答案回退。
- 验证：DeepSeek 真实适配器连续 3 次调用均返回非空响应；真实 `doc_qa.cli ask` 使用 v4 Embedding、Docker Qdrant 和 DeepSeek 返回 `answered`。
- Gradio 5.50.0 的 `upload_progress?upload_id=undefined` 404 未确认有应用层修复开关；实际上传和索引成功，暂记录为非阻塞依赖风险，后续通过隔离环境升级 Gradio 验证。
### 历史基线摘要（只读）

Phase 0～8 已收口；“多文档与 Markdown 知识库管理”任务卡已确认，Phase 0 基线审计和 Phase 1 规格、架构与测试矩阵设计均已完成，尚未进入业务实现，等待确认进入 Phase 2。

## 多文档与 Markdown 知识库管理：Phase 0 基线审计（2026-08-01）

- Git 基线可用：当前分支 `main`，基线提交 `b121f09`；工作区存在既有修改，本阶段未覆盖或提交。
- 运行环境可用：`docqa-qdrant` 正常运行，`http://localhost:6333/healthz` 返回 200；v4 collection 为 green、262 points、1024 维。
- 依赖已核对：`hello-agents==0.2.0`、`qdrant-client==1.18.0`；安装包真实 API 为 `RAGTool(...).run(parameters)` 和 `MemoryTool(...).run(parameters)`。
- 当前 PDF 能力完整：171 页基准 PDF 可提取文本，现有实现生成 262 个非空分块并支持真实 v4 索引。
- 当前 Markdown 能力缺失：没有 Markdown parser、Markdown chunk model、章节/段落/行号 `source_locator` 或统一文档摄入入口。
- 当前文档目录已有基础能力：SQLite `documents` 表和 Gradio 文档列表存在，但表结构与上传流程仍按 PDF 页数和 `index_pdf` 设计。
- 当前隔离能力部分可复用：Qdrant 查询支持 `document_id` 过滤，问答服务可接收该过滤；需要在后续 Phase 1 明确“指定文档”和“全部文档知识库”两种范围语义。
- 当前 UI 仍限制 `.pdf`，已有测试明确验证 Markdown 会被拒绝；该测试将在后续规格确认后改为格式校验与 Markdown 正常路径测试。
- 回归验证：`E:\Agent\docqa-venv311\Scripts\python.exe -m pytest tests -q` → 45 passed。

## Phase 0 结论

Phase 0 完成。主要差距已经定位到统一文档解析协议、Markdown 来源定位、文档元数据扩展、多文档索引幂等和 UI 上传/切换；下一步是 Phase 1 规格、架构与测试矩阵，不自动执行。

## 多文档与 Markdown 知识库管理：Phase 1 规格设计（已完成，2026-08-01）

- 已确定统一解析结果采用格式感知的文档、段落/块和分块三层模型；PDF 的页码字段可用，Markdown 的页码字段为空。
- 已确定 `document_id = SHA-256(原始文件字节)`；同内容重复上传返回 duplicate 结果，不增加 points；同名不同内容生成不同 document_id。
- 已确定 `chunk_id` 基于 document_id、稳定来源定位、规范化内容和 embedding_profile 生成；point ID 继续由 chunk_id 派生。
- 已确定 Markdown `source_locator` 使用章节路径、段落序号、起止行号和 chunk_id，不伪造 PDF 页码。
- 已确定所有文档继续写入 `docqa_text-embedding-v4_dim1024`，通过 document_id 过滤；不为单个文档创建 collection。
- 已确定切换文档范围时重置当前 UI 问答上下文、来源和待保存笔记状态；历史数据保留在 SQLite。
- 已完成 SQLite `documents` 表的兼容迁移审查，建议采用新增字段、默认值回填和备份恢复，不在本阶段执行迁移。
- 已建立测试矩阵文档：`docs/multi-document-test-matrix.md`。

### Phase 1 验证

- `E:\Agent\docqa-venv311\Scripts\python.exe -m pytest tests -q` → 45 passed；
- `git diff --check` → 通过，仅有工作区既有换行符提示；
- 文档路径回读和状态关键字检查 → 通过；
- 本阶段未修改业务代码、测试、Schema、真实配置、Qdrant collection 或真实数据。

### Phase 1 未实现项（设计阶段历史记录）

- Markdown parser、统一摄入入口、跨格式 chunk model 和 SQLite migration 尚未实现；
- 多文档真实索引、文档切换 UI 和 Markdown 来源浏览器验收尚未执行；
- 需要 Phase 1 文档评审完成后，才进入 Phase 2。

## 已完成

- 通过 Git 获取上游源码到独立参考目录 `E:\Agent\hello-agents-upstream`。
- 在 `E:\Agent\开发实践\Agent3-智能文档问答助手` 建立干净应用目录，保留项目文档、评测材料和基准 PDF。
- 检查基准 PDF：171 页，可提取文本；部分页面存在字符提取异常。
- 定位第八章示例：`code/chapter8/11_Q&A_Assistant.py`。
- 确认示例使用 `MemoryTool`、`RAGTool` 和 Gradio。
- 确认仓库根目录没有统一 `pyproject.toml`、`requirements.txt` 或 `hello_agents` 包源码。
- 准备 `data/reference/` 和 `eval/`。
- Phase 2 已实现单 PDF 解析、页感知分块、Embedding 适配、Qdrant 索引和状态验证。
- 真实基准 PDF 解析出 171 个有文本页面和 262 个非空分块。
- 本地 Qdrant 闭环测试首次写入 262 个点，重复执行保持 262 个点，元数据验证通过。
- 真实 Docker Qdrant 索引首次和重复执行均为 262 个 points，collection 维度为 1024，来源元数据完整。
- Embedding 适配层已增加批量上限校验、HTTP 错误透明度和临时错误重试；Phase 2 测试共 12 项通过。
- Phase 3 已实现查询 Embedding、Qdrant `query_points`、Top-K、分数阈值、`document_id` 过滤、DeepSeek 适配器、结构化回答和来源引用。
- DeepSeek 默认不继承系统代理，通过 `DEEPSEEK_TRUST_ENV` 显式控制；标准命令在本机代理变量存在时仍可完成真实调用。
- Phase 3 自动化测试共 21 项通过，真实 v4 查询检索已命中 Docker Qdrant 中的真实来源片段。
- 真实基准验证已覆盖：明确事实题 q001、跨章节归纳题 q011、无答案拒答题 q015、文档外问题 q020。
- q001 和 q011 的回答覆盖预期知识点，引用页码与 `source_locator` 一致；q015 未猜测密钥；q020 返回 `no_results` 且未调用 DeepSeek。
- 失败场景测试已覆盖 Embedding、Qdrant、DeepSeek 失败和伪答案阻断。
- Phase 4 已实现 SQLite 持久化、外键、WAL、事务和按会话/时间/事件类型索引。
- Phase 4 已实现会话历史、最近轮次记忆限制、来源快照、笔记创建/更新、学习事件和统计报告。
- Phase 4 测试新增 5 项，Phase 2/3/4 合计 26 项通过。
- 真实验证库 `data/phase4-validation.sqlite3` 完成一轮真实问答、来源保存、笔记创建/更新、统计和报告验证。
- 分离进程重新打开 SQLite 后，完整性检查为 `ok`，会话历史和笔记均可恢复。

## 历史下一步记录（已完成）

## Phase 2 实现进度（历史完成记录，2026-08-01）

- 状态：已完成，随后已确认进入 Phase 3。
- 新增 Markdown 解析、统一文档解析协议、格式/哈希/状态/错误元数据、稳定 Markdown chunk ID 和章节/段落/行号定位。
- PDF 继续沿用既有解析与分块路径，基准保持 171 个有文本页面、262 个非空分块，既有 PDF source_locator 和 chunk ID 不变。
- SQLite `documents` 已实现可重复的加法迁移；新增字段仅在临时 SQLite 上验证，未修改真实 `data/docqa.sqlite3`。
- 新增 `DocumentCatalogService` 管理 canonical 状态；duplicate 只作为操作结果，不覆盖 indexed 状态；不实现归档/删除。
- Phase 2 定向测试 9 项通过，全量回归测试 54 项通过；本阶段没有调用真实 Embedding、没有写入 Qdrant。
- Phase 3 已开始执行多文档真实索引和 document_id 隔离验证。

## 多文档与 Markdown 知识库管理：Phase 3 完成记录（2026-08-01）

- 已将 `DocumentIngestionService` 扩展为 PDF/Markdown 统一真实索引入口；保留 `index_pdf()` 兼容调用。
- 已将文档目录状态接入真实索引流程：validating → parsing → indexing → indexed；Embedding/Qdrant 失败进入 failed，不覆盖既有文档。
- 已实现同一 v4 collection 的按 `document_id` 计数和检索过滤；全部文档范围保留每个来源的 `document_id`。
- 已实现重复索引只处理缺失 chunk，重复执行返回 duplicate，不重复调用 Embedding。
- 已增加 `DocumentScopeState`，切换文档范围时清空会话临时上下文、来源和待保存笔记状态；UI 接入留到 Phase 4。
- 发现并修复历史 PDF points 缺少新格式元数据的问题：仅使用 Qdrant payload 更新补齐 `format`、`content_hash`、`embedding_profile` 和 `source_locator_scheme`，未重建向量或改变 point ID。
- 项目自有材料 `data/reference/phase3-multidocument-guide.md` 已真实索引 5 个 Markdown points；首次 collection 为 267 points，重复索引仍为 267。
- Phase 3 定向和全量自动化测试通过，真实 PDF/Markdown 范围过滤和全部文档范围验证通过；随后经负责人确认进入 Phase 4 UI。

历史记录：该段落记录 Phase 5 收口时的下一步计划，后续 Phase 6 已实际执行。

## Phase 5 已完成（历史阶段）

- 新增 `src/doc_qa/ui.py`，以 `DocumentIngestionService`、`LearningService` 和 Phase 3 问答服务为唯一业务调用入口。
- 新增 SQLite `documents` 表，页面展示文档名、页数、分块数、points 和索引状态。
- 实际安装并验证 Gradio `5.50.0`，启动命令为 `python -m doc_qa.ui`。
- 浏览器验证真实 PDF 索引、事实问答、来源查看、笔记创建/更新、统计刷新和会话隔离。
- UI 专项 5 项通过；Phase 2/3/4 回归保持通过，当前总计 31 项测试通过。
- 保存 1440×900、1024×768 和 390×844 截图到 `output/playwright/`。
## Phase 6 初次评测执行记录（历史记录，已被最新结果覆盖）

- 已新增可复现评测入口：`eval/run_embedding_comparison.py`。
- 使用同一份 30 题评测集，对真实 `text-embedding-v3` 和 `text-embedding-v4` 分别执行查询 Embedding、Qdrant Top-K 检索和 DeepSeek 回答。
- v3 使用独立 collection：`docqa_text-embedding-v3_dim1024_eval`；v4 仍使用 `docqa_text-embedding-v4_dim1024`。
- 评测结果：`eval/results/embedding-v3-v4-summary.json`、`eval/results/embedding-v3-v4-report.md`。
- 阶段中间状态：当时 v4 曾有 1 条 DeepSeek 空响应失败，且自动评分不能替代人工复核；该问题已由后续 Phase 6 收口记录修复并复核。
## Phase 6 最新验证（2026-07-31）

- 修复 `DeepSeekChatProvider` 空响应有限重试；新增首次空响应后成功、重试耗尽和不生成伪答案测试。
- q011 真实命令验证成功，返回 `answered`，引用第 2、3、6 页和对应 `source_locator`。
- 最新完整评测：v3 检索命中率 100%、来源自动准确率 83.3%、答案自动正确率 53.3%、拒答自动准确率 77.8%、平均 3487ms、失败 0；v4 分别为 96.7%、86.7%、60%、100%、3503ms、失败 0。
- q016–q017 均真实检索并引用第 4 页；q023–q028 按严格文档范围拒答且判定正确。
- v3 q014 保留为已解释的对照模型幻觉案例；v4 未出现对应拒答问题。
- 项目负责人已完成评测边界、默认模型和 Phase 6 收口确认。

## Phase 7 交付准备（2026-08-01）

- 当前推荐拓扑为本地 Python/Gradio 应用 + Docker Qdrant + 本地 SQLite；不建议当前版本直接公网部署。
- 已补充 `docs/deployment-plan.md`、`docs/operations-runbook.md`、`docs/backup-recovery.md` 和 `docs/observability-and-cost.md`。
- 已更新 README、`.env.example`、`.gitignore`、架构、技术栈、决策、路线图、任务卡、进度、证据和交付清单。
- 已统一 `docs/implementation-plan.md` 的 Phase 6 状态，明确 Phase 6 已完成，Phase 7 为交付准备阶段。
- 已定义本地/测试/生产配置边界、Secret Manager 迁移要求、日志脱敏、备份恢复、回滚和成本监控规则。
- 本轮没有执行部署、没有连接生产、没有提交或推送。

## Phase 7 结论

Phase 7 的文档和方案交付定义满足。历史检查曾遇到 Docker Desktop 暂时不可连接，后续已恢复并通过 healthz 验证；应用暂无独立健康端点的风险仍保留。

## Phase 8 本地运行时建设（已完成，2026-08-01）

- Docker Desktop 已恢复；`docqa-qdrant` healthz 返回 200，v3/v4 collection 均为 green、262 points、1024 维。
- 新增 `docker-compose.local.yml`，只运行 Qdrant，不自动增加应用容器；Compose 不伪造 HTTP healthcheck，真实 healthz 由 `health` CLI 检查。
- 新增 `doc_qa.cli health`：只读检查配置、Qdrant healthz、collection 状态/维度/点数和 SQLite `integrity_check`。
- 新增 `doc_qa.cli backup-sqlite`：使用 SQLite 原生 backup API，默认保护已有备份并校验恢复文件。
- 新增 7 项 Phase 8 定向测试，已通过。
- 真实 `.env` health CLI 返回 `ok`；v3/v4 collection 均为 green、262 points、1024 维；SQLite integrity check 为 `ok`。
- 真实 v4 smoke test 使用 `text-embedding-v4`、Docker Qdrant 和 DeepSeek 返回 `answered`，引用 Happy-LLM 第 6 页。
- 全量 45 项测试、compileall、Compose config、diff check 和凭据扫描通过。

## Phase 8 结论

Phase 8 完成定义满足。当前仍不具备公网生产条件：应用无认证、限流和独立 HTTP health endpoint，SQLite 仍是单实例存储。

## 后续独立方向进展（2026-08-01）

### 方向 A

- 已隔离验证 Gradio 5.50.0、5.49.1、6.22.0；前两者真实上传均出现 404，后者因 Chatbot `type` 不兼容无法启动，当前保留 5.50.0。

### 方向 B

- 已完成任务卡、状态机、事务边界、历史关联保护、恢复策略和测试矩阵设计。
- 设计接受 additive migration + tombstone + `deleting/inconsistent` 可恢复状态；尚未实现代码或操作真实 points。

### 方向 C

- 已完成搜索、筛选、排序、详情和错误反馈规格，等待方向 B 收口。

## 后续独立方向收口（2026-08-01）

- 方向 B 已实现 DocumentLifecycleService、Qdrant 按 document_id 删除、SQLite document_operations 审计记录、归档/恢复/删除/一致性检查和删除后笔记关联保护；UI 已接入归档、取消归档、删除确认和重新索引恢复入口。
- 方向 B 新增 5 项临时 SQLite/Qdrant 测试，覆盖确认、归档保点、删除 tombstone、Qdrant 失败恢复和源文件缺失恢复。
- 方向 C 已实现文档搜索、格式/状态筛选、更新时间排序、详情 JSON 和索引错误脱敏；新增 UI/查询回归测试。
- 全量 pytest 73 项通过，compileall 通过；真实 UI 三种视口复验通过，未执行真实删除。

## 多文档与 Markdown 任务：Phase 4 UI 实现（已完成，2026-08-01）

- Gradio `5.50.0` 页面已扩展为 PDF/Markdown 文档库，支持 `.pdf`、`.md` 和 `.markdown` 上传校验。
- 文档表显示文档名、格式、短 document_id、状态、PDF 页数或 Markdown 章节/段落单元数、分块、points、定位方案、更新时间和脱敏错误。
- 问答范围支持全部文档和指定 document_id；范围切换清空当前回答、来源、待保存笔记和临时上下文，SQLite 历史数据保持不变。
- Markdown 来源允许空页码并展示章节/段落/行号定位；PDF 继续展示页码和 source_locator。
- UI 通过 `DocumentIngestionService`、`LearningService` 和 `QuestionAnswerService` 调用业务能力，不直接操作 Qdrant、SQLite 或第三方 API。
- UI 定向测试 7 项通过，Phase 2/3/4 学习闭环回归通过；真实页面验证了 Markdown 重复上传不会新增 points，结果保持 267 points。
- Playwright 人工证据：`output/playwright/phase4-ui-1440x900.png`、`phase4-ui-1024x768.png`、`phase4-ui-390x844.png`。

## 多文档与 Markdown 任务：Phase 4 结论

Phase 4 完成定义满足。下一阶段是 Phase 5 独立 QA，不在本轮自动执行。

## Phase 4 最终修复与回归（2026-08-01）

- 根因：旧版 SQLite `citations.page_start/page_end` 为 `NOT NULL`，Markdown 引用没有 PDF 页码，导致真实 UI 问答在保存引用时失败。
- 修复：增加旧表检测和兼容迁移，允许页码为空；读取引用时保留 `None`，不再执行 `int(None)`；既有 citation 数据保留。
- 真实 UI 复验：Markdown 问答返回 `answered`，回答已持久化；来源显示章节、段落和 `lines=`，页码字段为空。
- 全量质量门禁：pytest 64 项通过；compileall、`git diff --check`、Qdrant healthz 200、v3/v4 collection 检查、SQLite integrity check 和敏感信息扫描通过。

## Phase 5 独立 QA（已完成，2026-08-01）

- 已验证真实文档库加载、PDF/Markdown 重复索引、空文件、损坏 PDF、文档范围切换、来源隔离和三种视口响应式布局。
- v4 collection 当前为 267 points、1024 维，其中 Happy-LLM PDF 为 262 points、项目 Markdown 为 5 points；v4 payload 元数据完整。
- 全量 pytest 67 项、compileall、diff check、health CLI 和敏感信息扫描通过。
- 真实 PDF 和 Markdown UI 问答均成功；PDF 来源为页码 locator，Markdown 来源为章节/段落/行号 locator，未生成伪答案或伪页码。
- 真实浏览器完成来源展开、笔记创建与更新、文档范围切换和新会话隔离复验；切换和新会话均不会残留旧来源摘要。
- Phase 5 已完成，不进入 Phase 6；DeepSeek 连通性已恢复并通过真实 UI 验证。
