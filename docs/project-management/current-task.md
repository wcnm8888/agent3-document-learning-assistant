# 当前任务

## 当前状态

- 任务：`CTX-001 在 Agent3 中复现上下文工程核心知识`；
- 状态：`in_progress`；
- 当前 Step：`Step 7 文档与 Git 收口（ready_for_review：本地提交完成，等待推送授权）`；
- 当前分支：`feat/ctx-001-context-engineering`；
- 任务卡：[CTX-001](task-card-context-engineering.md)；
- 批准证据：负责人于 2026-08-06 依次确认任务卡和 Step 0～6，并批准进入 Step 7；
- 当前授权：Step 7 本地差异审查、全量门禁、权威文档收口和按意图创建本地提交已完成；推送、PR、合并仍须分别授权，不部署。

## Step 0 结果

1. 项目 `.venv` 下现有全量 pytest 95 项通过；
2. 已冻结现有问答、引用、`no_results`、范围过滤和 UI scope 行为；
3. 已冻结 ContextConfig 精确默认值与 Prompt 六分区契约；
4. 已新增 8 个失败先行测试，全部因尚未实现 ContextPacket/ContextConfig 而预期 RED；
5. 当前共收集 103 项测试；`compileall` 和 `git diff --check` 通过；
6. 未修改 `src/doc_qa/`、schema、collection 或真实数据。

## Step 0 冻结契约

- 总输入：18000 估算 Token / 20000 字符双上限；
- Evidence：12000 字符；history：6 轮/4000 字符；notes：3 条/2000 字符；
- 固定六分区：Policies、Task、Evidence、Conversation、Notes、Output；
- 本轮 Qdrant Evidence 是唯一文档事实依据；history/note 永久为 non-evidence；
- 超限必须确定性压缩或显式失败，不允许调用 LLM 发送超限 Prompt。

## Step 1 结果

1. 已在 `models.py` 建立不可变 `ContextPacket` 和 `ContextBuildResult`；
2. 已提供无外部依赖、确定性的中英文 Token 估算函数；
3. 事实权限只由 Packet kind 派生，只有 `rag_evidence` 具备 evidence eligibility；
4. 已在 `config.py` 建立不可变 `ContextConfig`，并通过 `Settings.context_config` 映射既有 Evidence/history 配置；
5. 已校验预算、权重、数量、截断标记、最小证据空间和 RAG 必需 metadata；
6. Step 1 模型/配置定向测试 5 项通过；原有 95 项回归通过；
7. 上下文测试共 11 项，剩余 6 项只因 `context_builder` 尚不存在而预期 RED；
8. 当前测试收集 106 项；`compileall` 和 `git diff --check` 通过。

## Step 2 目标

1. 新增纯 `ContextBuilder` 和 `ContextBuildError`；
2. Gather 将政策、任务、本轮 citations、历史、笔记和输出契约规范化为 Packet；
3. Select 完成范围、重复、相关性、新近性、稳定顺序和分区预算选择；
4. Structure 输出固定六分区；
5. Compress 确定性处理 Token/字符双预算，保留 Evidence 来源头；
6. 返回可比较的选择、丢弃、预算和压缩诊断；
7. 不访问网络、SQLite、Qdrant 或 LLM。

## Step 2 文件范围

- 允许新增：`src/doc_qa/context_builder.py`；
- 允许修改：`tests/test_context_builder.py` 和当前任务状态/证据文档；
- 如纯流水线测试证明模型字段不足，可最小修改 `models.py`/`config.py`，必须记录理由；
- 明确不修改：`qa.py`、`learning.py`、`memory_store.py`、`qdrant_index.py`、UI/CLI、schema、collection 和真实数据。

## Step 2 结果

1. 已新增纯 `ContextBuilder` 和 `ContextBuildError`，未访问网络、SQLite、Qdrant client 或 LLM；
2. Gather 已将政策、任务、本轮 citations、历史、笔记和输出契约规范化为 Packet；
3. Select 已实现 scope、去重、相关性/新近性、稳定顺序、数量限制和分区预算；
4. Structure 已生成固定六分区，并明确标记 Evidence 与 non-evidence；
5. Compress 已按冻结顺序确定性降级，保留 Evidence citation/locator 和截断标记，无法满足最小契约时 fail-closed；
6. `ContextBuildResult` 可观察选择、丢弃原因、分区预算和压缩事件，默认不记录正文；
7. 上下文定向测试 15 项、全量测试 110 项通过；`compileall`、`git diff --check` 和纯模块边界检查通过；
8. 未修改 QA/Learning/Memory/Qdrant/UI/CLI、schema、collection、向量或真实数据。

