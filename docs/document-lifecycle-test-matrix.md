# 文档生命周期测试矩阵

本矩阵是 [测试策略](testing-strategy.md) 的领域附录。最近记录的项目全量基线为 95 项通过；具体 case 数以 pytest 实际收集和执行结果为准。

| 编号 | 风险 / 行为 | 层级 | 预期证据 |
|---|---|---|---|
| LC-001 | indexed 归档不删 points | 服务 / 集成 | 状态为 archived，point count 不变，默认可用范围排除 |
| LC-002 | archived 取消归档 | 服务 / 集成 | 状态恢复 indexed，仍使用原 document_id |
| LC-003 | 删除必须确认 | 服务 / UI | 未确认不改 SQLite / Qdrant |
| LC-004 | 只按 document_id 删除 | 集成 | 同名或其他文档 points 不受影响 |
| LC-005 | 删除成功 | 集成 | 目标 points 为 0，SQLite 保留 deleted tombstone |
| LC-006 | Qdrant 删除失败回退 | 服务 | 原 indexed / archived 状态和计数保持或明确 inconsistent |
| LC-007 | SQLite 最终提交失败 | 故障注入 | 不伪造 deleted，状态和操作日志可恢复 |
| LC-008 | 删除前存在笔记、引用和会话 | 集成 | 历史记录保留，新的无效关联被拒绝 |
| LC-009 | deleted 同内容重新导入 | 服务 | 返回 tombstone / 显式恢复要求，不新增业务身份 |
| LC-010 | 源文件缺失时恢复 | 服务 | 不进入 indexed，返回可定位错误 |
| LC-011 | 重新索引 | 集成 | 只重建目标 document_id points，计数一致 |
| LC-012 | 一致性检查 | 服务 / 集成 | indexed、archived、deleted、inconsistent 结果正确 |
| LC-013 | document_id 隔离 | 回归 | 删除 / 恢复不改变其他文档问答范围 |
| LC-014 | 产品全量回归 | 回归 | 全量 pytest 通过；最近记录基线为 95 项 |

## 数据边界

所有生命周期测试必须使用临时 SQLite 和内存/临时 Qdrant 或安全替身。禁止读取、删除或重建真实 collection、真实 SQLite 和真实 points。

## 额外门禁

- PDF 页码与 Markdown 章节/段落/行号保持原语义；
- 错误信息脱敏；
- 删除失败不得显示成功；
- 浏览器危险操作必须有确认文字；
- 真实生产删除和恢复演练未执行时必须明确记录。
