# 当前实施计划

## 状态

- 当前任务：`CTX-001 在 Agent3 中复现上下文工程核心知识`；
- 当前分支：`feat/ctx-001-context-engineering`；
- 当前 Step：`Step 7 文档与 Git 收口（ready_for_review：Draft PR #2 已创建，等待审查）`；
- 任务卡：[CTX-001](project-management/task-card-context-engineering.md)；
- 方案 A2、自动门禁和真实 UAT 已获负责人复核；负责人接受窄表格关系问法的剩余模型限制并确认 Step 6 通过，现已批准进入 Step 7，未部署。

## Step 地图

| Step | 目标 | 状态 |
|---|---|---|
| Step 0 | 基线与契约冻结 | `completed` |
| Step 1 | 上下文模型与配置 | `completed` |
| Step 2 | GSSC 纯流水线 | `completed` |
| Step 3 | SQLite 历史与笔记候选 | `completed` |
| Step 4 | 现有问答链路接入 | `completed` |
| Step 5 | 上下文评测与安全回归 | `completed` |
| Step 6 | 全量门禁与真实验收 | `completed` |
| Step 7 | 文档与 Git 收口 | `ready_for_review` |

## Step 0 执行计划

1. 记录分支、工作区和现有配置事实；
2. 运行 `python -m pytest`，确认现有全量行为基线；
3. 冻结以下兼容契约：现有 Evidence 12000 字符、history 6 轮/4000 字符、`document_id` filter、引用定位、无结果不调用 LLM、UI scope 切换清空短期上下文；
4. 冻结新配置默认值和六分区 Prompt 契约；
5. 新增 `tests/test_context_builder.py`，覆盖模型、配置、分区、事实权限、预算、稳定性和超限错误；
6. 运行新增测试，确认只因尚未实现 ContextBuilder API 而按预期失败；
7. 更新任务卡、current-task、progress 和 evidence，标记 Step 0 结果；
8. 停止并等待负责人确认 Step 1。

## Step 0 文件范围

允许修改：

- `docs/project-management/task-card-context-engineering.md`；
- `docs/project-management/current-task.md`；
- `docs/project-management/roadmap.md`；
- `docs/project-management/progress.md`；
- `docs/project-management/evidence.md`；
- `docs/README.md`；
- 本文件；
- `tests/test_context_builder.py`。

明确不修改：

- `src/doc_qa/` 下全部业务代码；
- 现有测试文件；
- SQLite schema、真实 SQLite 数据、Qdrant collection 和 points；
- CI、部署、认证或多租户配置。

## Step 0 完成门禁

- [x] 现有全量测试重新运行通过：95 项；
- [x] 默认预算、稳定分区、事实权限和失败行为写入 8 个可执行测试；
- [x] 新测试以预期缺失实现原因 RED，不是语法、环境或夹具错误；
- [x] `compileall` 和 `git diff --check` 通过；
- [x] 工作区只有批准范围内文件；
- [x] 文档与 Git 分支、当前 Step 和真实证据一致；
- [x] 负责人复核 Step 0 输出并批准进入 Step 1。

## Step 0 冻结结果

- 默认总预算：18000 估算 Token、20000 字符；
- 分区预算：Evidence 12000 字符、history 6 轮/4000 字符、notes 3 条/2000 字符；
- 固定顺序：Policies → Task → Evidence → Conversation → Notes → Output；
- 事实权限：只有实际进入 Prompt 的本轮 Qdrant Evidence 可进入 source IDs；
- RED：`tests/test_context_builder.py` 8 项失败，失败原因是 `ContextPacket` / `ContextConfig` 尚未实现；
- 测试收集：现有 95 + 新增 8 = 103 项。

## Step 1 执行计划

