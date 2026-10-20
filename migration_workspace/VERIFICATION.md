# 验证台账（哪些结论已 PASS、哪些仍是 PARTIAL）

口径：`PASS` = 有可复现的交叉验证或实测；`PARTIAL` = 单源静态证据；`NOT_RUN` = 未验证。
每条给出可复核的命令或文件。

---

## A. 已 PASS（有交叉验证）

| # | 结论 | 验证方式 | 结果 |
| --- | --- | --- | --- |
| A1 | 安装包 458 条目 / 506.6 MB / 139 PE | MSI `File` 表 ↔ CAB 成员 ↔ 实际字节数三方对齐 | 一致 |
| A2 | `.cwx` 是类型标签对象图，根 `HWKWallContext` | 头部字节实测 + 15 个样例类型抽取 | 216 种类型 |
| A3 | `.cwx` 的 216 种类型 ⊆ 二进制类表 | 合并 **81 个模块 / 4,979 个类** 后比对：覆盖 **209/216 = 96.8%** | 见下 A3 备注 |
| A4 | 公式库为 GBK 明文（非加密） | 2,079 条按 cp936 解码，可打印率 >80% 的 **2,077（99.9%）** | 成立 |
| A5 | 计算引擎 = `HWKSciCal.dll`，被 12 个模块导入 | 导入表实测 | 成立 |
| A6 | 379 个节点 = 379 个类 = 379 个互不相同的 `eval` | vtable 槽 8 与基类逐槽比对 | 379/379 |
| A7 | 注册表存原型对象、取用时 clone | `functionFactory` 反编译（`ev_b27a76d7…`） | 成立 |
| A8 | `setName` 的 bool = 是否入字典 | 反编译（`ev_66eb0fe5…`）+ 380 条注册全为 true | 成立 |
| A9 | `CalGlassDisp = ms×qwk×aw⁴÷dw×theta×1e9` | 反编译（`ev_9910259c…`） | 成立 |
| A10 | 节点内含时间+概率许可校验（≈1/89） | 反编译 + 常数 `89.0` 与 `(int)(f*89)==44` 一致 | 成立 |
| A11 | 玻璃挠度体系模板的节点调用面可判定：25 条模板、555 处调用，434 命中 379 注册名，39 处为可变参数节点，**真正形参个数不一致 0** | 生成脚本 + 自检脚本对 `formulas.json`/`cxmap-*`/`raw/nodes` 交叉核对 | 成立 |
| A12 | 玻璃挠度模块的模板算术与原版打印的中间量逐位一致：te 7.18155 / D 2314912.5 / θ 5.221494 / μ 0.00406 / η 0.998228 / df 1.750738；μ、η 均由解出的轴表算出，不再当外部输入 | 冻结样例计算书原文（`frozen-report-head.txt`）+ `scripts/check-module-numeric.py glass-disp` | 成立 |
| A13 | 玻璃面板强度模块全链与原版打印值逐位一致：q1/q2/qk1/qk2 0.919618/0.836016/0.55/0.5、m 0.0442、θ1/θ2 5.894204/5.358368、η1/η2 0.992846/0.997133、σ1/σ2 6.726054/6.140995（最大差 3.9e-7） | 冻结样例计算书原文 + `scripts/check-module-numeric.py glass-stress` | 成立 |
| A14 | 查表节点读的静态表布局已解（`[double count][count × double]`），三套 η 表已提取，锚点 η(5.221494)=0.998228048 与原版打印 0.998228 一致 | `scripts/extract-lookup-table.py` 直接解析 PE .data 并与报告文本对照 | 成立 |
| A19 | `.cwx` 记录的**字段顺序**可解：`Serialize` 链（自身写 + 基类调用位置）叠加出有序字段表，`HWKWallContext` 根按链走 `b.cwx` 载荷，三个单字段差分锚点全部落在预测偏移上——`+0x14` double 0.4（城市基本雪压，对象 `+0x98`）、`+0x1c` 10 字符串"各种样式栏杆计算样例"（工程名称，`+0xa0`）、`+0x56` double 0.45（城市基本风压，`+0x110`） | `scripts/build-serialize-chains.py --root HWKWallContext --cwx b.cwx`（13 个根、412 个 `Serialize`、3/3 锚点） | 成立 |
| A15 | `Serialize` 字段布局可机械读取：模式（`this+0xc` 版本门 + `operator<</>>`）已在 `HWKCalc_GlassBase` 上用反汇编实证；本模块 412 个 `Serialize` 中玻璃族 10 个已提取偏移/宽度/阈值 | REA(Ghidra 12.1.4) 反编译 + `scripts/extract-serialize-fields.py` objdump 解析 | 成立 |
| A16 | `GetSDr`/`GetSMr`（`FUN_1802a0fa0`/`FUN_1802a2940`）的语义闭合：读 `$0..$3` → 归一化成边长比 → 按 `$2`（材料代码）/`$3`（支承代码）选一对内嵌轴表 → 共享插值器 `FUN_180299d50`；23 条分支（含常数返回与 ratio 变形特例）逐条转录 | 反编译原文逐句对照 + `scripts/extract-coefficient-tables.py`（分支模型写进 `raw/coefficient-tables.json`） | 成立 |
| A17 | 两个节点引用的 38 个去重轴地址全部按 `[double count][count × double]` 解析成功（count ∈ {11,13,15,16}），2 参路径与代码路径在 a/b=1 上给出原版打印的 μ=0.00406 / m=0.0442（4 个锚点） | `scripts/extract-coefficient-tables.py` 直接解 PE `.data`，对照计算书原文 | 成立（推翻 B10 旧负面结论） |
| A18 | 外片应力 6.726054 闭合：θ1=5.894204（原文打印）→ η 表 0.992846 → `6×m×q1×a²×1000/t1²×η1` = 6.726053902（差 9.8e-8）；原文同时打印了 η1，旧记录所称"未打印"不成立 | `scripts/check-module-numeric.py glass-stress` + η 三锚点 | 成立（推翻 B9 旧结论） |

