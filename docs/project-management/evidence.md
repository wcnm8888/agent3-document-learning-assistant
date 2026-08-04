# 项目证据

## UI-REC4 移动端上下文与最终回归证据（2026-08-03～2026-08-04）

| 项目 | 证据 |
| --- | --- |
| 确定性状态 | `tests/fixtures/ui_visual_baseline.py` 提供临时 SQLite 中的索引文档、真实回调问答、PDF/Markdown 来源和当前会话笔记；未使用或删除生产数据与真实 Qdrant points。 |
| 390×844 学习会话 | `output/playwright/ui-rec4-mobile-session-390x844.png`；页面 `scrollWidth/scrollHeight=390/844`，导航菜单可打开并在选择页面后关闭。 |
| 移动来源面板 | `output/playwright/ui-rec4-mobile-context-sources-390x844.png`；底部面板边界 `x=0, y=454, w=390, h=390`；PDF 显示 Happy-LLM 第 6 页，Markdown 显示第 3 章、段落 2、行 11-14。 |
| 移动笔记面板 | `output/playwright/ui-rec4-mobile-context-notes-390x844.png`；使用真实保存回调写入临时 SQLite，状态显示“笔记已保存”，笔记仍绑定当前会话和 `fixture-pdf-happy-llm`。 |
| 移动文档详情 | `output/playwright/ui-rec4-mobile-document-detail-390x844.png`；全屏面板边界 `x=0, y=8, w=390, h=836`，完整 `document_id`、hash、统计、定位方案和生命周期入口可访问；开启时菜单触发器隐藏。 |
| 触控与可访问性 | 来源/笔记 Tab 均为 `174×44px`，关闭按钮为 `44×44px`；状态有文字，错误/定位说明不只依赖颜色，Markdown 明确不伪装成页码。 |
| 1024×768 | `output/playwright/ui-rec4-regression-tablet-1024x768.png` 与 `ui-rec4-tablet-context-1024x768.png`；页面无溢出，菜单触发器为按钮式入口，导航抽屉打开后边界为 `280×768`，检查器打开时为 `300×616`。 |
| 桌面回归 | `output/playwright/ui-rec4-regression-session-1440x900.png`、`ui-rec4-regression-library-1440x900.png`；页面 `1440×900`，工作区 `1392×790`，会话 Composer 底边约 `865px`，文档库与检查器无结构回归。 |
| 浏览器日志 | 隔离浏览器 console errors 0、warnings 0；三种视口均无页面级横向或全局纵向溢出。 |
| 自动化与质量 | `tests/test_phase5_ui.py` 30 项通过；全量 `pytest` 95 项通过；`compileall src tests`、`git diff --check` 通过。 |
| CSS 架构 | `src/doc_qa/ui.css` 2481 行、162 个 `!important`、3 个 `@media`；仍是唯一运行时样式权威，未恢复 UI-R/UI-HF/HF-R 历史选择器。 |
| 负责人最终视觉批准 | 负责人于 2026-08-04 明确回复“UI-REC4 最终视觉验收通过”。 |
| 当前结论 | 工程门禁和负责人最终视觉验收均通过，状态为 `completed`；UI-REC0～UI-REC4 全部完成，本轮 UI 高保真恢复任务结束。 |
| Git 收口 | UI 实现提交为 `c9f1a64`，文档收口提交为 `7cd53e9`；暂存差异检查、敏感信息扫描和 `git diff --check` 通过。 |
| 远程交付 | `main` 已推送至私有仓库 `wcnm8888/agent3-document-learning-assistant`，本地与远程 HEAD 一致；未创建 PR、未部署。 |
| 后续边界 | 当前权威路线没有 UI-REC5；历史 HF-R5、UI-R6、UI-R7 不再执行。Gradio 404 修复仍是独立任务。 |

## UI-REC3 桌面文档库高保真证据（2026-08-03）

| 项目 | 证据 |
| --- | --- |
| 冻结基准 | `docs/assets/ui-visual-baseline/figma-desktop-library-1440x900.png`。 |
| 确定性真实状态 | `tests/fixtures/ui_visual_baseline.py`；临时 SQLite 包含真实 PDF、Markdown 和归档文档记录，不使用生产 Qdrant points。 |
| 桌面实现 | `output/playwright/ui-rec3-final-library-1440x900.png`。 |
| 负责人反馈校准 | `output/playwright/ui-rec3-feedback-library-final-1440x900.png`；上传外壳、按钮和内部内容边界一致，最近文档标题由 `y=544.8` 上移到 `y=353.8`，3 条记录无需挤在底部小区域。 |
| 同屏对照 | `output/playwright/ui-rec3-library-comparison-1440x900.png`；详细结论见项目根 `design-qa.md`。 |
| 真实选择 | 点击第二个文档行后，选中 ID、详情标题和隐藏 Gradio 详情状态均切换为 `fixture-markdown-multidocument`；键盘 Enter/Space 复用同一事件链。 |
| 1440×900 几何 | document `1440×900`；工作区 `1392×790`；侧栏 `216×790`；主区 `768×790`；检查器 `368×790`；工具栏 `710×106`；列表 `710×338.4`；三栏无重叠。 |
| 结构回归 | `output/playwright/ui-rec3-regression-1024x768.png`、`ui-rec3-regression-390x844.png`、`ui-rec3-regression-390x844-context.png`；两视口 `scrollWidth === clientWidth`。 |
| 浏览器日志 | console errors 0、warnings 0。 |
| 学习会话交互复核 | `output/playwright/ui-rec3-feedback-session-function-1440x900.png`；文档库切换学习会话后成功提交“解释一下如何搭建 RAG”，回答、2 个来源、复制按钮和真实回合时间同步更新；复制按钮短暂进入 `copied/回答已复制`。 |
| 自动化 | `tests/test_phase5_ui.py` 30 项通过；全量 `pytest` 95 项通过；`compileall`、`git diff --check` 通过。 |
| CSS 门禁 | `src/doc_qa/ui.css` 2172 行、162 个 `!important`、3 个 `@media`；未新增阶段式尾部补丁。 |
| 安全边界 | 未读取或删除真实文档、真实数据库或 Qdrant points；差异敏感信息匹配数为 0。 |
| 视觉结论 | 实现方同屏 QA 通过；负责人已于 2026-08-03 明确批准 UI-REC3 视觉结果，状态为 `completed`。 |

