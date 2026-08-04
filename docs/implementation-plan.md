# 实现计划

## 当前计划：UI-REC4（已完成，2026-08-04）

状态：`completed`。下列工程步骤和负责人最终视觉审核均已完成；UI 高保真恢复任务至此结束，不自动启动新阶段。

1. 同步 UI-REC3 负责人视觉批准，将 UI-REC3 收敛为 `completed`。
2. 以冻结的 390×844 基准原位实现移动导航、来源/笔记底部面板和移动文档详情，不增加阶段式 CSS 尾部补丁。
3. 使用确定性真实回调夹具验证 PDF/Markdown 来源、当前会话笔记、详情和危险操作入口。
4. 完成 390×844 高保真对照、1024×768 结构校准和两个 1440×900 已批准页面回归。
5. 运行 UI 定向、全量测试、`compileall`、`git diff --check`、CSS 数量和敏感信息门禁并同步项目文档。
6. 负责人于 2026-08-04 明确确认 UI-REC4 最终视觉验收通过，状态收敛为 `completed`。

停止条件：已满足。当前权威计划没有 UI-REC5；历史 HF-R5、UI-R6、UI-R7 不再执行。最终 Git 收口已执行，UI 实现提交为 `c9f1a64`，文档收口提交为 `7cd53e9`，`main` 已推送至私有远程仓库；不创建 PR、不部署，也不自动启动其他产品任务。

## 历史计划：UI-REC3（2026-08-03）

1. 使用冻结的 1440×900 文档库基准和确定性临时 SQLite 夹具，固定同视口、同数据、同页面状态。
2. 原位调整文档库标题、上传/索引入口、搜索筛选工具栏、紧凑文档行和右侧详情检查器；不改变查询和生命周期业务语义。
3. 使用真实 Gradio HTML 点击事件连接文档行与既有详情选择器，使鼠标和键盘选择更新真实元数据，而非静态高亮。
4. 记录三栏、工具栏、列表与文档行几何；对 1024×768、390×844 只做结构回归。
5. 运行 UI 定向、全量测试、`compileall`、`git diff --check`、CSS 数量门禁、敏感信息检查和同屏视觉 QA。
6. 状态收敛为 `ready_for_review`，等待负责人审核 UI-REC3 文档库截图。

停止条件：实现和自动化门禁通过后停止；不自动进入移动端上下文高保真或下一阶段，不提交、不推送、不部署。

## 历史计划：UI-REC2（2026-08-03）

UI-REC2 已由负责人确认视觉校准通过，状态为 `completed`；其会话布局和 CSS 门禁继续作为稳定回归基线。

## 历史计划：UI-REC1（2026-08-03）

1. 将 `APP_CSS` 从 `ui.py` 抽离为唯一 `src/doc_qa/ui.css`，并纳入 Python 包资源。
2. 以唯一顶部栏、导航、主工作区、检查器布局根替换多代覆盖；只保留 1100px、760px 和 reduced-motion 媒体查询。
3. 通过 Gradio 实际 DOM 校准 `Column/Group/Form/Markdown/Button` 包装层，消除横向换列、表单白底和响应式容器失控。
4. 使用 UI-REC0 确定性夹具验证 1440×900、1024×768、390×844，并保存桌面文档库、桌面学习会话、移动抽屉和移动上下文证据。
5. 运行 UI 定向测试、全量测试、`compileall`、`git diff --check`；更新当前任务、路线图、进度、证据、设计规格和发布清单。

停止条件：UI-REC1 达到 `ready_for_review` 后停止；不自动进入逐页视觉细节实现，不提交、不推送、不部署。

## 历史计划：UI-REC0（2026-08-03）

1. 冻结现有 UI，不修改 `src/doc_qa/ui.py` 或追加 CSS。
2. 固定 Figma 图片、视口、数据状态和确定性浏览器夹具。
3. 收敛 `current-task.md` 为唯一当前状态，旧 UI 路线标记为历史。
4. 建立产物清理决策清单并修正 `.gitignore`。
5. 运行定向测试、全量测试、`compileall`、`git diff --check` 和敏感信息检查。
6. 只提交源码、测试、文档、冻结基线资产和依赖锁，创建本地恢复点。