1. 在 `models.py` 新增 Token 估算器、`ContextPacket` 和 `ContextBuildResult`；
2. Packet 校验 kind、内容、score、稳定顺序和 RAG 必需来源元数据；
3. Packet 的 `char_count`、`estimated_tokens`、`evidence_eligible`、`pinned` 由模型派生；
4. 在 `config.py` 新增 `ContextConfig`，落实冻结默认值和跨字段校验；
5. 先运行 Packet/Config 两项定向测试，再运行整个 context test 文件；
6. Builder 相关 6 项必须继续因缺少 `context_builder` 而 RED；
7. 运行原有 95 项回归、compileall 和 diff 检查；
8. 更新证据并停止等待 Step 2。

## Step 1 完成门禁

- [x] Packet/Config/BuildResult/Settings 映射共 5 项定向测试通过；
- [x] `ContextBuildResult` 是不可变、可比较的诊断结果模型；
- [x] 事实权限不能由 metadata 提升；
- [x] 冻结默认预算与跨字段校验通过；
- [x] Builder 相关 6 项测试保持预期 RED；
- [x] 原有 95 项回归通过；
- [x] `compileall`、`git diff --check` 和范围检查通过；
- [x] 负责人复核 Step 1 并批准进入 Step 2。

## Step 1 实现结果

- 新增 `estimate_tokens`，覆盖中文、英文/数字和标点的确定性保守估算；
- 新增不可变 `ContextPacket`，校验 kind、内容、时区、score、稳定顺序、保留 metadata 和 RAG 来源字段；
- `evidence_eligible` 与 `pinned` 只从 kind 派生；
- 新增不可变 `ContextBuildResult`，冻结分区预算、丢弃原因和压缩事件；
- 新增 `ContextConfig`；`Settings.context_config` 只映射现有 Evidence/history 配置，其余使用冻结默认值，不扩大环境变量表面；
- 测试收集：原有 95 + 上下文契约 11 = 106 项；
- 当前 context 文件：5 项 GREEN，6 项因 Step 2 Builder 未实现而预期 RED。

## Step 2 执行计划

1. 新增无 I/O 的 `ContextBuilder` 和 `ContextBuildError`；
2. 实现 Gather：Citation/history/note 和固定分区适配；
3. 实现 Select：scope、去重、相关性/新近性、稳定顺序与分区字符预算；
4. 实现 Structure：固定六分区及 Evidence/non-evidence 标签；
5. 实现 Compress：history → notes → 低排名 Evidence → 最小 Evidence 的确定性降级；
6. 生成 `ContextBuildResult` 预算、选择、丢弃和压缩诊断；
7. 运行全部上下文测试和原有 95 项回归；
8. 更新证据并停止等待 Step 3。

## Step 2 完成门禁

- [x] 现有 6 项 Builder RED 全部转绿，并补充边界用例至 15 项；
- [x] 六分区顺序和空状态稳定；
- [x] history/note 永久为 non-evidence；
- [x] scope/重复/低相关/预算丢弃原因可观察；
- [x] Token/字符双预算和 fail-closed 通过；
- [x] 相同输入、配置、时钟结果完全一致；
- [x] 原有 95 项回归通过；新增测试后全量 110 项通过；
- [x] `compileall`、`git diff --check`、纯模块边界和范围检查通过；
- [x] 负责人复核 Step 2 并批准进入 Step 3。

## Step 2 实现结果

- 新增纯 `ContextBuilder` / `ContextBuildError`，不访问网络、SQLite、Qdrant client 或 LLM；
- Gather、Select、Structure、Compress 均使用不可变 Packet/BuildResult 契约；
- Prompt 固定为六分区，Evidence 与 Conversation/Notes 明确隔离；
- 支持 scope、重复、最低相关性、稳定排序、分区预算、总预算和 pinned reserve；
- 超限按 Conversation → Notes → 低排名 Evidence → 最终 Evidence 截断确定性降级，无法满足最小契约时 fail-closed；
- 定向测试 15 项、全量测试 110 项通过；`compileall`、`git diff --check` 和纯边界检查通过。

