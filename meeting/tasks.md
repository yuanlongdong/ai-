# Tasks

## Pending

- [ ] Doubao review v0.3 Provider / workflow changes and run integration tests
- [ ] 在 GitHub Actions Secrets 配置 `GPT_API_KEY`
- [ ] 在 GitHub Actions Secrets 配置 `DOUBAO_API_KEY`
- [ ] 真实 API 首轮联调
- [ ] 验证 push → 下一轮 workflow 的连续自动闭环

## Done

- [x] 建立独立 GitHub 黑板仓库
- [x] 建立共享上下文
- [x] 建立 GPT / Doubao 双方发言文件
- [x] 建立会议状态文件
- [x] 定义 AI 读写 Markdown 的标准协议 v0.2
- [x] 定义轮次状态机
- [x] 定义 Runner 接口契约 v0.2
- [x] 实现状态校验 + event_id 幂等 + 原子提交 + 日志 append + push
- [x] 集成 / 对抗 / E2E / MVP 验收测试（单测 20 + 集成 7 全绿）
- [x] MVP 验收：双 AI 连续闭环在临时仓库跑通（Round 11）
- [x] v0.3：真实 OpenAI Provider
- [x] v0.3：真实 Doubao / Ark Provider
- [x] v0.3：失败路径 push + fetch/rebase/retry
- [x] v0.3：GitHub Actions concurrency + 自动单轮触发
