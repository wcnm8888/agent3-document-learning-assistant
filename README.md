# Agent3 文档学习助手

一个面向本地单用户的 PDF / Markdown 知识工作台。它把文档解析、向量检索、可追溯问答、会话记忆、学习笔记和文档生命周期管理放在同一套 Gradio 界面与 Python 服务中。

## 当前能力

- 上传并索引多个 PDF / Markdown 文档；
- 按名称、格式、状态搜索、筛选和排序文档；
- 在全部文档或指定文档范围内问答；
- PDF 来源保留页码，Markdown 来源保留章节、段落和行号；
- 保存和更新学习笔记，隔离不同会话和文档关联；
- 查看学习统计与报告；
- 归档、取消归档、重新索引、确认删除、删除失败保护和一致性检查；
- 桌面、平板和移动端响应式知识工作台。

## 技术概览

- Python `>=3.10`；
- Gradio 5.x UI；
- SQLite 保存文档目录、会话、引用、笔记、学习事件和生命周期操作；
- Qdrant 保存向量；
- `text-embedding-v4`，1024 维；
- 默认 collection：`docqa_text-embedding-v4_dim1024`；
- DeepSeek 兼容接口生成回答，默认模型配置为 `deepseek-v4-flash`。

详细说明见 [架构](docs/architecture.md)、[技术栈](docs/tech-stack.md) 和 [数据库设计](docs/database-design.md)。

## 本地启动

### 1. 创建环境并安装

```powershell
cd E:\Agent\开发实践\Agent3-智能文档问答助手
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

也可以按已有锁文件或 `requirements.txt` 安装。不要把 `.env`、Token 或本地数据库提交到仓库。

### 2. 配置环境变量

```powershell
Copy-Item .env.example .env
```

按需配置 Embedding、LLM 和 Qdrant 连接。默认本地数据路径为：

- SQLite：`data/docqa.sqlite3`；
- Qdrant：`data/qdrant`。

### 3. 启动 UI

```powershell
python -m doc_qa.ui
```

默认访问：`http://127.0.0.1:7860/`。

## CLI

```powershell
python -m doc_qa.cli index <文件路径>
python -m doc_qa.cli ask "问题"
python -m doc_qa.cli session-create
python -m doc_qa.cli ask-session <session_id> "问题"
python -m doc_qa.cli note-create <session_id> "笔记"
python -m doc_qa.cli note-update <note_id> "新内容"
python -m doc_qa.cli notes
python -m doc_qa.cli history <session_id>
python -m doc_qa.cli stats
python -m doc_qa.cli report
python -m doc_qa.cli health
python -m doc_qa.cli backup-sqlite <备份路径>
```

命令参数以 `python -m doc_qa.cli --help` 为准。

## 测试与质量门禁

```powershell
python -m pytest
python -m compileall -q src tests
git diff --check
```

最近记录的全量基线为 **95 项通过**。DOC-001 Step 5 重新执行 pytest 收集并确认仍为 95 项，但没有重新运行应用全量测试，因此不把收集结果伪装为新的全量通过记录。测试范围与证据口径见 [测试策略](docs/testing-strategy.md) 和 [证据索引](docs/project-management/evidence.md)。

## 数据安全边界

- 当前仅支持本地单用户；
- 不包含认证、用户系统、多租户或公网部署；
- 不接入 Neo4j；
- 不切换现有 Embedding 模型或维度；
- 删除文档必须确认，并以 `document_id` 精确删除对应 Qdrant points；
- 测试生命周期操作必须使用临时 SQLite / Qdrant 夹具；
- 不应删除真实文档、真实数据库或真实 Qdrant points 来验证异常流程。

## 已知限制与技术债务

- Gradio 控制台可能出现 `upload_progress?upload_id=undefined` 404；已确认是非阻塞运行时风险，尚未真正修复；
- 仓库未配置 GitHub Actions 或其他 CI，不能宣称 CI 已通过；
- `pyproject.toml` 的项目描述仍保留早期 Phase 2 文案，属于配置元数据债务；
- 认证、多租户、公网部署和真实生产故障演练均未执行。

## 文档入口

- [文档权威地图](docs/README.md)
- [产品范围](docs/product-brief.md)
- [当前任务](docs/project-management/current-task.md)
- [路线图](docs/project-management/roadmap.md)
- [实现计划](docs/implementation-plan.md)
- [发布清单](docs/release-checklist.md)
- [运维手册](docs/operations-runbook.md)
- [备份与恢复](docs/backup-recovery.md)

## 交付状态

产品功能与 UI 高保真恢复已完成并形成 Git 历史。DOC-001 Step 5 已在独立分支完成文档审计；尚未提交、推送、创建 PR 或部署。远端仓库是否私有、是否存在 PR 或部署，需要在相应 Git/GitHub 步骤中单独核验，不能仅凭本地文档推断。