停止条件：恢复点创建后停止；不执行 CSS/布局重构，不新增 UI 功能，不推送、不部署。

---

# 历史实现计划（非权威）

## HF-R4 后续实施计划（2026-08-03）

当前状态：`ready_for_hf_r5`。HF-R4 已完成真实 PDF/Markdown 来源卡、当前会话笔记卡、1024px 右侧抽屉与 390px 上下文底部面板。搜索、筛选、详情选择和生命周期入口继续使用既有业务语义；HF-R5 尚未执行。

1. **HF-R5**：以 Figma 并排截图为硬门禁完成视觉 QA，同时运行功能回归；测试结论与视觉结论分开记录。

技术原则：保留服务层与 Gradio 回调；必要时以受控展示层包装原生组件；不使用静态伪造数据；不改核心业务、数据库或 Qdrant。详见 `docs/project-management/ui-fidelity-recovery-task-card.md`。

# UI-HF5 实施收口（历史阶段，2026-08-02）

## UI-HF6 实施结果（2026-08-03）

- 状态：`ready_for_release_review`。
- 已完成：P0 结构重叠修复、Figma 高保真视觉 QA、1440×900 / 1024×768 / 390×844 浏览器验证、临时夹具来源/笔记验证、全量测试和文档收口。
- 测试：UI 定向 22 项通过，全量 87 项通过；`compileall` 和 `git diff --check` 通过。
- 仅修改 UI 表现层、CSS/布局和 UI 契约测试；未修改核心业务、数据库、Embedding 或 Qdrant。
- 保留风险：Gradio `upload_progress?upload_id=undefined` 404；笔记保存成功依赖外部 Embedding，本轮未进行真实外部服务调用。
- 下一阶段建议：UI-R6/UI-R7 最终回归和交付收口；不进入 UI-HF7。

- 状态：实现已完成、验收待收口；当前状态：`ready_for_review`。
- 已完成：1024×768 紧凑三栏布局、390×844 导航菜单抽屉、上下文底部面板、来源/笔记 Tab 移动端切换和 UI-HF5 状态契约。
- 验证：UI 定向测试 21 项、当前工作区全量测试 86 项、`compileall`、`git diff --check` 通过；三种视口截图已保存，横向溢出检查通过；上传动作仍记录 Gradio upload progress 404，不能写成 error/warn 为 0。
- 下一步规划：先补齐 UI-HF5 独立浏览器状态矩阵；UI-HF6 暂不得进入，本轮停止。

# 实现计划

> 文档职责：本文件只记录当前任务的执行计划、步骤、验证命令、完成状态和下一步；项目历史阶段与验证证据分别以 `roadmap.md`、`progress.md` 和 `evidence.md` 为准。

## UI-HF0 高保真差距审计收口（历史阶段记录，2026-08-02）

- 状态：已完成；后续 UI-HF1 已完成，当前进入 UI-HF2 前置等待。
- 基线：`docs/ui-high-fidelity-baseline.md`。
- 已完成：对照 Figma 与 UI-R5 截图，形成差距矩阵、Figma 尺寸基线、组件映射、业务语义保护规则、风险和 UI-HF1～UI-HF6 阶段门槛。
- 未完成：文档库、学习会话、上下文检查器和移动端的后续高保真实现。
- 本阶段未修改代码、测试、配置、数据库、Qdrant 或真实数据。

| 阶段 | 目标 | 状态 | 主要输出 |
| --- | --- | --- | --- |
| UI-HF0 | 高保真差距审计与实现基线 | 已完成 | `docs/ui-high-fidelity-baseline.md`、差距矩阵、组件映射 |
| UI-HF1 | 应用外壳与空间导航重构 | 已完成 | 顶栏、左侧导航、最近文档、主工作区骨架 |
| UI-HF2 | 文档库高保真工作区 | 已完成 | 工具栏、文档行、详情面板、生命周期视觉入口 |
| UI-HF3 | 学习会话与底部 Composer | 已完成 | 消息时间线、回答卡片、输入区 |
| UI-HF4 | 上下文检查器、来源与笔记 | 已完成 | Tab、PDF/Markdown 来源卡、笔记卡 |
| UI-HF5 | 响应式与状态落地 | 已完成 | 平板/移动抽屉、底部面板、状态矩阵 |
| UI-HF6 | 高保真视觉 QA 与收口 | 已完成，待最终发布回归 | P0 修复、对照截图、三视口回归、全量测试、文档收口 |

