# 项目路线图

## 当前唯一路线状态（2026-08-04）

- 当前任务：UI-REC4“移动端上下文高保真与最终视觉收口”，状态为 `completed`。
- UI-REC0 已建立恢复点与冻结基线，UI-REC1 已完成 CSS 架构重置，UI-REC2、UI-REC3 与 UI-REC4 均已由负责人视觉批准并完成。
- UI-REC4 只收口 390×844 移动端上下文/文档详情、1024×768 平板结构和两个已批准桌面页面的最终回归。
- UI-REC4 工程实现、三视口浏览器验收和质量门禁已完成；负责人已于 2026-08-04 审核现有截图并批准最终视觉验收。
- UI 高保真恢复路线至此完成；当前权威路线不包含 UI-REC5，也不恢复执行历史 HF-R5、UI-R6 或 UI-R7。后续产品任务必须重新从路线图候选中选择并建立独立任务卡。
- 最终本地 Git 收口已执行：UI 实现提交为 `c9f1a64`，文档由独立收口提交保存；未推送、未创建 PR、未部署。
- 历史 UI-0/UI-R/UI-HF/HF-R 阶段只保留追溯价值，不再作为当前路线或完成证明。
- 解析、RAG、Embedding、Qdrant、SQLite、会话、笔记和生命周期业务语义不在本任务范围内。

---

# 历史路线记录（非权威）

## 2026-08-03 HF-R 路线历史状态

## 当前路线：HF-R4 已完成，等待 HF-R5 确认

当前 UI 任务仍不是发布收口，而是分阶段的高保真修复。视觉权威基线为 Figma Review v1 与 `docs/project-management/ui-fidelity-recovery-task-card.md`。HF-R1 已完成工作台外壳与 P0 结构修复，HF-R2 已完成学习会话与 Composer，HF-R3 已完成文档库与详情检查器，HF-R4 已完成来源/笔记与响应式检查器；UI-HF0～UI-HF6 的功能性实现和历史测试记录保留，但其“高保真通过/ready_for_release_review”结论仍不能替代 HF-R5 的 Figma 对照验收。

HF-R4 已完成来源/笔记检查器与平板/移动容器的受控展示层，当前唯一后续阶段为 HF-R5 Figma 对照视觉 QA 与收口。任何阶段均不改变核心业务语义；HF-R5 必须经负责人确认后才能启动。

## 历史 UI-HF6 收口状态（不作为当前视觉结论）

UI-HF6 已完成 P0 结构重叠修复、Figma 高保真视觉 QA、三视口验证、全量回归和文档收口，当前进入 `ready_for_release_review`。1440×900、1024×768、390×844 均无明显横向溢出；平板会话头部不再异常折叠，移动端上下文检查器在有来源卡片时保持纵向布局。

当前门禁：UI 定向 22 项、全量 87 项通过，`compileall` 和 `git diff --check` 通过。笔记保存成功依赖外部 Embedding 服务，本轮仅验证了安全可复现的保存失败态；Gradio upload progress 404 仍独立记录为非阻塞风险。

下一阶段建议：执行原路线图的 UI-R6/UI-R7 最终回归与交付收口；本轮不执行该阶段，也不创建或执行 UI-HF7。

UI-HF5 响应式实现已完成但验收未完全收口，当前状态为 `ready_for_review`。本阶段已完成平板紧凑布局、移动端导航抽屉、上下文底部面板和来源/笔记 Tab 响应式入口；异步/故障状态的独立浏览器矩阵仍待补齐，UI-HF6 暂不得进入。

UI-HF5 证据：`output/playwright/ui-hf5-final-1440.png`、`ui-hf5-final-1024.png`、`ui-hf5-final-390-base.png`、`ui-hf5-390-context-final.png`；UI 定向测试 20 项、当前工作区全量测试 85 项通过；79 项保留为上一阶段历史基线。

# 智能文档学习助手路线图

## 项目目标

基于 Datawhale Hello-Agents 第八章 8.4，建设一个可验证的个人文档学习助手。第一阶段以真实 PDF 为输入，完成文档摄入、检索问答、来源展示、学习记录和基础统计。

## 任务顺序

