# 工程基础规范（P0/P1/P2）

状态：P0 生效中；P1/P2 按里程碑落地。每条都有编号，`planning/standards.json` 记录落地状态，
`scripts/check-standards.py` 对可机器判定的条目给 PASS/FAIL（`python3 scripts/check-standards.py`）。

级别：**强制** = 违反即不得合并/不得发布；**建议** = 评审时说明理由可偏离。

## P0（现在生效）

| ID | 级别 | 条文 | 强制方式 |
| --- | --- | --- | --- |
| ES-01 | 强制 | **单位与量纲**：内部统一 长度 mm、力 N、应力 MPa、面积 mm²、惯性矩 mm⁴、角度 rad；仅在输入/输出边界转换；数值变量名带单位后缀（如 `spanMm`）或使用类型化封装 | 命名评审 + 单测（单位往返） |
| ES-02 | 强制 | **计算确定性**：`packages/**/src/**`（计算内核）禁止 `Date.now/Date/performance.now`、`Math.random/crypto.random`、`localeCompare`、依赖对象键序；浮点比较必须走容差函数 | `check-standards.py` 扫描 |
| ES-03 | 强制 | **数值输出契约**：打印位数与舍入在对齐规范后固定（对齐原版 `%.6f` 语义）；NaN/Inf 必须显式处理，不得静默吞掉 | 单测 + 差分样例 |
| ES-04 | 强制 | **纯函数内核**：计算/几何/报告为纯函数；IO、时钟、网络、日志只在 adapter/scripts 层 | 目录约定 + 评审 |
| ES-05 | 强制 | **命名政策**：新系统表面积只允许标准名；**旧产品名（XWall/HWKSoft/HWK 前缀等）不得出现在代码/UI/API/包名**；旧系统不规范命名按映射表规范化；旧名只许存在于 T2 适配层与 T3 证据层；不得据缩写猜含义（见 `naming-conventions.md` §5） | `check-standards.py` 扫描 + 映射表评审 |
| ES-06 | 强制 | **证据分级**：结论必须标 静态/反编译/实测/差分/未运行；`NOT_RUN` 不得表述为通过；无证据不得写 PASS | HANDOFF/VERIFICATION 模板 |
| ES-07 | 强制 | **资产只读**：`vendor/`、`evidence/` 原始件、`evidence/poc/*/input` fixture 只读；写入只到本轮工作目录或新的 evidence 子目录 | 哈希校验（`--full`） |
| ES-08 | 强制 | **远端操作 preflight**：先只读刷新会话/进程/哈希；只 `SELECT`；凭据不打印、不落日志 | 操作清单 + 独立复核 |
| ES-09 | 强制 | **交接规则**：状态栏 75% 触发 handoff；交接含 状态/证据/下一条命令/阻塞/决定 | HANDOFF 模板 |
| ES-10 | 强制 | **禁 `any` / `@ts-ignore`**：确需例外必须同行注释理由并被 allowlist 收录 | `check-standards.py` 扫描 |

## P1（MVP 前生效）

| ID | 级别 | 条文 | 强制方式 |
| --- | --- | --- | --- |
| ES-11 | 强制 | **测试四层**：单元（解析解）→ 契约（JSON Schema）→ 差分（原版/黄金样例）→ E2E（UI 冒烟）；`npm run check` 一键全跑 | `npm run check` |
| ES-12 | 强制 | **黄金样例库**：每个样例含 输入快照 + 期望值 + 容差 + 来源版本；新增/修改期望值需审批，禁止"改标准过关" | 目录结构 + 评审 |
| ES-13 | 强制 | **RulePack 规范**：schema 校验、语义化版本、生效区间、不可变；升级=新包+差异报告 | schema + 测试 |
| ES-14 | 强制 | **PDF/审计**：内容 hash、元数据（rulepack_fp/engine_version/figure_hashes/audit_id）、字体嵌入、签章占位、归档格式 | 模板 + 断言 |
| ES-15 | 强制 | **依赖与许可证**：白名单；DWG 等商业 SDK 需法务确认；禁止 GPL 进产品 | 依赖清单评审 |
| ES-16 | 强制 | **代码规范**：`strict` + `oxlint` 规则集固化；单文件行数、函数复杂度上限 | tsc + oxlint |
| ES-17 | 强制 | **ADR 流程**：架构/选型决策写 `docs/adr/NNNN-*.md`；`decisions.md` 只留索引 | 目录 + 评审 |
| ES-18 | 强制 | **提交与评审**：小步单主题；评审清单（正确性/确定性/证据/测试）；Definition of Done | 评审清单 |
| ES-19 | 强制 | **日志分层**：业务审计（谁/何时/规则包/图）与运行日志分离；不落 PII/口令 | 代码评审 |

## P2（发布前）

| ID | 级别 | 条文 |
| --- | --- | --- |
| ES-20 | 强制 | **三版本号**：引擎 / 规则包 / PDF 模板独立编号，结果记录三者 |
| ES-21 | 强制 | **运维基线**：健康检查、备份恢复演练、容量与告警、回滚 |
| ES-22 | 强制 | **安全基线**：AD 组→角色最小权限矩阵、审计留存期、密钥/证书管理 |

## Definition of Done（任何一项"完成"必须同时满足）

1. 自动化回归：`python3 scripts/check-standards.py` 与 `cd replica && npm run check` 均 exit 0；
2. 原版对照证据（数值/文本/文件之一）+ 证据级别标注；
3. 文档同步：受影响规范/规格/台账已更新；
4. 无新增 `NOT_RUN` 项被表述为通过；
5. HANDOFF 写明下一条命令与阻塞。

## 偏离流程

需偏离强制条目时：在 PR/交接里写 ①条目号 ②理由 ③补偿措施 ④失效日期，并在 `planning/standards.json`
记 `DEVIATION`（不得写成 ENFORCED）。
