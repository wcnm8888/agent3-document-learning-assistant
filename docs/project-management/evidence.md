# Phase 0/1 证据

## 仓库

- 项目工作目录：`E:\Agent\开发实践\Agent3-智能文档问答助手`
- 上游源码目录：`E:\Agent\hello-agents-upstream`
- 获取方式：通过 Git 获取 Datawhale `hello-agents` 的 main 分支。
- 项目目录将建立独立的本地 Git 基线，不与上游仓库共享 Git 历史。

## 基准 PDF

- 文件：`data/reference/Happy-LLM-0727.pdf`
- 页数：171
- 文本提取：成功
- 质量观察：部分页面抽取文本出现重复字符，需要在文档转换阶段验证标题、代码和表格保真度。

## 代码定位

- `code/chapter8/11_Q&A_Assistant.py`：示例助手和 Gradio UI。
- 示例通过 `MemoryTool.run` 和 `RAGTool.run` 调用能力。
- 文档说明中部分示例使用 `execute`，与当前代码存在接口表述差异，需以后以安装包实际 API 为准。

## 未执行

- 尚未安装依赖。
- 尚未连接 DeepSeek、百炼、Qdrant 或 Neo4j。
- 尚未运行第八章示例。
- 尚未宣称任何真实问答或 UI 验收通过。
