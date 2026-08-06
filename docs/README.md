# Agent3 文档权威地图

## 使用规则

同一事实只允许有一个当前权威来源。当前代码、测试、schema 和 Git 事实优先于文档；已关闭任务卡、阶段日志和聊天记录不构成执行授权。

项目级规则见 [AGENTS.md](../AGENTS.md)。

## 当前状态

- 唯一活动任务：[DOC-001 文档治理与权威状态收口](project-management/current-task.md)；
- 当前分支：`chore/agent3-document-governance`；
- 当前 Step：Step 5——全仓链接、状态、敏感信息和漂移审计已完成，状态为 `ready_for_step6`；
- 最近记录全量测试基线：95 项通过；
- Step 6～7 尚未执行；
- 历史材料入口：[archive/README.md](archive/README.md)；
- Gradio 上传进度 404 是独立非阻塞技术债务；
- CI 未配置。

## 最小读取顺序

普通任务只读取：

1. [项目规则](../AGENTS.md)；
2. 本文档；
3. [当前任务](project-management/current-task.md)；
4. 当前任务直接引用的规格、计划、代码或测试。

只有选择下一任务时才读取 [路线图](project-management/roadmap.md)；只有发生事实冲突时才扩展到决策和历史归档。

## 当前权威文档

| 文档 | 唯一职责 | 是否保存完整历史 |
|---|---|---|
| [项目 README](../README.md) | 产品入口、启动、能力和交付边界 | 否 |
| [项目规则](../AGENTS.md) | 读取顺序、安全、文档和 Git 规则 | 否 |
| 本文档 | 文档职责、权威关系和读取入口 | 否 |
| [产品说明](product-brief.md) | 当前用户目标、范围和非目标 | 否 |
| [架构](architecture.md) | 当前组件、边界、数据流和一致性 | 否 |
| [技术栈](tech-stack.md) | 当前依赖、配置与技术约束 | 否 |
| [数据库设计](database-design.md) | 当前 schema、关系、状态和数据保护 | 否 |
| [设计规格](design-spec.md) | 当前 UI、交互、响应式和视觉契约 | 否 |
| [测试策略](testing-strategy.md) | 测试分层、夹具、命令和质量门禁 | 否 |
| [当前任务](project-management/current-task.md) | 唯一活动任务与当前 Step | 否 |
| [实施计划](implementation-plan.md) | 唯一活动任务的执行步骤 | 否 |
| [路线图](project-management/roadmap.md) | 未批准候选、优先级和短完成摘要 | 仅短摘要 |
| [进度](project-management/progress.md) | 当前状态、最近完成、阻塞和下一批准 | 仅最近摘要 |
| [证据](project-management/evidence.md) | 当前可复现证据索引 | 不复制原始日志 |
| [决策](decisions.md) | 长期有效 ADR、理由和后果 | 是，追加式 |
| [发布清单](release-checklist.md) | 当前发布边界、门禁和风险 | 否 |

## 长期运行文档

- [部署计划](deployment-plan.md)；
- [运维手册](operations-runbook.md)；
- [备份与恢复](backup-recovery.md)；
- [可观测性与成本](observability-and-cost.md)。

## 领域附属文档

- [文档生命周期规格](document-lifecycle-spec.md)；
- [文档生命周期测试矩阵](document-lifecycle-test-matrix.md)；
- [多文档测试矩阵](multi-document-test-matrix.md)；
- [视觉基准说明](assets/ui-visual-baseline/README.md)；
- [评测入口](../eval/README.md)；
- [评测标准](../eval/rubric.md)；
- [UI 安全夹具](../tests/fixtures/README.md)。

这些文件补充具体领域，不替代当前任务、架构、设计或测试策略。

## 历史材料

已关闭任务卡、旧 UI 路线、阶段 QA 和视觉验收记录已按批准矩阵迁入 [历史归档](archive/README.md)。不得从归档恢复阶段、执行 Prompt 或完成状态。

历史内容只用于追溯，当前事实仍以本文档所列权威入口为准。

`eval/results/` 是历史实验结果，不是当前产品状态来源。

## 冲突优先级

```text
当前代码、测试、schema、配置和 Git 事实
→ 负责人批准的产品范围、当前任务和设计基线
→ 当前 architecture / design-spec / testing-strategy
→ roadmap / progress / evidence
→ archive、旧任务卡、历史阶段和聊天记录
```

GitHub 仓库可见性、PR、CI 和部署等外部状态如果没有外部证据，必须写为“未外部核验”，不得推测为通过。

## 更新规则

- 当前文档覆盖更新，不追加完整阶段历史；
- 任务关闭后，详细过程迁移到归档，当前文档只保留短摘要；
- 新增、移动或废弃文档时同步更新本地图；
- 测试、视觉、Git、PR、CI 和部署结论必须能指向可复现证据；
- 不在文档中记录 `.env`、API Key、Token、cookie、密码、私钥或真实连接串。