## UI-R5 最终验证补充（历史阶段记录，2026-08-02）

- UI 定向测试 13 项、全量测试 76 项通过；`compileall` 和 `git diff --check` 通过。
- 三种视口浏览器复核完成；原 UI-R6/UI-R7 尚未执行，现已延后至 UI-HF1～UI-HF5 高保真实现完成后作为最终回归门禁。

## 当前 UI 重设计任务：UI-HF5 实现完成，验收待收口

- 任务卡：`docs/project-management/ui-redesign-task-card.md`
- 当前状态：`ready_for_review`
- 当前阶段：UI-R0～UI-R5 原阶段功能性实现完成；UI-HF0～UI-HF4 已完成，UI-HF5 实现完成但状态验收待收口；UI-HF6 暂不执行。
- Figma 文件：`https://www.figma.com/design/TjKze3Fwc19gCADBrgtuzJ`
- UI-R1 参考规格：`docs/ui-redesign-reference-spec.md`
- UI-R2 设计证据：`output/figma-ui-r2/`
- 当前停止条件：本轮完成 UI-HF5 响应式实现，但未完成全部独立浏览器状态矩阵；不自动进入 UI-HF6。

| 阶段 | 目标 | 状态 | 输出 |
| --- | --- | --- | --- |
| UI-R0 | 复查旧 UI、确认结构性问题、建立独立任务卡 | 已完成 | 新任务卡、问题清单、范围和风险 |
| UI-R1 | 提取模板实际规格 | 已完成 | `docs/ui-redesign-reference-spec.md` |
| UI-R2 | 制作可审核 Figma 设计稿 | 已完成 | Figma 文件和 `output/figma-ui-r2/` 截图 |
| UI-R3 | 负责人设计评审 | 已完成 | 冻结默认入口、详情面板、上下文检查器和移动端策略 |
| UI-R4 | 应用外壳与主工作区实现 | 已完成 | `src/doc_qa/ui.py`、UI 定向测试、三视口截图 |
| UI-R5 | 文档库与上下文检查器深化 | 已完成 | 文档库/来源/笔记的独立深化与状态验证 |
| UI-R6 | 响应式与交互验收 | 待执行 | 三视口、可访问性、交互和状态矩阵 |
| UI-R7 | 独立视觉 QA 与文档收口 | 待执行 | QA 报告、全量回归和文档状态一致 |

本轮已完成 UI-R5 的 UI 表现层实现和验证；不自动执行 UI-R6/UI-R7。

## 历史 UI 美化任务：文档学习助手 UI 美化与设计系统收口

- 任务卡：`docs/project-management/ui-beautification-task-card.md`
- 当前阶段：UI-5 已完成；当前任务停止，等待负责人决定是否进入新的产品阶段
- 当前状态：`completed`（UI-0～UI-5 已完成）
- UI-0/UI-1/UI-2/UI-3/UI-4/UI-5 已完成。

| 阶段 | 目标 | 状态 | 主要验证/输出 |
| --- | --- | --- | --- |
| UI-0 | 现状审计与边界确认 | 已完成 | 三视口截图、DOM/源码审计、问题和风险清单 |
| UI-1 | Figma 参考提取与视觉方向确认 | 已完成 | Figma Chat 只读参考、不能照搬项、方向确认 |
| UI-2 | Design System、信息架构和核心页面规格 | 已完成 | `docs/design-spec.md`、UI 任务卡、组件/状态/响应式规格 |
| UI-3 | 应用外壳与一个核心页面实现 | 已完成 | `src/doc_qa/ui.py`、定向测试、三视口截图和 UI-3 实施记录 |
| UI-4 | 状态、响应式、可访问性和交互验收 | 已完成 | 11 项 UI 定向测试、76 项全量测试、三视口截图，以及输入校验、上传边界、解析、索引、外部服务、数据库、问答、删除、笔记和加载状态浏览器证据 |
| UI-5 | 独立视觉 QA、全量测试和文档收口 | 已完成 | QA 报告、全量门禁和文档状态一致 |

