# 命名规范

配套：`docs/engineering-standards.md` ES-05、`planning/naming-observations.json`（原名/证据/未知台账）。

总原则：**代码标识用英文；显示名与规范文本用数据；不据缩写猜含义；旧产品名不进新系统；旧的不规范命名必须规范化（见 §5）。**

## 0. 产品名（T0）

| 项 | 值 |
| --- | --- |
| 产品名 | **FORCITIS-x**（显示写法，全大写词干 + 小写后缀） |
| 技术标识 | `forcitis-x`（包名、可执行文件、日志前缀、环境变量前缀 `FORCITIS_`） |
| npm scope | `@forcitis-x/*` |
| 报告页眉/落款 | `FORCITIS-x` |
| 中文显示名 | 待定 |
| 状态 | 已定名（D24）；商标/域名可用性 **未核查** |

规则：产品名只出现在 T0；领域标识与数据 ID 与产品名解耦，改名不影响它们。旧品牌字样仍按 §5.2 禁用。

## 1. 代码标识

| 对象 | 规则 | 例 |
| --- | --- | --- |
| 包 | `kebab-case`，按能力命名 | `packages/section`、`packages/geometry`、`packages/rulepack` |
| 类型/接口 | `PascalCase`，名词；无 `I` 前缀 | `SectionProperties`、`RulePack` |
| 函数 | `camelCase`，动词开头；纯函数不带 `do/handle` | `sectionProperties()`、`interpolate()` |
| 常量 | `UPPER_SNAKE`；物理量带单位 | `TOLERANCE_REL`、`MM_PER_M` |
| 数值变量 | 带单位后缀，杜绝裸 `length/width` | `spanMm`、`ixMm4`、`areaMm2`、`thetaRad` |
| 布尔 | `is/has/can/should` 前缀 | `isBlocked`、`hasOutlines` |
| 文件 | `kebab-case.ts`；测试 `*.test.ts`；CLI `*.mts` | `section-properties.test.ts` |

**禁止**：`data/info/item/tmp` 之类无语义名；拼音缩写（`lmb`、`jgm`）；把中文当标识符；
为"看起来新"而改旧名（旧名兼容层优先）。

## 2. 显示名与规范文本

| 内容 | 存放位置 | 规则 |
| --- | --- | --- |
| UI 标签、报告文案、条文号 | 资源/数据文件（RulePack、locale 文件） | 与代码标识**分离**；保留原版措辞（含已知缺陷，如 μ 标"表6.1.3"） |
| 规范编号 | RulePack 字段 | 用原编号（`JGJ102-2003 6.1.2-1`），不改写 |
| 单位符号 | 报告模板 | 原版形式（`N/mm2`、`kN/m2`）照抄，不"美化" |

## 3. 数据与文件 ID

| 对象 | 格式 | 说明 |
| --- | --- | --- |
| 实体 ID | `PREFIX-uuidv7`（如 `PRJ-`、`SCH-`、`CASE-`） | 时间有序，便于排序/分片 |
| RulePack | `规范号@版本`，如 `JGJ102-2003@1.0.0` | 不可变；修订=新版本号 |
| Figure | `FIG-<ordinal>-<type>`，如 `FIG-014-deflection` | 报告内序号稳定 |
| Deviation | `DEV-<yyyymmdd>-<seq>` | 与差异台账一一对应 |
| 证据文件 | `evidence/<阶段>/<卡号>/<attempt>/<动作>.<ext>` | 动作名英文短横线 |

## 4. 版本号

三类独立语义化版本，任何结果必须记录三者：`engine`、`rulepack`、`pdfTemplate`。
不把三者揉成一个"产品版本号"。

## 5. 旧系统名称与产品名政策（用户 2026-10-21 决定）

**总则：旧系统的产品名不得进入新系统；旧系统不规范的命名必须规范化。**

### 5.1 四层划分（决定一个旧名字能不能出现在哪里）

