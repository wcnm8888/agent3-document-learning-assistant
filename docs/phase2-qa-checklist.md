# Phase 2 QA 清单

> 本清单是原单 PDF Phase 2 的历史 QA 基线。当前多文档任务的 Phase 2 已完成，状态以 `docs/project-management/current-task.md`、`roadmap.md`、`progress.md` 和 `evidence.md` 为准。

## 范围

只验收：单 PDF → 解析 → 分块 → Embedding 适配 → Qdrant 索引 → 索引状态。

## 已验证

- [x] 文件不存在
- [x] 损坏 PDF
- [x] 无可提取文本 PDF
- [x] 空分块过滤
- [x] 真实基准 PDF 页级解析
- [x] 分块数量与 Qdrant point 数量一致
- [x] 重复索引不增加 point 数量
- [x] Embedding 失败不被吞掉
- [x] Qdrant 不可用错误可定位
- [x] collection 向量维度不匹配时拒绝写入
- [x] 分块来源元数据完整

## 后续评测（不属于本清单收口）

- [x] 真实百炼 v4 API 调用和 1024 维返回
- [x] Docker Qdrant 服务模式
- [ ] v3/v4 召回质量、速度和成本对比

## 收口证据

- 真实模型：`text-embedding-v4`
- 向量维度：1024
- PDF：171 页，262 个非空分块
- Qdrant collection：`docqa_text-embedding-v4_dim1024`
- 首次索引：262 个 points
- 重复索引：仍为 262 个 points，幂等通过
- 测试：`pytest tests -q` → 12 passed

## 复现

```powershell
$env:PYTHONPATH='E:\Agent\开发实践\Agent3-智能文档问答助手\src'
E:\Agent\docqa-venv311\Scripts\python.exe -m pytest E:\Agent\开发实践\Agent3-智能文档问答助手\tests -q
E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.cli index E:\Agent\开发实践\Agent3-智能文档问答助手\data\reference\Happy-LLM-0727.pdf
```

真实命令需要先在本地 `.env` 配置 `EMBED_API_KEY`，不得把密钥写入仓库或命令历史。