本 UI-3/UI-4/UI-5 阶段只允许修改 UI 表现层、UI 专用测试和设计证据；不得修改解析、RAG、数据层、配置、数据库或 Qdrant。UI-5 已完成。

## 当前任务：多文档与 Markdown 知识库管理

- 当前任务卡：`docs/project-management/task-card-multi-document-markdown.md`
- 当前状态：多文档任务卡 Phase 0～6 及后续方向 A、B、C 已完成；Git P0 已完成；本计划停止在当前任务收口，不自动执行后续阶段。
- 本计划中的 Phase 6 指多文档任务卡的全量质量门禁与交付收口；旧单 PDF 项目的历史 Phase 6 不在本计划中重复执行。

### 执行步骤

| 步骤 | 目标 | 状态 | 主要验证 |
| --- | --- | --- | --- |
| Step 0 | Phase 0 基线审计：Git、依赖、PDF、SQLite、Qdrant 和现有能力 | 已完成 | 基线审计记录、45 项原有回归测试 |
| Step 1 | Phase 1 统一规格、架构边界、迁移审查和测试矩阵 | 已完成 | 任务卡、架构、数据库设计和测试矩阵 |
| Step 2 | Phase 2 Markdown 解析、统一解析结果、分块和文档目录闭环 | 已完成 | 定向 9 项、全量 54 项、compileall、临时 SQLite integrity_check |
| Step 3 | Phase 3 多文档真实索引、文档切换和 `document_id` 隔离 | 已完成 | 真实 v4/1024、Qdrant 范围过滤、幂等和全量回归 |
| Step 4 | Phase 4 文档库 UI、问答范围切换、来源展示和会话/笔记隔离 | 已完成 | Gradio 5.50.0、真实 PDF/Markdown UI 验证、响应式截图、全量 67 项 |
| Step 5 | Phase 5 真实验收与独立 QA | 已完成 | 浏览器真实问答、来源、笔记、文档切换、响应式和异常场景已验证；全量 67 项通过 |
| Step 6 | Phase 6 全量质量门禁与交付收口 | 已完成 | 全量 67 项、compileall、diff check、health、Qdrant/SQLite 和敏感信息检查通过 |

### Phase 2 完成边界

- 已实现 Markdown 解析、统一解析协议、稳定 document/chunk identity、SQLite 目录元数据和状态管理。
- 未调用真实 Embedding，未写入 Qdrant，未修改真实 SQLite，未实现多文档真实检索隔离。
- 详细证据见 `docs/project-management/evidence.md`，当前进度见 `docs/project-management/progress.md`。

## 历史路线（只读，不属于当前实施计划）

## Phase 0：基线与审计

- 获取仓库并确认源码边界。
- 检查 PDF、Python、外部包和启动入口。
- 记录无 Git 元数据的风险。

## Phase 1：规格与评测

- 完成产品、技术栈、架构和 UI 规格。
- 建立 30～50 条评测问题。
- 设计 Embedding v3/v4 对比方案。
- 明确质量门禁和停止条件。

## Phase 2：文档摄入闭环

- [x] 实现单 PDF 解析、页级来源和结构化分块。
- [x] 实现显式 `text-embedding-v4`/1024 配置、适配器健康检查和分批调用。
- [x] 实现 Qdrant collection 隔离、维度校验、稳定 point ID 和幂等 upsert。
- [x] 实现索引报告、元数据完整性和分块/point 数量验证。
- [x] 使用真实 PDF 完成 171 页、262 分块的解析/分块和本地 Qdrant 闭环测试。
- [x] 使用真实百炼 v4 API 完成远程 Embedding 验证，返回 1024 维向量。
- [x] 使用 Docker Qdrant 完成首次索引和重复索引验证，262 个 points 保持幂等。

## Phase 3：问答闭环（已完成）

