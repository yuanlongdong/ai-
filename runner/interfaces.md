# Runner Interfaces v0.2

## 1. Provider contract

Provider 只负责调用对应模型并返回标准化 `OpinionDraft`，不得直接写入会议状态文件。

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

`OpinionDraft.round = status.round + 1`。
`event_id = R<round>-<writer>-<sha8>`；`sha8` 为正文（front matter 之后）的 SHA-256 前 8 位。

## 3. Runner transaction

一次 Runner turn 必须：
1. 读取 context / 双方观点 / status
2. 校验 `next_writer`
3. 调用 Provider
4. 校验 OpinionDraft
5. 计算 event_id 并检查幂等
6. 原子提交观点、状态、日志
7. 校验提交后的状态机
8. 成功后 push；失败则按 §4 处理

Provider 调用或草稿校验失败时最多重试 3 次（指数退避）。仍失败则记录 `failed`，状态置 `NEED_USER_DECISION`，保持 round 与 next_writer 不推进，不留下半写状态。

## 4. State keys

状态键统一为：`round / last_writer / next_writer / status / completion / last_event`。

`need_user_decision` 与事务失败均不推进 round / next_writer。

## 5. Ownership / Change Request

- GPT：state / github / main / validate / openai provider
- Doubao：doubao provider / trigger / logging / CI
- 集成、对抗、E2E：Doubao
- 单元测试：随模块归属
- 跨所有权修改必须先登记 `meeting/change-requests.md` 并获 owner 批准。

## 6. Testability

`main.py` 支持 `provider_factory` 注入；E2E 支持 `--target-dir` 临时仓库与 `--dry-run`。

## 7. Push / concurrency

成功事务必须 push 到共享仓库。push 前应检测远端推进；发生非快进时不得强推，应重新读取最新黑板并重试事务。
