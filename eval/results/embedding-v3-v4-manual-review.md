# Embedding v3/v4 逐题证据复核

- 评测结果主文件：`embedding-v3-v4-summary.json`
- 本文件记录人工/证据复核结论；实际问题、期望答案、完整回答、完整来源和失败原因均按 `id` 对应主文件。
- `pass`：回答和来源基本满足验收标准；`partial`：主要结论正确但覆盖不足；`fail`：出现错误事实、明显漏答或错误来源；`uncertain`：仍缺少已确认的评测边界或产品政策。
- 本轮已确认严格文档范围：q023–q028 属于当前 PDF 未覆盖的项目级规则问题，正确行为是明确拒答；q016–q017 不属于文档外问题，因为 PDF 第 4 页明确给出了 CC BY-NC-SA 4.0 许可证信息。
- `reviewer`：`agent-evidence-review`，负责整理证据；项目负责人已对评测边界、q016–q017 判定和 v4 默认模型完成确认。

## text-embedding-v3

| ID | 检索/来源 | 回答 | 幻觉 | 可读性 | 复核结论 | 复核说明 |
|---|---|---|---|---|---|---|
| q001 | pass | pass | pass | pass | pass | 覆盖 Transformer、LLaMA2、训练流程和 RAG/Agent。 |
| q002 | pass | pass | pass | pass | pass | 两部分结构回答准确。 |
| q003 | pass | pass | pass | pass | pass | NLP 第一章内容与第 2/3 页来源一致。 |
| q004 | pass | pass | pass | pass | pass | Transformer、注意力、Encoder-Decoder 和实现均覆盖。 |
| q005 | pass | pass | pass | pass | pass | 三种架构回答正确，来源片段直接支持。 |
| q006 | pass | pass | pass | pass | pass | LLM 定义、训练策略和能力均有覆盖。 |
| q007 | pass | pass | pass | pass | pass | PyTorch、LLaMA2、Tokenizer 和训练流程均覆盖。 |
| q008 | pass | pass | pass | pass | pass | LoRA/QLoRA 和高效微调内容基本准确。 |
| q009 | pass | pass | pass | pass | pass | 第 7 章、RAG、Agent 与项目相关性回答合理。 |
| q010 | pass | pass | pass | pass | pass | Python、深度学习和 NLP 基础均覆盖。 |
| q011 | pass | pass | pass | pass | pass | 章节路线顺序正确，引用第 2、3、6 页。 |
| q012 | pass | fail | pass | pass | fail | 对 Transformer 与 RAG/Agent 的关系错误地拒答，存在相关证据。 |
| q013 | pass | pass | pass | pass | pass | 推荐第 7 章并给出 RAG/Agent 依据。 |
| q014 | pass | fail | fail | pass | fail | 将代码中的 ZhipuEmbedding 当成文档明确选型，违反无答案约束。 |
| q015 | pass | pass | pass | pass | pass | 明确说明未提及 DeepSeek API Key。 |
| q016 | pass | pass | pass | pass | pass | 修复后准确回答 CC BY-NC-SA 4.0，并引用第 4 页。 |
| q017 | pass | pass | pass | pass | pass | 正确说明 CC BY-NC-SA 4.0 边界。 |
| q018 | pass | pass | pass | pass | pass | 理论与实践结合、复现代码和参与项目均覆盖。 |
| q019 | pass | pass | pass | pass | pass | 第 5～7 章的递进作用说明准确。 |
| q020 | pass | pass | pass | pass | pass | 正确拒答，不将外部数据库配置伪装成 PDF 内容。 |
| q021 | pass | pass | pass | pass | pass | 第二章及 Transformer 实践回答准确。 |
| q022 | pass | pass | pass | pass | pass | RAG 后的 Agent 回答准确。 |
| q023 | pass | pass | pass | pass | pass | 已确认严格文档范围；当前 PDF 未提供项目级文档路由验收步骤，拒答正确。 |
| q024 | pass | pass | pass | pass | pass | 已确认评测分类规范不在当前 PDF 中，拒答正确。 |
| q025 | pass | pass | pass | pass | pass | 已确认来源校验规则不在当前 PDF 中，拒答正确。 |
| q026 | pass | pass | pass | pass | pass | 已确认 v3/v4 对比指标不在当前 PDF 中，拒答正确。 |
| q027 | pass | pass | pass | pass | pass | 已确认多文档切换方案不在当前 PDF 中，拒答正确。 |
| q028 | pass | pass | pass | pass | pass | 已确认解析异常处理规范不在当前 PDF 中，拒答正确。 |
| q029 | partial | partial | pass | pass | partial | 文档含幻觉/RAG证据，但回答未完整说明来源可验证价值。 |
| q030 | pass | pass | pass | pass | pass | 学习路线总结完整，顺序和来源基本准确。 |

