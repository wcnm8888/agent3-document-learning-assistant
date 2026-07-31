# 初版架构

```text
Gradio UI
  -> Application Services
     -> Document Ingestion Service
        -> MarkItDown / parser -> chunker -> Embedding -> Qdrant
     -> Q&A Service
        -> query embedding -> Qdrant -> context/citations -> DeepSeek
     -> Learning Service
        -> MemoryTool / SQLite -> notes, events, statistics
```

## 模块边界

- UI 只负责输入、展示和状态，不直接依赖 Qdrant、Neo4j 或底层 Tool。
- 文档摄入服务负责解析、分块、哈希、幂等和索引状态。
- 问答服务负责检索、来源、提示词和回答结构。
- 学习服务负责会话、事件、笔记和报告。
- Qdrant 保存文档片段向量和元数据。
- SQLite 保存文档、会话、问题、笔记和索引任务状态。
- Neo4j 暂不进入第一版核心路径。

## 关键数据隔离

至少使用 `user_id`、`knowledge_base_id`、`document_id`、`chunk_id` 和 `embedding_profile` 进行隔离和追踪。

## 重要决策

Embedding 不能混用。v3 与 v4 必须分别使用不同 collection 或完成明确迁移。回答必须保留引用所需的文档名、页码、章节和 chunk 元数据。

