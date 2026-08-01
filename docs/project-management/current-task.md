# 当前任务

状态：completed（方向 A、B、C 已完成；等待 Git P0 决策）

项目工作目录：`E:\Agent\开发实践\Agent3-智能文档问答助手`

当前阶段：后续方向已收口；Gradio 上传进度 404 仍为非阻塞风险

## 任务

> 当前权威状态（2026-08-01）：多文档任务卡 Phase 2～6 以及后续方向 A、B、C 已完成。生命周期测试使用临时 SQLite/Qdrant，真实生产删除未执行；真实浏览器问答、来源、笔记、文档切换和三种视口复验保持通过。Gradio `upload_progress?upload_id=undefined` 404 已确认是版本级非阻塞依赖风险，未伪装为已修复。文件下方旧阶段内容属于历史记录，不再代表当前状态。

建立并确认“多文档与 Markdown 知识库管理”用户价值任务卡；本文件下方的 Phase 0～8 为历史阶段记录，新任务卡见 `docs/project-management/task-card-multi-document-markdown.md`。

## 当前活动任务卡

> 当前活动状态：方向 A、B、C 已完成，等待负责人决定是否进入 Git P0；下面早期的 Phase 0～8 描述属于历史执行记录，不能覆盖本文件顶部的当前状态。

- 任务卡：`docs/project-management/task-card-multi-document-markdown.md`
- 用户价值：上传、管理和切换多个 PDF/Markdown 文档，并按 `document_id` 隔离问答和来源。
- 当前阶段：Phase 6 全量质量门禁与交付收口已完成，当前状态为 `completed`。
- 当前允许：维护已发现的非阻塞依赖风险；未经确认不进入新的产品阶段。
- 当前禁止：进入新的业务阶段、切换 Embedding 模型、修改生产配置、删除或重建现有 points。

## Phase 0 基线审计结果（历史记录，2026-08-01）

- Git 基线存在：当前分支为 `main`，基线提交为 `b121f09`；工作区已有用户修改，本阶段未覆盖、重置、提交或推送。
- 当前实现仍以 PDF 为唯一文档输入：`PdfParser`、`PageAwareChunker`、`DocumentIngestionService.index_pdf` 和 Gradio 上传入口均为 PDF 专用。
- SQLite 已有 `documents` 文档目录，可保存文档名、路径、页数、分块数、point 数、状态和错误；尚缺格式、文件哈希、Embedding 配置和 Markdown 定位字段。
- Qdrant 已支持同一 v4 collection 的 `document_id` 过滤；现有来源模型和 payload 仍假设 PDF 页码，尚不支持 Markdown 章节/段落/行号定位。
- 问答服务已支持可选 `document_id` 过滤；文档库 UI 已支持查看和切换已索引 PDF，但不支持 Markdown。
- 本地运行证据：`docqa-qdrant` 正常运行，healthz 返回 HTTP 200；`docqa_text-embedding-v4_dim1024` 为 green、262 points、1024 维。
- 回归证据：`pytest tests -q` 为 45 项通过。

## Phase 0 停止条件（历史记录）

- Phase 0 已完成，不自动进入 Phase 1。
- 在 Phase 1 明确统一解析协议、Markdown `source_locator`、文档幂等键、SQLite 兼容迁移和文档范围过滤语义前，不修改业务代码、Schema、Qdrant points 或 UI。
- 当前禁止：修改业务代码、测试、Schema、真实配置、Qdrant collection；不创建分支、不提交、不推送。

## Phase 1 完成结果（历史记录）

- 已固化 PDF/Markdown 统一解析协议和来源定位规则；
- 已固化 document_id、chunk_id、Embedding profile 和幂等策略；
- 已完成 SQLite `documents` 表兼容迁移审查，未执行迁移；
- 已固化文档范围、切换隔离、UI 状态和测试矩阵；
- 已完成文档质量检查和 45 项回归测试；随后已进入并完成 Phase 2。

## 历史阶段记录

## 已知输入

- 上游仓库：`E:\Agent\hello-agents-upstream`，Git 分支 `main`。
- 基准文档：`data/reference/Happy-LLM-0727.pdf`。
- LLM 候选：DeepSeek API。
- Embedding 默认候选：阿里云百炼 `text-embedding-v4`，1024 维。
- Embedding 对照候选：`text-embedding-v3`，本阶段不作为隐式回退。

## Phase 3 禁止

