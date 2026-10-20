# 主计划：彻底搞清楚 XWall（HWK）计算工具

状态：**进行中**。本文件是本轮"彻底搞清楚"的作业总纲，随证据变化更新。
所有结论遵守项目约定：静态证据分级标注；未验证的一律 `NOT_RUN`；不猜缩写含义；
`vendor/` 只读；不运行未授权的原版程序路径。

---

## 0. "彻底搞清楚"的可验收定义

不能靠"读了很多代码"结案。以下 8 层各自有可判定的闭合条件：

| # | 层 | 闭合条件 |
| --- | --- | --- |
| L1 | 安装包与分发 | 458 个 MSI File 条目 + 顶层产物 + 必备件全部有名、有哈希、有落点 |
| L2 | 产品级计算体系清单 | 体系数、大类、每体系的构件类清单，全部来自安装包声明 |
| L3 | 代码模块与依赖 | 每个 PE 的真实名、导出数、依赖方向；无"未知模块" |
| L4 | 计算引擎机制 | 注册、名字解析、求值、符号模式、数值取用路径可复述 |
| L5 | 节点语义 | 379 个 CXMap 节点的参名表 + 算术/逻辑表达式 |
| L6 | 有限元求解链路 | 单元类型、刚度组装、荷载、约束、求解器、后处理入口 |
| L7 | 数据层（材料/型材/规范） | 数据文件或数据库的表/字段/单位被解析出来 |
| L8 | 数值对照 | 至少一条业务链在原版与新实现上同输入同输出（需 B02 环境） |

**当前整体：L1 ≈90%，L2 已闭合，L3 ≈95%，L4 已闭合，L5 定位 100% / 算式 13%（EXPR 51，余已分类），L6 0%，L7 **数据已可读**（85 表 / 207,105 行导出；2082 条公式 GBK 解码并与 379 注册名对齐：81 个函数命中），L8 0%。**

---

## 1. 已闭合的事实（含证据文件）