## Step 3 执行计划

1. 冻结 SQLite 历史/笔记候选的只读返回契约，不改变现有 schema；
2. 为当前 session 提供受轮数与字符预算约束的历史候选；
3. 为当前 session 提供受 document scope、数量与字符预算约束的笔记候选；
4. 未指定 document scope 时允许当前 session 的无文档/有文档笔记作为候选；指定 scope 时只允许无文档关联或同文档笔记；
5. 保持候选为历史/笔记数据，不赋予 Evidence 或引用资格；
6. 在 LearningService 暴露统一只读候选入口，但不接入 QA 或 ContextBuilder；
7. 用隔离 SQLite 夹具验证 session/document 隔离、稳定顺序、预算和无 schema 变化；
8. 完成定向与全量门禁后停止等待 Step 4。

## Step 3 文件范围

- 允许修改：`src/doc_qa/memory_store.py`、`src/doc_qa/learning.py`、`tests/test_phase4_learning.py`；
- 如只读返回契约确有必要，可最小修改 `src/doc_qa/models.py` 或新增独立测试文件；
- 允许更新当前任务状态与证据文档；
- 明确不修改：`qa.py`、`context_builder.py`、`qdrant_index.py`、UI/CLI、SQLite schema/迁移、Qdrant collection/points 和真实数据。

## Step 3 完成门禁

- [x] 历史候选只来自当前 session、遵守轮数窗口并至少保留最新一轮；最终严格预算由 Builder 收口；
- [x] 笔记候选只来自当前 session，并遵守 document scope、数量与字符预算；
- [x] 候选顺序稳定，超限行为可复现；
- [x] history/note 不获得 Evidence 或引用资格；
- [x] 不修改 SQLite schema，不写入或迁移真实数据；
- [x] Step 3 定向测试 12 项、联合定向测试 27 项和全量 115 项通过；
- [x] `compileall`、`git diff --check`、敏感信息和范围检查通过；
- [x] 负责人复核 Step 3 并批准进入 Step 4。

## Step 3 实现结果

- 新增不携带旧 citations 的不可变 `ConversationContextCandidate`；
- `context_history_candidates` 按 session 和最近轮次返回时间正序历史；为兼容原行为至少保留最新一轮，最终严格预算由 Builder 收口；
- `context_note_candidates` 严格按 session、document scope、更新时间、数量和字符预算返回完整笔记；
- 指定 document scope 时，仅允许无文档关联或关联当前文档的笔记；
- `LearningService.get_context_candidates` 返回不可变 `ContextCandidates`，不调用 QA、Builder 或 LLM；
- 只读测试确认候选读取不改变 schema、持久数据或 SQLite `total_changes`；
- 最终全量测试 115 项通过，既有 110 项无回归。

## Step 4 执行计划

1. 在 `QuestionAnswerService` 构造时注入或按配置建立唯一 `ContextBuilder`；
2. 将直接问答和会话问答的最终 system/user Prompt 统一交给 Builder；
3. `LearningService` 在未显式提供 UI scope history 时读取 SQLite history/notes 候选；显式 history 继续优先，保持范围切换后的清空语义；
4. 无检索结果继续在 Builder/LLM 前返回 `no_results`；
5. 最终引用只允许来自 `ContextBuildResult.included_citation_ids` 与模型 `source_ids` 的交集；
6. 保留现有模型 JSON、回答来源标记、PDF/Markdown locator 和错误传播行为；
7. 为直接 QA、session QA、document scope、notes non-evidence、预算和引用白名单补定向测试；
8. 完成定向与全量门禁后停止等待 Step 5。

## Step 4 文件范围

- 允许修改：`src/doc_qa/qa.py`、`src/doc_qa/learning.py`、必要的 UI/CLI 构造接线；
- 允许修改：`tests/test_phase3_qa.py`、`tests/test_phase4_learning.py`，必要时最小修改 UI/CLI 回归测试；
- 允许更新当前任务状态与证据文档；
- 明确不修改：`qdrant_index.py` 检索/collection 契约、SQLite schema/迁移、Embedding/摄取链路、真实数据和部署配置。

