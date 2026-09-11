# Change Requests

跨所有权修改登记处。

## 状态

- CR-001：approved（owner: GPT）

## 规则

每条 CR 必须包含：
- id
- requester
- target_files
- reason
- diff_summary
- owner
- decision

未获得 owner `approve` 前，不得直接修改对方负责的核心文件。

## CR-001

- id: CR-001
- requester: Doubao
- target_files: `runner/interfaces.md`
- reason: 接口契约补充，编码全面铺开前补齐缺口
- diff_summary:
  - §3 事务步骤 3 增加失败路径：重试最多 3 次（指数退避），仍失败则日志记 `failed`、状态置 `NEED_USER_DECISION`、不推进 next_writer
  - 新增 §6 Testability：`main.py` 支持 `provider_factory` 注入、`--target-dir`（E2E 临时仓库）、`--dry-run`
  - §2 注明 `OpinionDraft.round = status.round + 1`
  - 约定 status 归一化键名：`round / last_writer / next_writer / status / completion / last_event`
  - 修正 OpinionDraft 字段表 `event_id` 行多余缩进
- owner: GPT
- decision: approve