## 当前产品基线

- PDF / Markdown、Qdrant RAG、SQLite 会话/笔记、引用和 UI 已完成；
- 原有全量 pytest 已在 Step 1 最终代码状态下重新执行，95 项通过；
- Evidence 上限 12000 字符；history 默认 6 轮/4000 字符；
- 无检索结果时不调用 LLM；
- 已有尚未接入问答链路的纯 ContextBuilder；
- CI 未配置，未部署。

## Step 4 目标与范围

1. 直接 QA 和 session QA 使用同一个 ContextBuilder 生成最终 system/user Prompt；
2. LearningService 提供 SQLite history/notes 候选，UI 显式短期 history 继续优先；
3. 文档事实与最终 citations 只来自实际进入 Evidence 的本轮 Qdrant citations；
4. 保持 `document_id` 检索过滤、`no_results` 不调用 LLM、PDF/Markdown locator 和现有错误传播；
5. 保持现有 UI scope 切换后清空短期 history 的语义；
6. 不修改 Qdrant、SQLite schema/迁移、真实数据或部署配置。

## Step 4 结果

1. 直接 QA、session QA、UI/CLI 现有构造链路统一使用 ContextBuilder 的最终 system/user Prompt；
2. 已删除 QA 中两套旧字符串拼装，生产代码只保留一个 `context_builder.build` 和一个 `chat.generate` 入口；
3. LearningService 注入 SQLite history/notes；UI 显式空 history 继续优先，文档范围切换不会重新注入旧历史；
4. 无 Qdrant 命中时即使存在 history/notes 仍返回 `no_results`，不构建 Prompt、不调用 LLM；
5. 最终 citations 只来自 `included_citation_ids` 白名单，模型伪造或被预算丢弃的来源 ID 不能进入响应；
6. `last_context_build` 暴露最近成功构建的可比较诊断；
7. QA/Learning/Builder/UI 定向测试 77 项、全量测试 119 项通过，原有 115 项无回归；
8. `compileall`、`git diff --check`、唯一入口、敏感信息和范围检查通过；
9. 未修改 Qdrant collection/检索契约、SQLite schema/迁移、Embedding/摄取、向量或真实数据。

## Step 5 目标与范围

1. 冻结十类上下文评测情景，覆盖事实、范围、多轮、冲突、预算、注入和无结果边界；
2. 提供不访问网络、Qdrant、SQLite 或 LLM 的只读评测入口；
3. 自动检查 Evidence 来源纯度、引用白名单、固定分区、双预算、稳定压缩和 `no_results`；
4. 评测输出只暴露来源 ID 与诊断，不复制完整 Prompt、证据、历史或笔记正文；
5. 明确保留真实回答正确性和注入抵抗为人工验收，不用自动指标替代 Step 6/UAT；
6. 不修改 schema、collection、向量、真实数据或部署配置。

## Step 5 结果

1. 已冻结十类上下文工程场景，并提供默认只读、无外部服务访问的结构评测入口；
2. 10/10 自动结构门禁通过且重复运行一致，报告不包含完整 Prompt 或候选正文；
3. history/note 冲突、提示注入和跨文档候选均未进入事实/引用白名单；
4. 无检索用例保持 `no_results` 且未调用 Builder；超预算用例稳定压缩后满足字符/Token 上限；
5. 上下文、评测、QA、Learning、UI 联合定向测试 88 项，全量测试 127 项通过，原有 119 项无回归；
6. `compileall`、diff、敏感信息、外部调用和范围检查通过；未修改真实数据或外部存储；
7. 真实回答语义、冲突裁决和模型级提示注入抵抗仍为人工 `pending`，留待 Step 6/UAT。

## Step 6 目标与范围

1. 重新执行冻结评测、定向矩阵、全量测试和所有本地静态门禁；
2. 使用现有已索引 PDF/Markdown 与生产问答链路完成任务卡规定的六类真实问答；
3. history/notes 通过内存候选注入，不创建真实 session/note，不写真实 SQLite；
4. 验收前后核对 collection、文档目录、SQLite 和受保护路径未变化；
5. 将自动结构结论与真实模型人工语义判定合并到可复核 UAT 记录；
6. 不摄取、删除、重建或迁移任何真实外部数据。

