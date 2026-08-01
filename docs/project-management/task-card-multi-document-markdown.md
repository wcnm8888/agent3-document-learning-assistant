# 任务卡：多文档与 Markdown 知识库管理

状态：completed（Phase 6 全量质量门禁与交付收口已完成）

> 当前权威状态（2026-08-01）：Phase 0～6 已完成。真实浏览器问答、来源、笔记、文档切换、响应式验收和全量质量门禁均已通过；Gradio 上传进度 404 保留为非阻塞依赖风险。下方旧阶段描述属于历史记录。

任务等级：L（跨文档解析、Embedding/Qdrant 隔离、SQLite 文档目录、问答过滤和 UI 状态）

审批状态：任务卡和阶段地图已确认；Phase 0～6 均已完成；未执行提交、推送、PR 或 CI。

## 已确认边界

- 本地单用户，不实现认证、用户系统和多租户。
- 所有 PDF/Markdown 使用同一个 `text-embedding-v4`、1024 维 collection。
- 通过 `document_id` 隔离不同文档，查询必须携带明确文档范围或知识库范围。
- Markdown 来源使用章节标题、段落序号和行号生成可追溯定位；不强行伪造 PDF 页码。
- 第一阶段只做上传、解析、索引、查看和文档切换，不实现文档归档或删除。

## 用户目标

个人学习者可以在同一个文档学习助手中上传、管理和切换多个 PDF/Markdown 文档，并围绕指定文档提问，不发生跨文档串库。

## 业务价值

当前项目已经完成单个 PDF 的真实索引、问答、引用、笔记和本地运行闭环。本任务把产品从“单 PDF 演示”推进为可持续使用的个人文档知识库，并补齐产品简报中已经承诺但尚未完成的 Markdown 输入能力。

## 非目标

- 不接入 Neo4j、MQE、HyDE、多模态检索或新的 Embedding 模型。
- 不修改 `text-embedding-v4`、1024 维或现有 v4 collection。
- 不实现用户认证、复杂权限、多租户、计费或公网生产部署。
- 不把不同 Embedding 模型或不同维度向量写入同一 collection。
- 不删除原始 PDF、现有 Qdrant points 或历史学习数据。
- 不根据本任务自动扩展出学习计划、推荐系统或知识图谱。

## 前置条件与历史基线

- 当前项目：`E:\Agent\开发实践\Agent3-智能文档问答助手`
- 当前状态：Phase 0～8 已完成。
- 默认模型：`text-embedding-v4`，1024 维。
- 现有 collection：`docqa_text-embedding-v4_dim1024`。
- 基准文档：`data/reference/Happy-LLM-0727.pdf`。
- 现有全量测试：45 项通过。
- 任务卡已确认，Phase 0 基线审计已完成；业务实现仍须在 Phase 1 规格确认后开始。

## 输入、输出与状态

### 输入

- PDF 文件；
- Markdown 文件；
- 文档名称、格式、文件哈希和用户选择的知识库范围。

### 输出

- 文档目录记录；
- 解析和索引状态；
- 文档页数或章节/行号信息；
- 分块数量和 point 数量；
- 可按 `document_id` 过滤的问答结果和来源引用。

### 状态

`pending → validating → parsing → indexing → indexed`

失败时进入 `failed`，保留可定位错误；重复上传相同内容必须幂等，不得增加重复 points。旧文档仍可正常检索时，新文档失败不得破坏旧文档。

## 建议架构边界

- 新增统一文档解析协议，PDF 和 Markdown 分别实现适配器。
- PDF 继续保留页码来源；Markdown 使用章节标题、段落序号或行号生成 `source_locator`。
- 同一 v4 collection 通过 `document_id` 和 `embedding_profile` 隔离多个文档，不为每个文档创建独立 collection。
- SQLite 保存文档名称、格式、哈希、状态、分块数、point 数、错误信息和更新时间。
- Qdrant 保存向量及来源元数据；本任务不执行删除/归档。未来若增加此能力，必须另建任务卡，按 `document_id` 精确操作并设计恢复方案。
- UI 只调用文档服务和问答服务，不直接操作 Qdrant 或 SQLite。

## 数据与安全边界

- 文档内容只进入本地解析、Embedding、Qdrant 和 SQLite 所需的边界。
- API Key、Token 和 `.env` 内容不得进入日志、数据库、评测结果或来源展示。
- Markdown 中的 HTML、脚本和指令内容只能作为文档数据，不得提升为系统指令。
- 本任务不提供文档删除/归档入口；相关生命周期能力若未来需要，必须另立任务卡并单独设计。
- v4 collection 变更前必须检查 point 数量、维度和来源元数据。