### A3 备注（残差已定位）
7 个未在导出表中的类型全部是 `HWKCADGraph*`。字节扫描显示它们以 RTTI/序列化字符串形式存在于
`HWKCAD.dll`、`HWUtil*.arx/grx/zrx`、`XWall.exe`、`HWKGraphModelLib.dll`、`HWKKernal.dll`，
但**没有以 `@HWKCADGraphXxx@@` 形式导出**。结论：归属可解释，不等于缺证据。

---

## B. PARTIAL（单源，需第二来源）

| # | 结论 | 缺什么 |
| --- | --- | --- |
| B1 | 74 个体系 / 19 大类 | 与幕墙类别码表（40 行）只对上 39 行，`TYPEID` 语义未明 |
| B2 | 379 个节点的参数名表 | **已更正**：`$0/$1` 是可变参数节点的**位置参数名**（143 个节点），不是噪声；`Come Here N` 与错误提示串才是噪声。参数抽取已修（4 行内被 `look_string` 使用），378/379 已产出 |
| B3 | 数据库 85 表 / 708 列 | 结构完整，但**字段单位与含义未验证**（`E=72000`、`midu=25.6` 均为推测） |
| B4 | 模板函数 263 个中 88 个是节点 | 其余 175 个（运算符/绘图/表格/FE 数据）未逐一归属 |
| B5 | 公式内联链可切分为单元（1,665 式 → 12,176 候选） | 输入识别有噪声（如 `μzcal` 被误判为外部输入） |
| B6 | `.cwx` 持久化了 107 种 `HWKCalc_*` 结果 | **字段布局未解**，因此"能读回结果"未验证 |

---

