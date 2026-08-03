# 当前任务（唯一权威状态，2026-08-03）

## UI-REC0：可回退基线与单一事实源

- 状态：`baseline_frozen`。UI-REC0 已完成；当前 UI 已冻结，不得继续追加 CSS、创建新的视觉实现阶段或宣称 Figma 高保真通过。
- 当前事实：功能回归记录有效，但真实页面尚未达到冻结 Figma 基线；测试通过与视觉通过必须分开记录。
- 冻结视觉基线：`docs/assets/ui-visual-baseline/` 中的桌面学习会话、桌面文档库和移动上下文面板三张图片。
- 固定数据夹具：`tests/fixtures/ui_visual_baseline.py`，仅使用临时 SQLite/Qdrant 路径和确定性外部服务替身，继续走真实 UI、会话、来源和笔记回调。
- 清理状态：`docs/project-management/ui-rec0-cleanup-manifest.md` 已列出保留、归档和待确认清理范围；当前没有删除任何文件。
- 质量门禁：隔离夹具 HTTP 200；UI 定向 28 项、全量 93 项通过；`compileall`、`git diff --check` 和高置信敏感信息检查通过。
- Git 边界：本任务的本地提交即为恢复点；不推送、不创建 PR、不部署。
- 下一决策：UI-REC0 完成并经负责人确认后，才决定是否进行 CSS/布局架构重置；没有自动批准新的 UI 实现阶段。

> 本节是唯一当前状态。下方全部 UI-0/UI-R/UI-HF/HF-R 内容只用于历史追溯，不得作为下一轮实施入口或完成结论。

---

# 历史 UI 路线记录（非权威）

## HF-R4：来源、笔记、平板与移动端高保真落地（历史记录）

- 状态：`ready_for_hf_r5`；HF-R4 已完成，未自动进入 HF-R5。
- 完成：右侧检查器以真实 `citations` 渲染 PDF/Markdown 卡片；PDF 保留文档名、页码、片段及原始定位展开入口，Markdown 保留文档名、章节、段落、行号、片段及原始定位展开入口。笔记列表改为当前会话真实笔记的受控卡片，原 Dataframe 继续承接既有回调但不作为主视觉。
- 响应式：1024×768 使用显式右侧上下文抽屉；390×844 使用底部面板，保留来源/笔记 Tab、文字状态和触控入口。
- 保持：`document_id`、`source_locator`、PDF/Markdown 定位、`document_filter`、会话隔离、笔记关联和生命周期业务逻辑均未改变。
- 质量：UI 定向 28 项、全量 93 项测试通过；`compileall`、`git diff --check` 通过；证据位于 `output/ui-fidelity-recovery/hf-r4/`。
- 风险：移动端隔离浏览器的自动填充受浏览器剪贴板限制，未将“移动端有来源回答”写为独立通过证据；桌面隔离回调已验证真实来源与笔记保存。Gradio `upload_progress?upload_id=undefined` 404 仍是独立非阻塞技术债务。

## HF-R3：文档库、工具栏、文档行与详情检查器高保真落地（历史记录）

- 状态：`ready_for_hf_r4`；HF-R3 已完成，未自动进入 HF-R4。
- 完成：真实上传/索引入口、搜索和筛选工具栏、紧凑文档行、长文件名两行截断、文档格式/状态/更新时间，以及绑定当前选择文档的右侧详情检查器。
- 保持：搜索和筛选不会修改问答范围；选择详情不会修改 `document_filter`；PDF 页码与 Markdown 章节/段落/行号语义、会话/笔记隔离和生命周期业务逻辑均未改变。
- 质量：UI 定向 27 项、全量 92 项测试通过；`compileall`、`git diff --check` 通过；三视口隔离浏览器验证无页面级横向溢出。
- 风险：Figma 的整体验收仍未完成，HF-R4/HF-R5 待执行；Gradio `upload_progress?upload_id=undefined` 404 仍是独立非阻塞技术债务。

## HF-R1：统一应用外壳与 P0 结构修复（当前权威状态）

- 状态：`ready_for_hf_r2`。HF-R1 已完成，未自动进入 HF-R2。
- 已完成：唯一工作台布局根、顶部品牌栏、空间导航、最近文档真实数据入口、主区/检查器层级、导航说明流式布局、短会话状态和原生页脚隐藏；文档库与学习会话在隔离实例中可真实切换。
- 已验证：1440×900、1024×768、390×844 无页面级横向溢出；导航说明不重叠；会话状态无内部 `session_id` 或横向滚动；证据位于 `output/ui-fidelity-recovery/hf-r1/`。
- 质量门禁：UI 定向 23 项通过；全量 `pytest` 88 项通过；`compileall`、`git diff --check` 通过。87 项是 HF-R0 前的历史基线。
- 边界保持：未修改解析、RAG、Embedding、Qdrant、SQLite Schema、会话/笔记/引用/生命周期业务逻辑，未处理 Gradio 上传进度 404，未提交、推送、PR 或部署。
- 下一候选：HF-R2“学习会话、消息时间线与 Composer 高保真落地”；必须由负责人确认后执行。

