# UI 视觉基线夹具

`ui_visual_baseline.py` 只用于浏览器视觉验收。它启动真实 Gradio 应用和真实 SQLite 会话、来源、笔记回调，但在现有 QA 服务边界使用确定性替身，从而不需要 API Key，也不会连接生产 SQLite 或删除真实 Qdrant points。

运行：

```powershell
.\.venv\Scripts\python.exe tests\fixtures\ui_visual_baseline.py --port 7865
```

运行数据写入 `output/ui-visual-baseline-runtime/` 下的临时目录，进程结束后自动清理。固定页面状态和截图步骤见 `docs/assets/ui-visual-baseline/README.md`。