1. Phase 0：仓库、依赖、PDF、Git 基线和外部服务边界审计。
2. Phase 1：产品规格、架构、UI 规格、评测集和实现计划。
3. Phase 2：文档摄入与索引闭环。
4. Phase 3：问答、引用和检索策略闭环。
5. Phase 4：记忆、笔记和学习统计闭环。
6. Phase 5：Gradio UI 状态、响应式和人工验收。
7. Phase 6：v3/v4 评测、质量门禁和交付收口。
8. Phase 7：交付准备、部署方案和可运维性建设。
9. Phase 8：本地部署实施、运行时健康检查和可运维性验证。
10. 下一项产品任务：多文档与 Markdown 知识库管理。

## 当前优先级

> 当前权威状态（2026-08-01）：多文档与 Markdown 任务卡的 Phase 2、Phase 3、Phase 4、Phase 5、Phase 6 及后续方向 A、B、C 已完成；Git P0 已完成，提交为 `f3c5403`。本文件前部的“等待 Phase 2”属于历史规划记录。Gradio 上传进度 404 仍是非阻塞依赖风险。
### 历史单 PDF 路线摘要（只读）

Phase 0/2/3/4/5/6/7/8 已收口；多文档与 Markdown 知识库管理已完成任务卡确认、Phase 0 基线审计和 Phase 1 规格设计，尚未开始业务实现，等待确认进入 Phase 2。Phase 8 只完成本地运行时能力和验证，没有执行生产部署或公网暴露。Neo4j、用户系统、多租户和多模态能力仍不属于第一版范围。

## 当前任务：多文档与 Markdown 知识库管理（Phase 6 completed）

- 用户价值：从单 PDF 闭环扩展为可持续使用的个人文档知识库。
- 关键范围：Markdown 解析、多文档目录、文档切换、索引幂等、文档隔离和来源定位。
- 任务卡：`docs/project-management/task-card-multi-document-markdown.md`。
- 当前阶段：Phase 6 全量质量门禁与交付收口已完成；未经负责人确认不自动进入新的产品阶段。
- 已确认：本地单用户、单一 v4 collection、document_id 隔离、Markdown 章节/段落/行号定位、第一阶段不做归档/删除。
- 已在 Phase 3 范围内修改相关业务代码和测试，并使用真实 v4 collection 完成阶段性验证；未修改生产配置。

## 已完成 UI 产品方向：文档学习助手 UI 美化与设计系统收口（历史任务）

- 任务卡：`docs/project-management/ui-beautification-task-card.md`。
- 当前阶段：UI-5 已完成；高保真补全进入 UI-HF6 前的收口准备。
- 当前状态：`ready_for_review`；UI-0/UI-1/UI-2/UI-3/UI-4/UI-5、UI-R0～UI-R5、UI-HF0～UI-HF4 已完成，UI-HF5 实现已完成但验收未完全收口。
- 已确认视觉方向：深色知识工作台 + Zinc 表面 + 蓝色主交互；橙色仅用于警告/注意状态。
- 该方向只改变 UI 表现、布局、文案和状态展示，不改变解析、RAG、Embedding、Qdrant、SQLite、会话、笔记或生命周期语义。
- UI-3 已按负责人确认的 Design Tokens 实现；UI-4 已完成独立状态、响应式、可访问性和交互验收；UI-5 已完成独立视觉 QA、全量回归和文档收口；真实生产故障演练未执行，不作为 UI 功能验收前提。

## 当前 UI 重设计任务（负责人反馈后新建，2026-08-02）

- 新任务卡：`docs/project-management/ui-redesign-task-card.md`。
- 当前状态：`ready_for_review`；UI-R0～UI-R5 原阶段功能性实现已完成，UI-HF0～UI-HF4 已完成，UI-HF5 待补齐独立浏览器状态矩阵；UI-HF6 暂不进入。
- Figma 文件：`https://www.figma.com/design/TjKze3Fwc19gCADBrgtuzJ`。
- UI-R1 参考规格：`docs/ui-redesign-reference-spec.md`。
- UI-R2 设计证据：`output/figma-ui-r2/desktop-session.png`、`desktop-library.png`、`mobile-session.png`、`mobile-context-sheet.png`。
- 任务原因：上一轮 UI 主要在原有三栏 Gradio 结构上做主题和 CSS 适配，未充分落实模板的应用外壳、内容宽度、导航层级、消息组件和上下文面板关系。
- 新任务目标：以 Figma 模板实际规格为参考，重设计“空间导航 → 主工作区 → 上下文检查器”的应用骨架、文档库、问答 Composer、来源和笔记组件。
- 当前边界：只允许 UI 表现层、布局、组件组合、文案、Figma 设计和 UI 验证；不得修改解析、RAG、Embedding、Qdrant、SQLite、会话、笔记、引用或生命周期业务语义。
- 阶段顺序：UI-R0 任务卡规划（已完成）→ UI-R1 模板规格提取（已完成）→ UI-R2 Figma 设计稿（已完成）→ UI-R3 负责人评审（已完成）→ UI-R4 应用外壳与主工作区功能性实现（已完成）→ UI-R5 文档库与上下文检查器功能性深化（已完成）→ UI-HF0 高保真差距审计（已完成）→ UI-HF1 应用外壳与空间导航（已完成）→ UI-HF2 文档库高保真工作区（已完成）→ UI-HF3 学习会话与 Composer（已完成）→ UI-HF4 上下文检查器、来源与笔记（已完成）→ UI-HF5 响应式实现完成、独立状态验收待收口→ UI-HF6（不得进入）→ UI-R6/UI-R7 最终回归和收口。
- UI-R3 已冻结默认入口、详情面板、上下文检查器、移动端底部面板和危险操作确认策略。