- [x] 检查 `qdrant-client==1.18.0` 的 `query_points` 检索 API。
- [x] 实现查询 `text-embedding-v4`/1024 适配和模型/维度校验。
- [x] 实现 Top-K、分数阈值、`document_id` 过滤和来源元数据返回。
- [x] 实现 DeepSeek OpenAI 兼容 API 适配、错误透明度和有限重试。
- [x] 实现基于检索片段的 JSON 回答和来源编号校验。
- [x] 实现 `doc_qa.cli ask`，不接入完整 UI。
- [x] 增加 Phase 3 测试，当前总测试 21 项通过。
- [x] 使用真实 v4 查询向量完成 Docker Qdrant 检索验证。
- [x] 配置本地 `DEEPSEEK_API_KEY` 并完成真实回答生成和最小基准问题验证。
- [x] 根据真实回答证据确认本阶段不启用 MQE/HyDE。
- [x] 增加 `DEEPSEEK_TRUST_ENV` 代理策略，默认不继承系统代理，保证标准命令可复现。

## Phase 4：学习闭环（已完成）

- [x] 实现 SQLite schema、外键、WAL、事务和索引。
- [x] 实现会话创建、恢复、问答历史和受限记忆上下文。
- [x] 实现问答来源快照持久化，保留 document_id、chunk_id、页码和 source_locator。
- [x] 实现笔记创建、查询、更新和来源关联校验。
- [x] 实现 `session_created`、`question_asked`、`answer_generated`、`no_results`、`note_created` 和 `note_updated` 事件。
- [x] 实现统计和确定性 JSON 报告，不使用 LLM 生成统计事实。
- [x] 增加 Phase 4 测试并完成真实 PDF 学习闭环验证。

## Phase 5：Gradio UI、响应式和人工验收（已完成）

- [x] 实现文档库、会话、问答、来源、笔记和学习统计页面。
- [x] 通过服务层调用文档摄入、问答和学习能力，UI 不直接操作 Qdrant、SQLite 或第三方 API。
- [x] 覆盖 empty、loading、normal、success、validation error、service error、no results、indexing failed、database error 和移动端折叠状态。
- [x] 验证 Gradio `5.50.0` 启动方式和现有 CLI 兼容性。
- [x] 使用真实基准 PDF 完成页面索引、事实问答、来源查看、笔记创建/更新、统计刷新和会话隔离。
- [x] 完成 1440×900、1024×768、390×844 浏览器视口检查并保存截图。
- [x] UI 定向测试 5 项通过，Phase 2/3/4 回归测试通过，总计 31 项。

## Phase 6：v3/v4 评测、质量门禁和交付收口（已完成）

- 对同一评测集执行 Embedding v3/v4 召回、来源准确性、回答正确性、速度和成本对比。
- 完成质量门禁、风险复盘、交付文档和最终人工验收。
## Phase 6 实际执行补充（已完成）

- 评测脚本只允许 v3 使用 `docqa_text-embedding-v3_dim1024_eval`，只允许 v4 使用 `docqa_text-embedding-v4_dim1024`。
- 评测前先核验 v4 的维度、point 数量和来源元数据；评测后再次核验，避免 v3 污染 v4。
- 自动指标用于初筛，不代替人工判断；报告必须记录每题检索结果、来源、回答、耗时和失败原因。
- DeepSeek 空响应已通过有限重试处理，并完成 q011 最小真实验证。
- v3/v4 完整评测、逐题证据复核、q016–q017 许可证来源修复和项目负责人确认均已完成。
- 本项目当前只完成交付准备设计，未执行部署、发布、提交或推送。

## Phase 7：交付准备、部署方案和可运维性建设（已完成）

- [x] 统一阶段状态、README、启动命令和环境变量说明。
- [x] 明确本地、测试和生产环境边界，以及密钥和日志脱敏规则。
- [x] 设计 Qdrant、SQLite、基准文档和评测结果的备份、恢复与校验流程。
- [x] 设计启动顺序、健康检查、有限重试、优雅关闭、故障排查和回滚流程。
- [x] 评估本地运行、Qdrant-only Compose 和应用容器化方案，明确当前推荐方案。
- [x] 设计日志、指标、错误追踪和成本监控字段，不记录密钥和完整敏感内容。
- [x] 完成部署前检查清单；未执行部署、发布、提交或推送。

## Phase 8：本地部署实施、运行时健康检查和可运维性验证（已完成）

