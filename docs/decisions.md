# 关键决策

## D-001：Embedding 默认候选为 v4

新项目优先评估 `text-embedding-v4`，固定 1024 维作为第一轮对比基线。`text-embedding-v3` 只作为兼容回退或对照实验。最终选择必须由真实评测集决定。

## D-002：开发阶段本地数据库

Qdrant 使用本地 Docker，SQLite 使用本地文件。Neo4j 暂不进入第一版核心路径。这样可以降低网络、费用和数据隔离风险。

## D-003：不把教程示例直接当生产架构

第八章示例集中在一个 `PDFLearningAssistant` 类和 Gradio 回调中。本项目通过应用服务层隔离 UI、RAG、Memory 和存储，以便测试和后续替换 UI。

## D-004：源码获取方式

项目应用目录与上游源码目录分离：应用目录为 `E:\Agent\开发实践\Agent3-智能文档问答助手`，上游参考源码为 `E:\Agent\hello-agents-upstream`。应用目录建立独立的本地 Git 历史，不修改上游仓库。