## UI-REC2 桌面学习会话高保真证据（2026-08-03）

| 项目 | 证据 |
| --- | --- |
| 冻结基准 | `docs/assets/ui-visual-baseline/figma-desktop-session-1440x900.png`。 |
| 确定性真实状态 | `tests/fixtures/ui_visual_baseline.py`；已索引文档、问题、回答、PDF/Markdown 来源和学习笔记均经真实回调产生。 |
| 桌面完成态 | `output/playwright/ui-rec2/calibrated-desktop-session-complete-1440x900-review3.png`；真实问答、PDF/Markdown 来源与已保存笔记均可见。 |
| 桌面空态 | `output/playwright/ui-rec2/after-desktop-session-empty-1440x900.png`；Composer 不随空态失控下沉。 |
| 1440×900 几何 | 文档 `1440×900`；工作区 `1392×790`；主区 `768×790`；时间线 `702.4×493.2`；Composer `702.4×93.3`，底边 `865.2`；检查器 `368×790`；三栏与 Composer 边界无重叠。 |
| 滚动策略 | document `scrollWidth=clientWidth=1440`、`scrollHeight=clientHeight=900`；时间线自身承担消息滚动；Composer 首屏完整可见。 |
| 结构回归 | `output/playwright/ui-rec2/calibrated-regression-1024x768-review2.png`、`calibrated-regression-390x844-review2.png`；无横向或纵向页面溢出，Composer 可见。 |
| 浏览器日志 | 最终稳定实例 console errors 0、warnings 0。 |
| 自动化 | `tests/test_phase5_ui.py` 29 项通过；全量 `pytest` 94 项通过。 |
| CSS 门禁 | `src/doc_qa/ui.css` 2038 行、162 个 `!important`、3 个 `@media`；原位整合校准规则，未新增 UI-REC2/final/fix/override 尾部阶段块。 |
| 视觉校准 | 面板阴影变量为 `none`；顶部与会话状态胶囊只保留单层；消息卡统一 14px 圆角；最近文档仅首项使用弱表面；来源检查器显示真实来源、真实笔记预览和真实问答范围。 |
| 第二轮校准 | 范围选择器为统一胶囊形；来源/笔记 Tab 外框上下边界实测均为 `0.8px`；成功勾选已移除；复制按钮真实浏览器点击后进入 `copied` 状态并显示“回答已复制”；回答时间来自 SQLite 回合 `created_at`。 |
| 第三轮校准 | 范围选择器及其 Gradio 外层均实测为 `132×36px`；来源/笔记 Tab 容器实测 `34px`，两个按钮均为 `30px`，上下内衬各 `2px`，只保留单一均匀内描边。 |
| 视觉结论 | 实现与浏览器硬门禁通过；负责人已确认视觉校准通过，状态为 `completed`。 |
| 安全边界 | 临时 SQLite/确定性夹具；未读取或删除真实文档、真实数据库或 Qdrant points。 |

## UI-REC1 CSS 架构重置证据（2026-08-03）

| 项目 | 证据 |
| --- | --- |
| 单一样式权威 | `src/doc_qa/ui.css`；`src/doc_qa/ui.py` 使用 `APP_CSS_PATH` 加载；`pyproject.toml` 声明 `doc_qa = ["ui.css"]`。 |
| 规模收敛 | `ui.py` 1601 行；`ui.css` 1624 行、162 个 `!important`、3 个媒体查询；旧基线为 4345 行 `ui.py`、578 个 `!important`、20 个媒体查询。 |
| 架构契约测试 | `tests/test_phase5_ui.py` 28 项通过；新增外部 CSS 加载、包资源、唯一网格、断点数量、`!important` 上限及历史阶段标记禁入断言。 |
| 全量回归 | `pytest` 93 项通过；`compileall` 与 `git diff --check` 通过。 |
| 桌面浏览器 | `output/playwright/ui-rec1/desktop-session-complete-1440x900.png`、`desktop-library-final-1440x900.png`。 |
| 平板浏览器 | `output/playwright/ui-rec1/tablet-session-1024x768-approved.png`；无横向溢出，主区与检查器边界明确。 |
| 移动浏览器 | `output/playwright/ui-rec1/mobile-session-390x844.png`、`mobile-navigation-drawer-390x844.png`、`mobile-context-sheet-390x844.png`。 |
| 浏览器日志 | 隔离实例 `http://127.0.0.1:7865/`；Playwright console errors 0、warnings 0。 |
| 报告显隐复核 | 1440×900 打开“学习报告”后报告区按需展开；返回“学习会话”后页面恢复为 `scrollHeight=900`、无全局纵向溢出，最终截图为 `output/playwright/ui-rec1/desktop-session-post-stats-fix-1440x900.png`。 |
| 数据安全 | 使用 `tests/fixtures/ui_visual_baseline.py` 与临时 SQLite；未删除真实文档、数据库或 Qdrant points。 |
| 视觉结论 | CSS 架构与结构重叠门禁通过；Figma 高保真视觉验收仍未通过。 |

## UI-REC0 基线证据（2026-08-03）

| 项目 | 证据 |
| --- | --- |
| 当前源码规模 | `src/doc_qa/ui.py` 为 4345 行、约 169 KB；多代 UI 样式仍位于同一文件中。 |
| CSS 风险 | 审计到 578 个 `!important`、20 个媒体查询及多组重复组件选择器；当前 UI 已冻结。 |
| 视觉测试边界 | `tests/test_phase5_ui.py` 主要验证 CSS/HTML 契约，不能证明浏览器最终几何或 Figma 一致。 |
| 视觉基线 | `docs/assets/ui-visual-baseline/` 固定三张 Figma 图片、视口、状态和 SHA-256。 |
| 真实状态夹具 | `tests/fixtures/ui_visual_baseline.py` 使用真实应用、SQLite、会话、citation 和笔记回调；只替代外部 QA 服务。 |
| 敏感信息 | `.env` 仍被忽略；候选提交范围经高置信规则复核后未发现密钥、Token 或私钥。 |
| 清理边界 | `docs/project-management/ui-rec0-cleanup-manifest.md` 已分类；本阶段没有删除任何文件。 |
| 夹具冒烟 | `tests/fixtures/ui_visual_baseline.py --port 7865` 在隔离运行目录返回 HTTP 200，随后进程终止。 |
| 测试门禁 | UI 定向 28 项、全量 93 项、`compileall` 和 `git diff --check` 通过。 |
| Git 边界 | 仅允许本地恢复提交；不推送、不创建 PR、不部署。 |