## Step 6 已完成部分

1. 定向矩阵 93 项、全量测试 127 项、冻结评测 10/10 和全部静态门禁通过；
2. SQLite 验收前后 schema、表计数、主库/WAL 大小与散列完全一致，`total_changes=0`；
3. 真实 PDF/Markdown 原文、生产 Builder/QA 与真实模型的降级 UAT 已覆盖事实、locator、多轮、恶意笔记、scope、no_results 和超预算；
4. Evidence 引用白名单、其他文档丢弃、无结果不调用模型和稳定压缩在降级 UAT 中成立；
5. 首轮 PowerShell stdin 中文编码失真造成两次假失败，统一 UTF-8 后消除；多轮问题需避免无法消解的过度含糊指代；
6. 未写入 SQLite、Qdrant、`eval/results/` 或工作区外数据。

## Step 6 阻塞

- 配置指向 `localhost:6333`，healthz 返回 502，v4/v3 collection 均不可读；
- Docker daemon 不可连接，本机未找到 Docker Desktop；本地文件式 Qdrant 没有 collection；
- 因此无法执行真实在线 Qdrant 检索，也无法核对验收前后 point 数；降级 UAT 不能替代该门禁；
- 解除条件是恢复包含既有 `docqa_text-embedding-v4_dim1024` points 的服务，不能重新摄取或重建 collection。

上述运行环境阻塞已由负责人启动 Docker Desktop解除，后续在线验收结果见下方。

## Step 6 恢复基线

- 负责人已启动 Docker Desktop，`localhost:6333` healthz 和 collection 读取恢复正常；
- v4 collection：1024 维、300 points；当前 Markdown 5 points、PDF 295 points；
- v3 eval collection：1024 维、262 points；
- SQLite 记录 Markdown 5 chunks、PDF 262 chunks；PDF 存在既有 33-point 差异，本任务不修改或清理；
- 以上数值冻结为在线 UAT 前基线，验收后必须保持完全一致。

## Step 6 在线 UAT 结果

1. PDF 授权事实、Markdown locator、恶意笔记隔离、文档范围切换、no_results 和超预算场景通过；
2. PDF→Markdown 切换后的 citations 只来自当前 `document_id`；恶意 note 的 `[S9]` 未获得引用资格；
3. no_results 检索为 0 且未调用模型；超预算结果满足 1700 字符/1100 Token 上限并产生可解释压缩事件；
4. Qdrant 前后均为总计 300、PDF 295、Markdown 5 points；SQLite 和受保护路径未变化；
5. 多轮指代题的检索结果包含第 2 页，history Packet 已进入 Conversation，但真实模型连续三次返回“根据当前文档片段不足以回答”；
6. 已两次最小澄清指代消解政策，并补自动化断言；34 项 Builder/QA 定向测试、全量 127 项和冻结评测 10/10 通过，但真实模型行为未改善；
7. 已达到“同一根因连续 3 次修复/验证失败”停止条件，不再扩大实现范围。

## 历史决策阻塞（方案 A 批准前）

- 选项 A：重新批准查询改写/显式指代解析设计，作为 CTX-001 范围扩展；
- 选项 B：接受当前模型对模糊多轮问题的限制，并由负责人调整真实 UAT 验收口径；
- 当时授权不足以自行选择任一方向，Step 6 保持 `blocked`；该阻塞随后由负责人批准方案 A 解除。

负责人已选择方案 A，以上决策阻塞解除。批准范围仅包括确定性、受预算、无额外模型调用的指代解析与检索/Task 补全；history 继续为 non-evidence。

## 方案 A 实现与复验结果

1. 已新增纯 `ReferenceResolver`：只在问题包含显式指代且存在有效历史时启用，选择最近一轮并生成最多 600 字符的 non-evidence 提示；
2. 同一提示用于单次检索查询和 Task 指代补全；没有 MQE、HyDE、多查询、额外 LLM 或 Agent；
3. `ContextBuildResult` 已提供解析启用状态、来源轮次和提示字符数诊断；固定六分区、Evidence 唯一事实来源、引用白名单和 no_results 短路不变；
4. 指代/Builder/QA 定向 41 项、全量 pytest 134 项、冻结评测 10/10、compileall 和 diff 门禁通过；
5. 在线复验确认解析启用、提示 54 字符、Qdrant 返回 5 个命中且第 2 页排首位，但 DeepSeek 仍回答“根据当前文档片段不足以回答”；
6. Qdrant v4/v3 point 数和 SQLite 文件散列、表计数前后完全不变。