## HF-R0：UI 高保真落地修复（当前权威状态）

- 状态：`needs_fidelity_rework`；HF-R0 已完成，尚未进入 HF-R1。
- 任务卡：`docs/project-management/ui-fidelity-recovery-task-card.md`。
- 事实：UI-HF0～UI-HF6 的功能测试记录仍有效，但 2026-08-03 的 Figma 对照与真实浏览器审计发现 P0 导航重叠、`session_id` 横向滚动、空时间线留白、Composer/文档库/检查器结构不符，且实时“文档库”导航未切换主工作区。因此不得再称高保真视觉验收通过。
- 历史全量 87 项测试通过只表示当时的功能回归基线；测试通过不等于 Figma 视觉一致。本阶段未修改代码或测试，也未重新执行测试。
- 下一个候选阶段：HF-R1“统一应用外壳与 P0 结构重叠修复”，须先获得负责人确认；不得自动进入。
- 保持边界：不改解析、RAG、Embedding、Qdrant、SQLite Schema、会话/笔记/生命周期业务逻辑；不处理 Gradio 404；不提交、推送、PR 或部署。

## 历史 UI-HF6 收口更新（2026-08-03；不作为当前视觉结论）

状态：`ready_for_release_review`

UI-HF6 已完成 P0 结构重叠修复、Figma 高保真视觉 QA、1440×900 / 1024×768 / 390×844 三视口验证、全量回归和本轮文档收口。修复内容仅限 UI 表现层：会话头部在平板端改为稳定的两行布局；上下文检查器固定为纵向不换行，避免移动端来源卡片被排到屏幕右侧。

- 当前 UI 定向测试 22 项通过，全量测试 87 项通过；79 项为历史阶段基线，86 项为 UI-HF6 修复前基线。
- 浏览器证据：`output/playwright/ui-hf6-p0-session-1440-final.png`、`ui-hf6-p0-session-1024-v2.png`、`ui-hf6-p0-session-390.png`、`ui-hf6-p0-menu-390.png`、`ui-hf6-fixture-sources-390-fixed.png`、`ui-hf6-fixture-notes-390-fixed.png`、`ui-hf6-library-1440-final.png`。
- 临时夹具验证了真实回答时间线、PDF 页码来源、Markdown 章节/段落/行号来源、来源/笔记 Tab 和笔记保存失败状态；笔记保存成功因需要外部 Embedding 服务，本轮未在安全夹具中伪造成功。
- 保持不变：解析、RAG、Embedding、Qdrant、SQLite Schema、会话、笔记和生命周期业务语义；未删除真实数据或 Qdrant points。
- Gradio `upload_progress?upload_id=undefined` 404 仍是独立非阻塞技术债务；未处理、未宣称修复。
- UI-HF7、UI-R6/UI-R7、Git 提交/推送/PR/部署、认证、多租户、公网部署和真实生产故障演练均未执行。

## 历史 UI-HF5 状态（截至 2026-08-02）

状态：`ready_for_review`

UI-HF5 的响应式实现和核心浏览器交互已完成：平板三栏收缩、移动端导航菜单、上下文底部面板和来源/笔记 Tab 响应式入口已落地；原有问答、来源定位和笔记回调保持不变。独立状态矩阵已补齐一部分，但仍缺少全部异步/故障状态的逐项重放，因此 UI-HF5 尚未达到严格完成定义，UI-HF6 尚未执行。

本阶段证据：`output/playwright/ui-hf5-final-1440.png`、`ui-hf5-final-1024.png`、`ui-hf5-final-390-base.png`、`ui-hf5-390-context-final.png` 及 `output/playwright/ui-hf5-matrix-*.png`；定向 UI 测试 21 项通过、当前工作区全量测试 86 项通过；`compileall` 与 `git diff --check` 通过。79 项保留为上一阶段历史基线，本轮新增 UI-HF5 状态契约和生命周期绑定测试。

本阶段仍保持：不修改解析、RAG、Embedding、Qdrant、SQLite Schema、会话、笔记、引用或生命周期业务语义；Gradio `upload_progress?upload_id=undefined` 404 仍为独立非阻塞风险；未提交、未推送、未创建 PR、未部署。

状态：ready_for_review（旧 UI-0～UI-5 已完成；UI-R0～UI-R5 原阶段功能性实现已完成；UI-HF0～UI-HF5 已实现但 UI-HF5 验收未完全收口）

项目工作目录：`E:\Agent\开发实践\Agent3-智能文档问答助手`

