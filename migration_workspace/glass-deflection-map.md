# 玻璃挠度体系：公式 → 引擎节点 映射（L5/L8 样板，第 1 步）

- 选取规则：`^(MG_)?(WDISPLACEMENT[A-Z]*|GLASSRIBDISP[A-Z]*|GLASSFEDISPMENT[A-Z]*)$`（来自 `formulas.json`，共 25 条模板）
- 调用总数 555：命中注册名 434，形参个数与注册元数一致 395、可变参数节点 39、**真正不一致 0**
- 普通变量引用 526 次、条件块 158 个
- 判定口径：**只有名字出现在 379 注册表里才算命中**；形参个数只作为核对，不做纠正。

## `WDISPLACEMENT`（iid 14，1262 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IFValue` | 1 | [3] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLS_to}mm`
- `GLS_ti` 运算 `+` → `te\: ${GLS_STRUCTDESC}的等效厚度    te=${IsLarge(GLS_tm,3.0):+0.95×}(t1^3+t2^3)^(1/3)      =$`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `GLS_ti` 运算 `+` → `e`
- `GLS_ti` 运算 `+` → `e`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLS_COMPK`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_to`, `GLS_θwe`, `νw`

## `WDISPLACEMENTJD`（iid 15，1206 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IFValue` | 1 | [3] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLS_to}mm`
- `GLS_ti` 运算 `+` → `te\: ${GLS_STRUCTDESC}的等效厚度    te=${IsLarge(GLS_tm,3.0):+0.95×}(t1^3+t2^3)^(1/3)      =$`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `GLS_ti` 运算 `+` → `e`
- `GLS_ti` 运算 `+` → `e`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLS_COMPK`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_to`, `GLS_θwe`, `νw`

## `GLASSRIBDISP`（iid 60，643 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetOKStr` | 1 | [1] | 1 | 是 | `FUN_1802541e0` |
| `IFValue` | 2 | [3] | None | 否 | `None` |

普通变量（8）：`GRIB_Bw`, `GRIB_COMPK`, `GRIB_DFRLIMIT`, `GRIB_H`, `GRIB_Hw`, `GRIB_dfribcal`, `GRIB_dfrlim`, `GRIB_ttrib`

## `GLASSRIBDISPJD`（iid 61，487 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetOKStr` | 1 | [1] | 1 | 是 | `FUN_1802541e0` |
| `IFValue` | 2 | [3] | None | 否 | `None` |

普通变量（8）：`GRIB_Bw`, `GRIB_COMPK`, `GRIB_DFRLIMIT`, `GRIB_H`, `GRIB_Hw`, `GRIB_dfribcal`, `GRIB_dfrlim`, `GRIB_ttrib`

## `WDISPLACEMENTTHRLAYER`（iid 273，1377 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLS_COMPK`, `GLS_DESC`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwe`, `νw`

## `WDISPLACEMENTTHRLAYERJD`（iid 274，1377 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLS_COMPK`, `GLS_DESC`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwe`, `νw`

## `MG_WDISPLACEMENT`（iid 282，1999 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 4 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetSSubFormat` | 10 | [3] | 3 | 是 | `FUN_180254620` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IFValue` | 1 | [3] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLS_to}mm`
- `GLS_ti` 运算 `+` → `${GetEQSSubFormat('t','','e')}\: ${GLS_STRUCTDESC}的等效厚度    ${GetEQFormat(0)}${GetSSubForm`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `GLS_ti` 运算 `*` → `t`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('t','','e')}`
- `GLS_ti` 运算 `*` → `t`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('t','','e')}`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLS_COMPK`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_to`, `GLS_θwe`, `νw`

## `MG_WDISPLACEMENTJD`（iid 283，1063 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetEQFormat` | 10 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 1 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 1 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IsLarge` | 1 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLS_to}mm`
- `GLS_ti` 运算 `+` → `te\: ${GLS_STRUCTDESC}的等效厚度    te=${IsLarge(GLS_tm,3.0):+0.95×}${GetEQFormat(0)}\\r(3,t1^`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `GLS_ti` 运算 `+` → `e`
- `GLS_ti` 运算 `+` → `e`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（13）：`GLS_COMPK`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_to`, `GLS_θwe`

## `MG_WDISPLACEMENTTHRLAYER`（iid 310，2123 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 8 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetSSubFormat` | 7 | [3] | 3 | 是 | `FUN_180254620` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLS_COMPK`, `GLS_DESC`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwe`, `νw`