## UI 与交互状态

- 文档库支持 PDF/Markdown 文件类型校验；
- 正常状态显示文档名、格式、状态、页数或章节数、分块数、point 数和更新时间；
- 覆盖 empty、validating、parsing、indexing、success、failed、duplicate 和 database error；
- 支持文档选择/切换，选择后问答必须携带 `document_id` 过滤；
- 切换文档时不得继承不相关文档的来源和问答上下文；
- 继续覆盖 1440×900、1024×768、390×844；
- 不新增认证和权限 UI。

## 阶段地图

### Phase 0：任务卡与基线审计

- 确认 Git 基线、工作区已有修改和允许文件范围；
- 检查当前 PDF 流程、SQLite documents 表、Qdrant metadata 和 UI 文档库；
- 输出能力差异和停止条件。

### Phase 1：规格、架构与测试矩阵

- 确认 PDF/Markdown 解析协议、source_locator 规则、文档生命周期和幂等键；
- 审查 SQLite 是否需要兼容迁移；
- 建立正常、重复、失败、隔离和恢复测试矩阵；
- 用户确认后才进入实现。

### Phase 2：解析与文档目录闭环

- 实现 Markdown 解析和统一解析结果；
- 完善文档格式、哈希、状态和错误记录；
- 先完成定向单元测试和临时目录验证。

### Phase 3：多文档索引与隔离

- 实现多个 PDF/Markdown 的 v4 索引；
- 验证重复索引幂等、失败恢复、point 数量和来源元数据；
- 验证 `document_id` 过滤、文档切换和失败恢复；不执行删除/归档。

### Phase 4：文档库 UI 与问答切换

- 支持 PDF/Markdown 上传；
- 显示文档状态和索引信息；
- 支持文档切换并保持问答、来源和会话隔离；
- 完成响应式和错误状态验收。

### Phase 5：真实验收与独立 QA

- 使用基准 PDF、至少一份项目自有 Markdown 和一个故意损坏文件；
- 验证多文档问答、文档外拒答、来源定位、重复执行和失败恢复；
- 由独立测试视角审查任务卡、diff、测试和真实行为。

### Phase 6：全量质量门禁与交付收口

- 全量测试、compileall、diff 检查、敏感信息扫描；
- 更新 progress、evidence、architecture、decisions 和 README；
- Git 分支、提交、PR 和 CI 只有在用户单独确认后执行。

## 验收标准

1. PDF 和 Markdown 均可通过统一入口上传并进入文档目录。
2. Markdown 能生成非空分块，并保留章节、段落或行号来源。
3. 多个文档可写入现有 v4 collection，向量维度保持 1024。
4. 相同文件重复索引不增加 points，文档失败不破坏已有文档。
5. 按 `document_id` 提问时不会返回其他文档内容。
6. 文档切换后，问答来源和会话上下文不串库。
7. 每个来源包含文档名、document_id、chunk_id、章节/定位信息、source_locator 和分数。
8. 不存在的文档、损坏文件、空 Markdown、重复文档和索引失败均有明确错误。
9. 现有 Happy-LLM PDF 的 262 points、1024 维和既有真实问答结果不回归。
10. 现有 45 项测试不回归，新测试全部通过。

## 测试矩阵

| 风险/行为 | 测试层级 | 必测用例 |
| --- | --- | --- |
| Markdown 解析 | 单元 | 标题、段落、代码块、中文文本、空文件、HTML/指令文本 |
| PDF 回归 | 集成 | 171 页、262 分块、页码和 source_locator 不变 |
| 文档格式校验 | 单元/UI | 非 PDF/Markdown、扩展名伪装、损坏文件 |
| 重复索引 | 集成 | 同文件重复、同名不同内容、相同哈希幂等 |
| 多文档隔离 | 集成/真实 | document_id 过滤、文档切换、跨文档拒答 |
| Qdrant | 集成 | 1024 维、point 数量、metadata 完整、失败恢复 |
| SQLite | 数据库 | 迁移、事务、唯一约束、重复执行、恢复和完整性 |
| UI | 浏览器 | empty、loading、success、failed、duplicate、三种视口 |
| 安全 | 静态/人工 | 无密钥泄露、Markdown 不提升为系统指令 |

## 允许与禁止修改

允许修改：