| B7 | 模板层与节点层是**两套并行实现**：玻璃四个算量节点（`CalGlassDisp`/`CalGlassPSDisp`/`CalGlassStress`/`CalGlassPSStress`）在 2,079 条模板里被调用 **0** 次；379 个注册节点中有 **293 个**从未被模板调用 | 谁在运行时驱动哪一套、二者数值是否恒等（需实机差分），未取证 |
| B8 | 玻璃算量节点（`CalGlassDisp` 等）**由谁在运行时调用**仍未知：2,079 条模板调用 0 次，现有反编译产物中除注册点与构造函数外无引用 | 需要更大反编译面或实机观察；模板算术已证明与原版数值逐位一致，故不影响功能等价结论 |
| B9 | ~~玻璃面板强度模块：外片应力 6.726054 未复算（原文未打印 η1）~~ **已闭合，见 A18**；仍留：`CalGlassStress`/`CalGlassPSStress` 模板调用 0 次，运行时驱动者未知 | 外片数值已复算；节点调用方需更大反编译面 |
| B10 | ~~μ/m 查表不是 η 那种自描述轴表~~ **已闭合，见 A16/A17**（38/38 地址解析成功，4 锚点命中；旧"19/22 失败"未能复现）；仍留：`$2/$3` 代码语义只证到 `11`=铝板族、`0/1/2`=PRJGLASS、`4`/`6`=支承；`GetSMr` 的 `$3∈{20,25,30}` 细分表无打印锚点 | 需要石材/铝板样例计算书才能给这三个分支加锚点 |
| B11 | ~~`.cwx` 字段顺序需沿基类链叠加~~ **顺序与类型已解并验证（A19）**：`HWKWallContext` 前 13 个字段与原版字节逐字段对齐。仍留：①记录边界（`u32 A` 语义）未知，只能按 tag 扫描定位；②聚合类型统一按 `u32+UTF-16` 解析，遇数组/嵌套对象漂移；③412 个类只验证 1 个根；④字段**语义**只证到 5 个（雪压/风压/工程名称/城市/粗糙度类别） | 需要逐类与真实记录对齐，并解出 `A` 与聚合槽位的细分类 |

## C. NOT_RUN（未开始或需实机）

| # | 项 | 依赖 |
| --- | --- | --- |
| C1 | 数值对照（同输入 → 原版结果 vs 公式复算） | 实机运行 |
| C2 | 中间量对照（μz/μf/βgz 级） | 实机运行 + 单元契约 |
| C3 | `.cwx` 字段布局与往返 | 反编译各类 `Serialize` |
| C4 | 计算书逐字段一致性 | 实机导出报告 |
| C5 | FE 求解链（114 个 `FEAdd*` + `HWKFeUtil`/`Structmodule`） | 反编译（批次中） |
| C6 | 依赖扰动实验（改一个输入，验证依赖图） | 实机运行 + 单元图 |

---

## D. 验证基础设施（可复用）

| 用途 | 命令 |
| --- | --- |
| 重生成安装包清点 | `python3 scripts/summarize-install-package.py --vendor <dir> --out ... --json ...` |
| 重生成体系清单 | `python3 scripts/summarize-calculation-systems.py --install ... --cab ... --out ...` |
| 重解码公式库 | `python3 scripts/decode-formulas.py --hex ... --out-json ... --out-md ...` |
| 重算节点 vtable | `python3 scripts/extract-node-vtables.py --bindings ... --dll ... --sci ...` |
| 批量节点摘要 | `python3 scripts/batch-node-dossier.py --family <名> --pattern <正则>` |
| 单元切分 | `python3 scripts/split-formula-units.py --formulas ... --out ...` |
| `.cwx` 类型清点 | `python3 scripts/analyze-cwx.py <install-package.json> --cab <dir> --out ...` |

---

## E. 下一步验证顺序（按信息量/成本）

