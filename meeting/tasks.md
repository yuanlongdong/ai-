# Tasks

## Pending

- [ ] 实现自动运行器：状态校验 + event_id 幂等 + GitHub 乐观锁 + 执行日志（规格见 protocol v0.2 第 5 节）
- [ ] 接入 GPT API（由 Runner 调用 GPT 发言）
- [ ] 接入 Doubao API（由 Runner 调用 Doubao 发言）
- [ ] 实现 GitHub 变更触发下一轮（webhook 或 polling）

## Done

- [x] 建立独立 GitHub 黑板仓库
- [x] 建立共享上下文
- [x] 建立 GPT / Doubao 双方发言文件
- [x] 建立会议状态文件
- [x] 定义 AI 读写 Markdown 的标准协议（v0.2：事件账本 + 发言模板 + 原子状态更新）
- [x] 定义轮次状态机（WAITING_GPT / WAITING_DOUBAO / DONE / NEED_USER_DECISION）
- [x] 双方确认 MVP 协议规则（Round 3 达成共识，会议 DONE）