## Step 4 完成门禁

- [x] 直接 QA 与 session QA 使用同一 ContextBuilder 最终入口；
- [x] RAG、history、notes 进入固定六分区，history/note 保持 non-evidence；
- [x] 最终 citations 只来自实际进入 Evidence 的本轮 Qdrant citations；
- [x] `document_id` 过滤、UI scope 清空和无结果不调用 LLM 行为不变；
- [x] Prompt 满足 Token/字符预算，构建失败不调用 LLM；
- [x] PDF/Markdown locator、JSON 解析、来源标记和错误传播不回归；
- [x] Step 4 定向测试 77 项、全量测试 119 项通过，原有 115 项无回归；
- [x] `compileall`、`git diff --check`、敏感信息和范围检查通过；
- [x] 负责人复核 Step 4 并批准进入 Step 5。

## Step 4 实现结果

- `QuestionAnswerService` 默认使用 `Settings.context_config` 构造唯一 ContextBuilder，也支持测试注入；
- 旧 `_build_context` / `_build_conversation_context` 已移除，chat 只接收 Builder 的 system/user Prompt；
- LearningService 未显式收到 history 时使用 SQLite 候选；UI 显式空 history 保持优先，同时仍注入当前范围笔记；
- 无检索结果继续在 Builder/LLM 前返回，历史或笔记不能单独触发回答；
- 模型 `source_ids` 只在 `included_citation_ids` 白名单内解析，回退也只使用实际进入 Evidence 的 citations；
- `last_context_build` 提供最近一次成功构建的选择、预算和压缩诊断，不记录额外正文日志；
- 直接 QA、session QA、UI/CLI 均通过现有服务构造进入统一入口，无需修改产品 UI/CLI 代码；
- 定向测试 77 项、全量测试 119 项通过；无 schema/write SQL、collection、向量或真实数据变化。

## Step 5 执行计划

1. 冻结单文档事实、Markdown 定位、多轮指代、历史/笔记冲突、文档范围、超预算、提示注入和无结果用例；
2. 新增离线、只读的上下文评测入口，只读取冻结 JSONL，不访问 Qdrant、SQLite、网络或 LLM；
3. 记录每例实际 Evidence 来源、最终引用白名单、分区预算、丢弃/截断事件、自动事实来源判定和待人工结论；
4. 将自动结构门禁与人工语义复核明确分离，不把自动通过等同于真实问答验收；
5. 补充历史/笔记 non-evidence、注入文本不可提升权限、no_results 不构建 Prompt 等安全回归；
6. 执行离线评测、定向测试、全量测试和静态门禁，完成后停止等待 Step 6。

## Step 5 文件范围

- 允许新增：`eval/context-engineering-cases.jsonl`、`eval/run_context_evaluation.py`、上下文评测定向测试；
- 允许修改：`eval/README.md`、`eval/rubric.md` 和当前任务状态/证据文档；
- 仅在回归揭示 CTX-001 缺陷时修改已批准的上下文/QA 测试或实现文件；
- 明确不运行真实 Embedding、Qdrant、DeepSeek，不修改 `eval/results/`、schema、collection、向量或真实数据。

## Step 5 完成门禁

- [x] 冻结评测集覆盖任务卡规定的十类上下文与安全情景；
- [x] 离线评测入口默认只读、输出结构化诊断且不包含完整 Prompt/正文；
- [x] 事实来源、引用白名单、范围、预算、稳定压缩和 no_results 自动门禁通过；
- [x] 人工 rubric 明确标记真实回答语义与提示注入抵抗仍需 Step 6/UAT 复核；
- [x] 上下文评测定向测试、相关回归和全量测试通过；
- [x] `compileall`、`git diff --check`、敏感信息、外部调用和范围检查通过；
- [x] 负责人复核 Step 5 并批准进入 Step 6。

