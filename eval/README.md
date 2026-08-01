# 评测集说明

`questions.jsonl` 是第一版人工评测集，基于 `Happy-LLM-0727.pdf` 的目录和正文主题编写。它用于比较基础检索、v3/v4 Embedding、MQE/HyDE 和来源引用质量。

第一阶段不把自动评分结果直接等同于产品完成。每次评测需要同时保存检索命中、引用位置、回答和人工判定。
## Phase 6 v3/v4 对比

使用以下入口复现实验：

```powershell
$env:PYTHONPATH="E:\Agent\开发实践\Agent3-智能文档问答助手\src"
E:\Agent\docqa-venv311\Scripts\python.exe eval\run_embedding_comparison.py
```

脚本使用同一份 `questions.jsonl`，v3 写入独立的 `docqa_text-embedding-v3_dim1024_eval`，不会覆盖 v4 collection。结果输出到 `eval/results/`。自动评分只用于初筛；每题结果包含来源、回答、耗时和失败原因，最终仍需人工复核。