当前阶段：UI-HF5 响应式与状态落地待补齐独立浏览器状态矩阵；UI-HF6 暂不得进入；Gradio 上传进度 404 仍为非阻塞风险

## 当前 UI 重设计任务卡

- 新任务卡：`docs/project-management/ui-redesign-task-card.md`
- 新任务状态：`ready_for_release_review`
- 新任务当前阶段：`UI-R0`～`UI-R5`、`UI-HF0`～`UI-HF6` 已完成本轮实现与 QA；下一步为 UI-R6/UI-R7 最终回归和交付收口
- 高保真基线：`docs/ui-high-fidelity-baseline.md`
- Figma 设计稿：`https://www.figma.com/design/TjKze3Fwc19gCADBrgtuzJ`
- 设计基线：使用模板节点的实际布局、组件和交互规格，重新设计应用外壳、主工作区和上下文检查器；不直接复制品牌、源码或无关业务页面。
- 参考规格：`docs/ui-redesign-reference-spec.md`
- 设计证据：`output/figma-ui-r2/desktop-session.png`、`desktop-library.png`、`mobile-session.png`、`mobile-context-sheet.png`
- UI-R3 冻结决策：已索引文档默认学习会话；空知识库引导文档库；桌面详情右侧面板；平板/移动端详情抽屉；来源/笔记共用上下文 Tab；移动端来源/笔记使用底部面板。
- 本轮停止条件：UI-HF6 已完成；本轮不自动进入 UI-R6/UI-R7 或其他新阶段。
- 旧任务卡 `docs/project-management/ui-beautification-task-card.md` 保留为历史完成记录，不代表新重设计任务完成。

- 历史任务卡：`docs/project-management/ui-beautification-task-card.md`
- 历史阶段：UI-5 已完成
- 历史阶段状态：`completed`
- UI-0 现状审计和 UI-1 Figma 参考提取已完成。
- UI-2 设计规格和负责人确认已完成，当前按 Design Tokens 实现应用外壳与文档库核心页面。
- UI-3 已完成代码实现；UI-4 已完成三视口、可访问性、交互和所有可安全复现状态验证；UI-5 已完成独立视觉 QA、全量回归和文档收口；真实生产故障演练不在安全范围内，已单独记录为运行时边界。
- 本阶段仍不得修改解析、RAG、数据层、真实数据或 Qdrant points。

## UI-R4 最终复核记录（2026-08-02）

- UI-R4 已完成；UI-R5 已完成并进入 `ready_for_review`，UI-R6/UI-R7 尚未执行。
- UI 定向测试 12 项、全量测试 76 项通过；`compileall` 和 `git diff --check` 通过。
- 临时实例 `http://127.0.0.1:7864/` 已完成三视口检查；1440、1024、390 均无横向溢出，浏览器 error/warn 为 0。
- 最终截图位于 `output/playwright/ui-r4-final-1440-clean.png`、`ui-r4-final-library-clean.png`、`ui-r4-final-1024-clean.png`、`ui-r4-final-390-clean.png`、`ui-r4-final-session-inspector.png` 和 `ui-r4-final-mobile-session.png`。

## 任务

> 当前权威状态（2026-08-01）：多文档任务卡 Phase 2～6 以及后续方向 A、B、C 已完成。生命周期测试使用临时 SQLite/Qdrant，真实生产删除未执行；真实浏览器问答、来源、笔记、文档切换和三种视口复验保持通过。Gradio `upload_progress?upload_id=undefined` 404 已确认是版本级非阻塞依赖风险，未伪装为已修复。文件下方旧阶段内容属于历史记录，不再代表当前状态。

建立并确认“多文档与 Markdown 知识库管理”用户价值任务卡；本文件下方的 Phase 0～8 为历史阶段记录，新任务卡见 `docs/project-management/task-card-multi-document-markdown.md`。

## 当前活动任务卡

> 当前活动状态：方向 A、B、C 和 Git P0 已完成；UI-3～UI-5 及 UI-R0～UI-R5、UI-HF0～UI-HF4 已完成；UI-HF5 已实现但独立浏览器状态矩阵未完全收口；真实生产故障演练未执行且不作为 UI 功能通过的前提；UI-HF6 未开始；下面早期的 Phase 0～8 描述属于历史执行记录，不能覆盖本文件顶部的当前状态。

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

## 当前独立方向（已完成记录，2026-08-01）

- 方向 A 已完成调查：Gradio 5.50.0 与 5.49.1 均复现 `upload_progress?upload_id=undefined` 404；6.22.0 对当前 UI 有启动回归，暂不升级。
- 方向 B 已完成规格、实现、临时存储测试和人工验收；真实生产删除未执行。
- 方向 C 已完成搜索、筛选、排序、详情和错误反馈；document_id、来源、会话和笔记隔离保持通过。
- Git P0 已完成，提交为 `f3c5403`；未推送、未创建 PR、未部署，也未执行认证、多租户和公网部署。

