# 当前实施计划：DOC-001

## 1. 目标

在不修改产品代码、测试逻辑、配置、数据库和真实数据的前提下，建立唯一文档权威、压缩当前事实、归档已关闭历史，并通过可审查的 Git 流程交付。

当前唯一活动任务：[DOC-001 当前任务](project-management/current-task.md)。

## 2. 范围

### 包含

- 项目级规则和文档地图；
- README、架构、技术栈、数据库、设计和测试策略当前化；
- current-task、roadmap、implementation-plan、progress、evidence 和 release checklist 压缩；
- 按已批准矩阵迁移历史任务卡和旧 UI 路线；
- 链接、状态、敏感信息、范围和漂移检查；
- 后续分批提交、推送和 Draft PR。

### 不包含

- 产品功能、UI、测试、依赖或配置修改；
- PDF/Markdown、RAG、Embedding、Qdrant、SQLite schema、会话、笔记或生命周期逻辑修改；
- 删除真实数据或历史资料；
- 修复 Gradio 上传进度 404；
- 认证、多租户、Neo4j、公网部署或 GitHub Actions；
- 未获批准的后续产品任务。

## 3. Step 地图

| Step | 交付物 | 状态 | 停止条件 |
|---|---|---|---|
| 0 | Git、代码、测试、文档事实基线 | completed | 事实冲突和风险已列明 |
| 1 | 权威地图、冲突清单、归档迁移方案 | completed | 负责人批准方案 |
| 2 | 功能分支、`AGENTS.md`、`docs/README.md` | completed | 入口和边界可用 |
| 3 | 当前权威文档重建 | completed | 文档当前、简洁、一致且通过门禁 |
| 4 | 按批准矩阵归档历史 | completed | 历史可追溯且不再冒充当前状态 |
| 5 | 链接、状态、敏感信息和漂移审计 | completed | 没有未解释冲突 |
| 6 | 差异审查、分批提交、推送、Draft PR | not_started | 提交与远端证据可追溯 |
| 7 | PR 审查、合并、同步 main 和任务归档 | not_started | DOC-001 正式关闭 |

每个 Step 完成后停止；下一 Step 需要负责人明确授权。

## 4. Step 3 执行内容

### 输入

- 当前代码、schema、测试和 Git 事实；
- Step 1 已批准的文档权威地图与迁移矩阵；
- Step 2 创建的规则和文档入口；
- 已完成产品与 UI 的最终证据。

### 重建文件

- `README.md`；
- `docs/architecture.md`；
- `docs/tech-stack.md`；
- `docs/database-design.md`；
- `docs/design-spec.md`；
- `docs/testing-strategy.md`；
- `docs/project-management/roadmap.md`；
- `docs/implementation-plan.md`；
- `docs/project-management/progress.md`；
- `docs/project-management/evidence.md`；
- `docs/release-checklist.md`；
- `docs/project-management/current-task.md`；
- `docs/README.md` 的状态和入口。

### 写作规则

- 当前文档只写当前事实，不按时间继续追加阶段日志；
- 测试基线写为“最近记录”，除非本 Step 实际重新运行；
- GitHub、PR、CI、仓库可见性和部署等外部状态无法验证时标记未核验；
- 历史任务在 Step 4 归档，本 Step 通过 Git 历史保留原文；
- 不复制原始运行日志、密钥或敏感配置。

### Step 3 门禁

- 所有新相对链接存在；
- 没有冲突标记和明显乱码；
- `git diff --check` 通过；
- 高置信敏感信息扫描无命中；
- diff 仅包含批准的文档治理文件；
- 不运行 Git 提交、推送、PR 或部署；
- 不进入 Step 4。

## 5. Step 4 完成结果

已按 Step 1 批准矩阵：

- 创建 `docs/archive/` 分类目录和非权威入口；
- 迁移已关闭任务卡、旧 UI 路线、阶段 QA 和必要验收记录；
- 在归档首页明确“非当前权威”；
- 修复所有受影响链接；
- 不删除长期有效规格、运行手册、决策和视觉基准；
- 不修改产品代码、测试、配置、数据或依赖；
- Step 4 当时不提交、推送、创建 PR、部署或越权进入 Step 5；Step 5 后续经负责人单独授权执行。

## 6. 验证与回退

### Step 5 完成结果

- 全仓 Markdown 相对链接、关键路径、CLI、状态、敏感信息、乱码、冲突标记和事实漂移审计通过；
- pytest 收集确认 95 项，未重新运行应用全量测试；
- 修复 README 备份命令、运维 Python 路径和长期文档中的旧未来时表述；
- 唯一保留的配置漂移是已登记的 `pyproject.toml` 早期 description，不属于本任务文档修改范围；
- 未修改或运行产品数据，未执行暂存、提交、推送、PR、合并或部署。

- 当前未提交变更可通过逐文件 diff 审查；
- 后续提交按“规则入口 / 当前权威 / 历史归档 / 最终链接”分批；
- 回退使用 Git `revert` 或对明确文件应用反向补丁，不使用 `reset --hard`、`clean` 或强制推送；
- 历史原文始终可从 `main` 基线和 Git 历史恢复。

## 7. 当前风险

- 归档文件保留历史状态和测试数字，必须通过归档声明避免被误读为当前事实；
- Step 5 全仓库链接、状态、敏感信息和漂移审计已通过；
- 仓库未配置 CI，文档门禁当前依赖本地命令；
- DOC-001 不处理 Gradio 404、产品元数据或任何产品功能。
