# Runner Interfaces v0.1

## 1. Provider contract

Provider 只负责调用对应模型并返回标准化 `OpinionDraft`，不得直接写 `status.md`、`tasks.md` 或其他会议状态文件。

```text
generate_opinion(context, counterpart_view, status) -> OpinionDraft
```

## 2. OpinionDraft

```text
round: int
writer: GPT | Doubao
adds: bool
status: proposed | confirmed | need_user_decision
 event_id: string
date: YYYY-MM-DD
facts_evidence: string
new_judgment: string
counterpart_response: string
improvement_plan: string
open_questions: string
```

`event_id = R<round>-<writer>-<sha8>`；`sha8` 为正文（front matter 之后）的 SHA-256 前 8 位。

## 3. Runner transaction

一次 Runner turn 必须按以下顺序完成：

1. 读取 context / 双方观点 / status
2. 校验 `next_writer`
3. 调用对应 Provider
4. 校验 OpinionDraft
5. 计算 event_id 并检查幂等
6. 原子提交观点、状态、日志
7. 校验提交后的状态机
8. 触发下一轮或结束

## 4. Ownership

- GPT：state / github / main / validate / openai provider
- Doubao：doubao provider / trigger / logging / CI
- 集成、对抗、E2E：Doubao
- 单元测试：随模块归属

## 5. Change Request

跨所有权修改必须先在 `meeting/change-requests.md` 登记并获得文件所有者批准。