---

# 历史 UI 证据（非权威）

## HF-R0 视觉基线重置证据（2026-08-03）

## HF-R4 来源、笔记与响应式上下文证据（2026-08-03）

| 项目 | 结果 |
| --- | --- |
| Figma 对照 | 读取 Review v1 `Desktop / 学习会话工作区`：检查器为来源/笔记分段 Tab，PDF 为紫色类型标签，Markdown 为蓝色类型标签，片段/原始引用是二级信息。 |
| 真实来源回调 | 临时 `LearningService` 仍通过 `UIController.ask` 保存真实临时会话 turn；受控 `FixtureAskService` 只替代外部 LLM/Embedding，且 PDF/Markdown citation 均对应临时目录文档。 |
| PDF / Markdown | 浏览器确认 PDF 显示“第 6 页”，Markdown 显示“核心章节 · 段落 2 · 行 11–14”；展开入口显示片段和经转义的原始定位。 |
| 笔记 | 浏览器完成一次问答后保存笔记，状态显示真实生成的 `note_id`，当前会话笔记卡片可见；单元测试另验证不会混入其他会话的笔记。 |
| 1440×900 | 通过 1440×900 iframe 视口包装页验证工作台与空检查器无页面级横向溢出。 |
| 1024×768 | 上下文入口打开后检查器为 `380px` 右侧抽屉；DOM 实测 `display:flex`、`width=380`、`height=672`。 |
| 390×844 | 上下文入口打开后面板贴底；DOM 实测 `bottom=844`、`height=484.25`、`width=375.2`，Tab 和空状态可见。 |
| 质量门禁 | `tests/test_phase5_ui.py`：28 passed；全量 `pytest`：93 passed；`compileall src tests`、`git diff --check`：通过。 |

截图：`output/ui-fidelity-recovery/hf-r4/session-1440x900.png`、`session-1024x768-drawer.png`、`mobile-390x844-context.png`。隔离运行脚本为 `output/ui-fidelity-recovery/hf-r4/fixture_app.py`，仅访问 `output/ui-fidelity-recovery/hf-r4/runtime/`。隔离浏览器自动填充在移动 iframe 被剪贴板限制阻断，因此该状态未作为通过结论；这不影响桌面已验证的真实问答、来源展开和笔记保存回调。

## HF-R3 文档库与详情检查器证据（历史记录）

| 项目 | 结果 |
| --- | --- |
| Figma 对照 | 按 Review v1 的“标题/上传 → 搜索/筛选 → 紧凑文档行 → 右侧详情”结构实现，不把原生 Dataframe/JSON 作为主视觉。 |
| 真实夹具数据 | 临时 SQLite 记录包含 PDF、Markdown 与已归档文档；右侧详情展示完整 `document_id`、hash、统计、状态和既有生命周期入口。 |
| 语义检查 | 搜索 `phase3` 后列表仅保留匹配 Markdown；当前详情仍为原 PDF，`document_filter` 仍为空（全部文档），证明列表搜索不改变问答范围。随后选择 Markdown 详情，检查器显示 `markdown-heading-line-v1`。 |
| 1440×900 | 无页面级横向溢出；上传、搜索、筛选、紧凑行和详情检查器层级成立。 |
| 1024×768 | 无页面级横向溢出；主工作区优先，详情检查器遵循既有收缩策略。 |
| 390×844 | 无页面级横向溢出；菜单可进入文档库，工具栏单列，文档行只保留名称、状态与时间。 |
| 质量门禁 | `tests/test_phase5_ui.py`：27 passed；全量 `pytest`：92 passed；`compileall src`、`git diff --check`：通过。 |

截图：`output/ui-fidelity-recovery/hf-r3/library-1440x900.png`、`library-1024x768.png`、`library-390x844.png`。隔离浏览器为 `127.0.0.1:7863`，使用临时 `SQLITE_PATH` 与 `QDRANT_LOCAL_PATH`；未上传、索引、归档、删除真实文档或 Qdrant points。控制台未发现来自该本地应用 URL 的 error/warn。

# HF-R1 应用外壳与 P0 结构修复证据（2026-08-03）

| 项目 | 结果 |
| --- | --- |
| Figma 读取 | 通过 Figma MCP 读取 Review v1 的桌面学习会话结构；Education team 验证横幅限制编辑，不阻塞只读设计上下文。 |
| 1440×900 | 顶栏、216px 导航、主区、368px 检查器层级成立；导航说明顶部在导航末端之后；会话状态为“✅ 会话已就绪”，无内部 ID/横向滚动。 |
| 1024×768 | 页面无横向溢出；检查器下移到主工作区后，主区不再被三栏压缩。 |
| 390×844 | 页面无横向溢出；既有移动菜单入口存在，检查器按既有移动策略收缩。 |
| 文档库元数据 | `0 个文档` 与 `PDF · Markdown` 的 Gradio Markdown 包装层不再出现横向滚动；搜索输入不再出现原生滚动条。 |
| 质量门禁 | `tests/test_phase5_ui.py`：23 passed；全量 `pytest`：88 passed；`compileall src` 与 `git diff --check`：通过。 |

截图：`output/ui-fidelity-recovery/hf-r1/hf-r1-desktop-1440x900.png`、`hf-r1-session-1440x900.png`、`hf-r1-tablet-1024x768.png`、`hf-r1-mobile-390x844.png`。测试使用隔离实例 `127.0.0.1:7862`、隔离 `SQLITE_PATH` 和 `QDRANT_LOCAL_PATH`；未上传、索引、归档、删除文档或删除 points。

运行注意：第一次临时启动误用了未被项目读取的 `DOCQA_DATABASE_PATH` 变量，因而默认本地库可能新增了一条初始化会话；没有执行上传、索引、删除或生命周期操作，且没有删除该记录来掩盖问题。随后已停止该实例并改用正确的隔离变量完成全部验证。该项作为本地数据安全复盘记录，不影响 HF-R1 UI 结论，但后续如需清理必须另行确认。

## 真实浏览器与 Figma 对照