## 历史阻塞（方案 A 后）

方案 A 没有满足多轮真实语义验收。继续引入更强查询改写、额外模型步骤、回答后处理，或调整真实 UAT 口径，都会改变当前批准范围；Step 6 因此保持 `blocked`，等待负责人重新决策。

负责人已批准方案 A2，以上决策阻塞解除。批准范围只包括：可靠对象的确定性独立问题改写、独立问题同时用于检索与 Task、明确拒答时 citations 为空，以及对应测试和同一只读在线 UAT；仍不允许额外模型调用、多查询或修改真实数据。

## 方案 A2 实现与复验结果

1. 章节指代可从最近有效历史中确定性提取，并把当前问题改写为独立问题；无法可靠提取的普通代词不会被猜测；
2. 在线示例的独立问题为“Happy-LLM 第二章的内容导航还列出了什么动手实践？”，同时用于 Embedding 检索与 Task；
3. 明确拒答时 citations 强制为空，即使模型错误返回 source ID，也不会附加引用或空的“参考来源”；
4. A2 定向测试 47 项、全量 pytest 140 项、冻结评测 10/10、compileall 和 diff 门禁通过；
5. 同一在线 UAT 检索 5 条 Evidence，上下文 6534 字符/3969 估算 Token且未超限，但 DeepSeek 仍返回“根据当前文档片段不足以回答”；最终 citations 正确为空；
6. Qdrant v4/v3 collection 保持 300/262 points；SQLite 文件指纹、表计数和 `total_changes=0` 前后不变。

## 历史阻塞（方案 A2 后）

方案 A2 没有满足真实多轮回答验收。继续改变检索候选、模型策略、Prompt 或验收口径会超出当前批准范围；Step 6 保持 `blocked`，等待负责人重新决策。

## Step 6 根因调查结论

1. 真实 S1 为 PDF 第 2 页、893 字符、score 0.817578，完整进入 Evidence 且没有压缩；预期答案所在行确实存在；
2. 源 PDF 同页顶部概览包含“动手实现一个完整的 LLaMA2 模型”，内容导航表格的第二章行包含“手把手搭建 Transformer”；当前 PDF 文本抽取/页级 chunk 把二者放进同一 Evidence，未保存“表格行属于第二章”的结构化关系；
3. 三轮根因验证排除 Unicode 兼容字符、Top-K 噪声和预算：规范化字符仍拒答；只保留 S1、2178 字符仍拒答；移除 CTX-001 严格多分区规则后模型不再拒答，但错误选择同页概览的 LLaMA2 条目；
4. PDF 第 2 页视觉核验确认概览和内容导航表格是两个不同版面区域，证明错误来自页内局部范围/表格关系丢失，而不是源文档缺少答案；
5. 两个当前范围内最小修复实验均失败：增加“内容导航 × 第二章”Task 范围约束仍拒答；把 S1 聚焦为标准化的第二章目标行后，生产 Prompt 仍拒答；
6. 代码根因位于 PDF 版面到 Evidence 的粒度契约，而非 ContextBuilder 预算、Qdrant 可用性或 SQLite；现有自动测试只验证结构、权限和假模型接线，没有覆盖“同一 chunk 内竞争事实 + 真实模型语义选择”。

## 负责人手工 UAT 复验

1. 普通问题“如何搭建RAG”能够回答并显示 `[S1] [S3] [S5]`，证明前端、问答调用和引用展示主链路正常；
2. 目标独立问题“Happy-LLM 第二章的内容导航中，‘手把手搭建’的对象是什么？”于 18:59、19:04 两次均返回“根据当前文档片段不足以回答”，且没有引用；
3. 后续指代问题“这一章的内容导航还列出了什么动手实践？”同样拒答且没有引用；
4. 负责人随后将问题改为“Happy-LLM 第二章讲了什么内容”，系统正确回答第二章包含 Transformer 架构、注意力机制、Encoder-Decoder 和“手把手搭建 Transformer”，并显示 `[S1]`、PDF 第 2 页定位；
5. 负责人判断此前失败属于问题表达过窄造成的模型理解限制，明确接受该限制并确认 Step 6 通过。拒答零引用继续作为安全降级行为保留。