## Step 5 实现结果

- 冻结十类 JSONL 用例并新增默认只读评测器，10/10 自动结构门禁通过且重复结果一致；
- 输出包含检索元数据、Evidence/最终引用 ID、分区用量、丢弃原因、压缩事件与事实来源判定，不包含完整 Prompt 或候选正文；
- history/note 冲突、提示注入、跨文档候选均未提升事实或 citation 权限；无检索用例不构建 Prompt；
- 联合定向测试 88 项、全量测试 127 项通过，Step 5 前既有 119 项无回归；
- 真实模型语义、冲突裁决和提示注入抵抗保持人工 `pending`，没有以自动结构结果替代 Step 6/UAT；
- 未访问或修改真实外部服务、schema、collection、向量、SQLite 数据和 `eval/results/`。

## Step 6 执行计划

1. 记录真实验收前的 collection、文档目录、SQLite 文件状态和工作区基线，禁止写入或重建；
2. 重新执行冻结上下文评测、任务卡定向矩阵、全量 pytest、compileall、diff、范围、敏感信息和链接门禁；
3. 使用现有真实已索引 PDF / Markdown 和生产问答链路完成只读事实问答、追问、笔记候选、范围隔离、无答案和超预算验收；
4. 真实会话/笔记场景只传入内存候选，不调用持久化写接口，不修改真实 SQLite；
5. 对每个 UAT 记录检索/引用元数据、事实来源、预算诊断和人工 rubric，不在文档中复制完整正文或凭据；
6. 验收后复核 collection point 数、文档目录和 SQLite 文件状态未变化；
7. 完成后停止等待 Step 7，不提交、不推送、不创建 PR、不合并、不部署。

## Step 6 文件与数据范围

- 允许修改：验收测试/脚本仅在现有入口无法安全复现时最小新增，以及当前架构、测试、评测、任务状态和证据文档；
- 允许读取：现有真实 collection、已索引文档元数据、本地配置和冻结评测集；
- 真实问答仅允许搜索和模型生成，不允许摄取、删除、重建 collection 或写入真实会话/笔记；
- 明确不修改：业务 schema、Qdrant points、Embedding/摄取链路、真实 SQLite 数据、`eval/results/`、部署与 CI 配置。

## Step 6 完成门禁

- [x] 冻结评测、任务卡定向矩阵、全量 pytest 和静态门禁全部通过；
- [x] 真实 PDF/Markdown 单轮事实问答与 locator 人工复核通过；
- [x] 多轮指代、相关笔记、文档范围、无答案和超预算真实链路按负责人调整后的口径完成验收；窄表格关系问法的拒答作为已接受限制保留；
- [x] history/notes 冲突或注入没有覆盖 Evidence，最终 citation 保持白名单；
- [x] 验收前后 collection、SQLite 和工作区受保护数据无变化；
- [x] 真实 API 失败、成本或非确定性如实记录，不伪造结论；
- [x] 非唯一实现者/负责人复核 UAT 结论；
- [ ] 负责人批准进入 Step 7。

## Step 6 当前结果与验收

