# 当前任务：DOC-001 文档治理与权威状态收口

## 当前状态

- 任务编号：`DOC-001`；
- 状态：`ready_for_step6`；
- 当前 Step：Step 5——链接、状态、敏感信息和漂移审计（已完成）；
- 当前分支：`chore/agent3-document-governance`；
- 当前停止点：Step 5 已完成并停止，等待负责人批准 Step 6；
- 当前授权：DOC-001 Step 5 已用尽，不包含暂存、提交、推送、PR、合并或部署。

## 目标

让维护者无需读取聊天历史，就能从一组互不冲突的权威文档中找到：

- 当前产品能力与边界；
- 唯一活动任务和当前 Step；
- 当前架构、数据、设计和测试策略；
- 可复现证据和发布风险；
- 非权威历史材料的归档位置。

## 当前问题

- 多份项目管理文档长期追加阶段日志，当前事实和历史过程混在一起；
- UI-0、UI-R、UI-HF、HF-R、UI-REC 等已关闭路线仍可能被误读为待执行任务；
- 旧 README 的 Git 和交付表述与当前历史不一致；
- 项目此前缺少统一测试策略入口；
- 历史任务卡、旧 UI 路线、阶段 QA 和验收记录已迁入明确的非权威归档。

## 已批准范围

1. 建立项目级规则和文档权威地图；
2. 重建当前 README、架构、技术栈、数据库、设计和测试策略；
3. 压缩 current-task、roadmap、implementation-plan、progress、evidence 和 release checklist；
4. 按已批准矩阵归档已关闭任务卡、旧 UI 路线和必要验收历史；
5. 检查链接、状态、敏感信息和文档漂移；
6. 后续通过功能分支、分批提交和 Draft PR 交付。

## 非目标与禁止范围

- 不修改业务代码、测试逻辑、依赖、SQLite schema 或生产配置；
- 不修改 PDF/Markdown 解析、RAG、Embedding、Qdrant、会话、笔记、引用或生命周期行为；
- 不删除历史材料、真实文档、真实 SQLite 数据或 Qdrant points；
- 不读取或输出 `.env`、API Key、Token、cookie、密码、私钥或真实连接串；
- 不修复 Gradio `upload_progress?upload_id=undefined` 404；
- 不创建认证、多租户、Neo4j、公网部署或 GitHub Actions；
- 不直接向 `main` 推送，不使用破坏性 Git 命令或强制推送；
- 未获授权不进入下一个 Step。

## Step 地图

| Step | 内容 | 状态 |
|---|---|---|
| 0 | Git、产品、测试和文档事实基线 | completed |
| 1 | 权威地图、冲突清单和归档迁移方案 | completed |
| 2 | 功能分支、项目规则和文档地图 | completed |
| 3 | 压缩并重建当前权威文档 | completed |
| 4 | 按批准矩阵归档历史任务和旧 UI 路线 | completed |
| 5 | 链接、状态、敏感信息和漂移审计 | completed |
| 6 | 差异审查、分批提交、推送和 Draft PR | not_started |
| 7 | PR 审查、合并、同步 main 和任务归档 | not_started |

## Step 3 交付物

- 项目 README；
- 当前架构、技术栈、数据库和 UI 设计规格；
- 新建统一测试策略；
- 当前路线图和 DOC-001 实施计划；
- 当前进度、证据索引和发布清单；
- 本文件与 `docs/README.md` 的状态同步。

## Step 3 完成定义

- 当前权威文档只描述当前事实，不再包含完整阶段日志；
- 代码、schema、配置、测试和 Git 事实一致；
- 最近 95 项测试被准确标记为历史最近记录，不伪装为本 Step 新执行；
- 所有新增/更新相对链接存在；
- 没有冲突标记、明显乱码或高置信敏感信息；
- `git diff --check` 通过；
- 工作区 diff 只包含批准的文档治理范围；
- 未修改产品代码、测试、配置、数据库、依赖或真实数据；
- 未提交、推送、创建 PR 或部署；
- 该条是 Step 2 当时的停止点；Step 4 现已按批准矩阵完成。

## Step 3 验证结果

