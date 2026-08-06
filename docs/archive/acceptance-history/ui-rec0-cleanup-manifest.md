# UI-REC0 产物清理决策清单

> **归档，非当前权威。** 本文件仅记录 UI-REC0 当时的清理决策，不构成新的删除授权；当前文件操作必须以当前任务和用户明确授权为准。

> 状态：等待负责人确认。UI-REC0 只建立清单，没有删除、移动或压缩任何现有文件。

## 保留并纳入版本控制

- `docs/assets/ui-visual-baseline/`：三张冻结 Figma 基准及复现说明。
- `tests/fixtures/ui_visual_baseline.py`：临时 SQLite/Qdrant 浏览器夹具。
- `src/`、`tests/`、项目管理文档、`.gitignore`、`uv.lock`：恢复点所需源码、测试、规格和依赖锁。

## 保留但不纳入 Git

- `.env`：本地敏感配置，继续由 `.gitignore` 排除。
- `.venv/`：当前项目虚拟环境。
- `data/`：当前本地业务数据和 Qdrant 数据；不得在 UI 清理中操作。
- `output/`：现有历史截图和临时验证证据；在负责人确认归档范围前不删除。

## 建议归档后清理

- 项目 `output/playwright/` 和 `output/ui-fidelity-recovery/` 中除最终选定证据外的阶段截图、HTML 包装页、临时日志和 SQLite sidecar。
- `E:\Agent\ui4-*`、`E:\Agent\ui5-*`、`E:\Agent\ui-audit-*` 及对应日志：历史浏览器夹具与阶段证据。
- 重复命名的 `final`/非 `final` 截图；已审计到至少三组内容完全相同的文件。

## 建议确认后直接清理

- 项目 `.playwright-cli/`：浏览器自动化运行缓存。
- 项目 `src/agent3_document_qa.egg-info/`：可再生成的构建元数据。
- 项目 `.pytest_cache/`：可再生成的测试缓存。
- `E:\Agent\_isolated/`：Gradio 版本隔离环境，约 6.3 万个文件、约 1.36 GB；必须先确认没有进程引用且不再需要复查兼容性。

## 明确保留或单独处理

- `uv.lock`：锁定当前 Gradio 5.50.0 等依赖，作为恢复点的一部分保留。
- Gradio `upload_progress?upload_id=undefined` 404：属于独立技术债务，不能通过删除隔离环境或日志伪装为已修复。
- 旧 UI 任务卡：保留用于追溯，但顶部必须标记为历史、非权威，不再驱动后续实现。

## 后续产物规则

1. 所有浏览器截图、日志和临时数据库只能写入项目 `output/`。
2. 可复用测试夹具放入 `tests/fixtures/`；冻结设计资产放入 `docs/assets/`。
3. 禁止继续向 `E:\Agent` 根目录直接写入阶段文件。
4. 每次验收结束必须报告保留、归档、可清理三类产物。
5. 任何清理操作必须在负责人确认具体路径后执行。