- 不实现 MemoryTool、学习笔记、学习统计或完整 UI。
- 不扩展 MQE、HyDE、多模态或 Neo4j。
- 不混用 Embedding 模型，不把测试向量当作生产实现。
- 不修改生产配置或生产数据，不提交、推送或创建 PR。

## Phase 3 允许修改

- `src/doc_qa/` 查询 Embedding、Qdrant 检索、DeepSeek 适配、问答服务和 CLI。
- `tests/` Phase 3 定向测试。
- `pyproject.toml`、`requirements.txt`、`.env.example`。
- 与本阶段直接相关的项目文档和评测辅助文件。

## Phase 3 验收标准

- 查询 Embedding 固定使用 `text-embedding-v4`、1024 维和现有 collection。
- Qdrant 检索支持 Top-K、分数阈值和 `document_id` 过滤。
- 检索结果保留文档名、document_id、chunk_id、章节、页码和 source_locator。
- DeepSeek API 失败、检索失败、无结果和文档外问题均有可定位处理。
- 回答只能依据检索片段，并返回结构化来源引用。
- Phase 2 的 12 项测试不回归，Phase 3 新增测试全部通过。
- 使用真实 v4 查询向量完成 Docker Qdrant 检索验证；真实 DeepSeek 生成需要可用凭据。

## 阶段验收

- 已确认仓库是教程/示例仓库，运行包来自外部 PyPI。
- 已确认第八章示例入口和当前示例的主要边界。
- 已形成架构、UI、测试和 v3/v4 对比方案。
- 已准备基准 PDF 和评测问题集结构。

## Phase 2 完成记录

- 已实现 `MarkdownParser` 和 `DocumentParser`，支持 `.md/.markdown`、ATX/Setext 标题、嵌套章节、段落、代码块、列表、表格、中文和原始行号。
- Markdown 内容始终作为不可信数据保留，不执行 HTML/script，也不提升文档内指令为系统指令；空内容和无效 UTF-8 会返回可定位错误。
- 已增加统一 `DocumentSource`、`DocumentUnit`、`ParsedDocument` 协议；PDF 继续保留既有页码、chunk ID 和 source_locator 语义。
- 已实现 Markdown 稳定 chunk ID、章节/段落/行号 source_locator 和 `text-embedding-v4:1024` profile 标识，但本阶段未调用 Embedding、未写入 Qdrant。
- SQLite `documents` 目录已增加可重复的加法迁移实现和格式、content_hash、Embedding profile、定位方案、单元数、创建时间字段；验证仅使用临时 SQLite。
- 已增加 `DocumentCatalogService`，支持 pending/validating/parsing/indexing/indexed/failed 状态和 duplicate 操作结果，不实现归档/删除。
- 定向 Phase 2 测试 9 项通过，全量测试 54 项通过；基准 PDF 回归为 171 个有文本页面、262 个分块。

## Phase 2 停止条件

- Phase 2 已完成；不自动进入 Phase 3。
- 本阶段未修改真实 `data/docqa.sqlite3`、原始 PDF、Qdrant points 或真实 Embedding 配置；多文档真实索引、document_id 检索隔离和 UI 扩展属于后续阶段。

- 真实 `text-embedding-v4` 调用成功，实际向量维度为 1024。
- Docker Qdrant `docqa-qdrant` 运行正常，健康检查返回 HTTP 200。
- `Happy-LLM-0727.pdf` 解析出 171 个有文本页面和 262 个非空分块。
- 首次和重复索引均为 262 个 points，collection 为 `docqa_text-embedding-v4_dim1024`。
- 来源元数据完整，重复索引不增加 points，幂等验证通过。
- Phase 2 定向测试 12 项全部通过。

## Phase 3 当前状态

- 查询 Embedding、Qdrant 检索、过滤、来源结构、DeepSeek 适配器和 CLI 已实现。
- 代理策略已收口：DeepSeek 默认使用 `DEEPSEEK_TRUST_ENV=false`，不继承不可控的系统 SOCKS/HTTP 代理；需要代理时显式开启。
- 21 项自动化测试、编译检查和 diff 检查已通过。
- 使用标准命令完成真实 DeepSeek 调用，模型为 `deepseek-v4-flash`。
- 已完成明确事实、跨章节归纳、无答案拒答和文档外问题四类真实基准验证。
- 未实现 MQE、HyDE、MemoryTool、笔记、统计、Neo4j 或 UI。

## Phase 3 完成结论