1. **C3 `.cwx` 字段布局** —— 解出后可直接做 C1/C2 的离线版本（文件里同时有输入和结果）
2. **C5 FE 链** —— 批次已在跑，补人工复核
3. **B1 码表语义** —— 查 `TYPEID` 的取值来源（可能在 `幕墙类别码表` 之外还有映射）
4. **B2 参数清洗** —— 用构造函数参数表交叉校验自动抽取
5. **C1/C2/C4/C6** —— 实机实验，按 `L8-实机验证清单.md` 执行

---

## F. 本轮新增验证结果（`.cwx` 跨源一致性）

生成器 `scripts/cwx-crosscheck.py`，结果 `cwx-crosscheck.md` / `raw/cwx-crosscheck.json`。

| 检查 | 口径 | 结果 |
| --- | --- | --- |
| C1 类型 ⊆ 二进制类表（4,979 类） | 体系名属数据定义、`HWKCADGraph*` 为已知 RTTI-only 例外 | **全通过** |
| C2 `HWKSchema_*` ⊆ 74 体系清单 | `HWKSchemaCalcInfo` 为通用信息类，不参与 | **全通过** |
| C3 每个工程声明体系 | — | 有类型的 9 个全部有体系 |

**结论：9 PASS / 6 N/A / 0 FAIL。**

### 新发现：`.cwx` 有两种格式

6 个 N/A 全是"优化类"工程（`玻璃组合优化`、`线材优化例子`、`铝板优化`、
`线材组合优化例子`、`线材优化示例1`、`玻璃优化示例`）——**里面没有任何 `HWK*` 类型名**，
说明它们用的不是 `CbArchive` 序列化，而是另一套格式（很可能是优化的数据文件）。

→ 对重构的影响：**文件兼容不是"一种格式"，至少两种**。优化类工程要单独取证。

### 检查器自身的两轮修正（记录在案）

1. 首轮 0/15 PASS：把体系名当 C++ 类、把 `HWKSchemaCalcInfo` 当体系 → **检查定义错，不是数据错**
2. 次轮 5/15：`HWKSOFTTHERMEND__________` 是结束哨兵，被当成类型 → 已排除
3. 终轮 9 PASS + 6 N/A + 0 FAIL

这条过程本身说明：**验证跑出 FAIL 时，先怀疑检查定义，再怀疑数据**。

---

## G. 更正记录（2026-10-18 收口）

### G1 `$0/$1` 不是 Ghidra 占位符，是应用自己的位置参数名

早前把 `$0`/`$1` 当噪声过滤掉，导致 153 个节点显示"参数数为 0"。实测：

| 事实 | 值 |
| --- | --- |
| 含 `$N` 字面量并用于 `look_string` 的节点 | **143 个** |
| `$0` 出现节点数 | 143 |
| `$1` / `$2` / `$3` | 73 / 26 / 2 |

这些是 `CXMapVariableArguments` 风格的可变参数节点，**位置参数就叫 `$0`、`$1`**。真噪声只剩两类：
`Come Here N`（Ghidra 未解析跳转标记）与嵌入的错误提示文案（`loadcase is empty! ...`）。

### G2 全量批次结果（378/379）

| 指标 | 值 |
| --- | --- |
| 已反编译节点 | 378（1 个 provider 失败可重试） |
| 不同算术核心 | 328 |
| 复用组 | 31 组 / 覆盖 81 个节点 |
| 最大复用组 | FE 建/删模型各 7 个节点（仅模型类型不同） |

结论：**FE 建模/删除高度模板化（可收敛成通用接口）；业务计算节点基本独立（≈87%）**。

### G3 方法教训

两次"验证跑出异常"的根因都是**我的判定规则**，不是数据：
1. 跨源一致性首轮 0/15 → 检查定义把体系名当 C++ 类
2. 参数数 153 个为零 → 过滤规则把应用自己的 `$N` 当噪声

→ 规则化结论：**任何"异常值"先做一次"规则是否误判"的复核，再写进结论。**