| 证据 | 结论 |
| --- | --- |
| `output/playwright/hf-r0-figma-baseline.png` | Figma Review v1 桌面基线：紧凑三段工作台、连续会话时间线/Composer、右侧来源与笔记卡片。 |
| `output/playwright/hf-r0-current-session-1440.png` | 左侧说明与导航重叠；`session_id` 原生横向滚动；范围卡/时间线/Composer 分离；右侧存在大面积原生空白。 |
| `output/playwright/hf-r0-current-session-1024.png` | 三栏被压缩而非主工作区优先收缩，P0 重叠和横向滚动仍存在。 |
| `output/playwright/hf-r0-current-session-390.png` | 未形成可验证的 Figma 移动菜单 + 单主区 + 上下文底部面板体验。 |

实测 1440×900 工作台为 `220px 680px 340px` 三栏，页面高度约 1212px；会话状态区域宽约 210px 且有横向滚动，导航说明区域高度约 74px 并覆盖导航流。点击实时“文档库”入口后选中态改变，但主工作区未切换为文档库视图，故本轮不能将文档库视觉验收记为通过。

## 结论

- 历史“UI 定向 22 项、全量 87 项通过”仅是功能回归记录；HF-R0 未修改代码，因此没有重新运行测试。
- 功能测试不能替代 Figma 对照视觉 QA；当前高保真状态调整为 `needs_fidelity_rework`。
- `upload_progress?upload_id=undefined` 404 仍为独立非阻塞技术债务，HF-R0 未处理。

## 结构修复

- 会话头部改为受约束的 Grid；桌面端保持标题、会话状态和新会话入口的层级，1024×768 使用标题整行、状态和操作并列的两行布局。
- 上下文检查器固定为纵向不换行；在 390×844 的回答状态下，PDF/Markdown 来源卡片不再被排到视口右侧。
- 新增 UI 契约测试，锁定会话头部、检查器纵向布局、隐藏重复 Tab 导航和 Composer 结构规则。

## 浏览器证据

- 1440×900：`output/playwright/ui-hf6-p0-session-1440-final.png`；会话头部、范围卡、时间线和 Composer 无重叠，页面宽度 1440。
- 1024×768：`output/playwright/ui-hf6-p0-session-1024-v2.png`；会话头部不再严重折行，页面宽度 1024。
- 390×844：`output/playwright/ui-hf6-p0-session-390.png`；移动端无横向溢出。
- 移动菜单：`ui-hf6-p0-menu-390.png`；导航抽屉展示文档库、学习会话、来源与笔记、学习报告和最近文档。
- 移动上下文：`ui-hf6-fixture-sources-390-fixed.png`、`ui-hf6-fixture-notes-390-fixed.png`；来源/笔记 Tab 可切换，PDF 页码和 Markdown 章节/段落/行号均可见。
- 文档库：`ui-hf6-library-1440-final.png`；搜索、格式、状态、排序、上传/索引、文档列表和右侧详情/生命周期区域可访问。

## 测试与限制

- UI 定向测试：22 passed。
- 全量测试：87 passed；79 项为历史阶段基线，86 项为 P0 修复前工作区基线。
- `compileall`：通过；`git diff --check`：通过。
- 临时夹具中的笔记保存失败明确显示外部 Embedding 服务不可用；没有输出密钥，也没有把失败伪装成成功。
- Gradio `upload_progress?upload_id=undefined` 404 在历史上传复现日志中仍可见，未修复。

- 代码范围：仅修改 `src/doc_qa/ui.py` 的 UI-HF5 响应式 CSS、移动端导航/上下文开关和视图切换状态绑定；在 `tests/test_phase5_ui.py` 新增 1 项移动端契约测试。未修改解析、RAG、Embedding、Qdrant、SQLite Schema 或业务服务。
- 平板证据：1024×768 下保留顶部品牌栏、左侧空间导航、主工作区和右侧上下文检查器，采用紧凑三栏比例；未出现页面级横向溢出。
- 移动端证据：390×844 下菜单开关打开左侧导航抽屉；切换“学习会话”后抽屉自动关闭；上下文开关打开底部面板；来源/笔记 Tab 分别显示并可切换，选中态由浏览器语义快照确认。
- 响应式测量：1440×900、1024×768、390×844 均未出现页面级横向溢出；移动端底部面板为全宽底部容器，未超过可视内容宽度。
- 浏览器日志：当前临时实例验证为 0 errors、0 warnings；截图：`output/playwright/ui-hf5-final-1440.png`、`ui-hf5-final-1024.png`、`ui-hf5-final-390-base.png`、`ui-hf5-390-context-final.png`。
- 质量门禁：UI 定向测试 20 项通过；全量 pytest 85 项通过；`compileall`、`git diff --check` 通过。79 项为历史基线，当前工作区的 85 项包含此前阶段测试及本轮新增 1 项。
- 未能安全复现：真实外部 Embedding/LLM 宕机、生产数据库故障、真实上传传输中断和真实生产删除失败未执行；原因是本项目明确禁止破坏真实服务、真实文档或真实 Qdrant points，相关错误语义由现有临时夹具/定向测试覆盖并保留风险记录。
- UI-HF5 当前仍为 `ready_for_review`，原因是异步/故障状态尚未逐项完成本轮三种视口浏览器重放；不得将 UI-HF4 或自动化夹具证据直接升级为 UI-HF5 完成证据。
- 未执行：UI-HF6、Git 提交/推送/PR/部署。Gradio 上传进度 404 未伪装为已修复。

# UI-HF4 独立实施证据（历史阶段记录，2026-08-02）

- 代码范围：仅修改 `src/doc_qa/ui.py` 的上下文检查器 UI、来源卡片 HTML、笔记区域 CSS/标签和 `tests/test_phase5_ui.py` 的 UI-HF4 契约测试；新增临时浏览器夹具 `output/ui_hf4_fixture.py`。
- 来源证据：PDF 卡片显示格式徽标、文件名、第 6–7 页、来源片段和完整 locator；Markdown 卡片显示格式徽标、文件名、章节、段落、行号、来源片段和完整 locator。
- 交互证据：真实浏览器中来源/笔记 Tab 可切换；笔记内容标签清晰；未完成问答时点击保存显示“请先完成一次问答，再保存笔记”，未伪造保存成功。
- 浏览器截图：`output/playwright/ui-hf4-1440-source-cards.png`、`ui-hf4-1440-notes.png`、`ui-hf4-1024-notes.png`、`ui-hf4-390-notes.png`。
- 三种视口：1440×900、1024×768、390×844 的 `body.scrollWidth` 分别为 1425、1009、375，均小于视口宽度；控制台 error/warn 为 0。
- 质量门禁：UI 定向测试 19 项、全量测试 79 项通过；`compileall` 和 `git diff --check` 通过。
- 业务保护：未修改 PDF/Markdown 解析、RAG、Embedding、Qdrant、SQLite Schema、会话服务、笔记服务、引用、生命周期、document_id 或 source_locator；浏览器使用临时 SQLite/Qdrant 和临时问答返回夹具。
- 未执行：UI-HF5～UI-HF6、原 UI-R6/UI-R7 最终回归、Git 提交/推送/PR/部署。Gradio 上传进度 404 未伪装为已修复。

