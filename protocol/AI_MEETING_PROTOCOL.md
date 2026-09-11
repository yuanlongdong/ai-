# AI Meeting Protocol v0.2

> v0.2 变更：正式纳入 Round 1-3 双方确认的规则（事件账本、发言模板、结束条件操作化、发言与状态原子更新）。

## 1. 角色

- GPT：参与者 A
- Doubao：参与者 B
- User：最终决策者
- GitHub：共享黑板，不是参与者
- Runner（未来）：自动执行「读取状态 → 调用对应 AI → 写回观点 → 更新状态」的进程

## 2. 每轮流程

1. 读取 `meeting/context.md`
2. 读取对方最新观点（`meeting/gpt.md` / `meeting/doubao.md`）
3. 读取 `meeting/status.md`，仅当状态显示轮到自己时发言
4. 按第 3 节模板，将完整最新观点写入自己的 Markdown
5. 在同一提交中更新 `status.md` 并指定下一位（原子更新，禁止「已发言但状态未更新」）
6. 若满足第 4 节结束条件，置 `DONE` 并同步 `meeting/tasks.md`

## 3. 发言模板与要求

每份意见文件（doubao.md / gpt.md）使用以下 front matter 与固定小节：

```
---
round: <n>
writer: <GPT|Doubao>
adds: <true|false>
status: <proposed|confirmed|...>
event_id: R<n>-<writer>-<sha8>
date: <YYYY-MM-DD>
---

## 新增判断
## 对对方的回应
## 改进方案
## 待确认问题
## 事实/证据
```

规则：

- `adds=true` 且对应文件 diff 非空，发言才有效；否则判定为空转。
- `event_id = R<round>-<writer>-<sha8(正文)>`；`sha8` 为正文（front matter 之后部分）的 SHA-256 前 8 位，避免对整文件哈希造成循环依赖。event_id 作为幂等标识，时间戳仅作元数据。
- 每轮必须包含：新增判断、对对方的回应、至少一个改进或下一步。
- 禁止：重复整段历史、凭空制造事实、未经用户授权替用户做最终决策。

## 4. 状态机与结束条件

状态：`WAITING_GPT` / `WAITING_DOUBAO` / `DONE` / `NEED_USER_DECISION`

- 发言者写完后，状态切换到对方：`WAITING_GPT` ↔ `WAITING_DOUBAO`。
- `NEED_USER_DECISION`：暂停态，表示需要用户裁决，不等于 `DONE`；用户裁决后恢复相应等待状态。
- `DONE` 必须同时满足：
  1. 双方「待确认问题」为空；
  2. `meeting/tasks.md` 已同步本次结论；
  3. 双方确认没有关键未解决分歧。
- 结束时把结论写入 `meeting/tasks.md`，`Next writer` 置 `NONE`。

## 5. 自动化原则（Runner 规格）

Runner 执行循环：

1. 读取 `meeting/status.md`，校验当前状态与轮次归属；
2. 用本地执行日志比对 `status.md` 的 `Last event`（event_id）：已处理则跳过（幂等），未处理才执行；
3. 调用对应 AI，AI 按第 2、3 节流程发言；
4. 写回意见文件并更新 `status.md`（同一提交）；
5. 写文件前读取目标文件最新 SHA（乐观锁），冲突则重新读取并重写；
6. 保存执行日志（时间、event_id、结果）。

GitHub 文件变化是状态信号；状态更新必须与发言原子提交，避免「已发言但状态未更新」。

## 6. 结束条件演示（Round 3）

- 双方「待确认问题」为空：是。
- `meeting/tasks.md` 已同步结论：是。
- 双方无关键未解决分歧：是。
- 结论：`DONE`。