## L5 / A 路线三步（2026-10-19）

| 步骤 | 状态 | 证据 |
| --- | --- | --- |
| 辅助函数反编译与分类（31 个 `FUN_*`） | PASS | `raw/helpers/*.rea.json`（31 份）、`raw/helpers.json` |
| 节点算式抽取（379 个） | PARTIAL | `nodes-expr.md`、`raw/nodes-expr.json`：`EXPR` 51 / `SELECTED` 1 / `TABLE_LOOKUP` 14 / `INTERPOLATION` 4 / `STRING_TABLE` 3 / `TABLE_BUILDER` 2 / `FE_OP` 13 / `EXTERNAL_CALL` 0 / `PARTIAL` 31 / `NO_ARITH` 260 |
| 节点头分类（379 个） | PASS（分类层面） | `node-kinds.md`、`raw/node-kinds.json`，`UNKNOWN`=0 |
| 补最后一个节点 `FEDelCBProb` | PASS | `raw/nodes/FEDelCBProb.rea.json`（`eval=0x1800b6eb0`） |
| 收尾待办清单 | PASS | `nodes-residual.md`、`raw/nodes-residual.json`（36 条，含未绑定符号与其赋值来源） |
| 辅助函数查表提取 | PASS | `helper-tables.md`、`raw/helper-tables.json`（11 个函数：条件 + 常量） |
| 辅助函数定性分类 | PASS | `raw/helpers.json`：`INTERPOLATE` 1、`STRING_TABLE` 3、`TABLE_BUILDER` 3、`NODE_CTOR` 4（节点构造函数，非取值）、`GLOBAL_GETTER` 1、`RNG` 1、`ARITH` 6、`OTHER` 16 |
| 节点结构描述 | PASS | `node-descriptions.md`、`raw/node-descriptions.json`（379 个节点） |
| `FUN_180251270` 性质 | PASS（假设证伪） | 它是 `GetAVmax` 构造函数，非代理取参 → 已用 `numeric_block()` 限定分析范围 |

自检：`CalGlassDisp` 抽取结果与 `calculation-core.md` §9 人工核对结论逐字一致；
`extract-node-expr.py` 与 `classify-node-kind.py` 各复跑一次，`counts` 完全一致（幂等）。

未闭合：`PARTIAL` 39 个（7 个 ARITH 辅助函数未内联）、9 个 ARITH 节点抽不出步骤、
283 个非算术节点缺逐节点文字说明。**单位/规范/物理含义仍为未知**，不得由结构反推。

## 计算链回归断言（2026-10-19）

`replica/scripts/test-calc-chains.py`（`python3` 直跑，退出码即结论），当前 **7 项全通过**：

| # | 断言 | 依据 |
| --- | --- | --- |
| 1–3 | 玻璃自重 `GSAK` 三条分支：6/12/18 mm → 0.1536 / 0.3072 / 0.4608 kN/m² | `WWEIGHT` 原文 + DB ρ=25.6 |
| 4 | 风荷载 B 区 80 m → `Wk≈1.338` | `WLS` 原文 + `GetKk`/`GetBgzcal` 反编译常量 |
| 5 | 同例 `βgz≈1.528` | 同上 |
| 6 | `CalGlassDisp` 算式与人工核对结论**逐字一致** | `calculation-core.md` §9 |
| 7 | `CalGlassDisp` 状态为 `EXPR` | `nodes-expr.json` |

第 6 条是防回归的关键：此前我给抽取器加"括号整理"时把
`((qwk * ms * (pow(aw,4.0))) / dw) * theta * 1e9` 改成了语义不同的分组，靠这条断言才被抓住。

写这条测试时还踩了一个自己的坑：解析 `calc-wind` 输出时按空格切列，把标签里的数字（`α2=2α=0.32`）
当成了数值列，导致 2 项假失败 → 改为从行尾倒取 5 个数。这条也说明：**断言本身也要能被证伪**。