## `MG_WDISPLACEMENTTHRLAYERJD`（iid 311，2123 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 8 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [2] | 2 | 是 | `FUN_1802986b0` |
| `GetSSubFormat` | 7 | [3] | 3 | 是 | `FUN_180254620` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLS_COMPK`, `GLS_DESC`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwe`, `νw`

## `MG_GLASSRIBDISP`（iid 415，844 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 10 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetOKStr` | 1 | [1] | 1 | 是 | `FUN_1802541e0` |
| `IFValue` | 2 | [3] | None | 否 | `None` |

普通变量（8）：`GRIB_Bw`, `GRIB_COMPK`, `GRIB_DFRLIMIT`, `GRIB_H`, `GRIB_Hw`, `GRIB_dfribcal`, `GRIB_dfrlim`, `GRIB_ttrib`

## `GLASSFEDISPMENT`（iid 446，79 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GLASSFE_SHTable` | 1 | [1] | None | 否 | `None` |

普通变量（0）：无

## `MG_GLASSFEDISPMENT`（iid 447，142 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GLASSFE_SHTable` | 2 | [1] | None | 否 | `None` |

普通变量（0）：无

## `WDISPLACEMENTPS`（iid 494，1569 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IFValue` | 1 | [3] | None | 否 | `None` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLSPS_to}mm`
- `GLSPS_ti` 运算 `+` → `te\: ${GLSPS_STRUCTDESC}的等效厚度    te=${IsLarge(GLSPS_tm,3.0):+0.95×}(to^3+ti^3)^(1/3)    `
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5.2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=qk×b^4/E/t${GLSPS_ti:+e}^4        (JGJ102-2003  8.1.5-4)      =${GLSPS_COM`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLSPS_COMPK`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `WDISPLACEMENTPSJD`（iid 495，1569 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IFValue` | 1 | [3] | None | 否 | `None` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLSPS_to}mm`
- `GLSPS_ti` 运算 `+` → `te\: ${GLSPS_STRUCTDESC}的等效厚度    te=${IsLarge(GLSPS_tm,3.0):+0.95×}(to^3+ti^3)^(1/3)    `
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5.2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=qk×b^4/E/t${GLSPS_ti:+e}^4        (JGJ102-2003  8.1.5-4)      =${GLSPS_COM`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLSPS_COMPK`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `WDISPLACEMENTTHRLAYERPS`（iid 500，1677 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=qk×b^4/E/te^4        (JGJ102-2003  8.1.5-4)      =${GLSPS_COMPK}×${GLSPS_a`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLSPS_COMPK`, `GLSPS_DESC`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `WDISPLACEMENTTHRLAYERPSJD`（iid 501，1677 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=qk×b^4/E/te^4        (JGJ102-2003  8.1.5-4)      =${GLSPS_COMPK}×${GLSPS_a`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLSPS_COMPK`, `GLSPS_DESC`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `MG_WDISPLACEMENTPS`（iid 502，1908 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IFValue` | 1 | [3] | None | 否 | `None` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLSPS_to}mm`
- `GLSPS_ti` 运算 `+` → `te\: ${GLSPS_STRUCTDESC}的等效厚度    te=${IsLarge(GLSPS_tm,3.0):+0.95×}${GetEQFormat(0)}\\r(3`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5.2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=${GetEQFormat(0)}\\f(qk×b^4,E×t${GLSPS_ti:+e}^4)${GetEQFormat(1)}        (J`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLSPS_COMPK`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `MG_WDISPLACEMENTPSJD`（iid 503，1908 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IFValue` | 1 | [3] | None | 否 | `None` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLSPS_to}mm`
- `GLSPS_ti` 运算 `+` → `te\: ${GLSPS_STRUCTDESC}的等效厚度    te=${IsLarge(GLSPS_tm,3.0):+0.95×}${GetEQFormat(0)}\\r(3`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `0.95×`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5.2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=${GetEQFormat(0)}\\f(qk×b^4,E×t${GLSPS_ti:+e}^4)${GetEQFormat(1)}        (J`
- `GLSPS_ti` 运算 `+` → `e`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLSPS_COMPK`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `MG_WDISPLACEMENTTHRLAYERPS`（iid 506，2399 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 7 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetSSubFormat` | 7 | [3] | 3 | 是 | `FUN_180254620` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=${GetEQFormat(0)}\\f(${GetSSubFormat('q','','k')}×b^4,E×${GetSSubFormat('t'`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLSPS_COMPK`, `GLSPS_DESC`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `MG_WDISPLACEMENTTHRLAYERPSJD`（iid 507，2399 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 1 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 7 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 2 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSDr` | 2 | [4] | 2 | 是 | `FUN_1802986b0` |
| `GetSSubFormat` | 7 | [3] | 3 | 是 | `FUN_180254620` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `IsEqual` | 6 | [2] | None | 否 | `None` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `*` → `0.95×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:     θ=${GetEQFormat(0)}\\f(${GetSSubFormat('q','','k')}×b^4,E×${GetSSubFormat('t'`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwe)}`
- `GLSPS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLSPS_COMPK`, `GLSPS_DESC`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl`, `GLSPS_dflim`, `GLSPS_dfw`, `GLSPS_te`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwe`, `νw`

## `WDISPLACEMENTTWOSIDE`（iid 1091，873 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLS_to}mm`
- `GLS_ti` 运算 `+` → `te\: ${GLS_STRUCTDESC}的等效厚度    te=${IsLarge(GLS_tm,3.0):+0.95×}(t1^3+t2^3)^(1/3)      =$`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `GLS_ti` 运算 `+` → `e`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLS_COMPK`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_SDr`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_to`, `νw`

## `MG_WDISPLACEMENTTWOSIDE`（iid 1092，1498 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 16 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 4 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetSSubFormat` | 8 | [3] | 3 | 是 | `FUN_180254620` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `t\: 玻璃板块厚度\: ${GLS_to}mm`
- `GLS_ti` 运算 `+` → `${GetEQSSubFormat('t','','e')}\: ${GLS_STRUCTDESC}的等效厚度    ${GetEQFormat(0)}${GetSSubForm`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `0.95×`
- `GLS_ti` 运算 `*` → `t`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('t','','e')}`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（14）：`GLS_COMPK`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_SDr`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_to`, `νw`

## `WDISPLACEMENTTWOSIDETHRLAYER`（iid 1095，1061 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLS_COMPK`, `GLS_DESC`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_SDr`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `νw`

## `MG_WDISPLACEMENTTWOSIDETHRLAYER`（iid 1096，1691 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 14 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 4 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 1 | [1] | 2 | 是 | `FUN_180254010` |
| `GetSSubFormat` | 9 | [3] | 3 | 是 | `FUN_180254620` |
| `GetVr` | 1 | [1] | 1 | 是 | `FUN_180275fa0` |
| `LAnd` | 3 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `    由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减 `
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `*` → `0.95×`
- `GLS_DWLESS` 运算 `*` → `不`

普通变量（16）：`GLS_COMPK`, `GLS_DESC`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_SDr`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_dflim`, `GLS_dfw`, `GLS_te`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `νw`

## 未解析（需继续取证）

- `IsLarge`：not in registry (MG_WDISPLACEMENT)；not in registry (MG_WDISPLACEMENTJD)；not in registry (MG_WDISPLACEMENTPS)；not in registry (MG_WDISPLACEMENTPSJD)；not in registry (MG_WDISPLACEMENTTWOSIDE)；not in registry (WDISPLACEMENT)；not in registry (WDISPLACEMENTJD)；not in registry (WDISPLACEMENTPS)；not in registry (WDISPLACEMENTPSJD)；not in registry (WDISPLACEMENTTWOSIDE)（全库出现 387 次）
- `IFValue`：not in registry (GLASSRIBDISP)；not in registry (GLASSRIBDISPJD)；not in registry (MG_GLASSRIBDISP)；not in registry (MG_WDISPLACEMENT)；not in registry (MG_WDISPLACEMENTPS)；not in registry (MG_WDISPLACEMENTPSJD)；not in registry (WDISPLACEMENT)；not in registry (WDISPLACEMENTJD)；not in registry (WDISPLACEMENTPS)；not in registry (WDISPLACEMENTPSJD)（全库出现 114 次）
- `LAnd`：not in registry (MG_WDISPLACEMENTTHRLAYER)；not in registry (MG_WDISPLACEMENTTHRLAYERJD)；not in registry (MG_WDISPLACEMENTTHRLAYERPS)；not in registry (MG_WDISPLACEMENTTHRLAYERPSJD)；not in registry (MG_WDISPLACEMENTTWOSIDETHRLAYER)；not in registry (WDISPLACEMENTTHRLAYER)；not in registry (WDISPLACEMENTTHRLAYERJD)；not in registry (WDISPLACEMENTTHRLAYERPS)；not in registry (WDISPLACEMENTTHRLAYERPSJD)；not in registry (WDISPLACEMENTTWOSIDETHRLAYER)（全库出现 271 次）
- `GLASSFE_SHTable`：not in registry (GLASSFEDISPMENT)；not in registry (MG_GLASSFEDISPMENT)（全库出现 21 次）
- `IsEqual`：not in registry (MG_WDISPLACEMENTPS)；not in registry (MG_WDISPLACEMENTPSJD)；not in registry (MG_WDISPLACEMENTTHRLAYERPS)；not in registry (MG_WDISPLACEMENTTHRLAYERPSJD)；not in registry (WDISPLACEMENTPS)；not in registry (WDISPLACEMENTPSJD)；not in registry (WDISPLACEMENTTHRLAYERPS)；not in registry (WDISPLACEMENTTHRLAYERPSJD)（全库出现 916 次）
- `Div`：not in registry (MG_WDISPLACEMENTPS)；not in registry (MG_WDISPLACEMENTPSJD)；not in registry (MG_WDISPLACEMENTTHRLAYERPS)；not in registry (MG_WDISPLACEMENTTHRLAYERPSJD)；not in registry (WDISPLACEMENTPS)；not in registry (WDISPLACEMENTPSJD)；not in registry (WDISPLACEMENTTHRLAYERPS)；not in registry (WDISPLACEMENTTHRLAYERPSJD)（全库出现 134 次）

## 可变参数节点（形参个数不参与判定）

- `GetLess`：1 args in GLASSRIBDISP (registry arity 2)；1 args in GLASSRIBDISPJD (registry arity 2)；1 args in MG_GLASSRIBDISP (registry arity 2)；1 args in MG_WDISPLACEMENT (registry arity 2)
- `GetSDr`：4 args in MG_WDISPLACEMENTPS (registry arity 2)；4 args in MG_WDISPLACEMENTPSJD (registry arity 2)；4 args in MG_WDISPLACEMENTTHRLAYERPS (registry arity 2)；4 args in MG_WDISPLACEMENTTHRLAYERPSJD (registry arity 2)

## 输入面（按前缀归类）

| 前缀 | 不同符号数 | 符号 |
| --- | --- | --- |
| `GLS` | 16 | `GLS_COMPK`, `GLS_DESC`, `GLS_DFNum`, `GLS_DISP`, `GLS_DWLESS`, `GLS_Dw`, `GLS_SDr`, `GLS_STRUCTDESC` … |
| `GLSPS` | 15 | `GLSPS_COMPK`, `GLSPS_DESC`, `GLSPS_DFNum`, `GLSPS_DISP`, `GLSPS_DWLESS`, `GLSPS_Dw`, `GLSPS_STRUCTDESC`, `GLSPS_awl` … |
| `GRIB` | 8 | `GRIB_Bw`, `GRIB_COMPK`, `GRIB_DFRLIMIT`, `GRIB_H`, `GRIB_Hw`, `GRIB_dfribcal`, `GRIB_dfrlim`, `GRIB_ttrib` |
| `other` | 1 | `νw` |

## 分支面（条件块按判定函数归类）

| 判定 | 出现次数 | 例 |
| --- | --- | --- |
| `IsEqual(GLSPS_LINKNUM,4)` | 48 | `+` 8.1.5.2 |
| `GLS_ti` | 25 | `*` t\: 玻璃板块厚度\: ${GLS_to}mm |
| `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` | 18 | `*`     由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减  |
| `GLSPS_ti` | 16 | `*` t\: 玻璃板块厚度\: ${GLSPS_to}mm |
| `GLS_DWLESS` | 12 | `*` 不 |
| `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` | 12 | `*`     由于有空气层存在,故需要按照规范JGJ102-2003 6.1.5进行折减  |
| `IsLarge(GLS_tm,3.0)` | 11 | `+` 0.95× |
| `IsLarge(GLSPS_tm,3.0)` | 8 | `+` 0.95× |
| `GLSPS_DWLESS` | 8 | `*` 不 |

## 节点库的调用面（同一次统计）

- 379 个注册节点里，**293 个在全部 2079 条公式模板中一次都没被调用**
- 玻璃四个算量节点的模板调用次数：`CalGlassDisp`=0、`CalGlassPSDisp`=0、`CalGlassStress`=0、`CalGlassPSStress`=0

即：模板层与节点层是**两套各自实现同一物理量的机制**，模板不走节点。

## 这一步能证明什么、不能证明什么

- 能证明：这些模板里出现的引擎调用名，哪些确实是注册节点、实参个数与注册元数对不对得上。
- 不能证明：调用顺序、默认值注入、查表数据来源，以及**这份模板是否就是运行时真正走的那条路**
  （同一物理量还存在于节点 `CalGlassDisp` 的自有算式中，两者参数化不同，谁被调用需另行取证）。
