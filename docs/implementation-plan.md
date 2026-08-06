# 当前实施计划

## 状态

- 当前没有获批准的活动任务；
- DOC-001 Step 0～7 已完成并归档；
- DOC-001 归档：[文档治理与权威状态收口](archive/task-cards/doc-001-document-governance.md)；
- 交付入口：[PR #1](https://github.com/wcnm8888/agent3-document-learning-assistant/pull/1)；
- 未部署。

## 下一任务建立规则

1. 负责人从 [路线图](project-management/roadmap.md) 选择候选方向；
2. 先建立独立任务卡，明确目标、范围、非目标、风险、阶段和完成定义；
3. 高风险数据、生产配置、认证、公网部署或真实 Qdrant 操作必须单独授权；
4. 实现前建立可复现测试与回退方案；
5. 通过功能分支、精确暂存、分批提交和 PR 交付；
6. 未获负责人批准不得自动开始下一任务。

## 当前质量基线

- 全量 pytest：95 项通过；
- `python -m compileall -q src tests`：通过；
- 当前文档本地相对链接检查：70 个，0 个失效；
- 高置信敏感信息扫描：0 个命中；
- GitHub Actions / CI：未配置。

## 保留边界

- 不自动修复 Gradio 上传进度 404；
- 不自动修改 Embedding、Qdrant collection、SQLite schema 或真实数据；
- 不自动添加认证、多租户、Neo4j 或公网部署；
- 不自动提交、推送、创建 PR、合并或部署。