# UI-HF2 独立实施证据（历史阶段记录，2026-08-02）

- 代码范围：仅修改 `src/doc_qa/ui.py` 的文档库 HTML 行、文档详情摘要、右侧检查器分组、UI-HF2 CSS 和脱敏展示；新增 `tests/test_phase5_ui.py` 两项 UI-HF2 契约测试。
- 文档库证据：可见文档列表由真实 SQLite 目录查询渲染；搜索、格式、状态和更新时间排序继续复用原有查询参数；原生 `gr.Dataframe` 仅保留为兼容输出，不作为可见主列表。
- 详情证据：右侧 `document-inspector` 可显示完整 document_id、内容 hash、定位方案、页数/章节单元、分块数、Qdrant points、更新时间、错误详情和生命周期按钮；删除确认仍保留。
- 脱敏证据：失败文档的错误提示在文档行和详情摘要中使用现有 UI 脱敏函数，测试验证 `API key` 值不会进入可见 HTML。
- 浏览器截图：`output/playwright/ui-hf2-final-1440-library.png`、`ui-hf2-final-1440-detail.png`、`ui-hf2-final-1024-library-top.png`、`ui-hf2-final-390-library-top.png`。
- 1440×900、1024×768、390×844 的 `body.scrollWidth` 均等于视口宽度，无横向溢出；浏览器 console error/warn 均为 0；三种视口均可看到文档库主区和检查器/详情入口。
- 质量门禁：UI 定向测试 16 项、全量测试 78 项通过；`compileall` 和 `git diff --check` 通过。
- 业务保护：未修改解析、RAG、Embedding、Qdrant、SQLite Schema、会话、笔记、引用、生命周期服务、document_id 或 source_locator 语义；浏览器使用临时 SQLite/Qdrant。
- 未执行：UI-HF3～UI-HF6、原 UI-R6/UI-R7 最终回归、Git 提交/推送/PR/部署。Gradio 上传进度 404 未伪装为已修复。

# UI-HF1 独立实施证据（历史阶段记录，2026-08-02）

- 代码范围：仅修改 `src/doc_qa/ui.py` 的 UI CSS、布局、组件组合、最近文档 UI 展示和导航状态绑定；新增 `tests/test_phase5_ui.py` 的真实最近文档 HTML 契约测试。
- 顶部品牌栏包含产品名称、副标题、当前范围、本地运行状态和语言入口；左侧空间导航包含文档库、学习会话、来源与笔记、学习报告以及最近文档区域。
- 最近文档由临时 SQLite 中的真实文档目录读取，浏览器中可见 `Happy-LLM-0727.pdf`、`phase3-multidocument-guide.md` 和 `RAG 评测笔记.md` 及格式/状态；HTML 文档名经过转义。
- 浏览器截图：`output/playwright/ui-hf1-final-1440-library.png`、`output/playwright/ui-hf1-final-1024-library.png`、`output/playwright/ui-hf1-390-library-fixed.png`、`output/playwright/ui-hf1-390-library-view.png`。
- 1440×900、1024×768、390×844 的 `body.scrollWidth` 均等于视口宽度，无横向溢出；浏览器 console error/warn 均为 0。
- 质量门禁：UI 定向测试 14 项、全量测试 76 项通过；`compileall` 和 `git diff --check` 通过。测试警告为既有 Gradio/Qdrant/Pydantic 弃用或兼容提示，不是 UI-HF1 失败。
- 未执行：UI-HF2～UI-HF6、原 UI-R6/UI-R7 最终回归、Git 提交/推送/PR/部署。Gradio 上传进度 404 未伪装为已修复。

# 项目证据归档

## UI 重设计任务 UI-R0/UI-R1 证据（2026-08-02）

- 负责人反馈确认：现有 UI 的主要问题是三个业务区域仍为同权重并列面板，未形成模板式的导航区、主工作区、底部输入区和上下文检查器层级。
- 已只读提取模板节点 `1239:27621` 的结构和设计上下文，获得 1440×900 画布、76px 顶部导航、200～220px 左侧导航、680px 中央内容宽度、68px 输入区、`#2F80ED` 用户气泡、`#27282A` 助手气泡和方向性圆角等具体参考规格。
- 已创建新的 Figma 文件：`https://www.figma.com/design/TjKze3Fwc19gCADBrgtuzJ`。
- 已创建独立任务卡：`docs/project-management/ui-redesign-task-card.md`，定义 UI-R0～UI-R7 阶段、范围、非目标、业务语义保护和验收门槛。
- 已完成 UI-R1 规格提取并写入 `docs/ui-redesign-reference-spec.md`，包含模板节点、尺寸、颜色、字体、间距、圆角、组件映射和产品化改造边界。
- UI-R1 明确提取了顶部导航、左侧资源导航、680px 主内容区、68px Composer、消息气泡和上下文层级；这些规格将作为 UI-R2 Figma 设计稿输入。
- Figma 文件尚未制作设计稿；本证据不代表新的 UI 设计或实现已经完成。
- 本轮未修改代码、测试、配置、数据库、Qdrant 或真实数据。

## UI 重设计任务 UI-R2 Figma 设计证据（2026-08-02）

- Figma 文件：`https://www.figma.com/design/TjKze3Fwc19gCADBrgtuzJ`。
- 已制作桌面端学习会话工作区：左侧空间导航、中央主问答区、底部 Composer、右侧来源/笔记上下文检查器。
- 已制作桌面端文档库工作区：搜索、格式筛选、状态筛选、更新时间排序、可读文档行项目、详情和生命周期操作。
- 已制作移动端学习会话默认态：折叠导航、连续问答、底部 Composer 和来源/笔记入口。
- 已制作移动端上下文底部面板打开态：PDF 页码来源、Markdown 章节/段落/行号来源和笔记入口。
- 截图证据：`output/figma-ui-r2/desktop-session.png`、`output/figma-ui-r2/desktop-library.png`、`output/figma-ui-r2/mobile-session.png`、`output/figma-ui-r2/mobile-context-sheet.png`。
- 设计稿保留 `document_id`、PDF/Markdown 定位差异、问答范围和笔记上下文的视觉映射；没有改变业务语义。
- UI-R2 仅修改 Figma 文件和截图证据，未修改本地 Python、CSS、测试、配置、数据库、Qdrant 或真实数据。
- UI-R3 负责人设计评审已在后续完成；评审结论和冻结决策见下方 UI-R3 记录。

