# 发布与恢复检查清单

## UI-REC4（2026-08-03～2026-08-04）

- [x] 390×844 导航、来源/笔记 390px 底部面板和文档详情 `390×836` 全屏面板使用确定性真实回调数据完成浏览器验收。
- [x] PDF 来源保留第 6 页；Markdown 来源保留第 3 章、段落 2、行 11-14；没有修改 `source_locator` 语义。
- [x] 笔记保存使用临时 SQLite 与现有回调，保存成功、会话关联和文档关联可追溯。
- [x] 1024×768 按钮式菜单和导航抽屉可操作；1440×900 学习会话与文档库无结构回归。
- [x] 1440×900、1024×768、390×844 无页面级溢出；浏览器 console error/warn 为 0。
- [x] 来源/笔记 Tab 与关闭按钮达到 44px 触控目标；状态不只依赖颜色。
- [x] UI 定向 30 项、全量 95 项、`compileall`、`git diff --check` 和 CSS 数量门禁通过。
- [x] 未修改解析、RAG、Embedding、Qdrant、SQLite Schema、会话/笔记/生命周期业务语义或真实数据。
- [x] 负责人最终视觉批准：已于 2026-08-04 明确确认“UI-REC4 最终视觉验收通过”，阶段状态为 `completed`。
- [x] UI 高保真恢复路线收口：UI-REC0～UI-REC4 全部完成；当前权威路线没有 UI-REC5，历史 HF-R5、UI-R6、UI-R7 不再执行。
- [x] 本地 Git 收口：UI 实现提交为 `c9f1a64`，文档由独立收口提交保存；精确暂存、staged diff 和敏感信息检查通过。
- [ ] 推送、PR、部署：均未执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，本阶段未处理。

## UI-REC3（2026-08-03）

- [x] 1440×900 文档库使用确定性临时 SQLite 的 PDF、Markdown 和归档文档真实记录。
- [x] 标题、上传/索引入口、搜索筛选工具栏、紧凑文档行和右侧详情检查器层级收敛。
- [x] 文档行可通过鼠标和键盘选择，并更新真实 Gradio 详情状态；不是静态伪选中。
- [x] 完整 `document_id`、hash、格式、统计、定位方案、错误详情和生命周期入口可访问。
- [x] 搜索/筛选/排序不修改 `document_filter`，生命周期确认与失败保护语义不变。
- [x] 1440×900 无横向/全局纵向溢出和栏间重叠；1024×768、390×844 无横向溢出。
- [x] UI 定向 30 项、全量 95 项、`compileall`、`git diff --check`、CSS 数量和敏感信息门禁通过。
- [x] 并排证据已生成：`output/playwright/ui-rec3-library-comparison-1440x900.png`；实现方 Design QA 为 passed。
- [x] 负责人反馈中的上传双层错位和最近文档下沉已修正；学习会话提问、来源更新和复制回答已在隔离浏览器复核可用。
- [x] 负责人 UI-REC3 Figma 并排批准：已于 2026-08-03 明确通过，UI-REC3 状态为 `completed`。
- [x] UI-REC4 移动端上下文高保真与最终视觉收口：工程、证据和负责人最终视觉批准均已完成，状态为 `completed`。
- [ ] Git 提交、推送、PR、部署：均未执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，本阶段未处理。

## UI-REC2（2026-08-03）

- [x] 1440×900 学习会话完成态使用确定性真实回调数据；问题、回答、PDF/Markdown 来源和笔记均可追溯。
- [x] 标题区、真实范围、文字状态和蓝色“新会话”层级收敛；未显示完整 `session_id`。
- [x] 消息时间线内部滚动，Composer 以 93px 一体式输入面完整位于首屏。
- [x] 文档无横向/全局纵向溢出，关键区域无重叠，浏览器 error/warn 为 0。
- [x] 1024×768、390×844 结构回归无横向溢出，未扩大为两视口高保真实现。
- [x] UI 定向 29 项、全量 94 项通过；CSS 为 162 个 `!important`、3 个 `@media`。
- [x] 负责人反馈校准已完成：移除双层光晕和消息阴影，统一字体/14px 圆角/尺寸比例，侧栏与最近文档减重，来源检查器补齐真实笔记预览和当前范围。
- [x] 第二轮反馈校准已完成：范围控件胶囊化、来源/笔记 Tab 边界统一、成功勾选移除、回答复制按钮和真实回合时间可用。
- [x] 第三轮反馈校准已完成：范围控件固定为 132×36px；来源/笔记 Tab 使用 34px 单一内描边容器和上下各 2px 的对称内衬。
- [x] 1024px 检查器变量实测为 300px、390px 顶栏变量实测为 56px；Gradio 媒体查询变量前缀问题已修复。
- [x] 未修改核心业务、数据库、Embedding、Qdrant、真实数据或来源定位语义。
- [x] 负责人已确认视觉校准通过，UI-REC2 状态为 `completed`。
- [x] 文档库高保真已进入 UI-REC3 并完成实现；移动端上下文高保真未执行。
- [ ] Git 提交、推送、PR、部署：本阶段均未执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，本阶段未处理。