### UI-HF 高保真补全路线

- 触发原因：当前 UI-R4/UI-R5 的功能性实现与负责人审核的 Figma 设计稿在应用外壳、信息层级、主工作区、Composer、详情面板和移动端面板上仍存在明显差距。
- 基线文档：`docs/ui-high-fidelity-baseline.md`。
- UI-HF0 已完成：已对照 Figma 和当前 UI-R5 截图形成差距矩阵、组件映射、业务语义保护规则和阶段门槛；未修改代码。
- UI-HF1、UI-HF2、UI-HF3、UI-HF4 已完成；UI-HF5 实现完成但验收待收口；UI-HF6 待负责人确认后执行，范围仅限 UI 表现层和 UI 验证。
- 原 UI-R6/UI-R7：不再作为高保真实现替代物，延后作为最终响应式、可访问性、交互和视觉 QA 门禁。

## Phase 2 实际收口（历史完成记录，2026-08-01）

- Phase 2“解析与文档目录闭环”已完成：Markdown 解析、统一解析协议、格式/哈希/状态/错误元数据、稳定定位和临时 SQLite 迁移均已实现并验证。
- 本阶段只完成解析、分块和目录准备；未调用真实 Embedding、未写入 Qdrant、未修改真实 SQLite，因此不宣称完成多文档真实检索隔离。
- 定向测试 9 项通过，全量回归测试 54 项通过；PDF 基线仍为 171 页、262 个非空分块，既有 PDF source_locator 和 chunk ID 未改变。
- 随后已确认进入 Phase 3。

## Phase 3 当前进度（2026-08-01）

- 已实现 PDF/Markdown 统一真实索引入口，保持 `index_pdf()` 兼容。
- 已实现同一 `docqa_text-embedding-v4_dim1024` collection 的 `document_id` 过滤、全部文档范围和文档范围状态切换。
- 已实现重复索引跳过已有 chunk 的 Embedding 调用，并保持 Qdrant point 幂等。
- 已对历史 262 个 PDF points 仅补齐 payload 元数据，未重建向量、未改变 point ID。
- 项目自有 Markdown 已使用真实 `text-embedding-v4` 索引 5 个 points，collection 从 262 增至 267；重复索引仍为 267。
- Phase 3 全量测试和真实范围隔离验证已通过；未经负责人确认不进入 Phase 4。

## Phase 7 完成记录（2026-08-01）

- [x] 完成本地、测试、生产环境边界和密钥管理规则。
- [x] 完成 Qdrant、SQLite、文档和评测结果的备份恢复方案。
- [x] 完成启动、健康检查、有限重试、优雅关闭和回滚方案。
- [x] 完成 Docker Compose、应用容器化与本地运行方式评估。
- [x] 完成日志、指标、错误追踪和成本控制设计。
- [x] 更新 README、环境模板、部署/运维文档和交付清单。
- [x] 保持 v4 1024 维和现有 collection 不变；未执行部署、提交或推送。

## Phase 8 当前记录

- [x] 新增 Qdrant-only `docker-compose.local.yml`，不增加应用容器；HTTP healthz 由 `health` CLI 验证。
- [x] 新增 `health` CLI 和 `backup-sqlite` CLI。
- [x] 新增健康检查、错误分类、备份恢复和脱敏测试。

## Phase 8 完成记录（2026-08-01）