- 任务卡定向矩阵 93 项、全量测试 127 项、冻结结构评测 10/10、compileall、diff、范围、敏感信息和链接门禁通过；
- SQLite 只读基线前后完全一致：schema 版本、7 张业务表计数、主库/WAL 大小与 SHA-256 均未变化，连接 `total_changes=0`；
- 使用 SQLite 已登记的真实 PDF/Markdown 原文、生产 ContextBuilder/QA 引用逻辑和真实 DeepSeek 完成降级 UAT：PDF 事实、Markdown locator、多轮指代、恶意笔记、scope、no_results 和超预算场景通过；
- 首轮临时脚本因 PowerShell stdin 编码把中文问题改成 `?`，连续两次产生假失败；统一 UTF-8 并验证输入后恢复正常，后续验收不得省略输入编码自检；
- 多轮 UAT 的首个过度含糊问法被模型拒答，改为仍依赖历史但指代更明确的问法后通过，说明模型对模糊指代仍有非阻塞质量风险；
- 上述降级 UAT 的候选来自真实源文件只读解析，不是在线 Qdrant 搜索，不能替代任务卡 17.5 的完整真实检索验收；
- 当前 `localhost:6333/healthz` 返回 502，v4/v3 collection 均不可读；Docker daemon 不可连接、Docker Desktop 不存在，本地文件式 Qdrant `collections={}`；
- 负责人已恢复 Qdrant；恢复后的只读基线为 v4 300 points（PDF 295、Markdown 5）和 v3 262 points。SQLite 对 PDF 记录 262 chunks，与 Qdrant 存在既有 33-point 差异；本任务只记录风险，不修改 collection。

在线 UAT 中，PDF 授权事实与第 4 页定位、Markdown 章节/段落/行号定位、恶意笔记 non-evidence、PDF→Markdown scope 切换、no_results 不调用模型和超预算压缩均通过。v4 point 数验收前后保持总计 300、PDF 295、Markdown 5；SQLite 和受保护路径保持不变。

多轮指代题中 Qdrant 已返回包含答案的第 2 页，Conversation Packet 已被选中，但模型仍回答证据不足。已两次最小强化“Conversation 仅用于指代消解、最终事实仍以 Evidence 为准”的 Prompt 契约；自动门禁通过，但真实模型仍拒答。同一根因连续三次验证失败，触发任务卡停止条件。

解除条件：负责人决定下一处理方向并重新批准范围——允许单独设计查询改写/显式指代解析，或接受当前模型限制并调整多轮 UAT 口径。当前不得继续扩大 Prompt 改动、改变固定分区顺序或进入 Step 7。

负责人已选择并批准方案 A，当前扩展契约如下：

- 新增无 I/O、无 LLM 的确定性指代解析器，只在当前问题包含指代且存在最近历史时启用；
- 最近历史只生成受字符预算约束的用户意图提示，用于检索查询补全和 Task 指代补全；
- 提示必须显式标记 non-evidence，不得获得 citation/evidence eligibility；
- 保持固定六分区、现有 Qdrant Evidence 唯一事实来源、no_results 短路和最终引用白名单；
- 不实现 MQE、HyDE、多查询、额外模型调用或 Agent；
- 完成后重跑自动门禁、在线多轮 UAT 和 Qdrant/SQLite 前后不变校验。

方案 A 复验结果：

- 新增纯 `ReferenceResolver`，仅识别显式指代、选择最近有效历史，并把不超过 600 字符的 non-evidence 提示用于单次检索和 Task；
- `ContextBuildResult` 增加是否启用解析、来源轮次和提示字符数诊断；固定六分区、Evidence 唯一事实权限、引用白名单与 no_results 短路不变；
- 指代/Builder/QA 定向 41 项、全量 pytest 134 项、冻结评测 10/10、compileall 和 diff 门禁通过；
- 在线复验中解析已启用，54 字符提示进入检索与 Task；Qdrant 首个命中为包含预期答案的 PDF 第 2 页，但 DeepSeek 仍返回证据不足；
- v4/v3 point 数与 SQLite 文件散列、表计数前后不变。方案 A 当时未满足多轮真实语义验收，Step 6 曾再次进入 `blocked`，不得继续扩大实现或进入 Step 7。

负责人随后批准方案 A2，新增契约：