## UI-REC1（2026-08-03）

- [x] `src/doc_qa/ui.css` 成为唯一运行时样式权威，`ui.py` 不再包含多代大段内嵌 CSS。
- [x] `pyproject.toml` 已包含 `ui.css` 包资源声明。
- [x] 桌面、平板、移动端布局职责唯一；未恢复历史 UI-R/UI-HF/HF-R 级联标记。
- [x] 1440×900、1024×768、390×844 隔离浏览器无页面级横向溢出；文档检查器、移动菜单和上下文面板结构可用。
- [x] UI 定向 28 项、全量 93 项、`compileall`、`git diff --check` 通过；浏览器 error/warn 为 0。
- [x] 未修改解析、RAG、Embedding、Qdrant、SQLite Schema、会话、笔记、引用和生命周期业务逻辑。
- [ ] Figma 高保真视觉验收：UI-REC1 仅完成 CSS 架构重置，尚未通过。
- [ ] Git 提交、推送、PR、部署：本阶段均未执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，本阶段未处理。

## UI-REC0（2026-08-03）

- [x] 当前 UI 冻结，不再追加 CSS 或新建视觉实现阶段。
- [x] 三张 Figma 视觉基线已进入 `docs/assets/ui-visual-baseline/`。
- [x] 确定性临时浏览器夹具已进入 `tests/fixtures/`。
- [x] E 盘与项目产物已形成清理决策清单，本阶段未删除文件。
- [x] `.gitignore` 已覆盖实际 `output/`、`.playwright-cli/` 和 `*.egg-info/`。
- [x] 隔离夹具 HTTP 200；UI 定向 28 项、全量 93 项、`compileall` 和 `git diff --check` 通过。
- [x] 高置信敏感信息检查通过，`.env` 未进入提交范围。
- [x] 以本任务本地提交建立恢复点；未推送、未创建 PR、未部署。
- [ ] Figma 高保真视觉验收：当前仍未通过。
- [ ] 推送、PR、部署：禁止执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，本任务不处理。

---

# 历史发布与视觉验收记录（非权威）

## HF-R4 发布/视觉验收状态（2026-08-03）

## HF-R4 阶段验收（2026-08-03）

- [x] 真实 PDF 来源保留文档名、页码、片段和原始引用展开入口。
- [x] 真实 Markdown 来源保留文档名、章节、段落、行号、片段和原始引用展开入口。
- [x] 来源/笔记 Tab、笔记空状态、保存、更新、成功、失败和前置条件保留文字表达。
- [x] 当前会话笔记展示不会混入其他会话数据。
- [x] 1024×768 右侧检查器抽屉和 390×844 上下文底部面板可打开。
- [x] UI 定向 28 项、全量 93 项测试、`compileall` 和 `git diff --check` 通过。
- [ ] Figma 整体高保真验收：HF-R5 尚未执行。
- [ ] Git 提交、推送、PR、部署：本阶段未执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，未处理。

## HF-R3 阶段验收（历史记录）

- [x] 文档库已成为独立主工作区；上传、索引、搜索、筛选、排序和真实文档行均可访问。
- [x] 完整 `document_id`、hash、统计、错误详情和既有生命周期入口位于当前选择文档的右侧检查器。
- [x] 搜索/筛选仅影响列表；浏览器验证确认 `document_filter` 问答范围未被写入。
- [x] PDF `pdf-page-v1` 与 Markdown `markdown-heading-line-v1` 均在真实详情中可见。
- [x] 1440×900、1024×768、390×844 隔离浏览器无页面级横向溢出；移动端无不可读多列表格。
- [x] UI 定向 27 项、全量 92 项测试、`compileall` 和 `git diff --check` 通过。
- [ ] Figma 整体高保真验收：尚未通过；HF-R4 和 HF-R5 尚未执行。
- [ ] Git 提交、推送、PR、部署：本阶段未执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，未处理。

