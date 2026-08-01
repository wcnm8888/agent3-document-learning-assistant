# 文档生命周期测试矩阵

| 编号 | 风险/行为 | 层级 | 预期证据 |
| --- | --- | --- | --- |
| LC-001 | indexed 归档不删 points | 服务/集成 | 状态 archived，point count 不变，默认检索排除 |
| LC-002 | archived 恢复 | 服务/集成 | 状态 indexed，仍使用原 document_id |
| LC-003 | 删除必须确认 | 服务/UI | 未确认不改 SQLite/Qdrant |
| LC-004 | 只按 document_id 删除 | 集成 | 同名文档 points 不受影响 |
| LC-005 | 删除成功 | 集成 | points=0，SQLite 保留 deleted tombstone |
| LC-006 | Qdrant 删除失败回滚 | 服务 | 原 indexed/archived 状态和计数保持不变 |
| LC-007 | SQLite 最终提交失败 | 故障注入 | 不伪造 deleted，状态为 deleting/inconsistent，可恢复 |
| LC-008 | 删除前有笔记/引用/会话 | 集成 | 历史记录保留；新关联被拒绝 |
| LC-009 | deleted 同内容重导入 | 服务 | 返回 tombstone/显式恢复要求，不新增记录 |
| LC-010 | 源文件缺失恢复 | 服务 | 不进入 indexed，给出可定位错误 |
| LC-011 | 重新索引 | 集成 | 临时 Qdrant 只产生该 document_id 的 points，计数一致 |
| LC-012 | 一致性检查 | 服务/集成 | indexed/archived/deleted/inconsistent 四类结果正确 |
| LC-013 | 会话与 document_id 隔离 | 回归 | 删除/恢复不改变其他文档问答范围 |
| LC-014 | 原有 67 项回归 | 回归 | 全量测试通过 |

## 数据边界

所有 LC 测试必须使用 `tmp_path` 下的 SQLite 和 Qdrant local path；禁止读取、删除或重建真实 v4 collection、真实 SQLite 和真实 points。
