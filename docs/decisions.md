# 关键决策

## D-001：Embedding 默认候选为 v4

新项目优先评估 `text-embedding-v4`，固定 1024 维作为第一轮对比基线。`text-embedding-v3` 只作为兼容回退或对照实验。最终选择必须由真实评测集决定。

## D-002：开发阶段本地数据库

Qdrant 使用本地 Docker，SQLite 使用本地文件。Neo4j 暂不进入第一版核心路径。这样可以降低网络、费用和数据隔离风险。

## D-003：不把教程示例直接当生产架构

第八章示例集中在一个 `PDFLearningAssistant` 类和 Gradio 回调中。本项目通过应用服务层隔离 UI、RAG、Memory 和存储，以便测试和后续替换 UI。

## D-004：源码获取方式

项目应用目录与上游源码目录分离：应用目录为 `E:\Agent\开发实践\Agent3-智能文档问答助手`，上游参考源码为 `E:\Agent\hello-agents-upstream`。应用目录建立独立的本地 Git 历史，不修改上游仓库。

## Phase 2 决策

1. 复用 `hello-agents==0.2.0` 的 Embedding 适配器，但不使用其默认 v3；项目显式传入 `text-embedding-v4`，并校验真实返回维度必须为 1024。无凭据时失败，不隐式回退 v3 或本地模型。
2. 直接使用 pypdf 做页级 PDF 解析。第八章的 MarkItDown/RAGTool 作为参考实现，后续可替换解析器，但本阶段优先保证页码和错误可定位。
3. Qdrant 优先支持 Docker URL，同时支持 `qdrant-client` 本地持久化模式。Docker 守护进程未运行时，本地模式用于开发验证；生产/团队环境仍应使用明确的 Qdrant 服务。
4. point ID 使用由 `chunk_id` 派生的稳定 UUID，重复索引通过 upsert 保持幂等；模型或维度变化必须换 collection。
5. Embedding 适配层固定单批最多 10 条文本，保留 HTTP 状态码和服务端错误码；仅对 429、5xx 和网络类临时错误重试，避免把参数或权限错误隐藏为重复请求。

## Phase 4 决策

1. 会话、问答来源快照、笔记、学习事件和统计统一落在本地 SQLite；Qdrant 只负责向量和文档分块检索，Neo4j 不进入本阶段。
2. 会话记忆按 `session_id` 隔离，并限制最近轮次和上下文字符数；历史只用于指代消解，不能替代 Qdrant 文档片段作为事实依据。
3. 学习统计和报告使用确定性的 SQL 查询，不调用 LLM 生成统计事实；事件使用实体唯一键和幂等插入，避免重复操作污染统计。

## Phase 5 决策

1. Gradio 仅作为适配层：页面不直接操作 Qdrant、SQLite 或第三方 API，所有业务调用统一经过 `UIController` 和已有应用服务。
2. 文档目录元数据新增 SQLite `documents` 表；页面显示索引状态、页数、分块数和 points，但不复制 Qdrant 向量数据。
3. Gradio 服务采用懒加载 Embedding、Qdrant 和 DeepSeek 客户端：只打开 UI 不触发外部 API，上传或提问时才建立连接，降低空页面启动失败概率。
4. 响应式布局使用 CSS 断点 `1100px` 和 `760px`；移动端采用纵向折叠顺序，来源面板放到问答和笔记之后。
5. 真实浏览器验证保留截图和操作证据；Playwright 记录的 `upload_progress?upload_id=undefined` 404 不影响上传和索引结果，后续升级 Gradio 时需复核。
## D-006：Phase 6 暂保持 v4 为默认模型

最新 30 题对比中，v4 平均响应时间约 3503ms，答案自动正确率 60.0%，拒答自动准确率 100%；v3 约 3487ms、53.3%、77.8%。v3 的检索命中率略高，但 v4 在答案和拒答指标上更适合作为默认模型。故当前默认仍为 v4，并保留 v3 评测 collection 供复核。

q023–q028 已确认采用严格文档范围，当前 PDF 未覆盖项目级工程规范时应拒答。q016–q017 因 PDF 第 4 页明确给出 CC BY-NC-SA 4.0，采用许可证术语扩展和局部低阈值检索，并通过关键词重排确保第 4 页进入引用候选。

该决策已通过 Phase 6 项目负责人确认，但不等同于部署或发布授权。若更换模型，必须新建 collection 或执行可审计迁移。

## D-008：Phase 7 采用本地优先交付方案

当前版本推荐 Python 应用运行在本机、Qdrant 运行在 Docker，SQLite 作为单实例本地持久化。暂不添加完整应用容器或公网部署，原因是认证、限流、Secret Manager、独立健康端点和多实例存储尚未具备。该决定不改变 `text-embedding-v4`、1024 维或现有 collection。

## D-009：运行数据与密钥分离

SQLite、Qdrant 存储、授权文档和评测结果使用独立目录和备份策略；真实 `.env` 不进入 Git、日志或评测结果。生产密钥必须由外部 Secret Manager 注入，应用日志只记录脱敏状态和指标。

## D-007：许可证事实题使用受限查询扩展

许可证、授权、许可协议和版权类问题使用独立的许可证术语查询扩展，并将局部检索阈值降至 0.25，再按实际文档内容中的许可证术语命中数重排。普通问题不改变原有检索阈值；回答仍只能依据 Qdrant 返回的真实分块，不能把扩展词当作答案来源。

## D-010：多文档使用内容哈希作为文档身份

`document_id` 和 `content_hash` 均使用原始文件字节的 SHA-256。文件名只作为展示字段，不参与唯一身份。同一内容重复上传返回 duplicate 操作结果，不增加 Qdrant points；同名不同内容生成不同 document_id 并允许并存。该方案兼容本地单用户场景，也避免路径和文件名变化导致重复索引。

## D-011：PDF 与 Markdown 使用统一模型、格式感知来源

统一解析协议采用 `DocumentSource`、`DocumentUnit` 和 `DocumentChunk` 三层结构。PDF 保留页码和原有 locator；Markdown 使用章节路径、段落序号和起止行号，页码字段为空。HTML、脚本和文档内指令只作为不可信文档数据，不执行、不提升为系统指令。

## D-012：多文档共用 v4 collection

所有 PDF/Markdown 继续写入 `docqa_text-embedding-v4_dim1024`，通过 `document_id` 和 `embedding_profile=text-embedding-v4:1024` 隔离。不得为每个文档创建 collection，也不得写入 v3、本地模型或其他维度向量。

## D-013：切换文档范围时重置当前问答上下文

切换指定文档、全部文档或其他知识库范围时，UI 清空当前回答、来源、待保存笔记和会话上下文，避免历史回答跨文档进入 Prompt；既有会话、问答和笔记仍保留在 SQLite。该行为将在 Phase 4 UI/学习服务实现并测试。

## D-014：Phase 1 只设计 SQLite 迁移，不执行 Schema 变更

现有 `documents` 表采用 additive migration 方向，补充格式、内容哈希、Embedding profile、locator scheme、来源单元数和 created_at 等字段，并通过备份、回填、完整性检查和既有引用回归保证兼容。Phase 1 不修改真实数据库，Phase 2 才能在临时数据库中实现和验证迁移。
