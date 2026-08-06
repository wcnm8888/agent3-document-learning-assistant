# 当前发布与交付清单

## 1. 当前交付对象

- 产品功能：已完成；
- UI 高保真恢复：已完成并获负责人视觉批准；
- 当前唯一活动任务：DOC-001 文档治理；
- 当前 Step：Step 6 交付已完成，Draft PR #1 等待审查和 Step 7 授权；
- 当前分支：`chore/agent3-document-governance`。

本清单区分“产品已完成”和“DOC-001 尚未交付”。

## 2. 产品基线

- [x] PDF / Markdown 解析、索引和来源定位；
- [x] 多文档搜索、筛选、排序、详情和问答范围；
- [x] RAG 问答、无结果处理和结构化来源；
- [x] 会话隔离、笔记、统计和报告；
- [x] 文档归档、删除、恢复、重新索引和一致性保护；
- [x] 桌面、平板和移动端 UI；
- [x] 负责人完成最终视觉批准；
- [x] 最近记录全量测试基线为 95 项通过；
- [x] DOC-001 Step 6 提交前重新运行全量测试，95 项通过；
- [ ] CI——仓库未配置 CI。

## 3. 当前数据与业务边界

- [x] Embedding 固定为 `text-embedding-v4` / 1024 维；
- [x] 当前 collection 为 `docqa_text-embedding-v4_dim1024`；
- [x] PDF 页码与 Markdown 章节/段落/行号分别保护；
- [x] `document_id`、会话、引用和笔记隔离有测试覆盖；
- [x] 删除需要确认，并精确按 `document_id` 删除 points；
- [x] 删除失败有操作记录和补偿状态；
- [x] 测试不删除真实 Qdrant points；
- [ ] 真实生产删除/恢复/故障演练——未执行，且不是当前本地单用户交付门禁。

## 4. DOC-001 文档门禁

- [x] Step 0：事实基线；
- [x] Step 1：权威地图和迁移方案获批准；
- [x] Step 2：功能分支、`AGENTS.md` 和 `docs/README.md`；
- [x] Step 3：当前权威文档重建并通过门禁；
- [x] Step 4：历史归档迁移；
- [x] Step 5：全量链接、状态、敏感信息和漂移审计；
- [x] Step 6：差异审查、分批提交、推送和 Draft PR；
- [ ] Step 7：PR 审查、合并、同步 main 和 DOC-001 归档。

Step 3 完成前需要验证：

- [x] 所有新增/更新相对链接存在；
- [x] 没有冲突标记或明显乱码；
- [x] `git diff --check` 通过；
- [x] 高置信敏感信息扫描无命中；
- [x] diff 仅包含批准的文档治理范围；
- [x] current-task、roadmap、implementation-plan、progress、evidence、release checklist 状态一致；
- [x] Step 3 当时明确停止且未越权；Step 4 后续经负责人单独授权并已完成。

## 5. Git 与远端交付

- [x] DOC-001 从同步的 `main` 基线建立功能分支；
- [x] DOC-001 分批提交；
- [x] DOC-001 功能分支推送；
- [x] [Draft PR #1](https://github.com/wcnm8888/agent3-document-learning-assistant/pull/1)；
- [ ] 合并——Step 7 前禁止；
- [ ] 部署——不在 DOC-001 范围。

外部仓库已通过 GitHub CLI 核验为私有；Draft PR #1 为 OPEN / Draft，目标分支为 `main`。PR 尚未合并，未部署。

## 6. 安全检查

- [x] 不在文档中记录 `.env` 内容、API Key、Token、cookie、密码或私钥；
- [x] 不修改生产配置；
- [x] 不修改 SQLite schema、Qdrant、Embedding 或真实数据；
- [x] 不删除历史文档；
- [x] 不执行 `reset --hard`、`clean` 或强制推送；
- [x] Step 5 全量敏感信息与历史链接审计；
- [x] 35 份 Markdown、70 个相对链接和关键路径检查通过；
- [x] 93 份 Git 跟踪或待交付文本文件高置信敏感信息扫描无命中；
- [x] `.env` 未被跟踪，仅 `.env.example` 进入版本控制；
- [x] pytest 收集确认 95 项，未伪装为新的应用全量测试结果；
- [x] Step 6 全量 pytest 重新执行，95 项通过；
- [x] `compileall`、`git diff --check` 和修改范围检查通过；
- [x] Step 5 停止点 Git index 为空；Step 6 按批准范围精确暂存、提交、推送并创建 Draft PR；
- [x] 没有未解释状态冲突或事实漂移。

## 7. 已知风险与非目标

### 技术债务

- Gradio `upload_progress?upload_id=undefined` 404 未修复；
- `pyproject.toml` 项目描述仍为早期 Phase 2 文案；
- 没有 CI。

### 数据安全风险

- SQLite 与 Qdrant 使用补偿一致性；进程中断可能留下 `inconsistent`；
- 源文件移动或删除会影响 tombstone 恢复；
- 真实生产恢复演练未执行。

### 运行时风险

- 外部 Embedding / LLM 服务可能不可用、限流或变更价格；
- Gradio 上游 DOM 和接口变化可能影响 UI 或上传日志。

### 未执行的产品/交付项

- 认证、用户系统、多租户；
- Neo4j；
- 公网部署和多实例；
- PR、合并和部署；
- GitHub Actions。

## 8. 发布结论

产品当前可作为本地单用户成果继续体验和学习；DOC-001 尚未完成交付。只有 Step 7 合并并归档后，文档治理任务才能标记为 `completed`。在此之前不得把本清单中的产品完成状态误写成 DOC-001 已完成。
