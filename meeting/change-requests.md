# Change Requests

跨所有权修改登记处。

## 状态

当前无待审批 Change Request。

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