- 从最近有效历史中确定性提取可验证的指代对象；只有可靠提取时才生成独立问题，无法提取时沿用有界 non-evidence 提示，不猜测对象；
- 独立问题同时用于单次 Qdrant 检索和 Task，历史对象只定义用户意图，文档事实仍只能来自 Evidence；
- 模型明确回答证据不足时，最终 citations 必须为空，不再回退附加全部 Evidence；
- 不新增 LLM 调用、MQE、HyDE、多查询、Agent，不修改 Qdrant/SQLite 数据与 schema；
- 完成后重跑方案 A2 定向测试、全量基线、冻结评测和同一在线 UAT。

方案 A2 复验结果：

- 示例被确定性改写为“Happy-LLM 第二章的内容导航还列出了什么动手实践？”，并同时用于 Embedding 检索和 Task；无法可靠提取的普通代词不会生成虚假独立问题；
- 模型明确拒答时，无论返回何种 source IDs，最终 citations 均为空且不追加空的“参考来源”；
- A2 定向测试 47 项、全量 pytest 140 项、冻结评测 10/10、compileall 和 diff 门禁通过；
- 同一在线 UAT 检索 5 条 Evidence、上下文 6534 字符/3969 估算 Token且未超限，但 DeepSeek 仍返回“根据当前文档片段不足以回答”；拒答引用修正生效，最终 citations 为空；
- v4/v3 collection 保持 300/262 points；SQLite 文件指纹、7 张业务表计数和 `total_changes=0` 前后不变；
- 方案 A2 当时仍未满足原多轮真实回答口径，Step 6 曾再次进入 `blocked`；该状态随后由负责人调整验收口径并确认通过而解除。

负责人最终人工验收：

- 普通问题可正常回答并展示引用；窄表格关系问题稳定安全拒答且不附加误导引用；
- 改用明确问题“Happy-LLM 第二章讲了什么内容”后，系统正确回答 Transformer 架构、注意力机制、Encoder-Decoder 和“手把手搭建 Transformer”，并显示 `[S1]`、PDF 第 2 页定位；
- 负责人判断此前失败属于问题表达导致的模型限制，明确接受该剩余风险并确认 Step 6 通过；
- Step 7 仍需单独授权，不因 Step 6 通过而自动开始。

## 保留边界

- 不自动修复 Gradio 上传进度 404；
- 不修改 Embedding、Qdrant collection、SQLite schema 或真实数据；
- 不添加 TerminalTool、多 Agent、Neo4j、认证、多租户或公网部署；
- Step 6 仅执行已批准的全量门禁和只读真实验收；未获批准前不进入 Step 7，不提交、不推送、不创建 PR、不合并、不部署。

## Step 7 本地收口结果

- 完整差异相对 `main/origin/main` 的共同基线 `b584d90` 审查；当前 26 个变更文件全部位于任务卡批准清单，未修改解析、分块、摄取、Qdrant collection、SQLite schema、部署或 CI；
- 任务卡定向矩阵 106 项通过；全量 pytest 140 项通过；冻结上下文评测 10/10 通过，确认不调用外部服务、不写评测结果；
- `compileall` 通过；43 份 Markdown、76 个本地相对链接无失效；高置信敏感信息、冲突标记和替换字符扫描均为 0；
- Qdrant health 200，v4/v3 collection 分别为 300/262 points；SQLite integrity `ok`；前端 `127.0.0.1:7860` 返回 200；
- 本地完整差异审查未发现阻塞提交的代码、测试、数据安全或规格问题；窄表格关系/指代问法的安全拒答是负责人已接受的剩余质量风险；
- 已按意图创建核心能力提交 `7caf787`、冻结评测提交 `05ffb30` 和初始文档收口提交 `f53050c`。根 `README.md` 不在任务卡批准文件范围内，保持最后已合并 `main` 的交付状态描述；
- 功能分支已推送，Draft [PR #2](https://github.com/wcnm8888/agent3-document-learning-assistant/pull/2) 已创建且合并状态为 `CLEAN`。Step 7 保持 `ready_for_review`；当前未合并、未部署，下一动作是审查 PR，合并仍需负责人另行授权。