- `src/doc_qa/` 文档解析、摄入、文档目录、Qdrant 元数据和 UI 适配层；
- `tests/` 相关测试；
- `docs/` 当前任务、架构、实现计划、进度和证据；
- 必要的 `.env.example` 和 README 说明。

禁止修改：

- 生产配置、生产数据、真实 `.env`；
- 现有 v4 collection 的模型和维度；
- v3 评测 collection；
- Neo4j、认证、计费和多租户系统；
- 与本任务无关的历史代码和测试；
- 不删除文件、不提交、不推送、不创建 PR，除非另行确认。

## 风险与回滚

- SQLite schema 变化必须先做兼容性审查和临时数据库迁移测试；
- 本任务不修改或删除既有 Qdrant points；未来若增加文档生命周期操作，必须另立任务卡并设计 point 数量校验与恢复方案；
- 解析策略改变可能影响既有 PDF 的 chunk ID，默认不得重建现有 v4 collection；
- 若 Markdown 解析或多文档索引失败，回滚到当前单 PDF 流程，不覆盖现有 points；
- 所有真实数据验证优先使用临时 Qdrant/SQLite，最后才进行基准文档只读回归。

## 完成定义

- [x] Phase 2/3/4 范围内的任务卡验收标准全部通过；
- [x] PDF 回归、Markdown 新增测试和 Markdown 引用定位测试全部通过；
- [x] 多文档隔离、重复索引和失败恢复有真实证据；
- [x] UI 状态和三种视口完成验收；
- [x] 独立 QA 已审查 diff、测试和真实结果；
- [x] README、architecture、implementation-plan、progress、evidence 已同步；
- [x] 本阶段修改范围内无敏感信息和无关修改；
- [ ] Git 提交、PR 和 CI 仅在用户明确确认后执行。

## 审批结论

1. 已确认接受“同一 v4 collection + `document_id` 隔离多个文档”。
2. 已确认 Markdown 使用章节、段落和行号定位，不伪造 PDF 页码。
3. 已确认第一阶段只做上传、索引、查看和切换，不做文档归档/删除。
4. 已确认保持本地单用户，不实现认证和多租户。

## 当前阶段完成状态

Phase 5 独立 QA 和 Phase 6 全量质量门禁均已完成。真实 DeepSeek 问答、PDF/Markdown 来源、笔记、文档切换、会话隔离、响应式验收和质量门禁均已通过。

## Phase 4 实际执行结果（2026-08-01）

- [x] Gradio 文档库支持 PDF、Markdown 和 `.markdown` 上传，并覆盖扩展名、文件存在性和空文件校验。
- [x] 文档表展示格式、短 document_id、状态、页数或 Markdown 单元数、分块、points、定位方案、更新时间和脱敏错误。
- [x] 问答范围支持全部文档和指定 document_id；切换时清空回答、来源、待保存笔记和临时上下文，保留 SQLite 历史数据。
- [x] PDF 来源展示页码；Markdown 来源允许空页码并展示章节、段落和行号定位。
- [x] Gradio 页面通过现有业务服务调用索引、问答、笔记和统计能力，不直接访问 Qdrant、SQLite 或第三方 API。
- [x] 1440×900、1024×768 和 390×844 浏览器检查通过，截图已保存到 `output/playwright/`。
- [x] UI 定向测试 7 项通过，Phase 2/3/4 回归测试通过。

Phase 4 完成定义满足；本轮不自动进入 Phase 5。

## Phase 1 设计结论（2026-08-01）

### 统一解析协议

采用 `DocumentSource → DocumentUnit → DocumentChunk` 三层结构：

- `DocumentSource`：`document_id`、`document_name`、`format`、`source_path`、`content_hash`、`embedding_profile`、`source_locator_scheme`；
- `DocumentUnit`：`section_path`、`section`、`paragraph_index`、`line_start`、`line_end`、`page_start`、`page_end`、`content`；
- `DocumentChunk`：继承文档身份和来源字段，增加稳定 `chunk_id`，用于 Embedding、Qdrant payload 和引用。

PDF 的 `page_start/page_end` 保留现有页码语义；Markdown 的页码字段为空，使用章节路径、段落序号和行号定位。

### 来源定位规则

- PDF：保持现有 `<document_name>#page=<page>&chunk=<chunk_id>` 兼容格式；
- Markdown：使用 `<document_name>#section=<encoded_section_path>&paragraph=<n>&lines=<start>-<end>&chunk=<chunk_id>`；
- 章节路径按嵌套标题从根到当前标题生成；无标题内容使用“根文档”；
- 代码块、列表、表格和 HTML 保留为文档数据并记录原始行范围；不执行 HTML/脚本，不把文档内指令提升为系统指令；
- 空章节不生成分块；空文件或过滤后无非空内容进入 failed。

