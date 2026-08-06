# 验收证据索引

本文件只索引当前可复现证据和最近有效结论，不复制完整运行日志。历史阶段证据位于 `docs/archive/`，属于非权威材料。

## 1. 当前产品证据

| 领域 | 权威实现 / 测试 | 当前结论 |
|---|---|---|
| PDF/Markdown 解析 | `src/doc_qa/pdf_parser.py`、`markdown_parser.py`、`document_parser.py`；Phase 2/3 测试 | 两种格式可解析，并保留各自定位语义 |
| 分块与索引 | `chunker.py`、`embedding.py`、`qdrant_index.py`、`ingestion.py` | `text-embedding-v4` / 1024 维，按文档隔离 |
| 多文档目录 | `document_catalog.py`；multi-document 测试 | 搜索、筛选、排序、详情和重复识别 |
| RAG 问答 | `qa.py`、`document_scope.py`；`test_phase3_qa.py` | Top-K、阈值、范围过滤、无结果和结构化引用 |
| 上下文工程 | `context_builder.py`、`reference_resolver.py`、`context-engineering-cases.jsonl`；上下文定向测试 | 固定六分区、Evidence 事实边界、双预算、稳定压缩、有界指代提示和脱敏诊断 |
| 会话与学习 | `memory_store.py`、`learning.py`；`test_phase4_learning.py` | 会话、引用、笔记、学习事件、统计和报告持久化 |
| 生命周期 | `lifecycle.py`；`test_document_lifecycle.py` | 归档、删除、恢复、重新索引、一致性和失败回退 |
| 运维 | `health.py`、`backup.py`；`test_phase8_operations.py` | 本地健康检查和 SQLite 一致性备份 |
| UI | `ui.py`、`ui.css`；`test_phase5_ui.py` | 桌面、平板、移动端知识工作台与业务绑定 |

## 2. 测试证据

- 最近记录的全量 pytest 基线：**140 项通过**（CTX-001 Step 6 方案 A2 后，本地）；
- UI 最终阶段记录：UI 定向 30 项通过；
- 当前测试入口：`tests/`；
- 当前测试策略：[testing-strategy.md](../testing-strategy.md)；
- 领域矩阵：[multi-document-test-matrix.md](../multi-document-test-matrix.md)、[document-lifecycle-test-matrix.md](../document-lifecycle-test-matrix.md)。

重要口径：DOC-001 Step 3～5 是纯文档治理，当时只重新确认测试收集数量；Step 6 在提交前使用项目 `.venv` 重新运行全量 pytest，95 项通过。仓库没有 CI，因此该结果只能表述为本地验证通过，不能表述为 CI 通过。

## 3. 视觉证据

冻结基准：

- `docs/assets/ui-visual-baseline/figma-desktop-session-1440x900.png`；
- `docs/assets/ui-visual-baseline/figma-desktop-library-1440x900.png`；
- `docs/assets/ui-visual-baseline/figma-mobile-context-390x844.png`。

最终 UI 恢复由负责人完成人工视觉批准。可复现浏览器契约见 [设计规格](../design-spec.md) 和 [测试策略](../testing-strategy.md)。本地 `output/` 中可能保留浏览器截图，但它不是当前权威文档，也不应全部提交。

## 4. 数据安全证据

- 生命周期测试使用临时 SQLite / Qdrant 或测试替身；
- 真实 Qdrant points 未用于删除测试；
- SQLite 删除保留 tombstone、历史引用和笔记；
- Qdrant 删除条件为精确 `document_id`；
- PDF 页码和 Markdown 章节/段落/行号在代码和测试中分别保护；
- 文档范围、会话和笔记隔离有自动化覆盖。

## 5. Git 与交付证据

当前已知提交链：

| Commit | 说明 |
|---|---|
| `b121f09` | 初始化智能文档问答项目 |
| `f3c5403` | 交付本地文档 QA 工作流 |
| `be419eb` | 建立 UI 视觉恢复基线 |
| `c9f1a64` | 完成高保真知识工作台实现 |
| `7cd53e9` | 收口 UI 视觉恢复文档 |
| `7e32b11` | 记录私有仓库发布状态 |

DOC-001 开始时：

- `main`、`origin/main` 和 HEAD 同步于 `7e32b11`；
- 从该基线创建 `chore/agent3-document-governance`；
- Step 2～5 尚未提交、推送或创建 PR；
- 当时未部署。

DOC-001 Step 6 交付状态：

