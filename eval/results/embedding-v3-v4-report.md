# Embedding v3/v4 Phase 6 对比评测报告

- 评测时间：`2026-07-31T16:05:59.997807+00:00`
- 测试文档：`Happy-LLM-0727.pdf`
- 页数/分块：`171` / `262`
- 评测问题：`30` 条
- 自动评分仅用于可复现初筛，最终质量仍需人工复核。

## 模型与集合

| 模型 | 维度 | Collection | Recall/检索命中率 | 来源准确率（自动） | 回答正确率（自动） | 拒答准确率（自动） | 平均耗时 |
|---|---:|---|---:|---:|---:|---:|---:|
| text-embedding-v3 | 1024 | `docqa_text-embedding-v3_dim1024_eval` | 100.0% | 83.3% | 53.3% | 77.8% | 3487 ms |
| text-embedding-v4 | 1024 | `docqa_text-embedding-v4_dim1024` | 96.7% | 86.7% | 60.0% | 100.0% | 3503 ms |

## 调用、失败与成本

成本是估算值：Embedding 按普通文本输入价格 0.0005 元/千 token；DeepSeek 使用记录到的 usage，按 cache miss 输入 1 元/百万 token、输出 2 元/百万 token 的保守假设计算。

| 模型 | Embedding API 调用/重试 | DeepSeek API 调用/重试 | 失败题数 | Embedding 估算成本 | DeepSeek 估算成本 |
|---|---:|---:|---:|---:|---:|
| text-embedding-v3 | 30/0 | 30/0 | 0 | ¥0.000283 | ¥0.108647 |
| text-embedding-v4 | 30/0 | 30/0 | 0 | ¥0.000283 | ¥0.103457 |

## 自动评分说明

- `retrieval_hit`：Top-K 是否返回来源；
- `source_accuracy`：依据评测集页码提示与返回页码交集；没有页码提示时只检查是否有来源；
- `answer_point_coverage`：期望答案要点的简单文本命中率；
- 文档外/无答案/拒答题要求出现明确拒答表达；返回的检索片段仍需人工核对是否相关；
- 这些规则不能替代人工判断，尤其不能单独证明回答事实正确。

## Collection 隔离证据

- 评测前 v4：`{'collection': 'docqa_text-embedding-v4_dim1024', 'dimension': 1024, 'points_count': 262, 'metadata_complete': True}`
- 评测后 v4：`{'collection': 'docqa_text-embedding-v4_dim1024', 'dimension': 1024, 'points_count': 262, 'metadata_complete': True}`
- v3：`{'collection': 'docqa_text-embedding-v3_dim1024_eval', 'dimension': 1024, 'points_count': 262, 'metadata_complete': True}`
- v3 与 v4 使用独立 collection，未混用向量。

## 人工复核结论

- q016–q017 已通过定向真实验证：均回答 CC BY-NC-SA 4.0 许可证边界，引用第 4 页和同一 `source_locator`。
- q023–q028 已按严格文档范围判定：当前 Happy-LLM PDF 未覆盖项目级路由、评测、来源校验、Embedding 对比、多文档切换和解析异常规范，拒答正确。
- q017 的“内部评测材料保留来源”已从 PDF 事实评分中移除，作为独立项目合规规则管理。
- v3 q014 保留为已解释的对照模型幻觉案例；v4 文档外/无答案拒答通过。
- 项目负责人已确认评测边界、v4 默认模型和 Phase 6 收口。
