# 当前任务

## 当前状态

- 状态：`idle`；
- 当前活动任务：无；
- 当前分支：`main`；
- 最近完成：`DOC-001 文档治理与权威状态收口`；
- DOC-001 归档：[任务记录](../archive/task-cards/doc-001-document-governance.md)；
- 交付证据：[PR #1](https://github.com/wcnm8888/agent3-document-learning-assistant/pull/1)；
- 当前授权：仅等待负责人选择下一方向；不授权创建任务卡、修改代码、提交、推送、合并或部署。

## 当前产品事实

- PDF / Markdown 多文档解析、索引、问答、来源、会话、笔记、生命周期和知识库 UI 已完成；
- UI 高保真恢复已完成并获负责人视觉批准；
- 全量 pytest 当前基线为 95 项通过；
- Embedding 为 `text-embedding-v4` / 1024 维；
- collection 为 `docqa_text-embedding-v4_dim1024`；
- 当前为本地单用户；
- GitHub Actions / CI 未配置；
- 未部署。

## 已知风险

- Gradio `upload_progress?upload_id=undefined` 404 尚未真正修复；
- SQLite 与 Qdrant 删除采用补偿一致性；
- `pyproject.toml` description 仍为早期 Phase 2 文案；
- 真实生产故障和恢复演练未执行；
- 认证、多租户、Neo4j 和公网部署属于当前非目标。

## 下一步

负责人可从 [路线图](roadmap.md) 选择候选方向。选择前不得自动创建或执行下一张任务卡。
