# 运行与运维手册

## 启动顺序

1. 进入项目目录，确认使用项目虚拟环境并设置 `PYTHONPATH=src`。
2. 确认本地 `.env` 存在且只在本机保存真实密钥。
3. 启动或确认 `docqa-qdrant`，检查 `http://localhost:6333/healthz` 返回 200。
4. 检查 v4 collection 为 1024 维，且没有被 v3 写入。
5. 启动 `python -m doc_qa.ui`，默认只监听 `127.0.0.1:7860`。
6. 打开页面后先检查文档库状态，再进行索引或问答。

## 自动健康检查

健康检查命令只读检查配置、Qdrant healthz、v4 collection、v3 评测 collection 和 SQLite 完整性；不会创建 collection、写入向量或调用 LLM。检查失败时退出码为 1，并在 JSON 中返回 `component`、`status`、`error_type` 和脱敏详情：

```powershell
cd "E:\Agent\开发实践\Agent3-智能文档问答助手"
$env:PYTHONPATH="$PWD\src"
python -m doc_qa.cli health
```

健康检查要求本地 `.env` 同时存在 `EMBED_API_KEY` 和 `DEEPSEEK_API_KEY`；输出只显示模型、维度、collection、点数和错误类型，不显示密钥。

## Qdrant-only Compose

`docker-compose.local.yml` 只定义 Qdrant 和持久化卷，不定义应用容器。Qdrant 官方镜像不内置 `curl/wget`，因此 Compose 不伪造容器内 HTTP healthcheck；启动后必须使用项目 `health` CLI 检查真实 `/healthz`。启动前先确认 6333/6334 端口没有被已有 `docqa-qdrant` 占用；已有容器运行时直接使用已有容器，不要重复启动 Compose 服务。

标准启动示例：

```powershell
cd "E:\Agent\开发实践\Agent3-智能文档问答助手"
$env:PYTHONPATH="$PWD\src"
python -m doc_qa.ui
```

## 健康检查

当前已实现并可验证的是 Qdrant healthz、collection 维度/点数校验、Embedding 维度校验和 SQLite integrity check。应用本身尚无独立 `/health` 端点，这是生产前的明确缺口；不要把浏览器页面能打开等同于依赖全部健康。

## 重试与故障处理

- Embedding：仅对 429、5xx 和网络类临时错误有限重试；批大小默认 10；参数、权限和维度错误直接失败。
- DeepSeek：默认使用 `DEEPSEEK_THINKING=disabled`，对临时网络/服务错误和空响应有限重试；耗尽后返回包含 `finish_reason` 的可定位错误，不生成伪答案。若启用思考模式，必须提高输出预算并重新执行真实问答验收。
- Qdrant：连接失败直接报告 URL、collection 和操作阶段，不能切换到其他模型或静默使用测试向量。
- SQLite：启用 WAL、外键和 busy timeout；写入失败时保留原文件，先备份再诊断。

## 优雅关闭

前台运行时使用 Ctrl+C 停止 Gradio 进程；应用的 `finally` 会关闭 Qdrant 客户端和 SQLite 连接。停止 Qdrant 使用 Docker Desktop 或 `docker stop docqa-qdrant`，不要删除卷。SQLite 的 `-wal` 和 `-shm` 文件由 SQLite 管理，备份时必须使用一致性备份流程。

## 日志规则

日志只允许记录阶段、状态、耗时、重试次数、collection、document_id 和 request/session/turn 标识。禁止记录 API Key、Authorization、完整 `.env`、完整用户文档内容和未经脱敏的第三方异常。
