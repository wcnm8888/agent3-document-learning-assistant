# 验收证据索引

本文件只索引当前可复现证据和最近有效结论，不复制完整运行日志。历史阶段证据位于 `docs/archive/`，属于非权威材料。

## 1. 当前产品证据

| 领域 | 权威实现 / 测试 | 当前结论 |
|---|---|---|
| PDF/Markdown 解析 | `src/doc_qa/pdf_parser.py`、`markdown_parser.py`、`document_parser.py`；Phase 2/3 测试 | 两种格式可解析，并保留各自定位语义 |
| 分块与索引 | `chunker.py`、`embedding.py`、`qdrant_index.py`、`ingestion.py` | `text-embedding-v4` / 1024 维，按文档隔离 |
| 多文档目录 | `document_catalog.py`；multi-document 测试 | 搜索、筛选、排序、详情和重复识别 |
| RAG 问答 | `qa.py`、`document_scope.py`；`test_phase3_qa.py` | Top-K、阈值、范围过滤、无结果和结构化引用 |
| 会话与学习 | `memory_store.py`、`learning.py`；`test_phase4_learning.py` | 会话、引用、笔记、学习事件、统计和报告持久化 |
| 生命周期 | `lifecycle.py`；`test_document_lifecycle.py` | 归档、删除、恢复、重新索引、一致性和失败回退 |
| 运维 | `health.py`、`backup.py`；`test_phase8_operations.py` | 本地健康检查和 SQLite 一致性备份 |
| UI | `ui.py`、`ui.css`；`test_phase5_ui.py` | 桌面、平板、移动端知识工作台与业务绑定 |

## 2. 测试证据

- 最近记录的全量 pytest 基线：**95 项通过**；
- UI 最终阶段记录：UI 定向 30 项通过；
- 当前测试入口：`tests/`；
- 当前测试策略：[testing-strategy.md](../testing-strategy.md)；
- 领域矩阵：[multi-document-test-matrix.md](../multi-document-test-matrix.md)、[document-lifecycle-test-matrix.md](../document-lifecycle-test-matrix.md)。

重要口径：DOC-001 Step 3～5 是纯文档治理，当时只重新确认测试收集数量；Step 6 在提交前使用项目 `.venv` 重新运行全量 pytest，95 项通过。仓库没有 CI，因此该结果只能表述为本地验证通过，不能表述为 CI 通过。

## 3. 视觉证据

冻结基准：

- `docs/assets/ui-visual-baseline/figma-desktop-session-1440x900.png`；
- `docs/assets/ui-visual-baseline/figma-desktop-library-1440x900.png`；
- `docs/assets/ui-visual-baseline/figma-mobile-context-390x844.png`。

最终 UI 恢复由负责人完成人工视觉批准。可复现浏览器契约见 [设计规格](../design-spec.md) 和 [测试策略](../testing-strategy.md)。本地 `output/` 中可能保留浏览器截图，但它不是当前权威文档，也不应全部提交。

## 4. 数据安全证据

- 生命周期测试使用临时 SQLite / Qdrant 或测试替身；
- 真实 Qdrant points 未用于删除测试；
- SQLite 删除保留 tombstone、历史引用和笔记；
- Qdrant 删除条件为精确 `document_id`；
- PDF 页码和 Markdown 章节/段落/行号在代码和测试中分别保护；
- 文档范围、会话和笔记隔离有自动化覆盖。

## 5. Git 与交付证据

当前已知提交链：

| Commit | 说明 |
|---|---|
| `b121f09` | 初始化智能文档问答项目 |
| `f3c5403` | 交付本地文档 QA 工作流 |
| `be419eb` | 建立 UI 视觉恢复基线 |
| `c9f1a64` | 完成高保真知识工作台实现 |
| `7cd53e9` | 收口 UI 视觉恢复文档 |
| `7e32b11` | 记录私有仓库发布状态 |

DOC-001 开始时：

- `main`、`origin/main` 和 HEAD 同步于 `7e32b11`；
- 从该基线创建 `chore/agent3-document-governance`；
- Step 2～5 尚未提交、推送或创建 PR；
- 当时未部署。

DOC-001 Step 6 交付状态：

