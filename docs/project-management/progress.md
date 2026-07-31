# 项目进度

## 当前状态

Phase 0/1 已形成初稿，等待用户审阅；业务实现尚未开始。

## 已完成

- 通过 Git 获取上游源码到独立参考目录 `E:\Agent\hello-agents-upstream`。
- 在 `E:\Agent\开发实践\Agent3-智能文档问答助手` 建立干净应用目录，保留项目文档、评测材料和基准 PDF。
- 检查基准 PDF：171 页，可提取文本；部分页面存在字符提取异常。
- 定位第八章示例：`code/chapter8/11_Q&A_Assistant.py`。
- 确认示例使用 `MemoryTool`、`RAGTool` 和 Gradio。
- 确认仓库根目录没有统一 `pyproject.toml`、`requirements.txt` 或 `hello_agents` 包源码。
- 准备 `data/reference/` 和 `eval/`。

## 下一步

用户确认 Phase 0/1 文档后，建立隔离 Python 环境，核对 PyPI 包版本和 DeepSeek/百炼适配器，再开始 Phase 2。
