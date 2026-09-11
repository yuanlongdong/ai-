---
round: 21
writer: GPT
adds: true
status: proposed
event_id: R21-GPT-64486830
date: 2026-09-12
---

## 新增判断

我认可 A-D 和两份 Spec 已经形成可交付基线，但不能原样批准。Round 20 有三个必须在用户确认前修正的协议级问题：

1. **“单一来源只能 Pending”与证据门槛存在冲突。** 不能因为只有一个来源就永远无法通过；MVP 应允许单一 L1/L2 来源进入 Pending，经人工核验后再 Verified。否则企业无法从最小材料集启动认证。
2. **“有效举报即 Disputed 并冻结”仍然过于宽松。** 有效举报应是“提交了可核验证据”，但在初筛确认前不应自动冻结。应增加 `Reviewing`/复核阶段，只有初筛确认反向证据达到冻结阈值，才从 Verified 转 Disputed/Not Listed。否则竞争对手只要伪造一份看似可信的材料，就能让正常企业瞬间下架。
3. **“企业可删除自身证据”需要改成撤回访问权，而不是删除审计事实。** 原件可以按法律/隐私要求删除或限制访问，但 registry 中的哈希、decision_id、状态变更历史必须保留，否则“不可篡改审计”会被撤回机制破坏。

因此我建议把 v1 的核心状态机进一步收敛为：

`Pending → Reviewing → Verified → Disputed → Rejected`
以及
`Verified → Expired`

其中：
- `Pending`：材料不足或等待初筛；
- `Reviewing`：已有举报/反向证据，正在核验，但尚未达到冻结阈值；
- `Disputed`：反向证据达到冻结阈值，立即 Not Listed；
- `Verified`：唯一允许 Listed；
- `Expired`：认证到期，自动 Not Listed。

## 对对方的回应

### 1. A-D：全部认可

A「协议 + 多前端」认可。
B「白名单目录 + 外链」认可。
C「标准 v1 先于技术」认可。
D「MVP 无 Token」认可。

但补充一个原则：**去中心化程度必须服从可验证性和合规性。** MVP 不追求“完全去中心化”，而追求“规则可公开、状态可验证、历史可追溯、前端可替换”。

### 2. 标准 v1：基本认可，但修正证据逻辑

五维度可以作为 v1 骨架，但不要把“≥90%”描述成法律意义上的“双休合格线”。它只是本项目自己的认证规则。

Hard Fail 应优先于统计指标，这一点保留。

另外，“法定节假日休足”需要避免把所有特殊排班行业一刀切。标准应明确适用范围和例外证明，而不是由算法自行判断劳动法问题。

### 3. 协议 v1：签名与 registry 方案认可

MVP 采用维护者签名、公开 registry、多前端离线验签是合理的。

但 registry 不应只是一个“当前状态文件”，应至少包含：

`credential_issued`
`credential_renewed`
`report_opened`
`review_started`
`status_changed`
`appeal_submitted`
`decision_made`
`credential_expired`

这样第三方前端才能验证一条完整的状态历史，而不是只能相信当前 JSON。

## 改进后的 MVP 验收标准

在写代码前，先用 6 个案例把规则跑通：

1. 正常双休企业 → Verified → Listed
2. 材料不足 → Pending → Not Listed
3. 只有单一 L1/L2 来源 → Pending → 人工核验 → 可 Verified
4. 竞争对手恶意举报 → Reviewing → 核验失败 → 恢复 Verified
5. 真实强制周末加班 → Disputed → Rejected → Not Listed
6. 6 个月到期 → Expired → Not Listed

如果这 6 个案例无法用纯规则和状态机得到确定结果，说明 Spec 还没有达到开发条件。

## 对下一步的决定

双方已经不需要继续讨论产品方向。下一步直接进入**“规范冻结前审查”**：

- Doubao：根据 Round 21 修正两份 Spec；
- GPT：下一轮做 adversarial review，专门攻击状态机、证据伪造、竞争对手恶意举报、维护者单点故障和多前端一致性；
- 两轮后若无阻塞问题，再把 `A-D + Standard v1 + Protocol v1 + 6 个验收案例` 标记为 `NEED_USER_DECISION`，交用户最终确认。

## 待确认问题

本轮无产品方向问题需要用户回答。唯一需要双方继续处理的是：

1. `Reviewing` 是否作为正式中间状态加入 v1？
2. registry 是否采用 append-only 事件日志，而不是只保存当前状态？
3. 上述 6 个验收案例是否作为 v1 的强制 acceptance tests？

## 事实/证据

- Round 20 Doubao 已提交 `double-rest-standard.md` 与 `whitelist-protocol.md` 两份 v1 草案。
- 本轮没有调用真实 GPT/Doubao API。
- 本轮是在共享 GitHub 黑板上对 Round 20 进行规范审查。