- [x] Figma Review v1 与当前真实浏览器页面完成独立对照审计。
- [x] 已建立 P0 阻塞清单、视觉契约、HF-R0～HF-R5 任务卡与证据路径。
- [x] HF-R1 外壳/P0 门禁：导航无重叠、短会话状态无横滚、默认页脚隐藏、三种视口无页面级横向溢出。
- [ ] 高保真视觉验收：**尚未通过**；HF-R2～HF-R5 未执行，不能以 HF-R1 或功能测试替代。
- [ ] Git 提交、推送、PR、部署：本任务未执行。
- [ ] Gradio `upload_progress?upload_id=undefined` 404：独立非阻塞技术债务，未处理。

# UI-HF5 发布前收口（历史阶段，2026-08-02）

## 历史 UI-HF6 发布前收口（2026-08-03；不作为当前视觉结论）

- [x] P0 会话头部与移动上下文检查器结构重叠修复。
- [x] 1440×900、1024×768、390×844 三视口浏览器验证，无明显横向溢出。
- [x] 文档库、移动导航、回答时间线、PDF/Markdown 来源卡片、来源/笔记 Tab 和笔记失败状态有独立证据。
- [x] UI 定向测试 22 项、全量测试 87 项通过。
- [x] `compileall` 和 `git diff --check` 通过。
- [ ] 笔记保存成功依赖外部 Embedding，本轮未在安全夹具中配置真实密钥或伪造成功；需在具备安全测试服务时补充浏览器证据。
- [ ] Gradio `upload_progress?upload_id=undefined` 404 仍未修复，作为独立非阻塞技术债务。
- [ ] UI-R6/UI-R7、UI-HF7、Git 提交/推送/PR/部署、认证、多租户、公网部署和真实生产故障演练未执行。

- [x] 1024×768 平板端三栏层级、主工作区和上下文区域保持可理解，未出现页面级横向溢出。
- [x] 390×844 移动端提供导航菜单抽屉、上下文底部面板和来源/笔记 Tab；文档库、学习会话和上下文入口可切换。
- [x] 状态文字、控件标签、禁用/空状态和错误脱敏规则保持；PDF/Markdown 来源定位语义未改变。
- [x] 1440×900、1024×768、390×844 浏览器检查完成；截图和复现步骤保存至 `output/playwright/`，当前临时实例 error/warn 为 0。
- [x] UI 定向测试 21 项、当前工作区全量测试 86 项、`compileall`、`git diff --check` 通过；79 项标记为上一阶段历史基线。
- [ ] 上传/解析/索引/问答/外部服务/数据库/删除/笔记失败等异步和故障状态尚未逐项完成本轮三种视口浏览器重放；UI-HF5 当前为 `ready_for_review`。
- [x] UI-HF6 已执行并完成本轮 P0、视觉 QA、三视口和回归门禁；历史 UI-HF5 清单不再作为当前状态。
- [ ] 未提交、未推送、未创建 PR、未部署；Gradio upload_progress 404 仍为非阻塞技术债务。

## UI-HF4 发布前收口（历史阶段记录，2026-08-02）

- [x] 上下文检查器内层统一深色表面，来源/笔记 Tab 可切换且选中态明确。
- [x] PDF 来源卡片显示页码；Markdown 来源卡片显示章节、段落和行号；完整 locator 可见。
- [x] 笔记内容标签、保存状态、保存前置条件和笔记列表已接入现有回调。
- [x] 1440×900、1024×768、390×844 浏览器检查通过，无横向溢出；console error/warn 为 0。
- [x] UI 定向测试 19 项、全量测试 79 项、`compileall`、`git diff --check` 通过。
- [ ] UI-HF5～UI-HF6 尚未执行；UI-HF5 为下一阶段规划。
- [ ] 未提交、未推送、未创建 PR、未部署；Gradio upload_progress 404 仍为非阻塞技术债务。

# UI-HF2 发布前收口（历史阶段记录，2026-08-02）

# UI-HF1 发布前收口（历史阶段记录，2026-08-02）

# 交付收口清单

## 新 UI 重设计任务启动状态（2026-08-02）

## UI-HF0 高保真差距审计（历史阶段记录，2026-08-02）