- [x] 提供 Qdrant-only 本地 Compose 配置，不增加应用容器。
- [x] 提供只读 `health` CLI，检查配置、Qdrant healthz、v3/v4 collection 和 SQLite 完整性。
- [x] 提供 `backup-sqlite` CLI，使用 SQLite 原生 backup API 并校验备份。
- [x] 增加健康检查、错误分类、备份恢复和敏感信息保护测试。
- [x] 完成真实 `.env` 下的 health CLI 和现有 v4 collection smoke test。
- [x] 完成 Phase 8 全量回归和本地运行证据收口。

## 当前任务执行记录（截至 Phase 4）

### Phase 2 实际执行结果（2026-08-01）

- [x] 实现 Markdown 解析、统一解析结果和原始行号 source_locator。
- [x] 实现稳定 document_id/chunk_id、Embedding profile 元数据和 PDF 兼容回归。
- [x] 实现 SQLite documents 加法迁移审查的临时数据库验证和 DocumentCatalogService 状态管理。
- [x] 增加 9 项 Phase 2 定向测试；全量测试 54 项通过。
- [x] 确认未调用真实 Embedding、未写入 Qdrant、未修改真实 SQLite。
- [x] 经负责人确认后进入 Phase 3：多文档真实索引、文档切换和 document_id 隔离。

- [x] 完成四项范围边界确认：本地单用户、单一 v4 collection、`document_id` 隔离、Markdown 章节/段落/行号定位，以及第一阶段不做归档/删除。
- [x] 完成任务卡和阶段地图正式审批。
- [x] 完成 Phase 0：Git、依赖、PDF/Markdown、SQLite 文档目录、Qdrant 元数据、问答过滤和 UI 基线审计。
- [x] 完成 PDF/Markdown 统一解析协议、source_locator、文档状态和幂等策略设计。
- [x] 完成 SQLite `documents` 表兼容迁移、索引、约束、事务和回滚审查；未执行 Schema 变更。
- [x] 完成同一 v4 collection、document_id 过滤、文档切换和会话上下文隔离设计。
- [x] 完成 PDF/Markdown 文档库 UI 状态、响应式影响和测试矩阵设计。
- [x] 完成 Phase 1 文档质量检查；未修改业务代码、测试、Schema、真实配置或 Qdrant。
- [x] Phase 1 评审确认已完成，并已执行 Phase 2：解析与文档目录闭环；随后已确认进入 Phase 3。

### Phase 3 实际执行结果（2026-08-01）

- [x] `DocumentIngestionService.index_document()` 统一支持 PDF/Markdown，`index_pdf()` 保持兼容。
- [x] 真实 Markdown 使用 `text-embedding-v4`/1024 写入现有 `docqa_text-embedding-v4_dim1024` collection。
- [x] 重复 Markdown 索引返回 duplicate，不重复调用 Embedding，points 保持不变。
- [x] 实现 Qdrant 按 `document_id` 计数、指定范围过滤和全部文档范围验证。
- [x] 实现 `DocumentScopeState`，切换范围清空临时会话上下文、来源和待保存笔记状态。
- [x] 对历史 PDF points 只补齐 payload 元数据，不重建向量、不改变 point ID。
- [x] 新增 Phase 3 多文档、失败隔离、元数据补齐和范围状态测试；全量测试 59 项通过。
- [x] 真实验证结果：PDF 262 chunks、Markdown 5 chunks；v4 collection 262 → 267 points，重复执行仍为 267；指定范围和 all-documents 范围均通过。
- [x] Phase 3 完成定义满足；随后经负责人确认进入并完成 Phase 4 UI。

## 多文档与 Markdown 任务：Phase 4 UI 实际执行（已完成，2026-08-01）

