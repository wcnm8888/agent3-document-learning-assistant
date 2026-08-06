# 当前进度

## 当前状态

- 当前活动任务：`CTX-001 在 Agent3 中复现上下文工程核心知识`；
- 状态：`in_progress`；
- 当前 Step：`Step 7 文档与 Git 收口（ready_for_review：本地提交完成，等待推送授权）`；
- 当前分支：`feat/ctx-001-context-engineering`；
- 任务卡已于 2026-08-06 获负责人批准；
- 方案 A2、自动门禁和真实 UAT 已获负责人复核；负责人接受窄表格关系问法的剩余模型限制并确认 Step 6 通过，现已批准进入 Step 7，未部署。

## 最近完成

- DOC-001 已完成、归档并通过 PR #1 合并；
- CTX-001 任务卡、Step 0 基线契约和 Step 1 模型/配置均已获负责人确认；
- 已实现无 I/O 的 ContextBuilder 与 Gather、Select、Structure、Compress 纯流水线；
- Evidence 与 history/note 事实权限隔离、固定六分区、双预算、稳定降级和 fail-closed 已通过测试；
- 上下文定向测试 15 项、全量测试 110 项通过；`compileall`、`git diff --check` 和纯模块边界检查通过；
- 未接入 QA/SQLite/Qdrant/LLM，未修改 schema、collection、向量或真实数据；
- Step 2 已停止在 `ready_for_review`，等待负责人复核。
- 负责人已复核 Step 2 并批准进入 Step 3。
- 已实现 SQLite 历史/笔记只读候选和 session/document scope 隔离；最终严格预算由 Builder 收口；
- 历史候选不携带旧 citations，LearningService 返回不可变候选集合且不调用 QA/Builder/LLM；
- Step 3 定向测试 12 项、联合定向测试 27 项、全量测试 115 项通过；
- 无 schema/write SQL 差异，未改写真实数据；Step 3 已停止在 `ready_for_review`。
- 负责人已复核 Step 3 并批准进入 Step 4。
- 已将直接 QA、session QA、UI/CLI 现有构造链路接入唯一 ContextBuilder Prompt 入口；
- 已冻结 Evidence 引用白名单、history/notes non-evidence、UI 显式 history 优先和无结果短路；
- QA/Learning/Builder/UI 定向测试 77 项、全量测试 119 项通过；
- Step 4 已停止在 `ready_for_review`，未修改 schema、collection、向量或真实数据。
- 负责人已复核 Step 4 并批准进入 Step 5。
- 已冻结十类上下文评测用例；只读离线评测 10/10 自动结构门禁通过且结果可重放；
- history/note 冲突、注入与跨文档候选未获得事实或引用资格；无结果与双预算契约通过；
- 联合定向测试 88 项、全量测试 127 项通过；真实模型语义 UAT 保持 `pending`；
- Step 5 已停止在 `ready_for_review`，未访问或修改真实外部数据、schema、collection 或向量。
- 负责人已复核 Step 5 并批准进入 Step 6。
- Step 6 定向矩阵 93 项、全量测试 127 项、冻结评测 10/10 和静态门禁通过；
- 真实 PDF/Markdown 原文 + 生产 Builder/QA + 真实模型的降级 UAT 覆盖七类语义/安全场景；
- SQLite 验收前后 schema、表计数、主库/WAL 大小和散列完全一致，未发生写入；
- 在线 PDF/Markdown、恶意笔记、范围切换、no_results、超预算和 points 前后校验通过；
- 多轮题已命中含答案的 Evidence 且 history 已入 Prompt，但真实模型连续三次拒答；两次最小 Prompt 澄清未改善。
- 方案 A 已新增确定性、受预算且无额外模型调用的显式指代解析：最近历史提示同时补全检索查询与 Task，并保持 non-evidence；
- 方案 A 后全量 pytest 134 项、指代/Builder/QA 定向 41 项、冻结评测 10/10、compileall 和 diff 门禁通过；
- 在线复验确认指代解析已启用、提示 54 字符、Qdrant 返回 5 个命中且第 2 页为首个 Evidence，但 DeepSeek 仍回答证据不足；Qdrant 两个 collection point 数和 SQLite 文件/表计数前后不变。
- 方案 A2 已把同一问题改写为明确的 Happy-LLM 第二章独立问题，同时用于检索与 Task；拒答时 citations 归零；
- A2 定向测试 47 项、全量 pytest 140 项、冻结评测 10/10 和静态门禁通过；
- 同一在线 UAT 仍被 DeepSeek 拒答，但不再附加误导引用；Qdrant/SQLite 前后完全不变。
- Step 6 根因调查确认 S1 同时包含页面概览的 LLaMA2 实践和内容导航表格的第二章 Transformer 实践；页级文本 chunk 丢失两个版面区域及表格行关系；
- Unicode 规范化、仅保留 S1、Task 局部范围约束和 S1 目标行聚焦均不能让生产 Prompt 正确作答；简化安全策略后模型会回答，但选择错误的 LLaMA2 条目；
- 当前失败已分类为 PDF 版面/分块粒度代码缺口与已批准事实安全规格的边界冲突，不是测试运行、环境、Qdrant/SQLite 可用性或权限故障。
- 负责人通过前端再次复验：普通 RAG 问题可回答并显示 `[S1] [S3] [S5]`，但 Happy-LLM 第二章目标独立问题连续两次拒答，后续指代问题也拒答；拒答均无引用，安全修正有效但真实语义 UAT 仍失败。
- 负责人改用明确问题“Happy-LLM 第二章讲了什么内容”后，系统正确回答 Transformer 架构、注意力机制、Encoder-Decoder 和“手把手搭建 Transformer”，并引用 `[S1]`、PDF 第 2 页；负责人据此接受原窄问法限制并确认 Step 6 通过。
- Step 7 已完成本地差异审查和文档收口：26 个变更文件全部在批准范围，定向 106 项、全量 140 项、冻结评测 10/10、compileall、文档链接和敏感信息门禁通过；运行态 Qdrant、SQLite 与 UI 健康；
- 已按意图创建核心能力提交 `7caf787` 和冻结评测提交 `05ffb30`；文档状态由当前 `docs(context)` 提交收口；

## 当前事实摘要

- 产品核心能力和 UI 高保真恢复已完成；
- Embedding：`text-embedding-v4` / 1024 维；
- collection：`docqa_text-embedding-v4_dim1024`；
- 当前本地单用户；
- GitHub Actions / CI 未配置；
- Gradio `upload_progress?upload_id=undefined` 404 仍是独立非阻塞风险；
- 认证、多租户、Neo4j、公网部署和真实生产故障演练未执行。

## 剩余风险

窄表格关系问法和部分指代问法仍可能安全拒答；负责人已接受该限制，不再阻塞 Step 6。若未来要求消除限制，需另行批准表格/版面感知解析与重建向量，或修改严格 Prompt/模型规格。既有 PDF 33-point 一致性差异继续只记录、不修改。

## 下一批准动作

等待负责人另行授权推送；PR、合并和部署仍未授权，不新建下一任务。

## 历史入口

- [DOC-001 归档](../archive/task-cards/doc-001-document-governance.md)；
- [全部历史归档](../archive/README.md)；
- [当前证据](evidence.md)。