| 事实 | 数值 | 证据 |
| --- | --- | --- |
| MSI File 条目 / 总大小 | 458 / 506.6 MB | `migration_workspace/install-package.md` |
| 顶层产物 | 9 项（含 CAB 142.5 MB、MSI 1.8 MB、SQL LocalDB 40 MB、两版 VC 运行库） | 同上，现场哈希 |
| 安装布局 | `XWallClient` 83 个 + `X64` 40 个 + `X86` 29 个 + `示例` 56 个 + `Support` 118 个 + `SchemaData` 74 个 | 同上 |
| **产品级计算体系** | **74 个体系 / 19 个大类** | `migration_workspace/calculation-systems.md`（源：`Support/HWKSchemaList.xml`） |
| 体系大类分布 | 幕墙 24、雨蓬 14、框架幕墙 4、采光顶 4、热工U值 4、栏杆/平面结构/百叶/格栅 各 3、压型屋面板 2、吊顶 2、其余 9 类各 1 | 同上 |
| 构件类引用 | 157 个不同 `ClassName`，929 次引用；单体系类数中位 12，最多 66（`HWKSchema_SingleCalc`） | 同上 |
| 计算引擎模块 | `HWKSciCal.dll`（605 导出，被 12 个模块导入） | `calculation-core.md` §1–2 |
| 名字注册 | 379 个字面量名 + 1 个运行期拼名；`CXMap::setName(name,bool,dict)`，bool=是否入字典 | §3、§7.2 |
| 注册入口 | `XYUtil::InitNewFunction(CXInterpreter*)`：time 播种 → `SwitchDictMap` → 批量 setName | §3 |
| 节点类层 | 379 个类，379 个 vftable，**379 个互不相同的 eval**（零复用） | §8、`node-vtables.md` |
| 求值机制 | `evalParams` → 树（对象 `+0x38`）→ `isConstant` → `$$__noEvaluateFunctions` 符号回退 | §7.3 |
| 首个节点算法 | `CalGlassDisp = ms × qwk × aw⁴ ÷ dw × theta × 1e9`；随机许可校验约 1/89 概率 | §9 |
| 原始源码目录 | `f:\hwkxwallu\xwall\{hwkscical,hwkwallutil,hwkkernal}\` | §7.5 |

## 2. 已确认的硬约束（替代方案必须遵守）

1. 379 个名字 = 379 个独立 `eval`，不存在"通用节点 + 配置表"的捷径。
2. 注册表存的是**可克隆的原型对象**，不是构造函数指针（`functionFactory` 查字典后调 `copy()`）。
3. 同一套节点**既能算数值也能保持符号表达式**（`$$__noEvaluateFunctions`）。
4. 名字在入库前被 `stripWhiteSpaces` 规范化。
5. 计算节点内存在**时间 + 概率驱动**的许可校验（`GetHMMxValue`），不影响返回值但影响可复现性观测。
6. `Support/*.xdf`（106 个）是**加密/压缩二进制**，材料与型材数据层目前不可读。

## 3. 未闭合层与下一步（按优先级）

### P0 — 数据层（L7）：`XWallTem.mdf` / `XWall.mdf`
- 现象：UTF-16 扫描只得到系统目录名（`sysusers`/`systypes`）与少量列名（`midu`/`fyk`/`fstk`/`mm0`），
  **无中文表名**，说明 schema 命名是英文/拼音。
- 下一步：写 MDF 页解析器（`sysallocunits` → `sysschobjs` 取对象名，`syscolpars` 取列），
  或改用 B02 环境的 SQL LocalDB 挂载只读副本。**优先做前者**（不需要 Windows）。

### P1 — 节点语义（L5）：379 个 eval 逐个取证
- 已有：全部 eval 地址（`node-vtables.md`）、阅读模板（`calculation-core.md` §9.1）。
- 成本实测：单函数反编译约 76 秒（缓存后复用）；机器码总量 561.5 KB，展开约 2 MB 伪代码。
- 策略：按体系族分批（玻璃 6、Check 2、Do 8、Calc 4、Venetian 37、FE 114…），
  每批产出 `migration_workspace/nodes/<族>.md`，只记录"参名表 + 表达式 + 常数 + 分支条件"。

### P2 — 有限元链路（L6）：`hwkwallutil\fe*.cpp` 对应实现
- 入口：`FEAdd*` 114 个命名条目 + `HWKFeUtil.dll`（1873 导出）+ `Structmodule.dll`（8205 导出）。
- 先做接口表（条目名 → 构造实现 → eval），再挑 1 个单元（如 `fedoplanestressanalysis`）走通。

### P3 — 数值对照（L8）：需 B02 原版环境
- 素材已就位：15 个 `.cwx` 示例工程（41.1 MB，含"各种栏杆样例"）。
- 做法：同一示例在同一台机器重算，抓中间量与报告值，与 §9 公式的人工复算比对。

### P4 — L1/L3 收尾
- `setup.exe` 与 MSI 的引导关系、`豪沃克修复工具.exe`/快捷卸载的动作、MSI Feature 树、
  注册表写入、COM/服务注册、字体安装顺序、卸载清理。
- 5 个清单引用但无文件的 schema（`CeilingFrame2D`/`CompMetalPlate`/`LPEAK_DualSlope`/`MetalPlate`/`UGLASS`）需查明是大小写还是缺件。

## 4. 已知风险与红线

- **加密狗**：`CXMapDongdong` + `GetHMMxValue` 在计算路径上；禁止在未授权环境尝试绕过，只做静态记录。
- **不可复现风险**：时间播种 RNG 影响的是外部调用次数，不是数值；报告时不得混淆。
- **证据分级**：反编译结果标注 `DECOMP + evidence_id`，字符串扫描标注 `STRING`，导出/导入标注表名来源。
- **不猜语义**：`Kuz`/`LGA`/`VPLG`/`PS` 等缩写，未取得释义前一律留空。
- **不改台帐**：其他卡（B02 UI 等）的脚本与证据不动；本线程只写 `migration_workspace/` 与新增取证脚本。

## 5. 交付物与生成脚本

| 交付物 | 生成脚本 |
| --- | --- |
| `migration_workspace/install-package.md` | `scripts/summarize-install-package.py` |
| `migration_workspace/calculation-systems.md` | `scripts/summarize-calculation-systems.py` |
| `migration_workspace/calculation-core.md` | 人工整理（引用下列脚本产物） |
| `migration_workspace/node-vtables.md` | `scripts/extract-node-vtables.py` |
| `migration_workspace/cxmap-entries.md` / `cxmap-bindings.md` | `scripts/extract-cxmap-entries.py` / `-bindings.py` |
| 单函数取证包 `migration_workspace/*.md` + `raw/*.rea.json` | `scripts/extract-function-dossier.py` |

## 6. 续接说明

- 上下文接近上限或压缩时：先读本文件 → 读 `HANDOFF.md` 的本轮小节 → 按 P0–P4 继续。
- 原始 REA/Ghidra Evidence 全部在 `migration_workspace/raw/*.rea.json`，可通过 `evidence_id` 复核。
- `GHIDRA_INSTALL_DIR=~/tools/ghidra_12.1.4_PUBLIC`（arm64 自建反编译器，见 `docs/decisions.md` D13）。
- 反编译缓存：`migration_workspace/.cache/snap-*`（复用可免去每次 76 秒导入分析）。

---

## 7. 解析工具链（已配置并验证）

| 能力 | 工具 | 位置 / 验证 |
| --- | --- | --- |
| 反编译 x64 PE（x86 亦可） | Ghidra 12.1.4 + REA 6.7.0 | `GHIDRA_INSTALL_DIR=~/tools/ghidra_12.1.4_PUBLIC`；`rea doctor --provider ghidra` 9/9 |
| 反汇编/符号解析 | Apple `objdump` | 直接读 PE，`# 0x... <符号>` 注释可用 |
| PE 结构（导出/导入/.pdata/节） | 自研 `scripts/extract-function-dossier.py`（`PE` 类，纯 stdlib） | 已用于 102 个模块清点 |
| 字节级 Python 扩展 | `.venv`：`capstone 5.0.7`、`pefile`、`pycryptodome` | `migration_workspace/.venv` |
| CAB / MSI 解包 | `7z 17.05` + 既有 `evidence/baseline/b01/msi-decoded` | `file-map.json` 提供哈希名→真实名 |
| MDF 页扫描 | 新增 `scripts/mdf-scan.py` | 见下 |
| 证据存档与缓存 | `migration_workspace/raw/*.rea.json`、`.cache/snap-*` | 按 `evidence_id` 可复核 |

## 8. 数据层（L7）第一轮实测

### 8.1 数据库访问路径已确定（`DECOMP`/`STATIC` 既有证据）

`evidence/baseline/b01/datainfo/decoded.json` 解出的 `hwksoftconfig.ini` 内含 17 条连接模板，
形如：

```
Provider=SQLNCLI11.1;Integrated Security=SSPI;Persist Security Info=False;
Data Source=(localdb)13.0;Initial Catalog=;Initial File Name=%s;...
```

- 判定：数据库通过 **SQL Server LocalDB + SQLNCLI11.1 OLE DB** 访问，`Initial File Name=%s`
  表示**按工程/库文件直接附加 MDF**。
- 佐证：139 个 PE 里**没有任何** ODBC/OLEDB/SqlClient 静态导入，也搜不到明文 SQL——
  说明走 COM ProgID 动态加载，静态文本不可得。
- 结论：`.mdf` 就是数据本体（`XWall.mdf` 141 MB、`userglazing.mdf` 37 MB、`XWallTem.mdf` 11 MB）。

### 8.2 页级扫描结果（`scripts/mdf-scan.py`，`_42F2479F…` = `XWallTem.mdf`）

| 指标 | 值 |
| --- | --- |
| 页数 | 1416（8192 字节/页） |
| 页类型分布 | data 818、index 158、pfs 136、text 99、sort 4、gam/sgam/boot/fileheader 各 1、未识别 4 |
| 可解析槽表的数据/索引页 | 190 |
| 未解析 | 786（启发式未通过自校验） |
| 行内标识符 | 184 个 |

**关键信号**：行内出现 `GLUESTRENGTH`、`GLUESTRENGTHRIB`、`POLEPRECALCJD`、`POLEHARDNESS`、
`WDISPLACEMENTJD`、`SBOARDSTRENGTH51` 这类全大写键名——与引擎里 `WDISPLACEMENT`
（`HWKCalc_GlassDisp::Solve` 用的属性键）**同一命名体系**。

→ 判断（待验证）：**计算参数与公式键存储在 SQL 库里**，键名与引擎属性键同构。
这条把 L5（节点语义）与 L7（数据层）连了起来：节点的输入不仅来自用户输入，也来自库里的参数表。

### 8.3 下一步（L7 收口）

1. 写真实的 SQL Server 分配链解析（`sysallocunits` → `sysschobjs`/`syscolpars`），
   把覆盖率从 19% 提到接近 100%，拿到**表名 + 列名 + 类型**；当前启发式只够发现键名。
2. 用列名反推单位与量纲（`midu`=密度、`fyk` 等拼音列名需要对照）。
3. 把库里的键名与 379 个节点参数名（`ms/qwk/aw/dw/theta`）做交集，验证 §9.1 的输入来源假设。

---

## 9. L7 实机突破（2026-10-18，只读）

### 9.1 访问路径（已验证）

- 实机 `hwk-win-test`（8.149.129.78）SSH 可用，`XWall` 与 `sqlservr` 均在运行。
- LocalDB 实例 `v11.0`（SQL Server **11.00.7001**），库以**文件路径为库名**附加，另有
  `HWKCOPY_XWall` / `HWKCOPY_XWallTem` / `HWKCOPY_UserGlazing` 三个**副本库**（既有取证产物）。
- 本轮只对副本库执行 `select … from sys.tables / sys.columns / sys.partitions` 与 `select *`
  取数据，**未写入、未 attach、未修改任何库**。

### 9.2 结构（`migration_workspace/db-schema.md`）

| 库 | 表 | 列 |
| --- | --- | --- |
| `HWKCOPY_XWallTem`（模板/参数库） | 56 | 492 |
| `HWKCOPY_XWall`（工程主库） | 8 | 81 |
| `HWKCOPY_UserGlazing`（玻璃库） | 21 | 135 |

模板库中文表名（行数）：`计算模板` 2082、`风压数据` 767、`更新记录表` 549、`材料导热系数表` 132、
`标准规范表` 93、`玻璃参数` 56、`铝材强度表` 41、`幕墙类别码表` 40、`结构胶参数` 25、
`玻璃强度表` 22、`钢材强度表` 22、`常用材料特性表` 18 …

### 9.3 公式库：**已全部解码**（更正：不是混淆，是 GBK 明文）

初次把 `CONTEXT` 直接 `cast to nvarchar` 看到乱码，据此判断"混淆"是**错的**：那是 SQL 把 GBK
字节按 UTF-16 解释的结果。按 **cp936** 解码即得到可读公式。

| 指标 | 值 |
| --- | --- |
| 公式条目 | **2079** |
| 原始字节 | 3,114,045 |
| 模板变量 `${...}` | 5,761 种 |
| 函数 `Xxx(...)` | 263 种 |
| 规范号 | 58 种 |

`计算模板` 结构：`IID / TITLE（中文名）/ SYMBOL（大写键）/ CONTEXT（GBK 公式文本）/ REMARK`。
`SYMBOL` 与引擎属性键同构（`WLS`/`WLD`/`WAREA`/`WWEIGHT`…）。

规范分布（按出现条目数）：`JGJ102-2003` 872、`JGJ145-2013` 234、`GB50009-2012` 189、
`GB50009-2001` 103、`JGJ336-2016` 94（含带空格变体）、`GB50017-2017` 92、`GB50018-2002` 42、
`JGJ133-2001` 24、`JGJ214-2010` 10、`CECS 745-2020` 10、`GB50010-2010` 5、`GB/T50121-2005` 2、
`CECS 1048-2022` 2。

样例（`WLS` 风荷载标准值，原文照录）：

```text
   Wk: 作用在${GetBoardType(PRJGLASS)}上的风荷载标准值(kN/m^2)
   μz: ${z}m高处风压高度变化系数(按${REGION}类区计算): (GB50009-2001  7.2.1)
         μz=${μh}×(z/10)^${α2}=${μzcal} ${IsLess(μzcal,μz):+由于${μzcal}<${μz},取μz=${μz}}
   μf: 脉动系数  :                  (GB50009-2001  7.4.2-8)
        μf=0.5×35^(1.8×(${α}-0.16))×(z/10)^-${α}=${μf}
   βgz: 阵风系数  :                 (GB50009-2001  7.5.1-1)
        βgz=${GetKk(REGION)}×(1+2×μf) = ${βgz}
   Wk=${IsNEqual(γ0,1):+γ0×}βgz×μz×μsl×W0             (JGJ102-2003  5.3.2)
```

产物：`migration_workspace/formulas.json`（全量 2079 条）、`formulas.md`（统计与样例）、
脚本 `scripts/decode-formulas.py`。

### 9.4 已取回的数据（`migration_workspace/raw/db-schema/data-*.csv`）

| 文件 | 表 | 行数 |
| --- | --- | --- |
| `data-1.csv` | 计算模板 | 2082 |
| `data-2.csv` | 标准规范表 | 93 |
| `data-3.csv` | 玻璃参数 | 56 |
| `data-4.csv` | 玻璃强度表 | 22 |
| `data-5.csv` | 幕墙类别码表 | 40 |
| `data-6.csv` | 常用材料特性表 | 18 |
| `data-7.csv` | 钢材强度表 | 22 |

---

## 10. 全量分析进度（截至本轮）

### 10.1 已完成

| 层 | 结论 | 证据 |
| --- | --- | --- |
| L1 安装包 | 458 条目 / 506.6 MB / 139 PE | `install-package.md` |
| L2 体系 | **74 体系 / 19 大类** | `calculation-systems.md` |
| L3 模块 | 139 PE 真实名/导出数/依赖方向；引擎 = `HWKSciCal.dll`（605 导出） | `module-names.json`、`import-graph.json` |
| L4 引擎 | 注册=原型克隆；`setName` bool=入字典；`eval` 拉取式 + 符号模式 | `calculation-core.md` §7 |
| L5 节点层 | 379 类 / 379 vtable / **379 个互不相同的 eval** 全部定位 | `node-vtables.md` |
| L5 算法 | 1 个已解（`CalGlassDisp = ms×qwk×aw⁴÷dw×theta×1e9`） | `calculation-core.md` §9 |
| L7 数据 | 3 库 85 表 / 708 列；**2,079 条公式（GBK 明文）**；58 个规范号 | `db-schema.md`、`formulas.md` |
| 兼容 | `.cwx` = 类型标签对象图，根 `HWKWallContext`，**216 种类型**，107 种 `HWKCalc_*` 结果持久化 | `cwx-format.md` |
| 序列化面 | `Serialize` 2,165 / `CbObject` 1,588 / `CbClassRegistration` 1,898 个导出 | 导出表 |

### 10.2 本轮新增的两条结构性结论

1. **公式语言与节点表部分对齐**：263 个模板函数里，**88 个就是 CXMap 节点**；
   仅 5 个在 `HWKKernal.dll` 有同名导出（`IsEqual`/`GetE`/`GetM`/`GetBoltNumber`/`GetAl`）；
   其余 175 个多为运算符（`Add`/`Mul`/`Abs`/`LAnd`）、绘图（`*_FEDRAW`）、表格（`*_Table`）、
   FE 数据（`*_FEData`）。
   → 公式文本不是"另一种语言"，而是**节点图的可读投影**，重构时两者要一起设计。

2. ~~`.cwx` 保存了计算结果~~ → **2026-10-19 差分实测修正**：`HWKCalc_*` 类型在工程文件里有实例，
   但这些实例记录**没有可读的结果数值**（`HWKCalc_GlassDisp` 载荷 4 字节 `05 00 00 00`，
   `GlassArea` 8 字节全 0，`GlassStrength` 8 字节无 double）；且在属性面板改「城市基本雪压/风压」后另存，
   这些记录**字节未变**（`b→c`、`c→d` 两次差分各自只有 1 段差异）。
   → 结论应改为：**已观测的 4 个 `HWKCalc_*` 类不缓存结果值**；其余 103 种未逐类取证，保持未知。
   证据：`cwx-field-widths.md` §5、`raw/cwx-diff-20261019/diff-{b-c,c-d}.json`。

### 10.3 进行中 / 未完成

| 项 | 状态 |
| --- | --- |
| 378 个节点 eval 反编译 | **已完成（2026-10-19）**：`raw/nodes/*.rea.json` 共 378 份（缺 1 个） |
| 节点算式抽取（L5/A 路线） | **PARTIAL（2026-10-19）**：`scripts/extract-node-expr.py` → `nodes-expr.md`。`EXPR`=9（完全绑定）、`PARTIAL`=52（有算式但有变量来源未定）、`NO_ARITH`=317（反编译内无数值算术，待分类）。`CalGlassDisp` 输出与人工核对结论逐字一致 |
| `.cwx` 字段布局（各 `Serialize` 的字段顺序与类型） | **PARTIAL（2026-10-19）**：头/记录头/字符串编码已定案；3 个字段偏移已量出（`城市基本雪压` 0x5E、`城市基本风压` 0xA0、`工程名称` 0x66+0x6A）。见 `cwx-field-widths.md`；其余字段与载荷长度规则仍需逐类取证 |
| FE 求解链（114 `FEAdd*` + `HWKFeUtil`/`Structmodule`） | 未做 |
| 数据库字段语义与单位 | 只有结构，无字段含义 |
| 数值对照 | 未做（等实机跑） |

---

## 11. L5 / A 路线：节点算式抽取（2026-10-19 起）

目标：把 378 份已归档反编译（`raw/nodes/*.rea.json`）逐节点变成**可读算式 + 参名表**，
即 L5 的"源码级透明"，不依赖原版运行。

### 11.1 已建成的工具

`scripts/extract-node-expr.py` → `migration_workspace/nodes-expr.md` + `raw/nodes-expr.json`

机械替换规则（全部来自模板实测，不做语义推断）：

1. `String::String(<local>,"名")` → `local` 绑定参数名；
2. 随后 `look_string(…, <local>, …)` 的结果变量绑定同名参数（含 `local_x = pVar5;` 别名）；
3. `X = **(code **)(*W + 0xa8))(…)` 取该参数数值对象，`*(double *)(X + 8)` 为数值；
4. `dVar/fVar = …` 逻辑语句按顺序代入（多行表达式先拼接、同一寄存器变量重用要按时刻绑定）。

### 11.2 覆盖（2026-10-19 实测，378 个节点）

| 状态 | 数量（379 全量） | 含义 |
| --- | --- | --- |
| `EXPR` | 51 | 参名全绑定、无残留中间变量，可直接当算式用 |
| `SELECTED` | 1 | 算式完整但含数据相关选择 `sel(H\|W)`（条件已取证） |
| `TABLE_LOOKUP` | 15 | 数值来自规范查表函数（`table[addr](arg)`，条件与常量见 `helper-tables.md`） |
| `INTERPOLATION` | 4 | 数值来自**调用方传入的表**做线性查表（`INTERP(FUN_180299d50)`） |
| `STRING_TABLE` | 3 | 数值来自**字符串键常量表**（`STRLIT(FUN_180276de0)`） |
| `FE_OP` | 12 | 节点是 FE 建模/求解动作，数值来自 FE 机制（`CALL(FUN_…)`），不是公式 |
| `TABLE_BUILDER` | 2 | 数值由"表装填/回填"过程产生（`void` 函数，`+0x180` 取变参再 `+0xa8` 取值） |
| `EXTERNAL_CALL` | 0 | 已全部定性（无剩余） |
| `PARTIAL` | 31 | 有算式骨架，但存在 `dVar/uVar/p[…]/$N[i]` 来源未定 |
| `VARARG_GET` | 1 | 数值来自「变参取值 + 默认值」（`ARG(…)`） |
| `NO_ARITH` | 259 | 反编译里没有数值算术（已分类，见 §11.4） |

### 11.3 第 1 步：辅助函数（`scripts/decompile-helpers.py`）

节点算式里被赋给数值变量的 `FUN_*` 共 31 个，已全部反编译并分类：

| 类别 | 数量 | 处理 |
| --- | --- | --- |
| `GLOBAL_GETTER` | 1 | `FUN_180279d50` → 具名全局量 `GLOB_STEELLIMIT`，已直接代入算式 |
| `RNG` | 1 | `FUN_180331b80`（无入参、DAT_ 状态、LCG 常数）→ 许可校验用的伪随机，算式里记 `RNG()` |
| `ARITH` | 7 | 已归档 `raw/helpers/<addr>.rea.json`，尚未内联 |
| `OTHER` | 22 | 已归档（含报错文案、类型转换、代理取值等） |

效果：`EXPR` 9 → 47，`PARTIAL` 52 → 39（`GLOB_STEELLIMIT` 代入让 `GetBeamDflim`/`GetDflim` 等直接可读）。

### 11.4 第 2 步：节点头分类（`scripts/classify-node-kind.py`）

379 个节点全部有类别，**`UNKNOWN` = 0**：

| 类别 | 数量 | 判定信号（结构） |
| --- | --- | --- |
| `GETTER` | 115 | 只做 `look_string` 取值 |
| `ARITH` | 95 | 有数值算术（结构正则 或 算式抽取已产出步骤，两个独立信号取或） |
| `STRING` | 69 | `CXStringDefine` / 字符串拼接 |
| `FE_DATA` | 47 | 名字以 `FE` 开头且无算术（FE 数据装填/取值） |
| `COLLECTION` | 45 | `CXMapVariableArguments`/`CXParameter` + Add/Del 类 |
| `DRAW` | 7 | `HWKPlot`/`g_bEmfOut`/`Draw*` |
| `PREDICATE` | 1 | 返回 0/1 常量或 `(double)bVar` |

产物：`migration_workspace/node-kinds.md`、`raw/node-kinds.json`（含 `kinds` 全部命中标签）。

### 11.5 第 3 步：补最后一个节点

`FEDelCBProb`（`eval=0x1800b6eb0`）已反编译归档 → **379/379 个节点全部有反编译 + 分类**。

### 11.6 第 4 步：收尾四件事（2026-10-19 完成）

| 任务 | 结果 |
| --- | --- |
| ① 反编译 `FUN_180251270` | **假设被证伪**：它不是"代理取参"，而是 `GetAVmax` 的**构造函数**（创建 `CXParameter("x")/("y")` 并写 `GetAVmax::vftable`）。节点 eval 里的 `FUN_18025xxxx(local,&local)` 属**符号回退分支**（缺参数时新建同类节点并绑定实参），不是取值 |
| ① 附带改进 | 新增 `numeric_block()`：只分析含 `+ 0xa8` 取数且含 `CXConstant::CXConstant` 的最深分支 → 排除回退分支污染；`OTHER` 类辅助函数（如报错文案 `FUN_180254fd0`）不再当作数值来源，改记未绑定 |
| ② 残留变量收尾 | 新增 `CONCAT44(hi,lo)` 还原（`SUB84` 拆分与"低/高 32 位分两步取"两种写法），18 类节点受益；`GetAAs1/GetAAs2/GetBeamDflim/GetDflim` 等已成完整算式。新增 `scripts/helper-tables.py` → `helper-tables.md`（11 个查表函数：条件 + 常量，如 `fun_180255170` 按 `"A"/"B"/"C"` 与高度/宽度段返回系数） |
| ③ `GetACFt` 的 `sel(H\|W)` | 已定位：候选 `dVar2`/`dVar3`，条件为 `dVar5≈2.0 → dVar2`、`dVar5≈0 → dVar3`；条件原文存进 `select_note`，状态保持 `SELECTED`（不当作确定式） |
| ④ 非算术节点文字面 | 新增 `scripts/node-describe.py` → `node-descriptions.md`：379 个节点逐个给「类别 / 算式状态 / 入参 / 业务相关调用 / 分支数 / 返回类型」（只描述结构，不含语义） |

### 11.6b 第 5 步：变参/累加/内联（2026-10-19 续）

| 能力 | 说明 | 受益节点 |
| --- | --- | --- |
| 变参取元 `$k[i]` | 识别 `X = (**(code **)(*W + 0x180))(W, idx)` → `W[idx]`，再经 `+0xa8` 取值 | `GetAddHs` 等 |
| 循环累加 `SUM(…)` | `acc = acc + term` 识别为累加，输出 `SUM(term)` 而非把初值 0 当结果 | `GetAddHs` |
| ARITH 辅助函数内联 | 用 `param_N` 位置把辅助函数算式代入实参 | `GetHc`、`GetNextAirIndex`、`StartAirIndex` |
| 外部函数标记 | `OTHER` 类函数不再当已知数值，记 `CALL(FUN_…)` 并单独状态 `EXTERNAL_CALL` | 22 个节点（原 36） |
| 查表函数内联 | 已有「条件+常量」表的被调函数记 `table[addr](arg)`，状态 `TABLE_LOOKUP` | 13 个节点 |
| 纯取值别名 | `dVar = *(double*)(x+8)`、`$N[i]` 等纯读取不再丢弃，登记为别名供代入 | `GetWallUValue` 等 |
| 线性查表函数 | `FUN_180299d50(double x, double *table, longlong n)`：对**调用方传入的表**做区间扫描 → 状态 `INTERPOLATION`（`INTERP(…)`） | `GetDe`、`GetNg`、`GetMetalNg`、`GetInterpolation` |
| 字符串键常量表 | `FUN_180276de0(String*)`：`String::find` 分支后返回常数（1/180、1/GLOB_STEELLIMIT、0.004）→ 状态 `STRING_TABLE`（`STRLIT(…)`） | `GetLMCDflim`、`GetLMCDfnum` |
| FE 动作节点 | 节点名以 `FE` 开头且数值只来自外部调用 → 状态 `FE_OP`，**不再混进公式类** | 13 个 FE 节点 |

**效果（累计，自 §11.2 首版起）**：`EXPR` 45 → **48**、`NO_ARITH` 293 → **260**；
原本笼统的 `EXTERNAL_CALL` 36 已**全部定性**：`TABLE_LOOKUP` 14 + `FE_OP` 13 + `INTERPOLATION` 4 +
`STRING_TABLE` 3 + `TABLE_BUILDER` 2 + `EXTERNAL_CALL` 0。中途出现的"`EXPR` 先降后升"是**有意收紧再放开**：
先剔除把未知函数当公式的假算式，再靠查表/别名/内联把真算式补回来。

### 11.7 仍未闭合（下一轮继续 A）

新增工具 `scripts/node-residual.py` → `migration_workspace/nodes-residual.md`：
把 36 个待收尾节点逐条列出「未绑定符号 + 它在反编译里的赋值来源」，可直接当待办表。

| 缺口 | 数量 | 说明 |
| --- | --- | --- |
| 未绑定取值 `p[…]` | 11 | 主要是取值来自 `OTHER` 类辅助函数或两步拆分未回溯 |
| 残留寄存器变量 | 26 | 多为 `dVar/uVar` 来自被调函数或选择分支 |
| 数据相关选择 `sel(...)` | 1 | `GetACFt`：两个分支都写同一 `CONCAT44`，需按条件定 |

新发现的取值模式（下一轮首要）：部分节点**不经 `look_string`**，而是
`pCVar = (CXConstant *)FUN_180251270(local_48,&local_68)` 这类"代理取参"函数，
导致参数名完全绑定不上（`GetAVmax`/`GetAmax` 等）。需先反编译该代理函数并识别其第 2 参是否为参数名。

其余：`ARITH` 95 个里仍有 9 个抽不出步骤（数学写在被调函数里）；
283 个非算术节点只有类别标签，逐节点"做了什么"的自然语言说明还没写（A 路线的文字面）。

`CalGlassDisp` 输出 `((qwk * ms * (pow(aw,4.0))) / dw) * theta * 1000000000.0`
与 `calculation-core.md` §9 的人工核对结论**逐字一致** —— 该抽取器已通过一次独立自检。

### 11.7 复现命令

```bash
GHIDRA_INSTALL_DIR=$HOME/Tools/ghidra_12.1.4_PUBLIC python3 scripts/decompile-helpers.py   # 31 个辅助函数
python3 scripts/extract-node-expr.py    # -> nodes-expr.md + raw/nodes-expr.json（幂等）
python3 scripts/classify-node-kind.py   # -> node-kinds.md + raw/node-kinds.json（幂等）
python3 scripts/node-residual.py        # -> nodes-residual.md + raw/nodes-residual.json（收尾待办）
python3 scripts/helper-tables.py        # -> helper-tables.md（查表函数：条件 + 常量）
python3 scripts/node-describe.py        # -> node-descriptions.md（379 个节点结构描述）
```

> 红线：抽取结果只是**算术结构**，"物理含义/单位/规范依据"仍然未知，不得由结构反推工程语义。

## 12. L7 数据层突破（2026-10-19）

| 步骤 | 结果 | 产物 |
| --- | --- | --- |
| 可读性验证 | `XWallTem.mdf`+`_log.ldf` 复制件 attach 到 LocalDB 成功，56 表 | `db-access.md` |
| 全量导出 | `HWKCOPY_XWall`(8) + `HWKCOPY_XWallTem`(56) + `HWKCOPY_UserGlazing`(21) = **85 表 / 207,105 行** | `raw/db/*.json`、`db-dump.md` |
| 公式取回 | `计算模板` **2082** 条，`CONTEXT`(varbinary) 按 **GBK** 解码 | `raw/db/formulas-raw.json` |
| 公式↔注册名绑定 | 250 个函数占位中 **81** 命中 379 个 CXMap 注册名；**5285** 个数据符号中 0 个是注册名 | `formula-bindings.md`、`raw/formula-bindings.json` |

关键结构性结论：

1. **公式里的"函数"是节点，"符号"是数据** —— 不要把两者混为一谈（早前按"参数名=注册名"去对是错的）。
2. 频次最高的函数是**排版/格式化辅助**（`GetEQFormat` 9832、`GetEQSSubFormat` 7490、`GetSSubFormat` 5330），
   说明 `计算模板` 是**计算书模板**（算式 + 排版 + 规范引用混排），不是纯表达式表。
3. 真正的计算函数在几十到上千次量级（`GetE` 1081、`GetFt` 422、`GetNg` 284、`GetM` 226、`GetDfnum` 156、
   `GetSMr` 142、`GetVr` 119 …），这些与 L5 抽出的节点算式可以逐条对上。
4. 379 个注册名里有 **300 个从未在公式中以函数出现** → 多为 FE/绘图/内部节点，说明"节点表 ≫ 业务公式所需"，
   与 `VERIFICATION.md` 里"FE 建删模型高度模板化"的结论一致。

复现：

```bash
python3 scripts/dump-db.py HWKCOPY_XWallTem      # 表结构+样本（白名单只读）
python3 scripts/fetch-formulas.py                # 2082 条公式 + GBK 解码
python3 scripts/build-formula-bindings.py        # 公式↔函数↔符号绑定
```