| 层 | 允许出现的内容 | 例子 |
| --- | --- | --- |
| **T0 新系统表面积**（代码标识、UI、品牌、包名、API、日志、报告文案） | **只允许标准名**；出现旧产品名即违规 | `sectionProperties`、`DeflectionCoefficient`、`ProjectContext` |
| **T1 领域标识**（规范/条文/单位/构件类型） | 用标准领域名；条文号与规范编号保持官方写法 | `momentCoefficient`、`JGJ102-2003 6.1.2-1` |
| **T2 兼容适配层**（导入器、`.cwx` 读写、旧 DB 适配、RulePack 来源引用） | 允许旧标识，但**必须集中**在 `packages/legacy-adapter`（规划）/`scripts/poc`，并逐条登记映射 | `HWKWallContext`、`型材参数表`、`GetSDr` |
| **T3 证据与文档**（evidence/、migration_workspace/、ADR 引用） | 保留原名，供追溯 | `HWKCADGraphArc`、`IZ/WZ1` |

### 5.2 禁止的产品名（出现在 T0 即 FAIL）

`XWall`、`HWKSoft`、`HWK`（作为品牌/前缀）、`HWKWall*`、`HWKCalc*`、`HWKCAD*`、`HWKWin*`、`HWKAlu*`、
以及旧安装目录名、旧窗口标题、旧公司名。新系统对外只用自己的产品名（待定，另行决定）。

### 5.3 必须规范化的命名类别

| 旧形态 | 问题 | 新系统标准做法 |
| --- | --- | --- |
| `GetSDr` / `GetSMr` / `GetNg` | 缩写不可释义 | 用领域语义名：`deflectionCoefficient` / `momentCoefficient` / `reductionFactor` |
| `Hw` / `Bw` / `al` / `bl` / `awl` | 单位与含义不明 | `longEdgeMm` / `shortEdgeMm` / `calcSpanMm` |
| `IZ/IY/WZ1/WZ2/SZ/SY/JA` | 单字母 + 下标数字 | `ixMm4` / `iyMm4` / `wxTopMm3` / `wxBottomMm3` / `staticMomentMm3` / `torsionConstantMm4` |
| `dflim` / `DWLESS` / `FWLESS` | 拼写与含义混叠 | `deflectionLimitMm` / `isDeflectionOk` / `isStrengthOk` |
| `IsLPeak` / `ISHOLW` / `ISDOUBLEW` | 标志位全大写 | `isLoadPeak` / `hasHollowGlass` / `isDoubleGlazing` |
| `HWK*` 类名前缀 | 品牌前缀进入领域模型 | 去掉前缀，用领域词（`ProjectContext`、`CalcCase`） |

### 5.4 映射表（逐步补全）

权威映射登记在 `planning/naming-observations.json`（每条加 `canonical_name` 与 `layer`）。
首���必须补齐的映射（已有证据）：

| 旧名 | 标准名（待审） | 依据 |
| --- | --- | --- |
| `GetSDr` | `deflectionCoefficient` | `coefficient-tables.md`（μ = f(a/b)） |
| `GetSMr` | `momentCoefficient` | 同上（m = f(a/b)） |
| `GetNg` | `reductionFactor` | `lookup-tables.md`（η = f(θ)） |
| `HWKWallContext` | `ProjectContext` | `.cwx` 根记录实测 |
| `.cwx` | `legacyProjectFile` | `cwx-format.md`（仅导入/证据，不再是新系统存储格式） |

### 5.5 兼容边界

- 旧名**只允许**出现在 T2 适配层与 T3 证据层；适配层必须**单向**（读旧写新），不得把旧名泄漏到新模型。
- 适配层的旧名必须来自映射表，不允许散落硬编码。
- 改名不得改变可观测行为：报告文案里的**规范条文号**照旧，产品名不出现。

## 6. 评审检查点

- 新增标识符是否通过"英文 + 单位 + 语义"三问？
- 是否又把中文文案写进代码？
- 是否引入了未登记的原版名称？
- 是否为了改名而破坏兼容边界？
