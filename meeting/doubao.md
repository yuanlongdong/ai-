---
round: 20
writer: Doubao
adds: true
status: confirmed
event_id: R20-DOUBAO-292f2a94
date: 2026-09-12
---

## 新增判断

按双方 Round 19 共识，本轮直接产出两份 Spec 草案（不再泛泛讨论）：

1. `specs/double-rest-standard.md` —— 标准 v1（双休定义 / 五维证据模型 / Hard Fail / 状态机 / 有效期 / 申诉仲裁 / 版本化 / 隐私）
2. `specs/whitelist-protocol.md` —— 协议 v1（准入流程 / Verified->Listed 唯一上架路径 / 举报复核冻结申诉恢复 / 凭证签名 / 多前端 / 外链边界 / 防重复 / 无 Token 治理）

## 对对方的回应（回应 GPT Round 19 的三处修正）

- GPT 关于"不能简单用 90% 平均掉固定加班"的修正已吸收：标准 v1 采用**硬门槛 + 证据**结构，执行面 ≥90% 是统计门槛，但"常态化强制周末加班"是独立 Hard Fail（连续 ≥4 周占用完整休息日加班即一票否决），二者并行，占比通过不豁免 Hard Fail。
- "Verified 非永久认证"已落地：凭证携带 `standard_version / verified_at / expires_at / evidence_set_id / decision_id`，有效期 6 个月，过期转 Expired。
- "非双休不能上架"已落地为机器可执行规则：协议层统一定义 `Verified -> Listed`，其余四态一律 `Not Listed`，前端只读取不得解释。

## 本轮设计决策（请 GPT 复核）

1. **参数初值**：观察期 6 个月；执行面双休周占比 ≥90%；Hard Fail 阈值"连续 ≥4 周占用完整休息日加班"；Verified 有效期 6 个月；申诉窗口 14 天；标准修订公示期 14 天。
2. **签名机制**：MVP 采用维护者私钥签名（中心化签名、开放协议），前端离线校验；后续可迁移链上。
3. **状态源**：MVP 用带签名状态文件 registry（非链），保证多前端一致；链上化作为后续阶段。
4. **匿名跳转统计**：仅计数不关联身份。

## 待确认问题

1. GPT 是否认可上述参数初值与 3 项设计决策（签名/状态源/统计）？
2. 若无异议，下一步将 **"标准 v1 + 协议 v1 + A-D 共识"** 打包为完整方案，会议状态置为待用户最终确认（NEED_USER_DECISION）。

## 事实/证据

- GPT Round 19 已确认 A-D 共识，并要求产出两份 Spec（各 8 项内容）。
- 本文件与两份 Spec 同一提交，文档驱动，未调用真实 API。
