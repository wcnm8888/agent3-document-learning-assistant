# 交付收口清单

> 本清单前部针对原单 PDF 项目的 Phase 6～8 交付基线；当前多文档任务的活动状态以 `docs/project-management/current-task.md`、`roadmap.md` 和 `implementation-plan.md` 为准。多文档任务卡 Phase 2～6 已完成；Gradio 上传进度 404 仍为非阻塞依赖风险。

## 多文档与 Markdown 任务 Phase 6 收口

- [x] 任务卡、路线图、进度、证据、实现计划和 README 状态已统一。
- [x] 全量 pytest 67 项通过。
- [x] compileall、`git diff --check`、敏感信息扫描通过。
- [x] Qdrant healthz HTTP 200；v4 collection 267 points、1024 维；PDF/Markdown document_id 隔离。
- [x] v4 point 来源元数据完整，未混用 v3 或测试向量。
- [x] SQLite integrity check 通过。
- [x] 未部署、未提交、未推送、未创建 PR；这些操作需负责人单独确认。
- [ ] Gradio 上传进度 404 尚未在依赖升级环境中消除，保留为非阻塞风险。

## 后续方向执行状态（2026-08-01）

- [x] 方向 A 已完成隔离调查并保留 5.50.0 稳定版本；404 未伪装为已修复。
- [x] 方向 B 规格、架构边界、实现和临时存储测试已完成；真实生产删除操作未执行。
- [x] 方向 C 搜索、筛选、排序、详情和错误展示已实现并完成 UI 回归。
- [ ] Git P0、提交、推送、PR、部署、认证、多租户和公网部署均未执行。

## Phase 6 状态（历史基线）

- [x] v3/v4 使用同一份 30 题评测集。
- [x] v3 collection 与 v4 collection 隔离。
- [x] v4 评测前后保持 262 points、1024 维、来源元数据完整。
- [x] 生成 JSON 原始结果和 Markdown 报告。
- [x] 全量自动化测试 38 项通过。
- [x] 结果与文档未发现密钥模式。
- [x] DeepSeek 空响应已增加有限重试策略并通过测试。
- [x] 30 题逐题证据复核已记录，结果见 `eval/results/embedding-v3-v4-manual-review.md`。
- [x] q023–q028 的严格文档范围政策已由项目负责人确认，不再作为 `uncertain` 项。
- [x] Phase 6 质量门禁全部通过；本轮仍不执行部署、发布、提交或推送。

当前建议默认模型：`text-embedding-v4`。
## 原单 PDF 项目最新收口状态（历史基线，2026-07-31）

- [x] DeepSeek 空响应有限重试已实现并有测试。
- [x] q011 真实验证成功。
- [x] 最新完整 v3/v4 评测无失败题。
- [x] v3/v4 collection 隔离、维度和 point 数量通过检查。
- [x] 逐题证据复核文件已生成。
- [x] q016–q017 许可证事实题均召回并引用 PDF 第 4 页。
- [x] q023–q028 严格文档范围政策已由项目负责人确认。
- [x] 项目负责人已完成最终人工确认，Phase 6 收口完成。
- [ ] 尚未执行部署、发布、提交或推送。

## 原单 PDF 项目 Phase 7 交付准备状态（历史基线）

- [x] 已检查 Git 基线；当前工作区保留用户已有未提交修改，本阶段不提交。
- [x] 已统一 `docs/implementation-plan.md` 中 Phase 6 的历史状态。
- [x] 已完成 local/test/production 配置边界和密钥管理规则。
- [x] 已完成 Qdrant、SQLite、文档和评测结果备份恢复设计。
- [x] 已完成启动顺序、healthz、有限重试、优雅关闭、排障和回滚设计。
- [x] 已评估本地 Python、Qdrant-only Compose 和应用容器化；当前推荐本地 Python + Docker Qdrant。
- [x] 已完成日志、指标、错误追踪和成本监控字段设计。
- [x] README、`.env.example`、部署/运维文档已补齐。
- [ ] 实际部署、发布、公网暴露、提交和推送：本阶段明确不执行。

## 原单 PDF 项目 Phase 7 阻塞条件（历史基线）

- Docker Desktop Linux Engine 的历史连接问题已解除；当前已通过 Qdrant healthz，后续运行仍必须先执行健康检查。
- 应用暂无独立健康端点；在补齐认证、访问控制、Secret Manager、持久化恢复演练和多实例存储前，不得作为公网生产服务。

## 原单 PDF 项目 Phase 8 本地运行时状态（历史基线）

- [x] Docker Desktop 已恢复，`docqa-qdrant` healthz 返回 HTTP 200。
- [x] v3/v4 collection 均为 green、262 points、1024 维。
- [x] 新增 Qdrant-only `docker-compose.local.yml`，不增加应用容器；HTTP healthz 由 `health` CLI 验证。
- [x] 新增 `health` CLI，失败时返回非零退出码且不输出密钥。
- [x] 新增 `backup-sqlite` CLI，备份后执行完整性检查。
- [x] 新增 7 项 Phase 8 定向测试。
- [x] 真实 `.env` health CLI、v4 collection smoke test 和 SQLite 备份恢复均已通过。
- [x] Phase 8 最终全量质量门禁和任务文档收口完成。
- [x] 未执行生产部署、公网暴露、提交或推送。