- [x] 已对照 Figma 桌面端会话、文档库、移动端会话和上下文面板截图。
- [x] 已对照 UI-R5 当前桌面端会话、文档库、平板和移动端截图。
- [x] 已形成 `docs/ui-high-fidelity-baseline.md`，记录差距矩阵、组件映射、业务语义保护和 UI-HF1～UI-HF6 阶段门槛。
- [x] 已确认原 UI-R4/UI-R5 的功能性实现完成，不将其误写为 Figma 高保真完成。
- [x] 已确认 UI-HF0 未修改 Python、CSS、测试、配置、数据库、Qdrant 或真实数据。
- [x] UI-HF1 已执行并完成；UI-HF2～UI-HF6 尚未执行。
- [ ] 原 UI-R6/UI-R7 最终回归尚未执行，需等高保真实现完成后执行。

- [x] 已根据负责人体验反馈确认上一轮 UI 的结构性不足。
- [x] 已创建独立任务卡 `docs/project-management/ui-redesign-task-card.md`。
- [x] 已确认使用 `longchenust's team` 创建 Figma 文件。
- [x] 已创建 Figma 文件 `https://www.figma.com/design/TjKze3Fwc19gCADBrgtuzJ`。
- [x] UI-R1 模板规格提取完成，参考规格记录于 `docs/ui-redesign-reference-spec.md`。
- [x] UI-R2 Figma 设计稿完成，保存桌面端、移动端和上下文面板截图。
- [x] UI-R3 负责人 Figma 设计评审完成，设计基线和交互策略已冻结。
- [x] UI-R4 应用外壳与主工作区实现、UI 定向测试和三视口初步浏览器检查完成。
- [x] UI-R5 文档库与上下文检查器深化、文档详情、来源/笔记 Tab 和最近文档动态刷新完成。
- [ ] UI-R6 响应式、可访问性和交互独立验收尚未执行。
- [ ] UI-R7 独立视觉 QA、全量回归和最终文档收口尚未执行。
- [x] 已明确本轮不修改核心业务、数据库、Qdrant、真实数据或生产配置。

> 本清单前部针对原单 PDF 项目的 Phase 6～8 交付基线；当前多文档任务的活动状态以 `docs/project-management/current-task.md`、`roadmap.md` 和 `implementation-plan.md` 为准。多文档任务卡 Phase 2～6 已完成；Gradio 上传进度 404 仍为非阻塞依赖风险。

## 历史 UI 美化任务收口状态（2026-08-02）

- [x] UI-0 现状审计完成，保存三视口和 Figma 参考证据。
- [x] UI-1 Figma 参考提取和“深色知识工作台 + Zinc + 蓝色主交互”方向确认完成。
- [x] UI-2 Design System、信息架构、核心页面、组件树、状态和响应式规格已写入设计文档。
- [x] UI-2 负责人设计评审已完成，Design Tokens 和页面规格作为 UI-3 基线。
- [x] UI-3 应用外壳和文档库核心页面实现完成，保留现有业务语义。
- [x] UI-3 定向测试 15 项通过，`compileall` 通过，三种视口浏览器截图和无横向溢出证据已保存。
- [x] UI-4 主体验收、三种视口、可访问性、交互和所有可安全复现状态的受控浏览器验收已完成；生产级故障演练未执行且不作为 UI 验收前提。
- [x] UI-5 独立视觉 QA、全量测试和文档收口已完成。

## 多文档与 Markdown 任务 Phase 6 收口

- [x] 任务卡、路线图、进度、证据、实现计划和 README 状态已统一。
- [x] 67 项 Phase 6 基线测试保持通过；方向 A/B/C 与 Git P0 收口时全量 pytest 为 73 项，当前 UI-4 回归全量 pytest 为 76 项通过。
- [x] compileall、`git diff --check`、敏感信息扫描通过。
- [x] Qdrant healthz HTTP 200；v4 collection 267 points、1024 维；PDF/Markdown document_id 隔离。
- [x] v4 point 来源元数据完整，未混用 v3 或测试向量。
- [x] SQLite integrity check 通过。
- [x] Git P0 和本地提交已完成，提交为 `f3c5403`；未推送、未创建 PR、未部署，这些操作仍需负责人单独确认。
- [ ] Gradio 上传进度 404 尚未在依赖升级环境中消除，保留为非阻塞风险。

## 后续方向执行状态（2026-08-01）