- 提交：`f87286a`（当前权威文档）、`dc2b000`（历史归档）、`c378839`（治理记录）；
- 远端分支：`origin/chore/agent3-document-governance`；
- 远端仓库经 GitHub CLI 核验为私有；
- [Draft PR #1](https://github.com/wcnm8888/agent3-document-learning-assistant/pull/1) 为 OPEN / Draft，base 为 `main`；
- 状态检查列表为空，仓库当前未配置 CI；
- 未合并、未部署，Step 7 尚未执行。

## 6. DOC-001 证据

### Step 0～1

- 完成 Git、产品、测试、文档体量和状态冲突审计；
- 形成并获得批准的文档权威地图、冲突清单和归档迁移矩阵；
- 确认旧 current-task、roadmap、implementation-plan、progress、evidence 和 release checklist 混入大量历史。

### Step 2

- 分支：`chore/agent3-document-governance`；
- 新增 `AGENTS.md`；
- 新增 `docs/README.md`；
- 将 DOC-001 设为唯一活动任务；
- `git diff --check`、入口链接和高置信敏感信息检查通过；
- 无产品代码、测试、配置、数据库或依赖修改。

### Step 3

已重建：

- 项目 README；
- 当前架构、技术栈、数据库设计和 UI 设计规格；
- 统一测试策略；
- 当前路线图、实施计划、进度、证据和发布清单。

最终门禁：相对链接、冲突/乱码、旧状态、敏感信息、`git diff --check` 和修改范围检查通过；pytest 无缓存收集确认 95 项。该段记录的是 Step 3 当时停止点，后续迁移见下方 Step 4。

### Step 4

- 归档入口：`docs/archive/README.md`；
- 迁移范围：2 张产品任务卡、5 份 UI 历史、1 份阶段 QA、2 份验收/清理记录；
- 所有归档文件增加非权威声明，并保留原路径映射；
- 10 组旧路径均已移除，目标文件均存在且可从 `7e32b11` 追溯；每份归档正文相对基线仅新增 1 行非权威声明；
- `docs/archive/` 仅包含批准的 10 份历史文件和 1 个归档入口；
- 35 份 Markdown 文档相对链接检查通过；旧路径、当前状态、高置信敏感信息、冲突标记、修改范围和 `git diff --check` 门禁通过；
- 当前长期规格、测试矩阵、运维文档、决策和冻结视觉资产未移动；
- 原始内容可从 Git 基线 `7e32b11` 追溯；
- 未修改产品代码、测试、配置、数据库、依赖或真实数据；
- Step 4 当时未提交、推送、创建 PR、部署或越权进入 Step 5；Step 5 后续经负责人单独授权执行。

### Step 5

- pytest 无缓存收集：95 项；未重新运行应用全量测试；
- Markdown：35 份文件、70 个相对链接全部有效；
- 当前文档引用的源码、测试、视觉基准、评测文件、Compose 和配置模板均存在；
- CLI `--help` 与 README 命令对照通过；修复 `backup-sqlite` 的错误参数写法；
- `Settings` 默认模型、维度、collection、分块、检索、会话和存储参数与文档一致；
- 运行依赖均由 `pyproject.toml` 表达，pytest 保持测试依赖；
- 扫描 93 份 Git 跟踪或待交付文本文件，高置信敏感信息无命中；`.env` 未跟踪；
- 35 份 Markdown 无冲突标记或常见乱码；
- 修复运维文档对外部 `docqa-venv311` 的硬编码依赖，以及 ADR/部署/可观测性旧阶段口吻；
- `pyproject.toml` description 与当前产品不一致，但已在 README、技术栈、路线图和发布清单登记为独立配置债务；
- `python -m compileall -q src tests` 与 `git diff --check` 通过；
- Git index 为空，33 条工作区状态均属于批准的文档治理范围；HEAD、`main`、`origin/main` 均为 `7e32b11`；
- 没有未解释状态冲突或事实漂移；未修改产品代码、测试、配置、数据库、依赖或真实数据；
- 未暂存、提交、推送、创建 PR、合并或部署。

### Step 6

- 完整差异和提交范围审查：仅包含 `README.md`、项目 `AGENTS.md` 和 `docs/`；
- 当前 Markdown 链接检查：41 份文件、70 个本地相对链接，0 个失效；
- 高置信敏感信息扫描：84 份 Git 跟踪或待交付文本文件，0 个命中；
- `.env` 未被跟踪，仅 `.env.example` 被跟踪；
- 全量 pytest：95 项通过；
- `python -m compileall -q src tests`、`git diff --check` 通过；
- 归档迁移被 Git 识别为 10 组 rename，原始内容仍可从 `7e32b11` 追溯；
- 已完成分批提交、功能分支推送和 Draft PR 创建；
- 未修改产品代码、测试、配置、数据库、依赖或真实数据；
- 未合并、未同步 `main`、未归档 DOC-001、未部署。

## 7. 已知未关闭项

| 类型 | 项目 | 状态 |
|---|---|---|
| 技术债务 | Gradio `upload_progress?upload_id=undefined` 404 | 非阻塞，未修复 |
| 交付工程 | GitHub Actions / CI | 未配置 |
| 配置债务 | `pyproject.toml` description 仍为 Phase 2 文案 | 未处理 |
| 数据安全 | 真实生产故障和恢复演练 | 未执行 |
| 产品边界 | 认证、多租户、Neo4j、公网部署 | 未实现，属于非目标 |

## 8. 复现命令

```powershell
python -m pytest
python -m compileall -q src tests
git diff --check
python -m doc_qa.cli health
python -m doc_qa.ui
```

运行需要本地配置，但不得把 `.env`、API Key、Token 或真实连接信息复制到证据文档。