### 后续方向收口

- 方向 B 已实现归档、删除、Qdrant 精确删除、SQLite tombstone、失败恢复、一致性检查边界和临时存储测试。
- 方向 C 已实现文档搜索、格式/状态筛选、更新时间排序、文档详情和脱敏错误展示。
- 方向 A/B/C 与 Git P0 收口阶段全量 pytest 为 73 项；当前 UI-4 回归全量 pytest 为 76 项通过，compileall 和浏览器三视口复验通过；UI-4 已收口，UI-5 尚未执行。

## Phase 8 完成记录（2026-08-01）

- 使用真实 `.env` 执行 health CLI，返回 `status=ok`。
- 使用真实 v4 collection 完成本地最小 smoke test，真实回答返回 `answered` 并带来源。
- 完成全量测试、compileall、diff 检查、Compose 配置检查和凭据扫描。
- Phase 8 完成定义满足；该段为历史阶段记录，不代表当前 Git 状态。

## 多文档与 Markdown 任务：Phase 4 最终收口（2026-08-01）

- Gradio 文档库、PDF/Markdown 上传、索引状态、问答范围切换、来源展示、笔记和会话隔离已完成。
- SQLite 已兼容 Markdown 无页码引用：旧版 `citations.page_start/page_end NOT NULL` 会迁移为可空字段，既有引用数据保留。
- 真实 Markdown 问答已成功保存并重新读取 `source_locator`；页码字段保持为空，定位保留章节、段落和行号。
- 全量测试最终 64 项通过；当前等待确认进入 Phase 5 独立 QA。
## UI-5 最新收口（2026-08-02）

- 当前状态：`completed`；UI-0～UI-5 已完成，当前任务停止，不自动进入新产品任务。
- UI-5 已完成独立视觉 QA、三种视口检查、可访问性回归、业务语义回归、全量测试和文档收口。
- 当前全量测试为 76 项通过；73 项仅保留为历史阶段基线。
- 本轮仅做 UI 表现层 CSS 修复：统一 Gradio 内部容器、表格行和表头的深色 Zinc 表面，并改善长文件名断行；未修改业务逻辑、数据库或 Qdrant。
- Gradio `upload_progress?upload_id=undefined` 404 仍是已知非阻塞技术债务，本轮未处理、未伪装为已修复。
- Git P0 已完成（`f3c5403`）；本轮未推送、未创建 PR、未部署。认证、多租户、公网部署和真实生产故障演练未执行。
# 独立浏览器状态矩阵补充（2026-08-02）

- 本轮已补齐并复验：390×844 移动端菜单抽屉、上下文底部面板、来源/笔记 Tab 点击、PDF 页码来源、Markdown 章节/段落/行号来源、格式校验失败、空文件索引失败、笔记保存失败前置状态、删除未确认保护，以及 1024×768/390×844 页面级无横向溢出。
- 本轮修复一个 UI 表现层绑定缺陷：生命周期按钮改为使用文档详情选择器作为输入，不再错误读取当前问答范围；同时修复移动端上下文 Tab 被推到面板外的问题。未修改生命周期服务、SQLite Schema、Qdrant 或真实数据。
- 最新质量结果：UI 定向测试 21 项通过；全量 pytest 86 项通过；`compileall` 和 `git diff --check` 通过。
- 仍未完成 UI-HF5 严格完成定义：上传传输中断、解析失败、完整加载中间态、外部服务不可用、数据库错误、问答失败、笔记保存成功和确认后的删除失败尚未在本轮安全临时浏览器夹具中逐项复现。当前仍为 `ready_for_review`，UI-HF6 不得进入。
- 上传空文件时再次观察到 `upload_progress?upload_id=undefined` 404；该日志未伪装为已修复，仍作为独立 Gradio 非阻塞风险记录。
## HF-R2：学习会话、消息时间线与 Composer 高保真落地（当前权威状态，2026-08-03）

- 状态：`ready_for_hf_r3`。HF-R2 已完成，未自动进入 HF-R3。
- 完成：真实会话历史受控展示、问题/回答时间线、真实来源数量提示、紧凑空状态、底部 Composer、三种视口检查和 UI 定向回归。
- 验证：UI 定向 25 项通过；全量 `pytest` 90 项通过；`compileall`、`git diff --check` 通过；隔离浏览器证据在 `output/ui-fidelity-recovery/hf-r2/`。
- 保持边界：未修改解析、RAG、Embedding、Qdrant、SQLite Schema、会话/笔记/引用/生命周期业务逻辑；未处理 Gradio 上传进度 404；未提交、推送、PR 或部署。
- 下一候选：HF-R3“文档库、工具栏、文档行与详情检查器高保真落地”，必须由负责人确认后执行。