- 重建 15 份当前权威/领域附属文档，并新增统一测试策略；
- pytest 无缓存收集结果为 95 项，和最近记录基线一致；本 Step 未运行全量应用测试；
- 更新文件的相对 Markdown 链接全部存在；
- 未发现冲突标记、常见乱码、旧测试数量或旧活动状态；
- 高置信敏感信息扫描无命中；
- `git diff --check` 通过，仅有 Git 的 LF→CRLF 工作区提示；
- 工作区改动仅位于 `README.md`、`AGENTS.md` 和 `docs/`；
- HEAD、`main` 和 `origin/main` 仍为 `7e32b11`；
- 未修改产品代码、测试、配置、数据库、依赖或真实数据；
- 该条是 Step 3 当时的停止点；Step 4 现已按批准矩阵完成，仍未提交、推送、创建 PR 或部署。

## 当前产品与风险事实

- 核心产品和 UI 高保真恢复已完成；
- 最近记录全量测试基线为 95 项通过；
- Embedding 为 `text-embedding-v4` / 1024 维；
- collection 为 `docqa_text-embedding-v4_dim1024`；
- 当前本地单用户；
- GitHub Actions / CI 未配置；
- Gradio 上传进度 404 是独立非阻塞风险；
- 认证、多租户、Neo4j、公网部署和真实生产故障演练未执行。

## Git 与回退

- DOC-001 基于 `main` / `origin/main` 的 `7e32b11` 创建功能分支；
- Step 3 不提交、不推送、不创建 PR；
- 历史原文仍可从 `7e32b11` 和 Git 历史恢复；
- 后续回退使用明确补丁或 `git revert`，不使用 `reset --hard`、`clean` 或强制推送。

## Step 4 完成结果

- 创建 `docs/archive/README.md`，明确归档非权威规则、原路径和迁移理由；
- 迁移 2 张产品任务卡到 `archive/task-cards/`；
- 迁移 5 份旧 UI 路线/基线文档到 `archive/ui-history/`；
- 迁移 1 份 Phase 2 QA 清单到 `archive/phase-history/`；
- 迁移 2 份清理/视觉验收记录到 `archive/acceptance-history/`；
- 为每份归档文件增加非权威声明，并修复已迁移路径引用；
- 当前规格、测试矩阵、运行手册、决策和冻结视觉资产保持原位；
- 未删除历史内容，原路径仍可从 Git 基线 `7e32b11` 追溯；
- 10 组旧路径均已移除、归档目标均存在且可从 `7e32b11` 追溯；每份归档正文相对基线仅新增 1 行非权威声明；
- `docs/archive/` 白名单为 10 份迁移文件和 1 个归档入口，没有额外迁移；
- 35 份 Markdown 文档的相对链接检查通过，旧路径、当前状态、高置信敏感信息、冲突标记和修改范围检查通过；
- `git diff --check` 通过，仅有 Git 的 LF→CRLF 工作区提示；
- 未修改业务代码、测试、配置、数据库、依赖或真实数据；
- Step 4 当时未提交、推送、创建 PR、部署或越权进入 Step 5；Step 5 后续经负责人单独授权执行。

## Step 5 完成结果

- 检查 35 份 Markdown 文档和 70 个相对链接，全部有效；
- 核验当前文档引用的源码、测试、视觉基准、评测文件、Compose 和配置模板均存在；
- pytest 无缓存收集仍为 95 项；本 Step 未重新运行应用全量测试；
- 运行时默认模型、维度、collection、分块、检索、会话和本地存储参数与技术文档一致；
- CLI 命令与真实 `--help` 对照通过，并修复 README 的 `backup-sqlite` 参数错误；
- 将运维命令从已废弃的外部虚拟环境路径改为当前激活环境的 `python`；
- 修正 ADR、部署和可观测性文档中的旧未来时/旧阶段表述；
- 扫描 93 份 Git 跟踪或待交付文本文件，未发现高置信密钥、Token 或私钥；`.env` 仍被忽略，仅 `.env.example` 被跟踪；
- 未发现冲突标记、常见乱码、未解释状态冲突或未解释事实漂移；
- `pyproject.toml` 的早期 Phase 2 description 是已解释、已登记的配置债务，不在 DOC-001 文档修改范围；
- `python -m compileall -q src tests` 和 `git diff --check` 通过；
- Git index 为空，33 条工作区状态均位于批准的文档治理范围；HEAD、`main`、`origin/main` 仍为 `7e32b11`；
- 未修改产品代码、测试、配置、数据库、依赖或真实数据；
- 未暂存、提交、推送、创建 PR、合并或部署。

## 下一步（未授权）

Step 6 将审查完整差异，按批准的提交结构暂存和提交，推送功能分支并创建 Draft PR。只有负责人在 Step 5 报告后明确批准，才能执行。