## UI 重设计任务 UI-R3 设计评审证据（2026-08-02）

- 负责人已确认 Figma 设计稿方向可接受，并接受 UI-R3 推荐的页面入口、详情面板、上下文检查器和移动端交互方案。
- 已冻结的实现基线：有已索引文档时默认进入学习会话；空知识库进入文档库；桌面端详情使用右侧面板；平板/移动端详情使用抽屉；来源与笔记共用右侧 Tab；移动端来源/笔记使用底部面板；删除确认使用全屏抽屉或确认弹窗。
- UI-R3 只冻结设计和交互决策，不代表 UI-R4 代码实现已完成。
- 当前未修改 Python、CSS、测试、配置、数据库、Qdrant 或真实数据。
- 下一阶段为 UI-R4，需单独执行实现和验证。

## UI 重设计任务 UI-R4 实现与浏览器证据（历史记录，2026-08-02）

- 已实现 Figma 基线对应的应用外壳：顶部品牌区、左侧空间导航、中央学习会话/主工作区、底部问答 Composer 和右侧上下文检查器。
- 文档库入口已组织上传/索引、文档列表、搜索/格式/状态/更新时间筛选、详情与生命周期操作；来源/笔记通过上下文 Tab 组织。
- `src/doc_qa/ui.py` 的改动限定于 UI CSS、布局、组件组合、文案和必要的 UI 状态绑定；未修改 PDF/Markdown 解析、RAG、Embedding、Qdrant、SQLite、会话、笔记、引用或生命周期业务逻辑。
- `tests/test_phase5_ui.py` 定向测试 11 项通过；全量 `pytest tests -q` 76 项通过；`compileall` 和 `git diff --check` 通过。
- 使用临时 SQLite/Qdrant 与临时 PDF/Markdown 文档完成浏览器验证：文档库、搜索筛选、来源/笔记 Tab、文档详情/生命周期入口、问答范围选择和切换清理均可见且可操作。
- 1440×900、1024×768、390×844 截图分别为 `output/playwright/ui-r4-1440.png`、`output/playwright/ui-r4-1024.png`、`output/playwright/ui-r4-390.png`；1024 和 390 的页面宽度检查无横向溢出；安全临时实例浏览器 error/warn 均为 0。
- UI-R4 当时已完成并进入 `ready_for_review`；后续 UI-R5 已在下方完成，UI-R6/UI-R7 尚未执行。

## 历史 UI 美化任务 UI-0～UI-5 证据（2026-08-02）

- UI-0 只读审计截图保存于 `E:\Agent\ui-audit-2026-08-01`，覆盖 1440×900、1024×768、390×844 和 Figma 参考页面。
- 当前运行页面审计确认：现有功能结构可用，但存在混合浅色/深色表面、部分标题低对比度、文档表格列过密、长文件名和 `document_id` 展示困难，以及窄屏面板层级不够明确的问题。
- UI-1 使用 Figma Chat 页面 `1239:27621` 做只读参考提取，提取内容限于布局、视觉层级、Zinc 表面、蓝色主交互、输入区和资源侧栏；未写入或修改 Figma 文件。
- UI-2 已将 Design Tokens、信息架构、核心页面规格、组件树、状态规则、Gradio 映射和 UI-3 前置门禁写入 `docs/design-spec.md` 与 `docs/project-management/ui-beautification-task-card.md`。
- UI-2 设计证据已转化为 UI-3 实现基线；UI-3 代码实现、定向测试和浏览器检查证据见下方当前 UI-3 记录。
- 当前没有重新捕获 Gradio `upload_progress?upload_id=undefined` 404；该历史风险继续保留，不能标记为已修复。

## 当前 UI-3 实施证据（2026-08-02）

- `src/doc_qa/ui.py` 只涉及 UI 外壳、样式、布局、组件组合和 UI 状态绑定；文档解析、RAG、Embedding、Qdrant、SQLite、会话、笔记、引用和生命周期业务语义未修改。
- 文档库表格展示收缩为文档名、格式、状态、更新时间；完整 `document_id`、hash、定位方案、统计和错误详情保留在文档详情区域。
- `tests/test_phase5_ui.py` 与 `tests/test_document_lifecycle.py` 定向测试共 15 项通过；`compileall -q src tests` 通过。
- 浏览器在 1440×900、1024×768、390×844 下检查通过：页面宽度分别为 1425/1009/375，均未出现横向溢出；移动端文档库、问答和来源区域按纵向顺序排列。
- 截图：`output/playwright/ui3-1440x900.png`、`output/playwright/ui3-1024x768.png`、`output/playwright/ui3-390x844.png`。
- 只读搜索交互使用 `phase3` 验证，文档列表仅返回匹配文档；清空搜索后恢复列表，未改变问答范围。
- 浏览器页面日志未发现项目错误或警告；Gradio `upload_progress?upload_id=undefined` 404 未在 UI-3 处理，仍为已知非阻塞依赖风险。
- UI-4 独立验收证据见下方记录；UI-5 独立视觉 QA 证据见文末最新收口记录。

## 当前 UI-4 独立验收证据（2026-08-02）

