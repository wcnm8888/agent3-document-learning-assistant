# 历史归档（非当前权威）

本目录保存已关闭任务卡、旧 UI 路线、阶段 QA 和验收记录，仅用于追溯。归档内容中的状态、测试数量、路径、执行 Prompt 和“下一阶段”均属于当时上下文，不构成当前执行授权。

当前事实请从 [文档权威地图](../README.md) 和 [当前任务](../project-management/current-task.md) 进入。发生冲突时，以当前代码、测试、schema、Git 事实和现行权威文档为准。

## 分类

### `task-cards/`

| 归档文件 | 原路径 | 归档理由 |
|---|---|---|
| [文档生命周期管理任务卡](task-cards/document-lifecycle-task-card.md) | `docs/document-lifecycle-task-card.md` | 功能已完成；现行规则由生命周期规格、数据库设计和测试矩阵承接 |
| [多文档与 Markdown 任务卡](task-cards/task-card-multi-document-markdown.md) | `docs/project-management/task-card-multi-document-markdown.md` | Phase 0～6 已关闭，不再驱动当前任务 |

### `ui-history/`

| 归档文件 | 原路径 | 归档理由 |
|---|---|---|
| [UI 美化任务卡](ui-history/ui-beautification-task-card.md) | `docs/project-management/ui-beautification-task-card.md` | 旧 UI-0～UI-5 路线已关闭 |
| [UI 外壳与组件重设计任务卡](ui-history/ui-redesign-task-card.md) | `docs/project-management/ui-redesign-task-card.md` | 旧 UI-R / UI-HF 路线已被 UI-REC 替代并关闭 |
| [UI 高保真恢复任务卡](ui-history/ui-fidelity-recovery-task-card.md) | `docs/project-management/ui-fidelity-recovery-task-card.md` | UI-REC0～UI-REC4 已完成并批准 |
| [高保真 UI 历史基线](ui-history/ui-high-fidelity-baseline.md) | `docs/ui-high-fidelity-baseline.md` | 保存 UI-HF / HF-R 审计推导；当前视觉基准在 `docs/assets/` |
| [Figma 模板提取历史](ui-history/ui-redesign-reference-spec.md) | `docs/ui-redesign-reference-spec.md` | 保存 UI-R1 模板观察，不作为当前设计规格 |

### `phase-history/`

| 归档文件 | 原路径 | 归档理由 |
|---|---|---|
| [Phase 2 QA 清单](phase-history/phase2-qa-checklist.md) | `docs/phase2-qa-checklist.md` | 原单 PDF 阶段清单已完成，现行测试入口为测试策略 |

### `acceptance-history/`

| 归档文件 | 原路径 | 归档理由 |
|---|---|---|
| [UI-REC0 产物清理清单](acceptance-history/ui-rec0-cleanup-manifest.md) | `docs/project-management/ui-rec0-cleanup-manifest.md` | 已执行的环境/证据清理决策记录 |
| [UI-REC3 Design QA](acceptance-history/ui-rec3-design-qa.md) | `design-qa.md` | 已完成桌面文档库视觉验收记录 |

## 仍在当前文档区的长期资产

以下内容没有归档：

- `docs/architecture.md`、`design-spec.md`、`database-design.md` 和 `testing-strategy.md`；
- `docs/document-lifecycle-spec.md` 及两个当前测试矩阵；
- 部署、运维、备份恢复、可观测性和决策文档；
- `docs/assets/ui-visual-baseline/` 冻结视觉基准；
- DOC-001 当前任务、计划、进度、证据和发布清单。

## 追溯与维护规则

- 原路径和迁移前内容可从 Git 基线 `7e32b11` 恢复；
- 不在归档文件中继续追加当前进度；
- 不从归档直接创建下一阶段；
- 如当前文档引用归档，必须明确标注“历史”；
- 归档文件可修复链接和增加归档声明，但不重写历史结论。
