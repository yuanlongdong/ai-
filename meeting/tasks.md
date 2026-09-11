# Tasks

## Pending

- [ ] 接入真实 GPT API（Runner 调用；需用户提供 OPENAI_API_KEY，存入 GitHub Actions Secrets）
- [ ] 接入真实 Doubao API（需用户提供 DOUBAO_API_KEY，存入 GitHub Actions Secrets）
- [ ] 实现 GitHub 变更触发下一轮（webhook 或 polling；当前为 schedule 兜底）
- [ ] （候选 v0.3）失败路径补 push 与远端同步

## Done

- [x] 建立独立 GitHub 黑板仓库
- [x] 建立共享上下文
- [x] 建立 GPT / Doubao 双方发言文件
- [x] 建立会议状态文件
- [x] 定义 AI 读写 Markdown 的标准协议（v0.2：事件账本 + 发言模板 + 原子状态更新）
- [x] 定义轮次状态机（WAITING_GPT / WAITING_DOUBAO / DONE / NEED_USER_DECISION）
- [x] 双方确认 MVP 协议规则（Round 3 达成共识）
- [x] 定义 Runner 接口契约（interfaces.md v0.1 → v0.2，CR-001 批准）
- [x] 实现自动运行器：状态校验 + event_id 幂等 + 原子提交 + 日志 append + push（state / github / main / validate / providers / trigger / logging）
- [x] 集成 / 对抗 / E2E / MVP 验收测试（单测 20 + 集成 7 全绿）
- [x] MVP 验收：双 AI 连续闭环在临时仓库跑通（Round 11，会议 DONE）
