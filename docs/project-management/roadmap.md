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

> 当前权威状态（2026-08-01）：多文档与 Markdown 任务卡的 Phase 2、Phase 3、Phase 4、Phase 5、Phase 6 已完成；本文件前部的“等待 Phase 2”属于历史规划记录。Gradio 上传进度 404 仍是非阻塞依赖风险。
### 历史单 PDF 路线摘要（只读）

Phase 0/2/3/4/5/6/7/8 已收口；多文档与 Markdown 知识库管理已完成任务卡确认、Phase 0 基线审计和 Phase 1 规格设计，尚未开始业务实现，等待确认进入 Phase 2。Phase 8 只完成本地运行时能力和验证，没有执行生产部署或公网暴露。Neo4j、用户系统、多租户和多模态能力仍不属于第一版范围。

## 当前任务：多文档与 Markdown 知识库管理（Phase 6 completed）

- 用户价值：从单 PDF 闭环扩展为可持续使用的个人文档知识库。
- 关键范围：Markdown 解析、多文档目录、文档切换、索引幂等、文档隔离和来源定位。
- 任务卡：`docs/project-management/task-card-multi-document-markdown.md`。
- 当前阶段：Phase 6 全量质量门禁与交付收口已完成；未经负责人确认不自动进入新的产品阶段。
- 已确认：本地单用户、单一 v4 collection、document_id 隔离、Markdown 章节/段落/行号定位、第一阶段不做归档/删除。
- 已在 Phase 3 范围内修改相关业务代码和测试，并使用真实 v4 collection 完成阶段性验证；未修改生产配置。

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
## 后续产品方向（独立执行，2026-08-01）

1. 方向 A：完成 Gradio 上传进度 404 的版本隔离调查，保留稳定版本和风险记录。
2. 方向 B：先审查文档生命周期规格，再实现归档、删除、恢复、重新索引和一致性检查；测试仅使用临时 SQLite/Qdrant。
3. 方向 C：实现知识库搜索、筛选、排序、详情和更清晰的索引错误信息。

三个方向分阶段交付；全部完成后等待负责人决定是否进入 Git P0。

## 后续方向完成记录（2026-08-01）

- 方向 A：已完成版本隔离调查，保留 Gradio 5.50.0，404 仍为已复现非阻塞依赖风险。
- 方向 B：已完成生命周期服务、临时 SQLite/Qdrant 测试和设计/实现证据；真实文档删除未执行。
- 方向 C：已完成文档搜索、筛选、排序、详情和索引错误脱敏展示，并通过三种视口 UI 回归。

## Phase 6 初次执行结果（历史记录，已被最新结果覆盖）

- [x] 使用同一份 30 题评测集运行 v3/v4。
- [x] v3 独立 collection `docqa_text-embedding-v3_dim1024_eval`，262 points，1024 维。
- [x] v4 collection `docqa_text-embedding-v4_dim1024` 评测前后均为 262 points，未被污染。
- [x] 生成 JSON 原始结果和 Markdown 报告。
- [x] 全量测试 34 项通过。
- [ ] 质量门禁未全部通过：v4 有 1 条 DeepSeek 空响应失败；自动评分仍需人工复核。
