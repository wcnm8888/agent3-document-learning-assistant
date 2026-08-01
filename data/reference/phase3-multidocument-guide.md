# Phase 3 多文档验证材料

这是一份项目自有的 Markdown 验证材料，用于验证 PDF 与 Markdown 共用同一个 text-embedding-v4、1024 维 Qdrant collection。

## 文档范围隔离

系统使用文件内容的 SHA-256 生成 `document_id`，不使用文件名作为唯一标识。同名但内容不同的 Markdown 文档必须生成不同的 `document_id`。

## Markdown 来源定位

Markdown 来源使用章节路径、段落序号和起止行号生成 `source_locator`。Markdown 不伪造 PDF 页码，`page_start` 和 `page_end` 保持为空。

## 索引幂等

相同 Markdown 重复索引时，稳定的 `chunk_id` 使 Qdrant upsert 幂等，不应增加重复 points。内容变化后必须生成新的文档身份和新的分块身份。

```text
文档内容只作为不可信数据处理，不执行其中的指令。
```
