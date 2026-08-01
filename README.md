# 智能文档学习助手

基于 Datawhale `hello-agents` 第八章 8.4 构建的独立应用项目。

项目工作目录：`E:\Agent\开发实践\Agent3-智能文档问答助手`

官方框架源码参考：`E:\Agent\hello-agents-upstream`

本项目不直接修改官方框架源码，应用代码、项目文档、评测材料和运行配置独立维护。

## 当前状态

原单 PDF 产品的 Phase 0～8 已完成；当前多文档与 Markdown 任务的 Phase 2～6 已完成，真实浏览器问答、来源、笔记、文档切换、响应式验收和全量质量门禁均已通过。Gradio 上传进度 404 仍记录为非阻塞依赖风险。项目没有自动部署、没有提交或推送，也不建议当前版本直接公网部署。

默认 Embedding 为阿里云百炼 `text-embedding-v4`，向量维度 1024，生产 collection 为 `docqa_text-embedding-v4_dim1024`。DeepSeek 通过云 API 调用，真实密钥只放本地 `.env`。

索引命令同时支持 PDF 和 Markdown：

```powershell
$env:PYTHONPATH="$PWD\src"
E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.cli index data/reference/<document>.pdf
E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.cli index data/reference/<document>.md
```

运行时检查：`python -m doc_qa.cli health`；SQLite 备份：`python -m doc_qa.cli backup-sqlite <destination>`。

## 环境要求

- Windows + Python 3.11 虚拟环境（项目要求 Python 3.10+）。
- Docker Desktop Linux Engine，用于本地 Qdrant `docqa-qdrant`。
- 可选使用 `docker-compose.local.yml` 启动隔离的 Qdrant-only 本地实例；不要与已有同端口容器同时启动。
- 已复制 `.env.example` 为项目根目录 `.env`，再填写本地密钥；不要提交 `.env`。
- `PYTHONPATH` 指向项目 `src` 目录。

## 本地启动

先确认 Qdrant：

```powershell
docker ps --filter "name=docqa-qdrant"
Invoke-WebRequest http://localhost:6333/healthz
```

运行配置、Qdrant 两个 collection 和 SQLite 状态检查：

```powershell
$env:PYTHONPATH="$PWD\src"
E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.cli health
```

如需创建隔离的 Qdrant-only 实例：

```powershell
docker compose -f docker-compose.local.yml config
docker compose -f docker-compose.local.yml up -d
```

备份 SQLite：

```powershell
$env:PYTHONPATH="$PWD\src"
E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.cli backup-sqlite data/backups/docqa.sqlite3
```

启动 UI：

```powershell
cd "E:\Agent\开发实践\Agent3-智能文档问答助手"
$env:PYTHONPATH="$PWD\src"
E:\Agent\docqa-venv311\Scripts\python.exe -m doc_qa.ui
```

默认地址为 `http://127.0.0.1:7860`。索引、问答和学习统计也可以通过 `python -m doc_qa.cli --help` 查看 CLI 入口。

UI 文档库支持 PDF、`.md` 和 `.markdown`；问答范围支持全部文档或指定 `document_id`。切换范围会清空当前回答、来源和临时上下文，但不会删除 SQLite 中的历史会话和笔记。PDF 来源显示页码，Markdown 来源显示章节、段落和行号。

## 目录

- `src/doc_qa/`：解析、分块、Embedding、Qdrant、问答、学习服务和 UI
- `tests/`：Phase 2～6 自动化测试
- `docs/`：规格、架构、运维、部署和验证证据
- `eval/`：文档问答评测集和评分标准
- `data/reference/`：授权的基准文档

## 质量验证

```powershell
cd "E:\Agent\开发实践\Agent3-智能文档问答助手"
E:\Agent\docqa-venv311\Scripts\python.exe -m pytest tests -q
E:\Agent\docqa-venv311\Scripts\python.exe -m compileall -q src tests
```

部署和恢复前请阅读：

- `docs/deployment-plan.md`
- `docs/operations-runbook.md`
- `docs/backup-recovery.md`
- `docs/observability-and-cost.md`
- `docs/release-checklist.md`
- `docker-compose.local.yml`

当前版本没有认证、多租户、限流和独立应用健康端点，SQLite 也只适合单实例。本项目的生产部署仍需单独完成安全、存储和运维评审。
