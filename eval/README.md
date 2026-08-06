# 评测集说明

`questions.jsonl` 是第一版人工评测集，基于 `Happy-LLM-0727.pdf` 的目录和正文主题编写。它用于比较基础检索、v3/v4 Embedding、MQE/HyDE 和来源引用质量。

第一阶段不把自动评分结果直接等同于产品完成。每次评测需要同时保存检索命中、引用位置、回答和人工判定。

## CTX-001：离线上下文结构评测

`context-engineering-cases.jsonl` 冻结十类上下文与安全情景：单文档事实、Markdown 定位、多轮指代、历史与 RAG 冲突、笔记与 RAG 冲突、只有笔记但无检索、双文档范围隔离、长上下文超限、三类候选中的提示注入和无检索结果。

评测入口默认只读，只调用纯 `ContextBuilder`，不连接 Qdrant、SQLite、网络或 LLM，也不写入 `eval/results/`：

```powershell
.\.venv\Scripts\python.exe eval\run_context_evaluation.py
```

每例输出检索来源元数据、实际进入 Evidence 的 citation ID、最终引用白名单、分区字符/Token 估算、丢弃原因、压缩事件、事实来源自动判定和人工复核状态。输出不包含完整 Prompt、证据、历史、笔记或生成答案正文。

自动通过只说明上下文结构、预算和权限边界满足冻结契约。真实回答是否正确、冲突时是否遵循 Evidence、恶意文本是否影响模型输出，必须由隔离真实问答与人工 rubric 复核；评测器输出的 `human_review.verdict=pending` 是结构报告的固定诚实口径，不因 Step 6 已完成人工 UAT 而伪装成自动判定。

## Phase 6 v3/v4 对比

使用以下入口复现实验：

```powershell
$env:PYTHONPATH="E:\Agent\开发实践\Agent3-智能文档问答助手\src"
E:\Agent\docqa-venv311\Scripts\python.exe eval\run_embedding_comparison.py
```

脚本使用同一份 `questions.jsonl`，v3 写入独立的 `docqa_text-embedding-v3_dim1024_eval`，不会覆盖 v4 collection。结果输出到 `eval/results/`。自动评分只用于初筛；每题结果包含来源、回答、耗时和失败原因，最终仍需人工复核。