- 查询使用真实 `text-embedding-v4`/1024 维向量，检索 Docker Qdrant 中的真实 points。
- DeepSeek 回答仅使用检索片段，并返回与实际检索结果绑定的页码和 `source_locator`。
- 文档外问题在无相关结果时返回“不足以回答”，不会调用 DeepSeek 生成伪答案。
- Embedding、Qdrant 和 DeepSeek 失败场景均有自动化测试和可定位错误。
- Phase 3 完成，下一阶段为 Phase 4；本任务不自动进入下一阶段。

## Phase 4 任务

完成“会话记忆 → 学习笔记 → 学习事件 → 学习统计/报告”的最小真实闭环。

## Phase 4 完成记录

- 使用 SQLite 保存 sessions、conversation_turns、citations、notes 和 learning_events。
- 启用外键、WAL、busy timeout、事务和 session/document/time/event 索引。
- 实现会话创建、恢复、问答历史和限定记忆窗口；默认最近 6 轮、最多 4000 字符，并优先保留最近轮次。
- 会话历史仅用于指代消解，回答事实仍必须来自 Phase 3 的 Qdrant 检索片段。
- 实现笔记创建、查询和更新；document_id/source_locator 必须关联当前会话的真实来源。
- 实现 session_created、question_asked、answer_generated、no_results、note_created 和 note_updated 事件。
- 实现确定性的统计和 JSON 报告，不调用 LLM 生成统计事实。
- Phase 4 定向测试 5 项通过，与 Phase 2/3 回归合计 26 项通过。
- 使用真实 Happy-LLM PDF、text-embedding-v4、Docker Qdrant 和 DeepSeek 完成问答、引用持久化、笔记和统计验证。
- 关闭并重新打开 SQLite 后，问答历史和笔记仍可读取，完整性检查返回 `ok`。

## Phase 4 完成结论

- Phase 4 完成定义满足，下一阶段为 Phase 5：Gradio UI 状态、响应式和人工验收。
- 本阶段未实现 Gradio UI、Neo4j、MQE、HyDE 或多模态能力。

## Phase 5 任务（历史阶段）

完成“文档库 → 会话 → 问答 → 来源 → 笔记 → 学习统计”的 Gradio UI、响应式布局和真实浏览器验收。

## Phase 5 完成记录（历史阶段）

- Gradio 实际版本为 `5.50.0`，启动入口为 `python -m doc_qa.ui`，默认监听 `127.0.0.1:7860`。
- UI 已通过文档库、学习会话、问答、来源引用、笔记和学习统计区域串联 Phase 2/3/4 服务。
- 使用真实 `Happy-LLM-0727.pdf` 完成页面上传和索引，结果为 171 页、262 个分块、262 个 points。
- 真实问题“Happy-LLM 的内容分为哪两个部分？”返回“基础知识与实战应用”，来源显示文档名、document_id、chunk_id、章节、页码、source_locator 和分数。
- 页面完成笔记创建、笔记更新、统计刷新和新会话切换；新会话未继承旧会话的问答和笔记。
- 已覆盖 1440×900、1024×768 和 390×844 浏览器视口，并保存 `output/playwright/` 截图证据。
- UI 定向测试 5 项通过，Phase 2/3/4 回归测试保持通过，总计 31 项通过。

## Phase 5 完成结论（历史阶段）

- Phase 5 完成定义满足，下一阶段为 Phase 6；本任务不自动进入 Phase 6。
- 已知风险：Gradio 5.50.0 在 Playwright 文件选择流程中记录一次 `upload_progress?upload_id=undefined` 的 404 控制台错误，但文件上传、索引和页面结果均成功；需在后续升级 Gradio 或真实用户浏览器回归时继续观察。
## Phase 6 初次收口状态（历史记录，已被最新结果覆盖）

历史中间状态：本阶段已完成真实 v3/v4 对比运行、独立 collection 隔离、全量回归测试和安全扫描；当时曾为 `blocked_by_quality_gate`，该状态已被后续空响应修复、人工复核和负责人确认覆盖。

当前默认模型暂保持 `text-embedding-v4`，不是因为模型名称，而是基于本轮证据：平均响应更快、自动答案正确率和拒答准确率更高，且现有生产 collection 已稳定运行。后续若要正式发布，需先处理空响应重试/失败策略并完成人工评分。
## Phase 6 最新收口结果（2026-07-31）