- [x] 真实 `.env` health CLI 返回 `status=ok`。
- [x] Qdrant healthz 返回 200，v3/v4 collection 均为 green、262 points、1024 维。
- [x] SQLite 备份恢复完整性检查通过。
- [x] 真实 v4 smoke test 返回 `answered`，来源页码和 `source_locator` 可追溯。
- [x] 全量 45 项测试、compileall、Compose 配置、diff 检查和凭据扫描通过。
- [x] Phase 8 完成；未执行生产部署、提交或推送。
## 后续产品方向（历史计划，已完成，2026-08-01）

1. 方向 A：完成 Gradio 上传进度 404 的版本隔离调查，保留稳定版本和风险记录。
2. 方向 B：先审查文档生命周期规格，再实现归档、删除、恢复、重新索引和一致性检查；测试仅使用临时 SQLite/Qdrant。
3. 方向 C：实现知识库搜索、筛选、排序、详情和更清晰的索引错误信息。

三个方向已分阶段交付完成；Git P0 已完成，后续不自动进入新的产品阶段。

## 后续方向完成记录（2026-08-01）

- 方向 A：已完成版本隔离调查，保留 Gradio 5.50.0，404 仍为已复现非阻塞依赖风险。
- 方向 B：已完成生命周期服务、临时 SQLite/Qdrant 测试和设计/实现证据；真实文档删除未执行。
- 方向 C：已完成文档搜索、筛选、排序、详情和索引错误脱敏展示，并通过三种视口 UI 回归。

## 当前阶段收口与后续边界（2026-08-01）

- Git P0 已完成：`f3c5403 feat(docqa): deliver local document QA workflow`。
- 方向 A/B/C 与 Git P0 收口阶段全量 pytest 为 73 项；当前 UI-4 回归全量 pytest 为 76 项通过，compileall、diff check、健康检查、敏感信息扫描和真实浏览器验证均已完成。
- Gradio `upload_progress?upload_id=undefined` 404 仍为已复现的非阻塞依赖风险，不能标记为已修复。
- 生命周期测试仅使用临时 SQLite/Qdrant；真实生产删除和真实生产 Qdrant point 删除未执行。
- 下一产品阶段未定义，需负责人另行确认；认证、多租户、公网部署仍不属于当前路线图范围。

## Phase 6 初次执行结果（历史记录，已被最新结果覆盖）

- [x] 使用同一份 30 题评测集运行 v3/v4。
- [x] v3 独立 collection `docqa_text-embedding-v3_dim1024_eval`，262 points，1024 维。
- [x] v4 collection `docqa_text-embedding-v4_dim1024` 评测前后均为 262 points，未被污染。
- [x] 生成 JSON 原始结果和 Markdown 报告。
- [x] 全量测试 34 项通过。
- [ ] 质量门禁未全部通过：v4 有 1 条 DeepSeek 空响应失败；自动评分仍需人工复核。
## UI-5 最新路线状态（2026-08-02）

- UI-0～UI-5：`completed`。UI-5 已完成独立视觉 QA、响应式、可访问性、交互和业务语义回归。
- 当前路线图在 UI-5 收口后停止；不自动创建或执行下一张产品任务卡。
- 全量测试：76 项通过；73 项为历史阶段基线。
- Gradio 上传进度 404 仍为非阻塞技术债务；Git P0 已完成但未推送、未 PR、未部署。
# 当前状态补充（2026-08-02）

UI-HF5 的独立浏览器矩阵已补齐一部分并修复两个 UI 表现层问题：生命周期操作读取文档详情选择器；移动端来源/笔记 Tab 被约束在底部面板内。当前 UI 定向测试 21 项、全量测试 86 项通过。由于仍有若干异步/故障状态未能在安全临时夹具中逐项复现，当前阶段仍为 `ready_for_review`；UI-HF6 不得进入。Gradio `upload_progress?upload_id=undefined` 404 在上传时再次复现，继续作为独立非阻塞风险。
## 当前 UI 高保真路线（2026-08-03）

- HF-R0：视觉基线与修复任务卡——完成。
- HF-R1：统一应用外壳与 P0 结构修复——完成。
- HF-R2：学习会话、消息时间线与 Composer 高保真落地——完成，状态 `ready_for_hf_r3`。
- HF-R3：文档库、工具栏、文档行与详情检查器高保真落地——待负责人确认。
- HF-R4：来源、笔记、平板与移动端高保真落地——待 HF-R3。
- HF-R5：Figma 对照视觉 QA、真实数据状态验收与文档收口——待 HF-R4。

注意：HF-R2 的测试通过不等于整个 Figma 高保真任务完成；当前整体仍需 HF-R3～HF-R5。