- UI 表现层修复仅涉及 `src/doc_qa/ui.py` 的焦点可见样式和禁用状态样式；`tests/test_phase5_ui.py` 新增状态/范围清理与样式契约测试。
- UI 定向测试 11 项通过；全量测试 76 项通过；`compileall -q src tests` 和 `git diff --check` 通过。
- 状态文字、警告/错误前缀、初始等待状态、文档范围切换清理、控件标签、焦点轮廓和禁用样式均有定向证据。状态不依赖颜色单独表达。
- 浏览器三视口检查：1440×900 为三栏并列；1024×768 为文档库/问答主区并列、来源区下移；390×844 为文档库、问答、来源纵向堆叠。DOM 宽度无横向溢出，移动端表格保留文档名、格式、状态、更新时间，完整 ID 由详情区承载。
- 截图：`output/playwright/ui4-1440x900.png`、`ui4-1024x768.png`、`ui4-390x844.png`。浏览器 error/warn 日志为空。
- 已在临时 SQLite/Qdrant 浏览器验证环境中观察到空文件校验、Gradio 不支持格式拒绝、上传边界失败、解析失败、索引失败、外部服务不可用、数据库错误、问答失败、删除失败、危险确认、笔记保存失败和 `processing` 加载中间态；截图为 `output/playwright/ui4-input-validation.png` 和 `output/playwright/ui4-failure-states.png`，其余新增状态由浏览器 DOM 快照和复现步骤记录。这些是安全受控的 UI 边界证据，不代表真实生产依赖中断演练。
- 未修改解析、RAG、Embedding、Qdrant、SQLite Schema、会话、笔记、引用或生命周期语义；未删除真实数据或 Qdrant points。
- UI-4 完成定义已满足：所有可安全复现的状态均有真实浏览器可见证据；真实生产故障演练未执行且不作为验收前提。Gradio `upload_progress?upload_id=undefined` 404 仍为已知非阻塞依赖风险，UI-4 未处理。

> 文档说明：本文前部的原单 PDF Phase 0～8 和旧任务状态均为历史证据；当前多文档与 Markdown 任务卡状态以本文后面的 Phase 4 证据及 `current-task.md` 为准。

## 仓库

> 当前权威状态（2026-08-01）：多文档与 Markdown 任务卡 Phase 2～6 及后续方向 A、B、C 已完成，Git P0 已完成并提交为 `f3c5403`。真实浏览器问答、来源展开、笔记创建/更新、文档切换、三种视口复验和全量质量门禁均已通过；Gradio 上传进度 404 记录为非阻塞依赖风险。本文前部“尚未进入业务实现”的描述属于 Phase 0/1 历史证据。

## 当前最终交付证据（2026-08-01）

- 方向 A、B、C 均已完成；该阶段全量 pytest 为 73 项通过。当前 UI-4 回归全量 pytest 为 76 项通过，compileall 通过，真实 UI 在 1440×900、1024×768、390×844 三种视口复验通过。
- Git P0 已完成：当前提交为 `f3c5403 feat(docqa): deliver local document QA workflow`；未推送、未创建 PR、未部署。
- 生命周期验证仅使用临时 SQLite/Qdrant；归档、删除、恢复、重新索引、一致性检查和失败保护已验证，但未删除真实生产文档或真实生产 Qdrant points。
- Gradio `upload_progress?upload_id=undefined` 404 在 5.50.0/5.49.1 中可复现，6.22.0 对当前 UI 存在启动回归；该问题仍为非阻塞依赖风险，未标记为已修复。
- 认证、用户系统、多租户、Neo4j、公网部署和生产删除演练不属于本阶段范围。

## Phase 5 独立 QA 最终证据（历史记录，2026-08-01）

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

## Phase 8 最终证据（历史基线，2026-08-01）

- `python -m doc_qa.cli health`：返回 `status=ok`；配置完整、Qdrant healthz HTTP 200、v3/v4 均 green/262 points/1024 维、SQLite `integrity_check=ok`。
- `python -m doc_qa.cli backup-sqlite data/backups/phase8-validation.sqlite3`：备份返回 `status=ok`；恢复文件完整性为 `ok`，包含 2 个 sessions、1 个 conversation turn。
- 真实 v4 smoke test：`text-embedding-v4` 查询 → Docker Qdrant → DeepSeek，返回 `answered`，引用 Happy-LLM 第 6 页和对应 `source_locator`。
- 全量测试：45 项通过；compileall、Compose 配置解析和 `git diff --check` 通过。
- Phase 8 完成；未部署生产、未公网暴露、未提交、未推送。
## UI-R4 最终复核补充证据（历史记录，2026-08-02）

- UI 定向测试 12 项、全量测试 76 项通过；`compileall` 和 `git diff --check` 通过。
- 临时 SQLite/Qdrant 与临时 Gradio 实例 `http://127.0.0.1:7864/` 完成复核，未连接真实生产数据。
- 1440×900、1024×768、390×844 页面宽度分别为 1425、1009、375，均无横向溢出；浏览器 error/warn 为 0。
- 复核流程包含文档库导航、搜索列表过滤、来源/笔记 Tab、详情与生命周期入口和移动端学习会话布局。
- 截图：`output/playwright/ui-r4-final-1440-clean.png`、`ui-r4-final-library-clean.png`、`ui-r4-final-1024-clean.png`、`ui-r4-final-390-clean.png`、`ui-r4-final-session-inspector.png`、`ui-r4-final-mobile-session.png`。
- UI-R4 记录形成时 UI-R5 尚未执行；当前 UI-R5 已在下方完成，UI-R6/UI-R7 尚未执行；Gradio `upload_progress?upload_id=undefined` 404 仍为独立非阻塞风险。

## UI-R5 文档库与上下文检查器深化证据（2026-08-02）

- `src/doc_qa/ui.py` 增加文档详情选择入口、详情摘要、完整 document_id 展示、生命周期危险区说明、来源卡片格式化和最近文档动态刷新绑定；未修改解析、RAG、Embedding、Qdrant、SQLite、会话、笔记或生命周期业务逻辑。
- PDF 来源卡片保留页码；Markdown 来源卡片展示章节、段落和行号；完整 locator 仍保留在原始引用数据中。
- UI 定向测试 13 项、全量测试 76 项通过；`compileall` 和 `git diff --check` 通过。
- 临时 SQLite/Qdrant Gradio 实例 `http://127.0.0.1:7864/` 完成文档库、详情选择、生命周期入口、来源/笔记 Tab 和移动端上下文面板验证。
- 1440×900、1024×768、390×844 页面宽度分别为 1425、1009、375，均无横向溢出；浏览器 error/warn 为 0。
- 截图：`output/playwright/ui-r5-1440-library-final.png`、`ui-r5-1440-detail.png`、`ui-r5-1024-library.png`、`ui-r5-390-notes.png`。
- UI-R5 已完成并进入 `ready_for_review`；UI-R6/UI-R7 尚未执行；Gradio `upload_progress?upload_id=undefined` 404 未处理，仍为独立非阻塞风险。

## UI-5 独立视觉 QA 与收口证据（2026-08-02）

