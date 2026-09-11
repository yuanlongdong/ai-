# 双休企业商品白名单协议 v1（Whitelist Protocol v1）

> 状态：草案（Doubao 起草，Round 20；Round 22 按 GPT Round 21 审查修正：Reviewing 阶段、append-only 事件日志、举报不自动冻结；待 GPT adversarial review 后交用户确认）
> 定位：定义"谁能上架、如何上架、如何下架、多前端如何读取"。
> 一句话产品定义：**一个开放的双休企业商品白名单协议——企业通过可验证的双休标准获得 Verified 凭证进入公开白名单；任何前端都可以读取这份准入状态。**
> 配套：`specs/double-rest-standard.md`｜会议：`meeting/doubao.md` Round 16-20

## 1. 企业准入流程

```
申请 → 提交材料（制度面/执行面/节假日证据/来源证据）
  → 规则引擎自动初筛（完整性 + Hard Fail 预检）
  → 人工复核（验证员，证据核验）
  → 状态结果：Verified / Pending / Rejected
  → 仅 Verified 进入目录（Listed）
```

申请主体 = 法律主体（营业执照主体）；重复申请自动合并（见 §7）。

## 2. `Verified -> Listed` 唯一上架路径

目录条目 = `{entity_id, product_ref, verified_credential, listed_at}`。

**唯一规则：**
- `Verified`（且未过期）→ `Listed`
- `Pending / Disputed / Rejected / Expired` → `Not Listed`
- `Reviewing` → **维持原准入状态**（来自 Verified 仍 Listed 但展示"复核中"标记；来自 Pending 则 Not Listed），直到转为 Disputed 才冻结

该规则由**协议层统一定义**，前端只读取状态、不得自行解释。

## 3. 举报、复核、冻结、申诉、恢复流程

**举报分级：**

| 举报类型 | 条件 | 效果 |
|---|---|---|
| 普通线索 | 无新证据 | 仅标记"复核中"，**不改准入** |
| 有效举报 | 附可核验新证据 | 进入 **Reviewing** 核验；初筛确认前**不冻结** |
| 冻结 | 初筛确认反向证据达冻结阈值 | 转 **Disputed**，立即 Not Listed |
| 确证违规 | 复核确认 | Rejected |

**关键语义**：有效举报不等于立即下架——竞争对手伪造一份看似可信的材料也不能瞬间冻结正常企业；只有初筛确认反向证据达到冻结阈值，才从 Reviewing 转 Disputed。

**防滥用：**
- 举报人信誉影响举报权重；重复恶意举报 → 举报资格受限；
- 恶意举报不直接扣币/扣 Token（MVP 无 Token），通过信誉降级约束。

**申诉与恢复：**
- 企业 14 天窗口申诉（须附新证据）→ 复核；
- 复核通过 → 恢复 Verified（新 decision_id）；失败 → 维持 Rejected。

## 4. 凭证字段与签名验证

`verified_credential`：

```
{
  entity_id,            // 法律主体唯一标识（哈希化）
  standard_version,     // 判定的标准版本
  verified_at,
  expires_at,
  evidence_set_id,
  decision_id,
  status,               // Verified
  signature
}
```

- 签名：MVP 由协议维护者私钥签名（中心化签名、开放协议）；前端**离线校验**签名与有效期；
- 签名无效 / 过期 / 版本不符 → 前端应展示为不可信状态。

## 5. 多前端读取规则

- **唯一状态源**：registry，采用 **append-only 事件日志**（不是只保存当前状态的 JSON 文件）；
- 事件类型至少包含：

```
credential_issued      // 发证
credential_renewed     // 续期
report_opened          // 举报受理
review_started         // 复核开始
status_changed         // 状态变更
appeal_submitted       // 申诉提交
decision_made          // 判定作出
credential_expired     // 认证过期
```

- 前端：读取事件日志 → 本地重放得出当前状态 → 校验签名 → 渲染；第三方可验证**完整状态历史**，而非只信任当前快照；
- MVP 实现：带签名的 append-only 文件（每次追加签名）；后续可迁移链上。

## 6. 外链跳转边界

- 目录条目携带 `product_ref`（外部商品 URL/ID）；
- 跳转 URL 携带准入标记：`?dl=verified&entity=<id>&sig=<signature>`；
- **平台不参与订单/支付/售后/资金托管**，不采集用户交易数据；
- 可选：匿名跳转统计（仅计数，不关联身份），为未来闭环积累行为数据。

## 7. 防重复企业/商品与状态同步

- `entity_id` = 营业执照主体的规范标识（统一社会信用代码哈希化）；重复申报自动合并，保留最早 evidence_set 与最新状态；
- 同一商品多主体供货：按生产主体分别判定，不允许以"品牌总部 Verified"覆盖代工厂；
- **状态同步以 registry 为唯一权威**；任何前端缓存不得成为事实源。

## 8. 无 Token 的 MVP 治理方式

- **验证员**：初期由维护者邀请 + 社区申请，人工复核兜底；
- **信誉值**：举报/复核行为累积信誉分；用于举报权重与复核优先级；恶意行为降级；**不形成可交易金融资产**；
- **治理决策**（标准修订、规则变更）：提案 + 公示 ≥14 天 + 维护者/社区确认，无经济激励；
- **未来**：验证真实社区规模与攻击模型后，再评估是否引入经济机制（届时走标准/协议版本化流程）。

## 9. 验收案例（v1 强制 acceptance tests）

与标准 v1 §9 一致的 6 个强制场景，必须以纯规则 + 状态机得出确定结果：

1. 正常双休企业 → Verified → Listed
2. 材料不足 → Pending → Not Listed
3. 单一 L1/L2 来源 → Pending → 人工核验通过 → Verified（可 Listed）
4. 竞争对手恶意举报 → Reviewing → 核验失败 → 恢复 Verified（期间不冻结、不下架）
5. 真实强制周末加班（Hard Fail）→ Reviewing → Disputed → Rejected → Not Listed
6. 6 个月到期未复核 → Expired → Not Listed

---

*本文件为 v1 草案，流程参数（窗口期/公示期/签名机制）均可在复核中调整。*
