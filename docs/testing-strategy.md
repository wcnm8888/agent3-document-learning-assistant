# 测试策略

## 1. 目的与口径

测试用于保护文档解析、索引、检索、问答、持久化、生命周期和 UI 业务语义。功能测试通过不等于视觉高保真通过，也不等于 CI、生产或灾备演练通过。

最近记录的全量基线为 **95 项通过**。该数字来自已完成阶段的本地测试记录；DOC-001 Step 5 重新执行收集并确认仍为 95 项，但没有重新运行应用全量测试。

仓库当前未配置 CI 工作流。

## 2. 测试层次

| 层次 | 目标 | 主要手段 |
|---|---|---|
| 单元测试 | 解析、分块、配置、格式化、状态转换 | 纯函数、临时文件、替身 |
| 服务集成 | SQLite、Qdrant 接口、问答编排、生命周期补偿 | 临时 SQLite、内存/临时 Qdrant、假 Embedding/LLM |
| UI 契约 | 组件、回调、状态文本、布局类和业务绑定 | Gradio 测试入口、确定性 fixture |
| 浏览器验收 | 真实渲染、响应式、焦点、滚动、重叠和关键状态 | 真实 Chromium / Playwright |
| 视觉验收 | 与冻结 Figma 基线比较信息密度与几何关系 | 固定视口、100% 缩放、同一数据状态、人工批准 |
| 运维检查 | 健康检查、备份、恢复步骤和脱敏 | CLI、临时数据库、文档演练 |

## 3. 测试文件地图

| 文件 | 主要覆盖 |
|---|---|
| `test_phase2_ingestion.py` | PDF 解析、分块、Embedding 和 Qdrant 索引 |
| `test_phase2_multidocument.py` | 多文档索引与隔离 |
| `test_phase3_multidocument.py` | 文档范围与多文档问答 |
| `test_phase3_multidocument_metadata.py` | 文档元数据、PDF/Markdown 来源定位 |
| `test_phase3_qa.py` | 检索、阈值、回答和引用 |
| `test_phase4_learning.py` | 会话、记忆、笔记、学习事件和报告 |
| `test_phase5_ui.py` | UI 结构、状态、响应式契约和视觉恢复约束 |
| `test_phase6_eval_helpers.py` | 评测辅助逻辑 |
| `test_phase8_operations.py` | 健康检查、备份和运行边界 |
| `test_document_lifecycle.py` | 归档、删除、恢复、一致性和失败回滚 |

测试函数数量和 pytest case 数可能因参数化不同。对外报告以 `pytest --collect-only -q` 和实际执行摘要为准，不手工推算。

## 4. 必须保护的业务契约

- PDF 来源使用页码；
- Markdown 来源使用章节、段落和行号，页码允许为空；
- `document_id` 隔离索引、问答、删除和详情；
- 搜索、筛选和排序不改变 `document_filter`；
- 文档范围切换清空当前回答、来源和待保存笔记；
- 会话历史和笔记关联不串用；
- 无检索结果返回明确状态，不生成伪答案；
- 归档保留向量；删除只删除目标文档 points 并保留 tombstone；
- 删除失败回退或标记不一致，不影响既有其他文档；
- 错误信息脱敏。

## 5. 安全夹具

- 数据库测试使用 `tmp_path` 下的 SQLite；
- Qdrant 使用内存客户端、临时路径或明确的测试替身；
- Embedding 和 LLM 使用确定性假实现，除非测试明确标记为外部集成；
- UI 视觉状态使用 `tests/fixtures/ui_visual_baseline.py` 的确定性业务数据；
- 禁止连接真实生产 collection 来验证删除、回滚或一致性故障；
- 禁止删除真实文档、真实数据库或真实 Qdrant points。

## 6. 标准命令

### 全量

```powershell
python -m pytest
python -m compileall -q src tests
git diff --check
```

### 收集与定向

```powershell
python -m pytest --collect-only -q
python -m pytest tests/test_phase5_ui.py
python -m pytest tests/test_document_lifecycle.py
python -m pytest tests/test_phase3_qa.py tests/test_phase4_learning.py
```

### 文档治理

文档任务至少执行：Markdown 相对链接检查、冲突标记检查、`git diff --check`、敏感信息高置信度扫描和修改范围检查。纯文档变更可以不重复运行应用全量测试，但必须明确说明。

## 7. 浏览器和视觉门禁

固定基线：

- 1440×900 桌面学习会话完成态；
- 1440×900 桌面文档库完成态；
- 390×844 移动端上下文面板；
- 1024×768 作为结构回归视口。

每次验收固定浏览器缩放 100%，使用同一确定性数据状态，并记录：

- `scrollWidth` / `clientWidth` 和全局纵向滚动；
- 主工作区、时间线、Composer 和检查器几何边界；
- 元素重叠；
- 长文件名和完整 `document_id` 访问路径；
- 标签、焦点、禁用、错误脱敏和触控目标；
- console error/warn；
- 可追溯截图和复现步骤。

截图必须与相同 Figma frame、视口和数据状态并排审核。CSS 字符串存在、类名存在或测试通过不能替代最终视觉审核。

## 8. 故障状态策略

上传中断、解析失败、索引失败、外部服务不可用、数据库错误、问答失败、笔记保存失败和删除失败应优先在临时应用中通过 UI 边界故障注入复现。不能安全复现时：

1. 用定向测试验证状态映射和脱敏；
2. 记录未进行真实故障演练的原因；
3. 不宣称真实生产故障验证通过。

## 9. 完成标准

一个功能阶段只有在以下条件满足后才可关闭：

- 相关定向测试通过；
- 全量测试通过或差异有明确解释；
- `compileall` 和 `git diff --check` 通过；
- 未修改范围外核心业务或真实数据；
- 浏览器证据满足该阶段规定；
- 文档、任务状态和实际证据一致；
- 已知未解决风险被如实记录。

## 10. 当前缺口

- 未配置 CI，因此没有远端自动化门禁；
- Gradio 上传进度 404 仍是未关闭的非阻塞风险；
- 认证、多租户、公网部署和真实生产故障/恢复演练未测试；
- 外部模型长期稳定性、成本和速率限制没有持续基准。
