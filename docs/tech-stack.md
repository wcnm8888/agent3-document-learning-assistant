# 技术栈与依赖策略

> 本文件同时保留原单 PDF 项目的技术基线和交付阶段记录；其中 Phase 7/8 部分属于历史基线。当前多文档任务的执行状态以 `docs/project-management/current-task.md`、`roadmap.md` 和 `implementation-plan.md` 为准。

## 已确认

- Python：项目要求 Python 3.10+；本次使用本机 Python 3.11.0rc2 虚拟环境 `E:\Agent\docqa-venv311` 验证。
- 运行包：`hello-agents==0.2.0`，其 `DashScopeEmbedding` 支持显式传入模型名，但默认仍为 v3。
- PDF：`pypdf>=5,<6`，保留页级来源。
- Qdrant：`qdrant-client>=1.12,<2`，支持本地持久化和 URL 远程服务。
- 测试：`pytest>=8,<9`。
- UI：第一阶段 Gradio。
- LLM：DeepSeek OpenAI 兼容 API，默认模型 `deepseek-v4-flash`；模型通过 `DEEPSEEK_MODEL` 配置。文档问答默认通过 `DEEPSEEK_THINKING=disabled` 关闭思考模式，避免有限 `max_tokens` 被 `reasoning_content` 耗尽。
- Embedding：当前显式使用百炼 `text-embedding-v4`，1024 维；v3 仅作为后续对照评测，不做隐式回退。
- 向量存储：Qdrant，本地 Docker 优先。
- 结构化存储：SQLite。
- 图存储：Neo4j 第二阶段按实际价值启用。
- UI：Gradio `5.50.0`，启动入口为 `python -m doc_qa.ui`，页面事件通过 `UIController` 调用业务服务。
- 网络环境兼容：`socksio>=1,<2` 用于当前 Python 环境中的 Gradio/httpx 导入兼容；DeepSeek 默认仍由 `DEEPSEEK_TRUST_ENV=false` 控制是否继承系统代理。

## 依赖风险

上游仓库根目录是教程和示例集合，不是单独可安装的运行时包。第八章文档要求安装外部 `hello-agents` 包，并提示 0.2.0 与 0.2.9 的兼容性问题。安装前必须核对实际 PyPI 版本、示例 API 和 Python 版本。

## 配置原则

真实密钥只放本地 `.env`，仓库只保留 `.env.example`。Qdrant collection 名称必须包含模型和维度版本，避免不同模型向量混用。

- 当前默认 collection 格式：`docqa_text-embedding-v4_dim1024`。
- Embedding 默认批大小为 10，符合 `text-embedding-v4` 单次请求上限；对临时 429/5xx/网络错误执行有限重试。
- 查询检索：`qdrant-client==1.18.0` 使用 `query_points`，默认 Top-K 为 5，普通问题分数阈值为 0.45；许可证/授权/版权类问题使用受限术语扩展、0.25 局部阈值和文档关键词重排，不改变普通问题阈值。
- 学习闭环：标准库 `sqlite3`，默认数据库 `data/docqa.sqlite3`；启用外键、WAL、事务和按会话/时间/事件类型索引。
- 记忆边界：默认最近 6 轮、最多 4000 字符；会话历史不替代 Qdrant 文档证据。

## Phase 7 交付边界（历史基线）

- 推荐运行方式：本地 Python/Gradio 应用 + Docker Qdrant；暂不容器化应用。
- 默认监听：`127.0.0.1:7860`；公网部署前必须补齐认证、限流和独立健康端点。
- 持久化：SQLite 单实例文件、Qdrant 独立 collection/卷、`data/reference/` 和 `eval/` 分开备份。
- 密钥：本地使用未提交 `.env`，测试使用 CI Secret 或 fake provider，生产使用 Secret Manager；任何环境都不得把密钥写入日志、结果或文档。
## 原单 PDF 项目 Phase 6 评测工具（历史基线）

- 评测运行时：现有 `E:\Agent\docqa-venv311` Python 3.11 环境。
- v3/v4：均为 1024 维，使用独立 Qdrant collection。
- 评测问答：真实 DeepSeek `deepseek-v4-flash`；结果记录 API 失败和重试次数，不记录密钥。
- 成本：Embedding 按普通文本输入价格估算；DeepSeek 按实际 usage 和 cache-miss 保守价格估算，详见评测报告。