## text-embedding-v4

| ID | 检索/来源 | 回答 | 幻觉 | 可读性 | 复核结论 | 复核说明 |
|---|---|---|---|---|---|---|
| q001 | pass | pass | pass | pass | pass | 覆盖核心学习目标，引用第 1/2 页。 |
| q002 | partial | pass | pass | pass | pass | 两部分结构正确，页码提示与实际引用存在轻微偏差。 |
| q003 | pass | pass | pass | pass | pass | NLP 第一章内容准确。 |
| q004 | pass | pass | pass | pass | pass | Transformer 核心内容覆盖完整。 |
| q005 | pass | pass | pass | pass | pass | 三种 PLM 架构回答准确。 |
| q006 | pass | pass | pass | pass | pass | LLM 定义、能力、训练过程和涌现能力覆盖。 |
| q007 | pass | pass | pass | pass | pass | 第 5 章实践目标覆盖完整。 |
| q008 | pass | pass | pass | pass | pass | LoRA/QLoRA 回答准确。 |
| q009 | pass | pass | pass | pass | pass | 第 7 章、RAG、Agent 及文档问答关联说明合理。 |
| q010 | pass | pass | pass | pass | pass | 学习基础要求回答准确。 |
| q011 | pass | pass | pass | pass | pass | q011 真实复核成功，引用第 2、3、6 页；未出现空响应。 |
| q012 | pass | pass | pass | pass | pass | 正确解释 Transformer 是基础、RAG/Agent 是应用。 |
| q013 | pass | pass | pass | pass | pass | 推荐第 7 章，符合文档内容。 |
| q014 | pass | pass | pass | pass | pass | 明确拒答，没有臆测 Embedding 选型。 |
| q015 | partial | pass | pass | pass | pass | 正确否认 DeepSeek Key，但引用片段包含其他 API Key，需人工确认展示是否过宽。 |
| q016 | pass | pass | pass | pass | pass | 修复后准确回答 CC BY-NC-SA 4.0，并引用第 4 页。 |
| q017 | pass | pass | pass | pass | pass | 修复后回答署名、非商业使用和相同方式共享边界，并引用第 4 页。 |
| q018 | pass | pass | pass | pass | pass | 理论与实践结合建议准确。 |
| q019 | pass | pass | pass | pass | pass | 第 5～7 章递进作用回答准确。 |
| q020 | pass | pass | pass | pass | pass | 正确拒答并保留边界。 |
| q021 | pass | pass | pass | pass | pass | Transformer 章节和实践回答准确。 |
| q022 | pass | pass | pass | pass | pass | RAG 后的 Agent 回答准确。 |
| q023 | pass | pass | pass | pass | pass | 已确认严格文档范围；当前 PDF 未提供项目级文档路由验收步骤，拒答正确。 |
| q024 | pass | pass | pass | pass | pass | 已确认评测分类规范不在当前 PDF 中，拒答正确。 |
| q025 | pass | pass | pass | pass | pass | 已确认来源校验规则不在当前 PDF 中，拒答正确。 |
| q026 | pass | pass | pass | pass | pass | 已确认 v3/v4 对比指标不在当前 PDF 中，拒答正确。 |
| q027 | pass | pass | pass | pass | pass | 已确认多文档切换方案不在当前 PDF 中，拒答正确。 |
| q028 | pass | pass | pass | pass | pass | 已确认解析异常处理规范不在当前 PDF 中，拒答正确。 |
| q029 | pass | pass | pass | pass | pass | 用幻觉和 RAG 证据解释来源展示价值。 |
| q030 | pass | pass | pass | pass | pass | 学习路线总结完整且有来源。 |

## 复核结论

- v4 的空响应问题本轮已通过有限重试修复；完整评测中 v4 失败题数为 0。
- v3 有 2 次 DeepSeek 空响应重试，最终全部成功；未出现失败题。
- v4 继续作为默认 Embedding 模型；q016–q017 修复后均正确回答并引用 PDF 第 4 页。
- q023–q028 的严格文档范围边界已由项目负责人确认，拒答判定正确，不再标记为 `uncertain`。
- v3 的 q014 仍记录为已解释的对照模型幻觉案例；它不影响 v4 默认模型选择，但保留为 v3 对照风险。
- 项目负责人已完成本轮 Phase 6 人工确认，技术门禁和人工复核门禁均可收口。