### 浏览器与视口

- 临时 SQLite/Qdrant 夹具和临时 Gradio 应用启动成功，未连接真实生产数据或删除真实 points。
- 1440×900、1024×768、390×844 均完成截图；浏览器检查确认页面无横向溢出。
- 关键截图：`output/playwright/ui5-1440x900.png`、`ui5-1024x768.png`、`ui5-390x844.png`、`ui5-pdf-source-top-1440.png`。

### 业务与可访问性

- 搜索、PDF/MARKDOWN 筛选、状态筛选、排序和详情展示通过；完整 `document_id` 仍在详情区域可查看。
- PDF 来源保留 `page=6`；Markdown 来源保留 `heading=核心章节; paragraph=1; lines=11-11`，未出现伪造页码。
- 范围切换清空回答/来源/待保存笔记；新会话隔离通过；笔记保存成功；未勾选危险确认时删除被拦截。
- 主要控件具备标签，状态文字不依赖颜色，禁用/危险/错误状态可辨识；浏览器控制台本地应用无 error/warn。

### 质量门禁

- UI 定向测试：17 passed；全量测试：76 passed；`compileall`：通过；`git diff --check`：通过。
- 本轮仅修改 `src/doc_qa/ui.py` 的 UI CSS/断行规则；Gradio 404、认证、多租户、公网部署和真实生产故障演练均未执行。
## UI-HF0 高保真差距审计证据（2026-08-02）

- 对照 Figma 目标截图：`output/figma-ui-r2/desktop-session.png`、`desktop-library.png`、`mobile-session.png`、`mobile-context-sheet.png`。
- 对照当前 UI-R5 截图：`output/playwright/ui-r5-1440-session.png`、`ui-r5-1440-library-final.png`、`ui-r5-1024-library.png`、`ui-r5-390-notes.png`。
- 审计结论：当前 UI 已具备深色主题、三栏容器和既有业务入口，但仍保留较强的 Gradio 原生表单/面板结构，与 Figma 的知识工作台外壳、独立主工作区、消息时间线、底部 Composer、来源/笔记卡片和移动端底部面板存在明显差距。
- 差距优先级：P0 为应用外壳与信息层级、文档库独立工作区、学习会话与 Composer、详情面板、上下文检查器和移动端结构；P1 为控件统一、来源卡片、笔记卡片和状态组件一致性。
- 新增基线文档：`docs/ui-high-fidelity-baseline.md`；新增阶段为 UI-HF0～UI-HF6。
- 历史 UI-HF0 审计记录：当时 UI-HF1 尚未执行；随后 UI-HF1 已完成，当前证据见本文顶部；该审计阶段未修改 Python、CSS、测试、数据库、Qdrant 或真实数据。
- 原 UI-R4/UI-R5 的测试和浏览器证据仍然有效，但只能证明原阶段功能性实现和可用性，不作为高保真实现完成证据。
# UI-HF5 独立浏览器状态矩阵补充证据（2026-08-02）

- 临时实例：`http://127.0.0.1:7875/`；使用临时 SQLite/夹具和固定问答返回，未连接真实生产数据，未删除真实文档或 Qdrant points。
- 已保存截图：`output/playwright/ui-hf5-matrix-format-error-1440.png`、`ui-hf5-matrix-index-error-1440.png`、`ui-hf5-matrix-sources-1440.png`、`ui-hf5-matrix-sources-1024.png`、`ui-hf5-matrix-sources-390.png`、`ui-hf5-matrix-sources-390-answer.png`、`ui-hf5-matrix-notes-390.png`、`ui-hf5-matrix-menu-390.png`。
- 已验证状态：空知识库、格式校验失败、空文件索引失败、PDF/Markdown 来源卡片、笔记保存失败、删除未确认保护、移动端菜单和上下文底部面板、来源/笔记 Tab 切换、无横向溢出。
- 浏览器 DOM 证据：390×844 下页面内容宽度 375；Tab `来源`/`笔记` 均位于面板内容范围内；来源文本包含 PDF 页码和 Markdown 章节/段落/行号定位。
- 上传空文件时浏览器控制台出现 `upload_progress?upload_id=undefined` 404；该风险保持如实记录，未作为本轮修复项。
- 未能安全复现：真实上传中断、损坏 PDF 解析失败、完整加载中间态、外部服务宕机、数据库故障、问答失败、笔记保存成功和确认后的删除失败。原因是禁止破坏真实服务/真实数据，当前临时夹具尚未为这些路径提供独立故障注入。
- 质量门禁：`tests/test_phase5_ui.py` 21 passed；全量 pytest 86 passed；`compileall` 通过；`git diff --check` 通过。UI-HF5 仍为 `ready_for_review`，UI-HF6 尚未执行。
## HF-R2：学习会话、消息时间线与 Composer（2026-08-03）

| 项目 | 证据 | 结论 |
| --- | --- | --- |
| 真实数据绑定 | `tests/test_phase5_ui.py::test_hf_r2_renders_real_history_as_timeline_without_fabricating_sources` | 问题/回答被转义并展示；来源数只来自实际 citation 列表；空状态不伪造来源。 |
| 组件契约 | `tests/test_phase5_ui.py::test_hf_r2_builds_controlled_timeline_and_compact_composer_contract` | 已存在受控时间线、紧凑输入和圆形发送按钮的 UI 契约。 |
| 桌面浏览器 | `output/ui-fidelity-recovery/hf-r2/desktop-empty-session.png` | 1440×900 会话工作区无横向溢出，标题/范围/时间线/Composer 层级可见。 |
| 平板浏览器 | `output/ui-fidelity-recovery/hf-r2/tablet-empty-session.png` | 1024×768 无横向溢出，主会话区保持可读。 |
| 移动浏览器 | `output/ui-fidelity-recovery/hf-r2/mobile-empty-session.png` | 390×844 可通过“菜单”进入会话，无横向溢出，Composer 可见。 |
| 回归与质量门禁 | UI 定向 25 passed；全量 `pytest -q` 90 passed；`compileall`、`git diff --check` 通过 | 功能回归未发现失败；Gradio 弃用警告已记录。 |

限制：隔离夹具未上传或索引文档，且未调用外部 Embedding/LLM；因此未把真实有来源回答卡的浏览器截图写成已完成。此项不影响 HF-R2 的受控展示层契约，但仍应在 HF-R5 以安全夹具的真实数据状态完成对照验收。