## 已接受的剩余风险

对于要求解析同页表格局部关系的窄问法，当前模型仍可能拒答。负责人已选择接受该限制并调整 Step 6 人工验收口径，因此它不再阻塞 CTX-001；若以后要求消除该限制，持久修复仍至少需要以下任一项并另行批准：

- PDF 表格/版面感知解析与行级分块，并重建当前 PDF 向量；这会触碰解析/分块架构和现有 Qdrant points；
- 调整严格 Prompt/事实充分性规格，接受模型在歧义 Evidence 上进行推断；这会改变已批准的安全契约；
- 更换或增加模型步骤处理表格关系；这会改变外部依赖、成本和调用架构。

此前调查曾依据任务卡停止条件 2、10、11、12 停止扩展修复；负责人现已接受剩余限制并确认 Step 6 通过。未写业务修复、未修改测试、未进入 Step 7。

## Step 3 目标与范围

1. `SQLiteMemoryStore` 提供当前 session 的只读历史和笔记候选；
2. 历史候选遵守轮数窗口和稳定顺序并至少保留最新一轮，最终严格预算由 Builder 收口；
3. 笔记候选遵守 session、document scope、数量、字符预算和稳定顺序；
4. `LearningService` 只负责取得候选，不拼 Prompt、不调用 Builder；
5. 不修改 schema/迁移，不访问或改写真实 SQLite 数据；
6. 不让 history/note 获得 Evidence 或引用资格。

## Step 3 结果

1. 新增不可变 `ConversationContextCandidate`，只包含当前会话问答文本和定位字段，不携带旧 citations；
2. 新增历史候选只读查询，按 session 隔离、最近轮数筛选并按时间正序返回；至少保留最新一轮，最终严格预算由 Builder 收口；
3. 新增笔记候选只读查询，按 session、document scope、更新时间、数量和严格字符预算筛选；
4. 指定 document scope 时只允许无文档关联或同文档笔记，其他文档笔记被排除；
5. `LearningService.get_context_candidates` 返回不可变 history/notes 元组，不调用 QA、Builder 或 LLM；
6. Step 3 定向测试 12 项、上下文联合定向测试 27 项、全量测试 115 项通过；
7. `compileall`、`git diff --check`、无 schema/write SQL 差异和敏感信息检查通过；
8. 未修改 SQLite schema/迁移、真实数据、QA、ContextBuilder、Qdrant、UI/CLI 或 LLM 链路。

## 停止条件

- 需要让 ContextBuilder 直接访问 SQLite、Qdrant、网络或 LLM；
- 需要修改批准范围外业务代码、schema、collection 或真实数据；
- history/note 必须获得 evidence eligibility 才能通过测试；
- 六分区、稳定排序或双预算无法同时满足；
- 原有 95 项测试回归；
- Step 6 完成后未获负责人确认进入 Step 7。

## 下一批准动作

等待负责人另行授权推送；PR、合并和部署仍未授权。

## Step 7 本地收口结果

1. 基线为 `main/origin/main=b584d90`；分支 `feat/ctx-001-context-engineering` 当前 26 个变更文件全部位于批准清单；
2. 完整差异审查未发现阻塞提交的代码、测试、数据安全或规格问题；没有新增 schema/write SQL、collection、解析/分块、命令执行或外部依赖变更；
3. 任务卡定向矩阵 106 项、全量 pytest 140 项、冻结评测 10/10 和 compileall 通过；
4. 43 份 Markdown、76 个本地相对链接全部有效；高置信敏感信息、冲突标记和替换字符均为 0；
5. Qdrant health 200、v4/v3 为 300/262 points，SQLite integrity `ok`，前端返回 HTTP 200；
6. 根 `README.md` 不在批准文件范围内，保持最后已合并 `main` 的交付状态描述；当前分支事实以 `docs/README.md` 和本文件为准；
7. 已创建核心能力提交 `7caf787` 和冻结评测提交 `05ffb30`，本节文档收口由当前 `docs(context)` 提交记录；未推送、未创建 PR、未合并、未部署，Step 7 停在 `ready_for_review`。