- DeepSeek 空响应根因已修复：空内容现在进入有限重试，耗尽后返回明确错误，不生成伪答案。
- 定向 q011 真实验证成功；完整 v3/v4 评测无失败题。
- v3 出现 2 次空响应重试后成功；v4 无失败、无重试。
- 逐题证据复核已记录在 `eval/results/embedding-v3-v4-manual-review.md`；q023–q028 的严格文档范围政策已确认，不再标记为 `uncertain`。
- q016–q017 修复后均准确回答 PDF 第 4 页许可证信息，并返回完整 `source_locator`。
- 当前保持 `text-embedding-v4` 为默认模型；项目负责人已确认 Phase 6 收口。

## Phase 7 完成记录（2026-08-01）

- 已统一 Phase 6 的历史状态文字，明确 Phase 6 已完成且未执行部署、发布、提交或推送。
- 已完成本地、测试和生产环境边界设计；真实密钥只允许进入未提交的 `.env` 或生产 Secret Manager。
- 已完成 Qdrant、SQLite、授权文档和评测结果的备份/恢复方案，明确 v4 collection 与 v3 评测 collection 隔离。
- 已完成启动顺序、Qdrant 健康检查、有限重试、优雅关闭、回滚和故障排查方案。
- 已完成本地运行、Qdrant-only Compose 和应用容器化评估；当前推荐本地 Python 应用加 Docker Qdrant。
- 已完成日志、指标、错误追踪和成本监控字段设计；当前没有引入集中式监控服务。
- README、`.env.example`、部署文档和运维文档已补齐；未执行部署。

## Phase 7 风险与停止条件

- Docker Desktop 已恢复；`docqa-qdrant` 运行中，healthz 返回 HTTP 200，v3/v4 collection 均为 green、262 points、1024 维。
- 应用暂无独立健康端点，SQLite 仅适合单实例；当前版本无认证、限流和多租户能力。
- 在补齐访问控制、Secret Manager、独立持久化和恢复演练前，不得公网部署。

## Phase 8 当前任务

完成本地 Qdrant-only Compose、只读运行时健康检查、SQLite 一致性备份和本地 smoke test；不连接生产、不公网暴露、不提交推送。

## Phase 8 已实现

- 新增 `docker-compose.local.yml`，只定义 Qdrant、端口和持久化卷，不增加应用容器；真实 HTTP healthz 由 `health` CLI 检查。
- 新增 `doc_qa.cli health`，检查配置、Qdrant healthz、v3/v4 collection 状态/维度/点数和 SQLite 完整性。
- 新增 `doc_qa.cli backup-sqlite`，使用 SQLite 原生 backup API，默认不覆盖已有备份，并校验 `integrity_check`。
- 新增 Phase 8 自动化测试，覆盖配置缺失、collection 缺失、SQLite 损坏、健康报告脱敏和备份恢复。

## 当前独立方向（2026-08-01）

- 方向 A 已完成调查：Gradio 5.50.0 与 5.49.1 均复现 `upload_progress?upload_id=undefined` 404；6.22.0 对当前 UI 有启动回归，暂不升级。
- 方向 B 已完成规格和设计审查，产物为 `docs/document-lifecycle-*.md`；尚未删除真实数据或实现删除代码。
- 方向 C 等待方向 B 完成后实现；本轮禁止 Git P0、提交、推送、PR、部署、认证、多租户和公网部署。

### 后续方向收口

- 方向 B 已实现归档、删除、Qdrant 精确删除、SQLite tombstone、失败恢复、一致性检查边界和临时存储测试。
- 方向 C 已实现文档搜索、格式/状态筛选、更新时间排序、文档详情和脱敏错误展示。
- 全量测试保持通过；全部方向完成后停止，等待负责人决定是否进入 Git P0。

## Phase 8 完成记录（2026-08-01）

- 使用真实 `.env` 执行 health CLI，返回 `status=ok`。
- 使用真实 v4 collection 完成本地最小 smoke test，真实回答返回 `answered` 并带来源。
- 完成全量测试、compileall、diff 检查、Compose 配置检查和凭据扫描。
- Phase 8 完成定义满足；不执行生产部署、公网暴露、提交或推送。

## 多文档与 Markdown 任务：Phase 4 最终收口（2026-08-01）

- Gradio 文档库、PDF/Markdown 上传、索引状态、问答范围切换、来源展示、笔记和会话隔离已完成。
- SQLite 已兼容 Markdown 无页码引用：旧版 `citations.page_start/page_end NOT NULL` 会迁移为可空字段，既有引用数据保留。
- 真实 Markdown 问答已成功保存并重新读取 `source_locator`；页码字段保持为空，定位保留章节、段落和行号。
- 全量测试最终 64 项通过；当前等待确认进入 Phase 5 独立 QA。
