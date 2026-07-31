# 当前任务

状态：ready_for_review

项目工作目录：`E:\Agent\开发实践\Agent3-智能文档问答助手`

## 任务

完成智能文档学习助手的 Phase 0/1：仓库审计、产品范围、架构、UI 规格、测试矩阵、Embedding 选型方案和评测材料准备。

## 已知输入

- 上游仓库：`E:\Agent\hello-agents-upstream`，Git 分支 `main`。
- 基准文档：`data/reference/Happy-LLM-0727.pdf`。
- LLM 候选：DeepSeek API。
- Embedding 默认候选：阿里云百炼 `text-embedding-v4`，1024 维。
- Embedding 备用候选：`text-embedding-v3`。

## 本阶段禁止

- 不修改业务代码、依赖、Schema 或生产配置。
- 不启动外部数据库，不写入真实 API 数据。
- 不提交、推送或创建 PR（Phase 0/1 期间）；应用目录的首次本地 Git 提交作为项目基线单独完成。

## 阶段验收

- 已确认仓库是教程/示例仓库，运行包来自外部 PyPI。
- 已确认第八章示例入口和当前示例的主要边界。
- 已形成架构、UI、测试和 v3/v4 对比方案。
- 已准备基准 PDF 和评测问题集结构。