- 提交：`f87286a`（当前权威文档）、`dc2b000`（历史归档）、`c378839`（治理记录）、`5b73d42`（Step 6 交付证据）；
- 远端分支：`origin/chore/agent3-document-governance`；
- 远端仓库经 GitHub CLI 核验为私有；
- [PR #1](https://github.com/wcnm8888/agent3-document-learning-assistant/pull/1) 已完成审查并合并到 `main`；
- 状态检查列表为空，仓库当前未配置 CI；
- 本地 `main` 已同步；未部署。

## 6. CTX-001 证据

### Step 0：基线与契约冻结

- 分支：`feat/ctx-001-context-engineering`；
- 现有全量基线：`.venv\Scripts\python.exe -m pytest -q`，95 项全部通过；
- 测试收集基线：原有 95 项；新增 `tests/test_context_builder.py` 后共 103 项；
- 失败先行测试：8 项预期失败；首项缺少 `ContextPacket`，其余缺少 `ContextConfig`，符合尚未进入 Step 1 的 RED 状态；
- 测试文件已通过 Python 编译，RED 不是语法、夹具或测试环境错误；
- `python -m compileall -q src tests`：通过；
- `git diff --check`：通过；
- 默认预算：完整输入 18000 估算 Token / 20000 字符；Evidence 12000 字符；history 6 轮/4000 字符；notes 3 条/2000 字符；
- Prompt 固定六分区：Policies、Task、Evidence、Conversation、Notes、Output；
- 事实权限：只有实际进入 Prompt 的本轮 Qdrant Evidence 可进入引用白名单；history/note 永久为 non-evidence；
- 未修改 `src/doc_qa/`、SQLite schema、Qdrant collection/points 或真实数据；
- 默认系统 Python 没有安装 pytest，实际门禁使用项目 `.venv`；
- CI 未配置，因此只能表述为本地基线通过和本地 RED 契约成立。

### Step 0 复现命令

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m py_compile tests\test_context_builder.py
.\.venv\Scripts\python.exe -m pytest tests\test_context_builder.py -q --tb=short
.\.venv\Scripts\python.exe -m compileall -q src tests
git diff --check
```

### Step 1：上下文模型与配置

- 新增实现：`src/doc_qa/models.py` 中的 `estimate_tokens`、`ContextPacket`、`ContextBuildResult`；
- 新增配置：`src/doc_qa/config.py` 中的 `ContextConfig` 和 `Settings.context_config`；只映射现有 Evidence/history 配置，不新增未文档化环境变量；
- Step 1 定向测试：5 项通过；
- 原有回归：排除新增 context 文件后，既有 95 项全部通过；
- 当前测试收集：106 项；
- 当前 context 契约：11 项中 5 项通过，6 项仅因 `doc_qa.context_builder` 尚不存在而预期 RED；
- `python -m compileall -q src tests`：通过；
- `git diff --check`：通过；
- 已确认 `src/doc_qa/qa.py`、`learning.py`、`memory_store.py`、`qdrant_index.py`、UI/CLI、schema、collection 和真实数据均未修改；
- CI 未配置，结论仅为本地验证。

### Step 1 复现命令

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_context_builder.py -q -k "context_packet or context_config or context_build_result or settings_context_config"
.\.venv\Scripts\python.exe -m pytest tests\test_context_builder.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest -q --ignore=tests\test_context_builder.py
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m compileall -q src tests
git diff --check
```

### Step 2：GSSC 纯流水线

- 新增 `src/doc_qa/context_builder.py`，实现无 I/O 的 Gather、Select、Structure、Compress；
- Gather 将政策、当前任务、本轮 Citation、会话历史、笔记和输出契约规范化为不可变 Packet；
- Select 覆盖 document scope、去重、最低相关性、相关性/新近性稳定排序、数量与分区预算；
- Structure 固定输出 Policies、Task、Evidence、Conversation、Notes、Output 六分区，history/note 保持 non-evidence；
- Compress 按 Conversation → Notes → 低排名 Evidence → 最终 Evidence 截断的稳定顺序降级，保留 citation/locator/截断标记，无法满足最小契约时 fail-closed；
- 构建结果提供选择、丢弃原因、分区字符/Token、压缩事件和引用白名单，不默认记录正文；
- 上下文定向测试：15 项全部通过；
- 全量测试：110 项全部通过，其中原有 95 项无回归；
- 测试收集：110 项；`python -m compileall -q src tests`、`git diff --check` 通过；
- 纯模块边界扫描未发现 SQLite、Qdrant client、HTTP 或 LLM 调用；
- 未修改 `qa.py`、`learning.py`、`memory_store.py`、`qdrant_index.py`、UI/CLI、schema、collection、向量或真实数据；
- CI 未配置，结论仅为本地验证；现有 Qdrant、Pydantic 和 Gradio 警告未新增失败。

### Step 2 复现命令

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_context_builder.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m compileall -q src tests
rg -n "sqlite|qdrant_client|requests|httpx|ChatProvider|\.generate\(" src/doc_qa/context_builder.py
git diff --check
```

### Step 3：SQLite 历史与笔记候选

- 新增不可变 `ConversationContextCandidate`，只保留历史理解所需字段，不携带旧 citations；
- 新增 `SQLiteMemoryStore.context_history_candidates`：当前 session 隔离、最近轮数、稳定时间正序，并兼容至少保留最新一轮；最终严格预算由 Builder 收口；
- 新增 `SQLiteMemoryStore.context_note_candidates`：当前 session、document scope、更新时间、数量和严格字符预算；
- 指定 document scope 时允许无文档关联或同文档笔记，排除其他文档关联笔记；
- 新增不可变 `ContextCandidates` 与 `LearningService.get_context_candidates`，只读取候选，不调用 QA、Builder、Qdrant 或 LLM；
- Step 3 定向测试：`tests/test_phase4_learning.py` 12 项通过；
- 上下文联合定向测试：27 项通过；
- 全量测试：115 项通过，其中 Step 3 前既有 110 项无回归；
- 测试收集：115 项；`python -m compileall -q src tests`、`git diff --check` 通过；
- 隔离 SQLite 夹具确认候选读取前后 schema、持久数据和 `total_changes` 不变；
- 差异扫描无新增 schema/write SQL，无高置信敏感信息命中；
- 未修改真实 SQLite 数据、schema/迁移、QA、ContextBuilder、Qdrant、UI/CLI、collection 或向量；
- CI 未配置，结论仅为本地验证；现有依赖警告未新增失败。

### Step 3 复现命令

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_phase4_learning.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest tests\test_phase4_learning.py tests\test_context_builder.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m compileall -q src tests
git diff -U0 -- src/doc_qa/memory_store.py
git diff --check
```

### Step 4：现有问答链路接入

- `QuestionAnswerService` 默认构造唯一 ContextBuilder，并允许测试注入自定义预算；
- 已移除 `_build_context` 和 `_build_conversation_context`，生产代码只有 `context_builder.build` → `chat.generate` 一条最终 Prompt 路径；
- 直接 QA、session QA、UI/CLI 的现有服务构造均进入该统一路径；无需修改产品 UI/CLI 代码；
- LearningService 在未显式提供 history 时使用 SQLite history/notes；UI 显式空 history 继续优先，保持文档范围切换清空语义；
- 固定 Policies、Task、Evidence、Conversation、Notes、Output 六分区进入真实 chat 调用；
- history/notes 中伪造的 source ID 不具备事实或引用资格；
- 最终 citations 以 `ContextBuildResult.included_citation_ids` 为白名单，模型伪造或被预算丢弃的 ID 不能进入响应；
- 无 Qdrant 命中时即使存在 history/notes，仍在 Builder/LLM 前返回 `no_results`；
- Builder 预算失败不调用 chat provider；最近成功构建结果可从 `last_context_build` 观察；
- QA/Learning/Builder/UI 定向测试：77 项通过；
- 全量测试：119 项通过，其中 Step 4 前既有 115 项无回归；
- 测试收集：119 项；`python -m compileall -q src tests`、`git diff --check` 通过；
- 唯一 Prompt 入口、无 schema/write SQL、敏感信息和修改范围检查通过；
- 未修改 Qdrant collection/检索契约、SQLite schema/迁移、Embedding/摄取、向量或真实数据；
- CI 未配置，结论仅为本地验证；现有依赖警告未新增失败。

### Step 4 复现命令

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_phase3_qa.py tests\test_phase4_learning.py tests\test_context_builder.py tests\test_phase5_ui.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m compileall -q src tests
rg -n "_build_context|_build_conversation_context|context_builder\.build|chat\.generate|included_citation_ids" src/doc_qa/qa.py src/doc_qa/learning.py
git diff --check
```

### Step 5：上下文评测与安全回归

- 新增 `eval/context-engineering-cases.jsonl`，冻结十类场景：单文档事实、Markdown locator、多轮指代、history/RAG 冲突、note/RAG 冲突、仅笔记无检索、document scope、超预算、提示注入和 no_results；
- 新增 `eval/run_context_evaluation.py`，默认只读冻结 JSONL，仅调用纯 ContextBuilder；未访问 Qdrant、SQLite、网络或 LLM，未写 `eval/results/`；
- 每例输出检索来源元数据、实际 Evidence/最终引用 ID、分区字符与 Token、丢弃/截断事件、事实来源自动判定和人工复核状态，不包含完整 Prompt 或候选正文；
- 离线评测 10/10 自动结构门禁通过，重复运行结果一致；2 个无检索用例均未调用 Builder，超预算用例产生 5 个稳定压缩事件并满足双预算；
- history/note 冲突、提示注入和跨文档来源均未获得 Evidence 或 citation 资格；最终引用均受实际 Evidence 白名单约束；
- 上下文、评测、QA、Learning、UI 联合定向测试 88 项通过；
- 全量测试 127 项通过，其中 Step 5 前既有 119 项无回归；测试收集 127 项；
- `python -m compileall -q src tests eval`、`git diff --check` 通过；
- 未修改 schema、collection、向量、真实 SQLite/Qdrant 数据或历史 `eval/results/`；未提交、推送、创建 PR、合并或部署；
- 自动通过只代表结构/权限/预算契约；10 例真实回答语义、冲突裁决和模型级提示注入抵抗保持 `pending`，留待 Step 6 的隔离 UAT，未伪装为安全验收完成；
- CI 未配置；现有 Qdrant、Pydantic、Gradio 警告未新增失败。

### Step 5 复现命令

```powershell
.\.venv\Scripts\python.exe eval\run_context_evaluation.py
.\.venv\Scripts\python.exe -m pytest tests\test_context_evaluation.py tests\test_phase6_eval_helpers.py tests\test_context_builder.py tests\test_phase3_qa.py tests\test_phase4_learning.py tests\test_phase5_ui.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m compileall -q src tests eval
git diff --check
```

### Step 6：全量门禁与真实验收（已获负责人确认）

- 任务卡定向矩阵：93 项通过，覆盖 Builder、上下文评测、QA、Learning、多文档、PDF/Markdown locator、UI 和既有评测辅助逻辑；
- 全量 pytest：127 项通过；测试收集 127 项；冻结上下文结构评测 10/10 通过；
- `python -m compileall -q src tests eval`、`git diff --check`、修改范围、高置信敏感信息、schema/write SQL、受保护路径和 Markdown 链接检查通过；
- 真实 SQLite 只读基线前后完全一致：schema version 26，`documents=2`、`sessions=91`、`conversation_turns=8`、`citations=14`、`notes=3`、`learning_events=113`、`document_operations=0`；主库/WAL 大小与 SHA-256 均一致，连接 `total_changes=0`；
- SQLite 登记两个 `indexed` 文档：`Happy-LLM-0727.pdf`（262 chunks）和 `phase3-multidocument-guide.md`（5 chunks）；源文件存在；
- 使用上述真实源文件、生产 ContextBuilder/QA 引用白名单和真实 DeepSeek 完成降级 UAT：PDF 单轮事实及页码、Markdown locator、多轮指代、恶意笔记 non-evidence、document scope、no_results 和超预算稳定降级均通过；
- scope 场景只保留 Markdown 的 `S2`，跨文档 PDF `rag:S1` 被丢弃；no_results 未调用模型；超预算场景产生 4 个压缩事件并丢弃超长 history；
- Markdown 初始自动判定将“**不伪造 PDF 页码**”误判为失败，人工 rubric 确认为正确否定表达；不得仅用否定词子串判定安全失败；
- 首轮 PowerShell inline Python 未显式设置 UTF-8，中文问题被改成 `?` 并连续两次产生假失败；设置 `$OutputEncoding`、`python -X utf8` 并在调用前校验输入后，PDF 事实与多轮用例通过；
- 多轮首个问法“它还包括什么实践”过度含糊而被模型拒答；改为仍依赖历史确定章节、但补充可消解限定的问法后通过。该非确定性记录为剩余质量风险，不视为事实边界失败；
- 降级 UAT 从真实源文件只读解析候选，没有执行在线 Qdrant 检索，因此不能替代任务卡 17.5 的完整验收。

初始环境阻塞证据（已解除）：

- 配置目标为本机 `localhost:6333`；两次只读 health/collection 检查均失败，healthz 返回 HTTP 502，v4/v3 collection 不可读；
- Docker daemon pipe 不存在，本机未找到 Docker Desktop；项目 `data/qdrant/meta.json` 显示本地文件式存储没有 collection；
- 无法读取在线 collection 验收前后的 point 数，也无法运行生产 `QuestionAnswerService` 的真实 Qdrant search；
- 未尝试启动摄取、重建 collection、写 points 或迁移数据；当时 Step 6 保持 `blocked`，没有把降级 UAT 伪装为完整通过。

负责人随后启动 Docker Desktop，已解除环境阻塞。恢复后只读基线为：v4 1024 维、总计 300 points，其中 PDF 295、Markdown 5；v3 eval collection 262 points。SQLite 对 PDF 记录 262 chunks，与 Qdrant 存在既有 33-point 差异，本任务未修改或清理。

在线生产链路 UAT：

- 使用真实 DashScope Embedding、Qdrant search、ContextBuilder、DeepSeek 和当前两个 `document_id`，未调用会话/笔记持久化写接口；
- PDF 授权事实正确引用第 4 页；Markdown 正确回答章节路径、段落序号和起止行号且未伪造页码；
- 恶意笔记中的 `[S9]` 未获得 citation 资格；PDF→Markdown 范围切换后 citations 只来自目标文档；
- no_results 使用严格阈值取得 0 命中且未调用模型；超预算用例最终 1540 字符/776 估算 Token，产生 3 个压缩事件并丢弃超长 history 和低排名 Evidence；
- v4 point 数在所有在线 UAT 前后保持总计 300、PDF 295、Markdown 5；SQLite schema、7 张表计数、主库/WAL 大小与散列保持不变；
- 多轮指代题失败：Qdrant 返回 5 个 PDF 命中并包含带预期答案的第 2 页，history Packet 已进入 Conversation，但真实模型回答“根据当前文档片段不足以回答”；
- 已两次最小澄清 Prompt：Conversation 可解析代词/省略/对话对象，对话对象属于用户意图且无事实/引用资格，最终文档事实仍只能来自 Evidence；34 项 Builder/QA 定向测试通过；
- 两次修正后真实模型仍拒答，同一根因累计三次验证失败，触发任务卡停止条件；未继续扩大为查询改写、单独指代解析或改变固定分区顺序；
- 修正后的全量 pytest 127 项、冻结评测 10/10、compileall 和 diff 通过；受保护数据未变化。

当前决策阻塞：负责人需选择并重新批准“查询改写/显式指代解析范围扩展”，或明确接受当前模型限制并调整多轮 UAT 口径。Step 6 未通过，不能进入 Step 7。

方案 A 已获批准、实现并完成复验：

- 新增无 I/O、无 LLM 的确定性 `ReferenceResolver`；仅对显式指代启用，选取最近有效历史，并把最多 600 字符的 non-evidence 提示用于单次检索和 Task；
- `ContextBuildResult` 增加解析启用、来源轮次和提示字符数诊断；固定六分区、Evidence 唯一事实来源、引用白名单和 no_results 短路保持不变；
- 指代/Builder/QA 定向 41 项、全量 pytest 134 项、冻结评测 10/10、compileall 与 diff 门禁通过；
- 在线复验中解析已启用，来源轮次为 `uat-reference-turn`，提示 54 字符；Qdrant 返回 5 个命中，首个 Evidence 为包含预期答案的 PDF 第 2 页；
- DeepSeek 仍返回“根据当前文档片段不足以回答”，因此方案 A 未满足真实多轮语义验收；
- v4/v3 collection 分别保持 300/262 points；SQLite 7 张业务表计数、主库/WAL/SHM 大小与 SHA-256 前后完全一致，`total_changes=0`；
- Step 6 再次标记 `blocked`。继续扩大查询改写、额外模型步骤、回答后处理或调整 UAT 口径均需负责人重新批准；Step 7 未授权。

方案 A2 随后获批、实现并完成复验：

- `ReferenceResolver` 对可靠章节对象生成确定性独立问题；同一在线示例被改写为“Happy-LLM 第二章的内容导航还列出了什么动手实践？”，并同时用于单次 Embedding 检索与 Task；
- 无法可靠提取的普通代词不生成虚假独立问题，继续使用原有有界 non-evidence 提示；
- `QuestionAnswerService` 对明确证据不足回答强制返回空 citations，即使模型错误返回 source ID，也不追加引用或空的“参考来源”；
- A2 指代/Builder/QA 定向 47 项、全量 pytest 140 项、冻结评测 10/10、compileall 与 diff 门禁通过；
- 同一在线 UAT 检索 5 条 Evidence，ContextBuilder 输出 6534 字符/3969 估算 Token、未超预算；DeepSeek 仍返回“根据当前文档片段不足以回答”，但最终 citations 已正确为空；
- v4/v3 collection 分别保持 300/262 points；SQLite 7 张业务表计数、主库/WAL/SHM 文件指纹前后完全一致，`total_changes=0`；
- 方案 A2 未满足真实多轮回答验收，Step 6 保持 `blocked`；没有进入 Step 7，也没有提交、推送、部署或修改真实数据。

Step 6 根因调查证据：

- 分类：代码层为 PDF 版面/表格关系到页级文本 chunk 的粒度缺口；测试层缺少“同一 chunk 竞争事实 + 真实模型语义”的可离线断言；环境层 Qdrant、SQLite、预算均正常；外部模型调用正常但在严格 Prompt 下拒答、在简化 Prompt 下选错；规格层存在“严格证据充分性”与“扁平歧义 Evidence 必须作答”的冲突；持久修复所需的重建向量或模型/规格变更未获权限；
- S1：PDF 第 2 页、score 0.817578、893 字符，包含 `第⼆章 Transformer 架构 注意⼒机制、Encoder-Decoder、⼿把⼿搭建 Transformer`，完整进入 Evidence、无压缩；
- 同页视觉核验：顶部产品概览写“动手实现一个完整的 LLaMA2 模型”，下方内容导航表格第二章行写“手把手搭建 Transformer”；两者属于不同版面区域，但 Qdrant S1 为同一个扁平文本块；
- 验证 1：仅对 CJK 兼容字符做内存 NFKC 规范化，预期短语变为标准汉字并进入 Prompt，模型仍明确拒答；
- 验证 2：只保留 S1，Prompt 降至 2178 字符/1252 估算 Token，模型仍明确拒答，排除 Top-K 噪声和预算；
- 验证 3：同一模型、S1 和独立问题移除 CTX-001 多分区/non-evidence 严格规则后，模型回答“动手实现一个完整的 LLaMA2 模型”并引用 S1；该答案来自同页概览而非内容导航第二章行，证明页内局部范围歧义；
- 最小修复实验：追加“内容导航 × 第二章”局部范围约束仍拒答；把 S1 聚焦为标准化目标行且保留生产 Prompt仍拒答；未将实验写入业务代码；
- 根因结论：源 PDF 有正确答案，检索/预算/Builder/服务环境均正常；当前扁平页级 Evidence 不能稳定表达问题要求的表格行关系，严格 Prompt 选择拒答，放松 Prompt 则产生错误事实关联；
- 最小持久修复范围是 PDF 表格/版面感知解析、行级分块及当前 PDF 重建向量；替代方案是修改严格事实规格或模型调用方式。两类方案均扩大当前架构、collection 或外部依赖/权限，触发任务卡停止条件；
- 本轮未新增失败测试：现有真实在线 UAT 已是可重复失败回归；在没有获批版面/索引契约前新增假模型断言不能证明真实根因，且不得把失败伪装成自动通过。

负责人手工前端复验（2026-08-06）：

- 普通问题“如何搭建RAG”能够正常生成回答并显示 `[S1] [S3] [S5]` 引用，证明前端、问答调用和引用展示主链路可用；
- 目标独立问题“Happy-LLM 第二章的内容导航中，‘手把手搭建’的对象是什么？”在 18:59 和 19:04 两次复验均返回“根据当前文档片段不足以回答”，未显示引用；
- 同会话追问“这一章的内容导航还列出了什么动手实践？”同样返回证据不足且无引用；
- 结论：拒答零引用安全修正确实生效，但独立问题与多轮指代问题的真实语义验收均未通过；该结果复现既有在线失败，不支持解除 Step 6 阻塞。
- 最终人工验收：负责人改问“Happy-LLM 第二章讲了什么内容”，系统正确回答第二章包含 Transformer 架构、注意力机制、Encoder-Decoder 和“手把手搭建 Transformer”，显示 `[S1]` 并定位 `Happy-LLM-0727.pdf` 第 2 页；
- 负责人将前述失败判定为问题表达导致的已知模型限制，明确接受该限制并确认 Step 6 通过。此前失败与根因调查记录继续保留为剩余风险证据，不改写为成功；Step 7 尚未授权。
- 调查后重新执行指代/Builder/QA 定向测试 47 项、compileall 和 diff 检查，全部通过；Qdrant v4/v3 仍为 300/262 points，SQLite 表计数与主库/WAL/SHM 指纹保持既有值，`total_changes=0`。

恢复环境后的只读复现入口：

```powershell
.\.venv\Scripts\python.exe -m doc_qa.cli health
.\.venv\Scripts\python.exe -m doc_qa.cli ask "Happy-LLM 第二章的关键内容是什么？" --document-id 1b96edb5cb7be57b14ceba1733f5f6a74c94c972769457c3f504952064034713
.\.venv\Scripts\python.exe -m pytest tests\test_context_builder.py tests\test_context_evaluation.py tests\test_phase3_qa.py tests\test_phase4_learning.py tests\test_phase3_multidocument.py tests\test_phase3_multidocument_metadata.py tests\test_phase5_ui.py tests\test_phase6_eval_helpers.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src tests eval
git diff --check
```

### Step 7：本地差异审查与文档收口

- Git 基线：`main`、`origin/main` 和功能分支 HEAD 在审查开始时均为 `b584d90`；当前分支为 `feat/ctx-001-context-engineering`；
- 变更范围：26 个文件，全部属于任务卡批准清单；禁止修改的解析、分块、摄取、Qdrant collection、SQLite schema、部署和 CI 文件无差异；`memory_store.py` 没有新增 write/schema SQL；
- 任务卡定向矩阵：106 项通过；全量 pytest：140 项通过；冻结结构评测：10/10 通过，`external_services_called=false`、`wrote_result_files=false`；
- `python -m compileall -q src tests eval` 通过；43 份 Markdown、76 个本地相对链接均有效；高置信敏感信息、冲突标记、Unicode 替换字符均为 0；`git diff --check` 通过；
- 运行态只读核验：Qdrant healthz HTTP 200，v4/v3 collection 为 300/262 points；SQLite integrity `ok`；Gradio 前端 HTTP 200；
- 本地完整差异审查未发现阻塞提交的代码、测试、数据安全或规格问题。外部独立审查与 CI 未执行：仓库未配置 CI，当前会话禁止子代理，且可选 `review` 技能缺少其强制 AskUserQuestion 工具；未将其伪装为通过；
- 根 `README.md` 不在 CTX-001 批准文件范围内，保持最后已合并 `main` 的交付状态；当前功能分支状态以 `docs/README.md`、`current-task.md` 和任务卡为准；
- 已按负责人授权精确暂存并创建核心能力提交 `7caf787`、冻结评测提交 `05ffb30`；本节文档收口由当前 `docs(context)` 提交记录。当前未推送、未创建 PR、未合并、未部署；下一步必须由负责人另行授权推送。

## 7. DOC-001 证据

### Step 0～1

- 完成 Git、产品、测试、文档体量和状态冲突审计；
- 形成并获得批准的文档权威地图、冲突清单和归档迁移矩阵；
- 确认旧 current-task、roadmap、implementation-plan、progress、evidence 和 release checklist 混入大量历史。

### Step 2

- 分支：`chore/agent3-document-governance`；
- 新增 `AGENTS.md`；
- 新增 `docs/README.md`；
- 将 DOC-001 设为唯一活动任务；
- `git diff --check`、入口链接和高置信敏感信息检查通过；
- 无产品代码、测试、配置、数据库或依赖修改。

### Step 3

已重建：

- 项目 README；
- 当前架构、技术栈、数据库设计和 UI 设计规格；
- 统一测试策略；
- 当前路线图、实施计划、进度、证据和发布清单。

最终门禁：相对链接、冲突/乱码、旧状态、敏感信息、`git diff --check` 和修改范围检查通过；pytest 无缓存收集确认 95 项。该段记录的是 Step 3 当时停止点，后续迁移见下方 Step 4。

### Step 4

- 归档入口：`docs/archive/README.md`；
- 迁移范围：2 张产品任务卡、5 份 UI 历史、1 份阶段 QA、2 份验收/清理记录；
- 所有归档文件增加非权威声明，并保留原路径映射；
- 10 组旧路径均已移除，目标文件均存在且可从 `7e32b11` 追溯；每份归档正文相对基线仅新增 1 行非权威声明；
- `docs/archive/` 仅包含批准的 10 份历史文件和 1 个归档入口；
- 35 份 Markdown 文档相对链接检查通过；旧路径、当前状态、高置信敏感信息、冲突标记、修改范围和 `git diff --check` 门禁通过；
- 当前长期规格、测试矩阵、运维文档、决策和冻结视觉资产未移动；
- 原始内容可从 Git 基线 `7e32b11` 追溯；
- 未修改产品代码、测试、配置、数据库、依赖或真实数据；
- Step 4 当时未提交、推送、创建 PR、部署或越权进入 Step 5；Step 5 后续经负责人单独授权执行。

### Step 5

- pytest 无缓存收集：95 项；未重新运行应用全量测试；
- Markdown：35 份文件、70 个相对链接全部有效；
- 当前文档引用的源码、测试、视觉基准、评测文件、Compose 和配置模板均存在；
- CLI `--help` 与 README 命令对照通过；修复 `backup-sqlite` 的错误参数写法；
- `Settings` 默认模型、维度、collection、分块、检索、会话和存储参数与文档一致；
- 运行依赖均由 `pyproject.toml` 表达，pytest 保持测试依赖；
- 扫描 93 份 Git 跟踪或待交付文本文件，高置信敏感信息无命中；`.env` 未跟踪；
- 35 份 Markdown 无冲突标记或常见乱码；
- 修复运维文档对外部 `docqa-venv311` 的硬编码依赖，以及 ADR/部署/可观测性旧阶段口吻；
- `pyproject.toml` description 与当前产品不一致，但已在 README、技术栈、路线图和发布清单登记为独立配置债务；
- `python -m compileall -q src tests` 与 `git diff --check` 通过；
- Git index 为空，33 条工作区状态均属于批准的文档治理范围；HEAD、`main`、`origin/main` 均为 `7e32b11`；
- 没有未解释状态冲突或事实漂移；未修改产品代码、测试、配置、数据库、依赖或真实数据；
- 未暂存、提交、推送、创建 PR、合并或部署。

### Step 6

- 完整差异和提交范围审查：仅包含 `README.md`、项目 `AGENTS.md` 和 `docs/`；
- 当前 Markdown 链接检查：41 份文件、70 个本地相对链接，0 个失效；
- 高置信敏感信息扫描：84 份 Git 跟踪或待交付文本文件，0 个命中；
- `.env` 未被跟踪，仅 `.env.example` 被跟踪；
- 全量 pytest：95 项通过；
- `python -m compileall -q src tests`、`git diff --check` 通过；
- 归档迁移被 Git 识别为 10 组 rename，原始内容仍可从 `7e32b11` 追溯；
- 已完成分批提交、功能分支推送和 Draft PR 创建；
- 未修改产品代码、测试、配置、数据库、依赖或真实数据；
- 未合并、未同步 `main`、未归档 DOC-001、未部署。

### Step 7

- 远端 PR 评论、Review、状态检查和基线状态完成核验，没有待处理审查意见；
- 独立 Codex 结构化审查尝试在 5 分钟内无输出并超时，未将超时伪装为通过；
- 本地完整范围审查确认 33 个变更文件全部位于 `README.md`、项目 `AGENTS.md` 和 `docs/`；
- 41 份 Markdown、70 个本地相对链接全部有效；84 份文本文件高置信敏感信息扫描无命中；
- 全量 pytest 重新执行，95 项通过；`compileall` 和 `git diff --check` 通过；
- DOC-001 最终状态和归档记录在同一 PR 中收口；
- PR #1 已审查并合并到 `main`，本地 `main` 已同步；
- DOC-001 状态为 `completed`，当前活动任务恢复为无；
- 未部署，未自动创建或执行下一任务。

## 8. 已知未关闭项

| 类型 | 项目 | 状态 |
|---|---|---|
| 技术债务 | Gradio `upload_progress?upload_id=undefined` 404 | 非阻塞，未修复 |
| 交付工程 | GitHub Actions / CI | 未配置 |
| 配置债务 | `pyproject.toml` description 仍为 Phase 2 文案 | 未处理 |
| 数据安全 | 真实生产故障和恢复演练 | 未执行 |
| 产品边界 | 认证、多租户、Neo4j、公网部署 | 未实现，属于非目标 |

## 9. 复现命令

```powershell
python -m pytest
python -m compileall -q src tests
git diff --check
python -m doc_qa.cli health
python -m doc_qa.ui
```

运行需要本地配置，但不得把 `.env`、API Key、Token 或真实连接信息复制到证据文档。
