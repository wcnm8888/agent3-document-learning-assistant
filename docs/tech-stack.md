# 技术栈与依赖策略

## 已确认

- Python：以外部 `hello-agents` 包和实际依赖要求为准。
- UI：第一阶段 Gradio。
- LLM：DeepSeek API。
- Embedding：优先评估百炼 `text-embedding-v4`，1024 维；v3 作为兼容回退。
- 向量存储：Qdrant，本地 Docker 优先。
- 结构化存储：SQLite。
- 图存储：Neo4j 第二阶段按实际价值启用。

## 依赖风险

上游仓库根目录是教程和示例集合，不是单独可安装的运行时包。第八章文档要求安装外部 `hello-agents` 包，并提示 0.2.0 与 0.2.9 的兼容性问题。安装前必须核对实际 PyPI 版本、示例 API 和 Python 版本。

## 配置原则

真实密钥只放本地 `.env`，仓库只保留 `.env.example`。Qdrant collection 名称必须包含模型和维度版本，避免不同模型向量混用。