- [x] 方向 A 已完成隔离调查并保留 5.50.0 稳定版本；404 未伪装为已修复。
- [x] 方向 B 规格、架构边界、实现和临时存储测试已完成；真实生产删除操作未执行。
- [x] 方向 C 搜索、筛选、排序、详情和错误展示已实现并完成 UI 回归。
- [x] Git P0 和本地提交已完成，提交为 `f3c5403`。
- [ ] 推送、PR、部署、认证、多租户和公网部署未执行。

## 最终风险记录（2026-08-01）

- 产品功能：多文档、Markdown、生命周期管理、知识库可用性增强和 UI-3 已完成；当前 UI-4 回归全量 pytest 76 项通过，73 项为历史阶段基线。
- 技术债务：Gradio `upload_progress?upload_id=undefined` 404 在 5.50.0/5.49.1 中仍可复现；6.22.0 对当前 UI 存在启动回归，暂不升级。
- 数据安全：生命周期删除只在临时 SQLite/Qdrant 中验证；未删除真实生产文档、真实生产 Qdrant points，也未执行生产恢复演练。
- 运行时边界：当前为本地单用户应用，未配置认证、用户系统、租户隔离、访问控制或公网部署能力。
- 交付状态：Git P0 已完成并提交；未推送、未创建 PR、未部署。

## 新 UI 重设计 UI-R4 收口（2026-08-02）

- [x] 应用外壳、空间导航、主工作区、问答 Composer 和上下文检查器已实现。
- [x] 文档库上传/索引入口、搜索/筛选、详情/生命周期入口和问答范围选择已保留。
- [x] UI 定向测试 11 项、全量测试 76 项、`compileall` 和 `git diff --check` 通过。
- [x] 1440×900、1024×768、390×844 初步浏览器检查完成；安全临时实例无横向溢出，控制台 error/warn 为 0。
- [x] 未修改核心业务、数据库、Qdrant、真实数据、生产配置或 Gradio 404 依赖问题。
- [x] UI-R4 历史收口已完成；后续 UI-R5 已执行并完成，当前等待 UI-R5 评审。

## UI-R5 最终验证补充（2026-08-02）

- [x] UI 定向测试 13 项、全量测试 76 项、`compileall` 和 `git diff --check` 通过。
- [x] 1440×900、1024×768、390×844 浏览器复核完成；无横向溢出，浏览器 error/warn 为 0。
- [x] 文档库导航、搜索列表过滤、来源/笔记 Tab、详情与生命周期入口和移动端学习会话布局已复核。
- [ ] UI-R6、UI-R7 尚未执行；当前状态为 `ready_for_review`。

## Phase 6 状态（历史基线）

- [x] v3/v4 使用同一份 30 题评测集。
- [x] v3 collection 与 v4 collection 隔离。
- [x] v4 评测前后保持 262 points、1024 维、来源元数据完整。
- [x] 生成 JSON 原始结果和 Markdown 报告。
- [x] 全量自动化测试 38 项通过。
- [x] 结果与文档未发现密钥模式。
- [x] DeepSeek 空响应已增加有限重试策略并通过测试。
- [x] 30 题逐题证据复核已记录，结果见 `eval/results/embedding-v3-v4-manual-review.md`。
- [x] q023–q028 的严格文档范围政策已由项目负责人确认，不再作为 `uncertain` 项。
- [x] Phase 6 质量门禁全部通过；本轮仍不执行部署、发布、提交或推送。

当前建议默认模型：`text-embedding-v4`。
## 原单 PDF 项目最新收口状态（历史基线，2026-07-31）

- [x] DeepSeek 空响应有限重试已实现并有测试。
- [x] q011 真实验证成功。
- [x] 最新完整 v3/v4 评测无失败题。
- [x] v3/v4 collection 隔离、维度和 point 数量通过检查。
- [x] 逐题证据复核文件已生成。
- [x] q016–q017 许可证事实题均召回并引用 PDF 第 4 页。
- [x] q023–q028 严格文档范围政策已由项目负责人确认。
- [x] 项目负责人已完成最终人工确认，Phase 6 收口完成。
- [ ] 尚未执行部署、发布、提交或推送。

## 原单 PDF 项目 Phase 7 交付准备状态（历史基线）