- [x] Gradio 文档库支持 PDF、Markdown 和 `.markdown` 上传，并执行扩展名、文件存在性和空文件校验。
- [x] 文档表展示格式、短 document_id、状态、页数或 Markdown 单元数、分块、points、定位方案、更新时间和脱敏错误。
- [x] 问答范围支持全部文档和指定 document_id；范围切换清空回答、来源、待保存笔记和临时上下文。
- [x] Markdown 来源允许空页码并展示章节/段落/行号；PDF 保持页码和 source_locator。
- [x] UI 通过现有服务层调用摄入、问答、学习和统计能力，不直接访问 Qdrant、SQLite 或第三方 API。
- [x] Gradio 5.50.0 页面完成 1440×900、1024×768、390×844 浏览器检查并保存截图。
- [x] 新增 UI 定向测试 7 项；Phase 2/3/4 回归测试通过。
- [x] 真实 Markdown 重复上传验证为 duplicate，未新增 points；v4 collection 保持同一模型和 1024 维。
- [x] 修复旧版 SQLite `citations.page_start/page_end NOT NULL` 与 Markdown 空页码引用不兼容的问题；兼容迁移保留既有引用数据。
- [x] 真实 Markdown 问答保存并重新读取引用成功，`source_locator` 保留章节、段落和行号；全量测试最终 64 项通过。

## 后续独立方向执行计划（2026-08-01）

### 方向 A：Gradio 上传进度 404

- [x] 隔离确认 5.50.0 和 5.49.1 均可复现。
- [x] 隔离验证 6.22.0；现有 Chatbot `type` 参数不兼容，保留 5.50.0。
- [x] 完成真实浏览器上传日志记录；不宣称控制台错误已修复。

### 方向 B：文档生命周期管理

- [x] 完成生命周期任务卡、规格和测试矩阵。
- [x] 完成状态机、Qdrant 删除条件、SQLite 事务边界、历史关联保护和失败窗口审查。
- [x] 实现服务、Qdrant 删除/一致性检查、临时存储测试；真实生产删除操作不执行。

### 方向 C：知识库可用性增强

- [x] 完成搜索、筛选、排序、详情和错误反馈规格。
- [x] 实现 UI 和 document_id/来源/会话/笔记隔离回归。

### 后续方向完成证据

- 方向 A/B/C 与 Git P0 收口阶段全量 pytest 为 73 项；当前 UI-4 回归全量 pytest 为 76 项通过，compileall 通过。
- 方向 C 真实 UI 在 1440x900、1024x768、390x844 通过加载和响应式复验。
- Git P0 和提交已完成，提交为 `f3c5403`；未推送、未创建 PR、未部署，也未执行真实文档删除。

### Phase 4 结果（历史记录）

Phase 4 完成定义满足；下一步等待确认进入 Phase 5 独立 QA。本轮未执行 Phase 5。
## UI-5 最新实施状态（2026-08-02）

- 状态：`completed`。
- UI-5 独立视觉 QA、三种视口、可访问性、交互语义回归、全量测试和文档收口已完成。
- 仅修改 UI 表现层 CSS：Gradio 内部容器/表格深色主题和长文件名断行；核心解析、RAG、SQLite、会话、笔记、生命周期和 Qdrant 未修改。
- 当前全量测试为 76 项通过；73 项为历史基线。UI-5 完成后停止，不自动进入新阶段。
# UI-HF5 独立状态矩阵补充（2026-08-02）

- 已完成本轮安全浏览器复验：格式拒绝、空文件索引失败、PDF/Markdown 来源定位、笔记保存失败、删除确认保护、移动端菜单/上下文底部面板、来源/笔记 Tab 和页面宽度检查。
- 修复：生命周期事件绑定文档详情选择器；移动端实际可访问 Tab 导航不再越出上下文面板。
- 结果：定向 21 项、全量 86 项通过，`compileall` 和 `git diff --check` 通过；UI-HF5 仍 `ready_for_review`，未进入 UI-HF6。
## HF-R2 实现收口（2026-08-03）

HF-R2 仅修改 `src/doc_qa/ui.py` 的展示层和 `tests/test_phase5_ui.py` 的 UI 契约测试。实现方式为保留原 `UIController`、会话 state、`controller.ask`、`document_filter` 和来源/笔记回调；新增由真实 chat history、answer status、citations 驱动的时间线 HTML 展示层，并把原生 Chatbot 降为不可见状态承载组件。未变更业务服务层或数据层。

后续顺序：HF-R3 文档库/详情检查器 → HF-R4 来源、笔记与移动端 → HF-R5 Figma 对照与真实状态 QA。HF-R2 已完成但不代表整体高保真验收完成。
