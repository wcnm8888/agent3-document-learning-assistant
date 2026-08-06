# 当前技术栈

本文件只描述当前实现，不记录阶段演进。依赖范围以 `pyproject.toml` 和锁文件为准。

## 运行时与应用层

| 类别 | 当前选择 | 用途 |
|---|---|---|
| 语言 | Python `>=3.10` | 全部应用、CLI、数据与测试代码 |
| UI | Gradio `>=5,<6` | 本地知识工作台和交互回调 |
| Agent 基础 | `hello-agents==0.2.0` | 项目学习与 Agent 相关依赖 |
| LLM SDK | OpenAI Python `>=1,<2` | 调用 OpenAI 兼容接口 |
| HTTP | `httpx>=0.27,<1`、`socksio>=1,<2` | 外部服务请求与代理支持 |
| PDF | `pypdf>=5,<6` | PDF 文本和页码提取 |
| 环境变量 | `python-dotenv>=1,<2` | 本地配置加载 |

## 检索与存储

| 类别 | 当前选择 | 关键配置 |
|---|---|---|
| Embedding | `text-embedding-v4` | 1024 维 |
| 向量数据库 | Qdrant / `qdrant-client>=1.12,<2` | 默认本地 `data/qdrant`，也支持 URL |
| 当前 collection | `docqa_text-embedding-v4_dim1024` | 按模型和维度隔离 |
| 业务数据库 | SQLite | 默认 `data/docqa.sqlite3` |
| 回答模型 | DeepSeek 兼容接口 | 默认 `deepseek-v4-flash`，thinking disabled |

## 默认运行参数

| 参数 | 默认值 |
|---|---:|
| 分块大小 | 1200 字符 |
| 分块重叠 | 160 字符 |
| 检索 Top K | 5 |
| 相似度阈值 | 0.45 |
| 检索上下文上限 | 12000 字符 |
| 会话短期上下文 | 最近 6 轮 |
| 会话上下文上限 | 4000 字符 |
| Qdrant 超时 | 10 秒 |

运行值可以由 `.env` 覆盖；不得在文档、日志或提交中明文保存密钥。

## 开发与质量工具

| 工具 | 用途 |
|---|---|
| pytest | 单元、集成、UI 契约和安全夹具测试 |
| `compileall` | Python 语法和可编译性检查 |
| `git diff --check` | 空白与补丁格式门禁 |
| setuptools | `src` 布局打包，包含 `ui.css` |
| Docker Compose | 可选的本地 Qdrant 运行方式 |
| Playwright / 浏览器夹具 | UI 三视口和状态验收；不是运行时依赖 |

仓库当前没有 GitHub Actions 或其他 CI 配置。测试通过指本地已记录结果，不等于 CI 通过。

## UI 样式权威

- `src/doc_qa/ui.py`：Gradio 结构、组件、状态和回调；
- `src/doc_qa/ui.css`：唯一运行时样式权威；
- `docs/assets/ui-visual-baseline/`：冻结的视觉基准资产。

不得重新在 `ui.py` 中叠加多代大段 CSS，也不得以静态伪数据替代真实业务回调。

## 明确未采用

- Neo4j 或知识图谱；
- React / Vue 等独立前端运行时；
- PostgreSQL、Redis 或对象存储；
- 认证、用户系统、多租户；
- 公网生产部署、多实例和容器编排；
- Secret Manager、限流和生产可观测平台。

## 配置债务

`pyproject.toml` 的项目 description 仍为早期 Phase 2 文案，与当前产品范围不一致。DOC-001 只治理文档，不在本步骤修改项目配置；后续如处理，应建立独立、小范围工程任务。