### 身份与幂等

- `document_id` 和 `content_hash` 均基于原始文件字节 SHA-256；不使用文件名作为身份；
- 相同内容重复上传返回 duplicate 结果，不新建 points，不覆盖既有 canonical 文档元数据；
- 同名不同内容生成不同 document_id；内容变化保留为新文档，不执行旧文档删除；
- `chunk_id = SHA-256(document_id + stable_locator_without_chunk + normalized_content + embedding_profile)`；
- `embedding_profile` 固定为 `text-embedding-v4:1024`，不得与其他模型或维度混用。

### 状态与范围隔离

- 文档状态：`pending → validating → parsing → indexing → indexed`；失败路径进入 `failed`；`duplicate` 是一次摄入操作结果，不覆盖已索引文档的 canonical `indexed` 状态；
- 所有文档写入 `docqa_text-embedding-v4_dim1024`，查询使用 `document_id` 过滤或显式的“全部文档”知识库范围；
- 切换文档范围时清空当前 UI 的回答、来源、待保存笔记和会话上下文；旧会话与历史数据仍保留在 SQLite；
- 笔记只能关联当前会话真实引用中的 `document_id` 和 `source_locator`。

### SQLite 迁移审查

- `documents` 表建议新增 `format`、`content_hash`、`embedding_model`、`embedding_dimension`、`source_locator_scheme`、`created_at` 和通用来源计数字段；
- 现有 PDF 数据通过默认值和回填保持兼容；新增字段采用可重复的 additive migration；
- 迁移前备份 SQLite，迁移后执行 foreign key、integrity_check、唯一性和既有会话/引用回归；
- 本阶段不执行 Schema 修改，不做删除/归档，不覆盖现有真实数据。

### Phase 1 交付物

- 统一规格已写入 `docs/architecture.md`、`docs/database-design.md` 和本任务卡；
- UI 影响已写入 `docs/design-spec.md`；
- 测试矩阵已写入 `docs/multi-document-test-matrix.md`；
- 关键取舍已写入 `docs/decisions.md`；
- Phase 2 实现前置条件和风险已同步到 `current-task.md`、`progress.md`、`evidence.md` 和 `implementation-plan.md`。

## Phase 4 UI 最终收口（2026-08-01）

- Gradio 文档库、PDF/Markdown 上传、索引状态、范围切换、问答、来源、笔记和会话隔离已完成。
- 旧版 SQLite `citations.page_start/page_end NOT NULL` 已兼容迁移为可空字段，保留既有引用数据；Markdown 引用可保存和重新读取而不伪造页码。
- 真实 Markdown 问答来源已验证包含章节、段落和 `lines=` 定位；全量测试最终 64 项通过。
- Phase 4 完成，下一步仅为负责人确认后进入 Phase 5 独立 QA。

## Phase 5 独立 QA 最终结果（2026-08-01）

- 已通过：自动化回归、健康检查、v4 collection 隔离、PDF/Markdown 文档库、重复索引、空文件、损坏 PDF、范围切换、来源结构和响应式视口。
- 已确认：真实 DeepSeek PDF/Markdown 问答成功，来源展开、笔记创建/更新和完整会话端到端复验通过。
- 已确认：Gradio `upload_progress?upload_id=undefined` 404 不影响上传、索引和页面状态，保留为非阻塞风险。
- 当前状态：Phase 5 `completed`，已进入并完成 Phase 6 质量门禁。

## Phase 6 全量质量门禁与交付收口（已完成，2026-08-01）

- [x] 全量 pytest 67 项通过；compileall、`git diff --check` 和敏感信息扫描通过。
- [x] `doc_qa.cli health` 返回 `status=ok`；Qdrant healthz HTTP 200；SQLite integrity check 为 `ok`。
- [x] v4 collection `docqa_text-embedding-v4_dim1024` 为 267 points、1024 维，其中 PDF 262、Markdown 5；267 个 point 的必需来源元数据完整。
- [x] v4 全部 point 使用 `text-embedding-v4:1024`；v3 评测 collection 保持独立，未污染 v4。
- [x] README、current-task、roadmap、progress、evidence、implementation-plan 和 release-checklist 已同步当前收口状态。
- [x] 不提交、不推送、不创建 PR、不部署；Git 提交项保持待负责人单独确认。