- [x] 已检查 Git 基线；当前工作区保留用户已有未提交修改，本阶段不提交。
- [x] 已统一 `docs/implementation-plan.md` 中 Phase 6 的历史状态。
- [x] 已完成 local/test/production 配置边界和密钥管理规则。
- [x] 已完成 Qdrant、SQLite、文档和评测结果备份恢复设计。
- [x] 已完成启动顺序、healthz、有限重试、优雅关闭、排障和回滚设计。
- [x] 已评估本地 Python、Qdrant-only Compose 和应用容器化；当前推荐本地 Python + Docker Qdrant。
- [x] 已完成日志、指标、错误追踪和成本监控字段设计。
- [x] README、`.env.example`、部署/运维文档已补齐。
- [ ] 实际部署、发布、公网暴露、提交和推送：本阶段明确不执行。

## 原单 PDF 项目 Phase 7 阻塞条件（历史基线）

- Docker Desktop Linux Engine 的历史连接问题已解除；当前已通过 Qdrant healthz，后续运行仍必须先执行健康检查。
- 应用暂无独立健康端点；在补齐认证、访问控制、Secret Manager、持久化恢复演练和多实例存储前，不得作为公网生产服务。

## 原单 PDF 项目 Phase 8 本地运行时状态（历史基线）

- [x] Docker Desktop 已恢复，`docqa-qdrant` healthz 返回 HTTP 200。
- [x] v3/v4 collection 均为 green、262 points、1024 维。
- [x] 新增 Qdrant-only `docker-compose.local.yml`，不增加应用容器；HTTP healthz 由 `health` CLI 验证。
- [x] 新增 `health` CLI，失败时返回非零退出码且不输出密钥。
- [x] 新增 `backup-sqlite` CLI，备份后执行完整性检查。
- [x] 新增 7 项 Phase 8 定向测试。
- [x] 真实 `.env` health CLI、v4 collection smoke test 和 SQLite 备份恢复均已通过。
- [x] Phase 8 最终全量质量门禁和任务文档收口完成。
- [x] 未执行生产部署、公网暴露、提交或推送。
## UI-5 发布收口记录（2026-08-02）

- [x] 独立视觉 QA：1440×900、1024×768、390×844。
- [x] 可访问性、交互和业务语义回归完成。
- [x] UI 定向测试 17 项、全量测试 76 项通过。
- [x] `compileall` 和 `git diff --check` 通过。
- [x] UI-5 截图和复现步骤已保存至 `output/playwright/`。
- [x] 文档状态已收口；73 项明确为历史基线。
- [x] Gradio `upload_progress?upload_id=undefined` 404 仍按非阻塞技术债务记录，未宣称修复。
- [x] Git P0 已完成（`f3c5403`）；本轮未推送、未创建 PR、未部署。
- [x] 认证、多租户、公网部署和真实生产故障演练未执行。
# UI-HF5 状态矩阵补充（2026-08-02）

- [x] 重新验证格式失败、空文件索引失败、PDF/Markdown 来源定位、笔记保存失败、删除未确认保护、移动端菜单/上下文面板和来源/笔记 Tab。
- [x] 修复 UI-HF5 浏览器发现的两个表现层问题：生命周期操作读取文档详情选择器；移动端 Tab 导航越界。
- [x] UI 定向测试 21 项、全量 pytest 86 项、`compileall`、`git diff --check` 通过。
- [ ] 上传传输中断、解析失败、完整加载中间态、外部服务/数据库/问答失败、笔记成功和确认后的删除失败尚未逐项完成安全浏览器证据；UI-HF5 仍为 `ready_for_review`。
- [ ] UI-HF6 尚未执行；Gradio `upload_progress?upload_id=undefined` 404 仍为独立非阻塞技术债务。
## UI 高保真恢复：HF-R2 检查记录（2026-08-03）

- [x] 学习会话标题、范围、状态、时间线与 Composer 已按 Figma 基线进行受控展示层重构。
- [x] 不展示内部 session ID；不伪造答案、来源或笔记。
- [x] 隔离浏览器验证：1440×900、1024×768、390×844 无横向溢出；移动端菜单可进入会话。
- [x] UI 定向测试 25 项、全量测试 90 项、`compileall`、`git diff --check` 通过。
- [ ] HF-R3 文档库与详情检查器高保真落地。
- [ ] HF-R4 来源、笔记、平板/移动上下文高保真落地。
- [ ] HF-R5 Figma 对照视觉 QA、真实有数据状态验收与最终文档收口。
- [ ] Gradio `upload_progress?upload_id=undefined` 404 独立技术债务处理（不属于本任务）。
