# 玻璃面板强度（跨中应力）：公式 → 引擎节点 映射（模块透明化生成物，勿手改）

- 选取规则：`^(MG_)?WSTRENGTH[A-Z]*$`（来自 `formulas.json`，共 32 条模板）
- 调用总数 2532：命中注册名 1937，形参个数与注册元数一致 1809、可变参数节点 128、**真正不一致 0**
- 普通变量引用 2136 次、条件块 849 个
- 判定口径：**只有名字出现在 379 注册表里才算命中**；形参个数只作为核对，不做纠正。

## `WSTRENGTH`（iid 12，2800 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 10 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `Mul` | 5 | [2] | None | 否 | `None` |

条件块：
- `ISDOUBLEW` 运算 `*` → `=${fgwo}N/mm^2`
- `IsEqual(PRJGLASS,1)` 运算 `+` → `玻璃计算跨度`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `玻璃短边边长`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `\r\n   b\: 玻璃长边边长\: ${bl}m`
- `ISDOUBLEW` 运算 `*` → `t\: 玻璃板块厚度\: ${to}mm`
- `ISDOUBLEW` 运算 `+` → `ti\:  ${GLASSSTRUCTNAME}内侧玻璃厚度为\: ${ti}(mm) \r\n`
- `ISDOUBLEW` 运算 `+` → `to\:  ${GLASSSTRUCTNAME}外侧玻璃厚度为\: ${to}(mm)`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `IsLPeak` 运算 `*` → `风荷载与地震荷载`
- `IsLPeak` 运算 `+` → `恒载荷+风载荷+雪载荷`
- `IsLPeak` 运算 `*` → `W+ψE×qEA`
- `IsLPeak` 运算 `+` → `γg×GAk×cosα+0.9×(W+S)`
- `IsLPeak` 运算 `*` → `${ω}+${ψE}×${qEA}`
- `IsLPeak` 运算 `+` → `${γGf}×${GAK}×cos${ShapeAngle}+0.9×(${ω}+${SNOW})`
- `ISDOUBLEW` 运算 `+` → `\r\n   荷载分配计算\r\n   qo=${ISHOLW:+1.1×}q×to^3/(to^3+ti^3)\r\n     =${ISHOLW:+1.1×}${qw}×${t`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISDOUBLEW` 运算 `*` → `θ`
- `ISDOUBLEW` 运算 `+` → `θo`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `\r\n   θi=qi×${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}^4×10^9/E/ti^4\r\n     =${`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `η${ISDOUBLEW:+o}×`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwo)}×`
- `ISDOUBLEW` 运算 `+` → `\r\n   σwi=6×m×${Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):*ηi×}qi×${IsNEqual(PRJGLASS,2`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηi×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwi)}×`
- `ISDOUBLEW` 运算 `+` → `\r\n    ${σwi}N/mm^2${GetLess(FWILESS)}ｆg=${fgwi}N/mm^2`
- `FWLESS` 运算 `*` → `不`

普通变量（28）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `ISDOUBLEW`, `ISHOLW`, `IsLPeak`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwo`, `qEA`, `qw`, `qwi`, `qwo`, `ti`, `to`, `γGf`, `θwi`, `θwo`, `σwi`, `σwo`, `ψE`, `ω`

## `WSTRENGTHJD`（iid 13，2741 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 10 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `Mul` | 5 | [2] | None | 否 | `None` |

条件块：
- `ISDOUBLEW` 运算 `*` → `=${fgwo}N/mm^2`
- `IsEqual(PRJGLASS,1)` 运算 `+` → `玻璃计算跨度`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `玻璃短边边长`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `\r\n   b\: 玻璃长边边长\: ${bl}m`
- `ISDOUBLEW` 运算 `*` → `t\: 玻璃板块厚度\: ${to}mm`
- `ISDOUBLEW` 运算 `+` → `ti\:  ${GLASSSTRUCTNAME}内侧玻璃厚度为\: ${ti}(mm) \r\n`
- `ISDOUBLEW` 运算 `+` → `to\:  ${GLASSSTRUCTNAME}外侧玻璃厚度为\: ${to}(mm)`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `IsLPeak` 运算 `*` → `风荷载与地震荷载`
- `IsLPeak` 运算 `+` → `恒载荷+风载荷+雪载荷`
- `IsLPeak` 运算 `*` → `W+ψE×qEA`
- `IsLPeak` 运算 `+` → `γg×GAk×cosα+0.9×(W+S)`
- `IsLPeak` 运算 `*` → `${ω}+${ψE}×${qEA}`
- `IsLPeak` 运算 `+` → `${γGf}×${GAK}×cos${ShapeAngle}+0.9×(${ω}+${SNOW})`
- `ISDOUBLEW` 运算 `+` → `\r\n   荷载分配计算\r\n   qo=${ISHOLW:+1.1×}q×to^3/(to^3+ti^3)\r\n     =${ISHOLW:+1.1×}${qw}×${t`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISDOUBLEW` 运算 `*` → `θ`
- `ISDOUBLEW` 运算 `+` → `θo`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `\r\n   θi=qi×${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}^4×10^9/E/ti^4\r\n     =${`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `η${ISDOUBLEW:+o}×`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwo)}×`
- `ISDOUBLEW` 运算 `+` → `\r\n   σwi=6×m×${Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):*ηi×}qi×${IsNEqual(PRJGLASS,2`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηi×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwi)}×`
- `ISDOUBLEW` 运算 `+` → `\r\n    ${σwi}N/mm^2${GetLess(FWILESS)}ｆg=${fgwi}N/mm^2`
- `FWLESS` 运算 `*` → `不`

普通变量（28）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `ISDOUBLEW`, `ISHOLW`, `IsLPeak`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwo`, `qEA`, `qw`, `qwi`, `qwo`, `ti`, `to`, `γGf`, `θwi`, `θwo`, `σwi`, `σwo`, `ψE`, `ω`

## `WSTRENGTHXZ`（iid 269，2377 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [2] | 2 | 是 | `FUN_180298f50` |
| `IsLarge` | 4 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `=${GLS_fgwo}N/mm^2`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `t1\:${GLS_STRUCTDESC}外层玻璃厚度\: ${GLS_to}mm    t2\:${GLS_STRUCTDESC}内层玻璃厚度\: ${GLS_ti}mm`
- `LNot(LOr(GLS_tmg,GLS_ti))` 运算 `+` → `t1\:${GLS_STRUCTDESC}玻璃板块厚度为\: ${GLS_to}(mm)`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `    荷载分配计算\:    q1=${IsLarge(GLS_tm,3.0):+1.1×}q×t1^3/(t1^3+t2^3)      =${IsLarge(GLS_t`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    θ2=qk2×a^4×10^9/E/t2^4      =${GLS_qwki}×${GLS_awl}^4×10^9/${GetE(GLOB_BOARDMATERIAL`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    σw2=6×m×q2×η2×a^2×1000/t2^2          =6×${GetSMr(GLS_Bw,GLS_Hw)}×${GLS_qwi}×${GetNg(`
- `GLS_ti` 运算 `+` → `    ${GLS_STRESSI}N/mm^2${GetLess(IsNLarge(GLS_STRESSI,GLS_fgwi))}ｆg=${GLS_fgwi}N/mm^2`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（20）：`GLS_COMP`, `GLS_COMPK`, `GLS_DESC`, `GLS_FWLESS`, `GLS_STRESSI`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwko`, `GLS_qwo`, `GLS_ti`, `GLS_to`, `GLS_θwi`, `GLS_θwo`, `GLS_σwi`, `GLS_σwo`

## `WSTRENGTHXZJD`（iid 270，1998 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [2] | 2 | 是 | `FUN_180298f50` |
| `IsLarge` | 4 | [2] | None | 否 | `None` |
| `LAnd` | 1 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `=${GLS_fgwo}N/mm^2`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `    荷载分配计算\:    q1=${IsLarge(GLS_tmg,3.0):+1.1×}q×t1^3/(t1^3+t2^3)      =${IsLarge(GLS_`
- `IsLarge(GLS_tmg,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tmg,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tmg,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tmg,3.0)` 运算 `+` → `1.1×`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    θ2=qk2×a^4×10^9/E/t2^4      =${GLS_θwi}    查表6.1.2-2 得η2 = ${GetNg(GLS_θwi)} `
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    σw2=6×m×q2×η2×a^2×1000/t2^2          =6×${GetSMr(GLS_Bw,GLS_Hw)}×${GLS_qwi}×${GetNg(`
- `GLS_ti` 运算 `+` → `    ${GLS_STRESSI}N/mm^2${GetLess(IsNLarge(GLS_STRESSI,GLS_fgwi))}ｆg=${GLS_fgwi}N/mm^2`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（22）：`GLS_COMP`, `GLS_COMPK`, `GLS_DESC`, `GLS_FWLESS`, `GLS_STRESSI`, `GLS_STRESSO`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwko`, `GLS_qwo`, `GLS_t1`, `GLS_t2`, `GLS_ti`, `GLS_to`, `GLS_θwi`, `GLS_θwo`, `GLS_σwi`, `GLS_σwo`, `ti`

## `WSTRENGTHTHREELAYER`（iid 271，4940 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 4 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [2] | 2 | 是 | `FUN_180298f50` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =t1^3/(t1^3+t2^3+t3^3)       =${GLS_to}^3/(${GLS_`
- `LAnd(IsNLarge(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑外层夹胶先组合然后与内层再组合的原则,    tew\:外层夹胶组合等效厚度    tew=(t1^3+t2^3)^(1/3`
- `LAnd(IsNLess(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ten\:内层夹胶组合等效厚度    ten=(t2^3+t3^3)^(1/`
- `LAnd(IsNLess(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC}    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =1.1×t1^3/(t1^3+t2^3+t3^3)`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（29）：`GLS_COMP`, `GLS_DESC`, `GLS_FWLESS`, `GLS_RGLASS0`, `GLS_RGLASS1`, `GLS_RGLASS2`, `GLS_STRESSI`, `GLS_STRESSM`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwm`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwkm`, `GLS_qwko`, `GLS_qwm`, `GLS_qwo`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwi`, `GLS_θwm`, `GLS_θwo`, `GLS_σwi`, `GLS_σwm`, `GLS_σwo`

## `WSTRENGTHTHREELAYERJD`（iid 272，4209 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [2] | 2 | 是 | `FUN_180298f50` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =t1^3/(t1^3+t2^3+t3^3)       =${GLS_to}^3/(${GLS_`
- `LAnd(IsNLarge(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑外层夹胶先组合然后与内层再组合的原则,    tew\:外层夹胶组合等效厚度    tew=(t1^3+t2^3)^(1/3`
- `LAnd(IsNLess(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ten\:内层夹胶组合等效厚度    ten=(t2^3+t3^3)^(1/`
- `LAnd(IsNLess(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC}    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =1.1×t1^3/(t1^3+t2^3+t3^3)`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（29）：`GLS_COMP`, `GLS_DESC`, `GLS_FWLESS`, `GLS_RGLASS0`, `GLS_RGLASS1`, `GLS_RGLASS2`, `GLS_STRESSI`, `GLS_STRESSM`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwm`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwkm`, `GLS_qwko`, `GLS_qwm`, `GLS_qwo`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwi`, `GLS_θwm`, `GLS_θwo`, `GLS_σwi`, `GLS_σwm`, `GLS_σwo`

## `WSTRENGTHTHLAYERCG`（iid 275，3310 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 19 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `IsNLess` | 2 | [2] | None | 否 | `None` |
| `Mul` | 13 | [2] | None | 否 | `None` |

条件块：
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNLess(tml,3)` 运算 `+` → `1.1×${IsNLess(tm,3):+0.95^3×}`
- `IsNLess(tm,3)` 运算 `+` → `0.95^3×`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwo×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwo)}×`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwm×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwi×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `FWLESS` 运算 `*` → `不`

普通变量（29）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwm`, `fgwo`, `qw`, `qwi`, `qwm`, `qwo`, `ti`, `tmg`, `to`, `γGf`, `ζto`, `θwi`, `θwm`, `θwo`, `σwki`, `σwkm`, `σwko`, `ω`

## `WSTRENGTHTHLAYERCGJD`（iid 276，3314 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 19 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `IsNLess` | 2 | [2] | None | 否 | `None` |
| `Mul` | 13 | [2] | None | 否 | `None` |

条件块：
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNLess(tml,3)` 运算 `+` → `1.1×${IsNLess(tm,3):+0.95^3×}`
- `IsNLess(tm,3)` 运算 `+` → `0.95^3×`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwo×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwo)}×`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwm×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwi×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `FWLESS` 运算 `*` → `不`

普通变量（29）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwm`, `fgwo`, `qw`, `qwi`, `qwm`, `qwo`, `ti`, `tmg`, `to`, `γGf`, `ζto`, `θwi`, `θwm`, `θwo`, `σwki`, `σwkm`, `σwko`, `ω`

## `MG_WSTRENGTH`（iid 312，3264 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetEQFormat` | 24 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 10 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `Mul` | 5 | [2] | None | 否 | `None` |

条件块：
- `ISDOUBLEW` 运算 `*` → `=${fgwo}N/mm^2`
- `IsEqual(PRJGLASS,1)` 运算 `+` → `玻璃计算跨度`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `玻璃短边边长`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `\r\n   b\: 玻璃长边边长\: ${bl}m`
- `ISDOUBLEW` 运算 `*` → `t\: 玻璃板块厚度\: ${to}mm`
- `ISDOUBLEW` 运算 `+` → `ti\:  ${GLASSSTRUCTNAME}内侧玻璃厚度为\: ${ti}(mm) \r\n`
- `ISDOUBLEW` 运算 `+` → `to\:  ${GLASSSTRUCTNAME}外侧玻璃厚度为\: ${to}(mm)`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `IsLPeak` 运算 `*` → `风荷载与地震荷载`
- `IsLPeak` 运算 `+` → `恒载荷+风载荷+雪载荷`
- `IsLPeak` 运算 `*` → `W+ψE×qEA`
- `IsLPeak` 运算 `+` → `γg×GAk×cosα+0.9×(W+S)`
- `IsLPeak` 运算 `*` → `${ω}+${ψE}×${qEA}`
- `IsLPeak` 运算 `+` → `${γGf}×${GAK}×cos${ShapeAngle}+0.9×(${ω}+${SNOW})`
- `ISDOUBLEW` 运算 `+` → `\r\n   荷载分配计算\r\n   qo=${ISHOLW:+1.1×}q×${GetEQFormat(0)}\\f(to^3,to^3+ti^3)${GetEQFormat(`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISDOUBLEW` 运算 `*` → `θ`
- `ISDOUBLEW` 运算 `+` → `θo`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `\r\n   θi=qi×${GetEQFormat(0)}\\f(${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}^4×10`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×η${ISDOUBLEW:+o}`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwo)}`
- `ISDOUBLEW` 运算 `+` → `\r\n   σwi=${GetEQFormat(0)}\\f(6×m×qi×${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηi`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwi)}`
- `ISDOUBLEW` 运算 `+` → `\r\n    ${σwi}N/mm^2${GetLess(FWILESS)}ｆg=${fgwi}N/mm^2`
- `FWLESS` 运算 `*` → `不`

普通变量（28）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `ISDOUBLEW`, `ISHOLW`, `IsLPeak`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwo`, `qEA`, `qw`, `qwi`, `qwo`, `ti`, `to`, `γGf`, `θwi`, `θwo`, `σwi`, `σwo`, `ψE`, `ω`

## `MG_WSTRENGTHJD`（iid 313，3205 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetEQFormat` | 24 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 10 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `Mul` | 5 | [2] | None | 否 | `None` |

条件块：
- `ISDOUBLEW` 运算 `*` → `=${fgwo}N/mm^2`
- `IsEqual(PRJGLASS,1)` 运算 `+` → `玻璃计算跨度`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `玻璃短边边长`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `\r\n   b\: 玻璃长边边长\: ${bl}m`
- `ISDOUBLEW` 运算 `*` → `t\: 玻璃板块厚度\: ${to}mm`
- `ISDOUBLEW` 运算 `+` → `ti\:  ${GLASSSTRUCTNAME}内侧玻璃厚度为\: ${ti}(mm) \r\n`
- `ISDOUBLEW` 运算 `+` → `to\:  ${GLASSSTRUCTNAME}外侧玻璃厚度为\: ${to}(mm)`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `IsLPeak` 运算 `*` → `风荷载与地震荷载`
- `IsLPeak` 运算 `+` → `恒载荷+风载荷+雪载荷`
- `IsLPeak` 运算 `*` → `W+ψE×qEA`
- `IsLPeak` 运算 `+` → `γg×GAk×cosα+0.9×(W+S)`
- `IsLPeak` 运算 `*` → `${ω}+${ψE}×${qEA}`
- `IsLPeak` 运算 `+` → `${γGf}×${GAK}×cos${ShapeAngle}+0.9×(${ω}+${SNOW})`
- `ISDOUBLEW` 运算 `+` → `\r\n   荷载分配计算\r\n   qo=${ISHOLW:+1.1×}q×${GetEQFormat(0)}\\f(to^3,to^3+ti^3)${GetEQFormat(`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISDOUBLEW` 运算 `*` → `θ`
- `ISDOUBLEW` 运算 `+` → `θo`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `\r\n   θi=qi×${GetEQFormat(0)}\\f(${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}^4×10`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×η${ISDOUBLEW:+o}`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwo)}`
- `ISDOUBLEW` 运算 `+` → `\r\n   σwi=${GetEQFormat(0)}\\f(6×m×qi×${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηi`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwi)}`
- `ISDOUBLEW` 运算 `+` → `\r\n    ${σwi}N/mm^2${GetLess(FWILESS)}ｆg=${fgwi}N/mm^2`
- `FWLESS` 运算 `*` → `不`

普通变量（28）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `ISDOUBLEW`, `ISHOLW`, `IsLPeak`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwo`, `qEA`, `qw`, `qwi`, `qwo`, `ti`, `to`, `γGf`, `θwi`, `θwo`, `σwi`, `σwo`, `ψE`, `ω`

## `MG_WSTRENGTHXZ`（iid 314，4146 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 32 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 8 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [2] | 2 | 是 | `FUN_180298f50` |
| `GetSSubFormat` | 32 | [3] | 3 | 是 | `FUN_180254620` |
| `IsLarge` | 4 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `=${GLS_fgwo}N/mm^2`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `${GetEQSSubFormat('t','','1')}\:${GLS_STRUCTDESC}外层玻璃厚度\: ${GLS_to}mm    ${GetEQSSubForma`
- `LNot(LOr(GLS_tmg,GLS_ti))` 运算 `+` → `${GetEQSSubFormat('t','','1')}\:${GLS_STRUCTDESC}玻璃板块厚度为\: ${GLS_to}(mm)`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `    荷载分配计算\:    ${GetEQFormat(0)}${GetSSubFormat('q','','1')} = ${IsLarge(GLS_tm,3.0):+1`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `GLS_ti` 运算 `*` → `θ`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('θ','','1')}`
- `GLS_ti` 运算 `*` → `qk`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('q','','k1')}`
- `GLS_ti` 运算 `*` → `t`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('t','','1')}`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    ${GetEQFormat(0)}${GetSSubFormat('θ','','2')} = \\f(${GetSSubFormat('q','','k2')}×a^4`
- `GLS_ti` 运算 `*` → `${GetSSubFormat('σ','','w')}`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('σ','','w1')}`
- `GLS_ti` 运算 `*` → `q`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('q','','1')}`
- `GLS_ti` 运算 `*` → `t`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('t','','1')}`
- `GLS_ti` 运算 `*` → `η`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('η','','1')}`
- `GLS_ti` 运算 `+` → `    ${GetEQFormat(0)}${GetSSubFormat('σ','','w2')} = \\f(6×m×${GetSSubFormat('q','','2')}`
- `GLS_ti` 运算 `+` → `    ${GLS_STRESSI}N/mm^2${GetLess(IsNLarge(GLS_STRESSI,GLS_fgwi))}${GetEQSSubFormat('f','`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（20）：`GLS_COMP`, `GLS_COMPK`, `GLS_DESC`, `GLS_FWLESS`, `GLS_STRESSI`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwko`, `GLS_qwo`, `GLS_ti`, `GLS_to`, `GLS_θwi`, `GLS_θwo`, `GLS_σwi`, `GLS_σwo`

## `MG_WSTRENGTHXZJD`（iid 315，2017 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 20 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetNg` | 3 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [2] | 2 | 是 | `FUN_180298f50` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |
| `LAnd` | 1 | [2] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `=${GLS_fgwo}N/mm^2`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `    荷载分配计算\:    q1=${IsLarge(GLS_tmg,3.0):+1.1×}q×${GetEQFormat(0)}\\f(t1^3,t1^3+t2^3)${`
- `IsLarge(GLS_tmg,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tmg,3.0)` 运算 `+` → `1.1×`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    θ2=${GetEQFormat(0)}\\f(qk2×a^4×10^9,E×t2^4)${GetEQFormat(1)}      =${GLS_θwi}    查`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    σw2=${GetEQFormat(0)}\\f(6×m×q2×a^2×1000,t2^2)${GetEQFormat(1)}×η2          =${GLS_σ`
- `GLS_ti` 运算 `+` → `    ${GLS_STRESSI}N/mm^2${GetLess(IsNLarge(GLS_STRESSI,GLS_fgwi))}ｆg=${GLS_fgwi}N/mm^2`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（18）：`GLS_COMP`, `GLS_DESC`, `GLS_FWLESS`, `GLS_STRESSI`, `GLS_STRESSO`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwko`, `GLS_qwo`, `GLS_ti`, `GLS_to`, `GLS_θwi`, `GLS_θwo`, `GLS_σwi`, `GLS_σwo`

## `MG_WSTRENGTHTHREELAYER`（iid 316，11328 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 4 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 96 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 71 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [2] | 2 | 是 | `FUN_180298f50` |
| `GetSSubFormat` | 101 | [3] | 3 | 是 | `FUN_180254620` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},${GetEQSSubFormat('r','`
- `LAnd(IsNLarge(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑外层夹胶先组合然后与内层再组合的原则    ${GetEQSSubFormat('t','','ew')}\:外层夹胶组合等效`
- `LAnd(IsNLess(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ${GetEQSSubFormat('t','','en')}\:内层夹胶组合`
- `LAnd(IsNLess(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC}    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（29）：`GLS_COMP`, `GLS_DESC`, `GLS_FWLESS`, `GLS_RGLASS0`, `GLS_RGLASS1`, `GLS_RGLASS2`, `GLS_STRESSI`, `GLS_STRESSM`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwm`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwkm`, `GLS_qwko`, `GLS_qwm`, `GLS_qwo`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwi`, `GLS_θwm`, `GLS_θwo`, `GLS_σwi`, `GLS_σwm`, `GLS_σwo`

## `MG_WSTRENGTHTHREELAYERJD`（iid 317，11081 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 4 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 96 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 68 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [2] | 2 | 是 | `FUN_180298f50` |
| `GetSSubFormat` | 101 | [3] | 3 | 是 | `FUN_180254620` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},${GetEQSSubFormat('r','`
- `LAnd(IsNLarge(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑外层夹胶先组合然后与内层再组合的原则    ${GetEQSSubFormat('t','','ew')}\:外层夹胶组合等效`
- `LAnd(IsNLess(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ${GetEQSSubFormat('t','','en')}\:内层夹胶组合`
- `LAnd(IsNLess(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC}    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（28）：`GLS_COMP`, `GLS_DESC`, `GLS_FWLESS`, `GLS_RGLASS0`, `GLS_RGLASS1`, `GLS_RGLASS2`, `GLS_STRESSI`, `GLS_STRESSM`, `GLS_STRESSO`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwm`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwkm`, `GLS_qwko`, `GLS_qwm`, `GLS_qwo`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_θwi`, `GLS_θwm`, `GLS_θwo`, `GLS_σwi`, `GLS_σwm`, `GLS_σwo`

## `MG_WSTRENGTHTHLAYERCG`（iid 318，3774 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetEQFormat` | 24 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 19 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `IsNLess` | 2 | [2] | None | 否 | `None` |
| `Mul` | 13 | [2] | None | 否 | `None` |

条件块：
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNLess(tml,3)` 运算 `+` → `1.1×${IsNLess(tm,3):+0.95^3×}`
- `IsNLess(tm,3)` 运算 `+` → `0.95^3×`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwo`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwo)}`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwm`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwi`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `FWLESS` 运算 `*` → `不`

普通变量（29）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwm`, `fgwo`, `qw`, `qwi`, `qwm`, `qwo`, `ti`, `tmg`, `to`, `γGf`, `ζto`, `θwi`, `θwm`, `θwo`, `σwki`, `σwkm`, `σwko`, `ω`

## `MG_WSTRENGTHTHLAYERCGJD`（iid 319，3774 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetEQFormat` | 24 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 19 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `IsNLess` | 2 | [2] | None | 否 | `None` |
| `Mul` | 13 | [2] | None | 否 | `None` |

条件块：
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNLess(tml,3)` 运算 `+` → `1.1×${IsNLess(tm,3):+0.95^3×}`
- `IsNLess(tm,3)` 运算 `+` → `0.95^3×`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwo`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwo)}`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwm`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwi`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `FWLESS` 运算 `*` → `不`

普通变量（29）：`Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `SNOW`, `ShapeAngle`, `al`, `awl`, `bl`, `fgwi`, `fgwm`, `fgwo`, `qw`, `qwi`, `qwm`, `qwo`, `ti`, `tmg`, `to`, `γGf`, `ζto`, `θwi`, `θwm`, `θwo`, `σwki`, `σwkm`, `σwko`, `ω`

## `WSTRENGTHYP`（iid 362，2554 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 10 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `Mul` | 5 | [2] | None | 否 | `None` |

条件块：
- `ISDOUBLEW` 运算 `*` → `=${fgwo}N/mm^2`
- `IsEqual(PRJGLASS,1)` 运算 `+` → `玻璃计算跨度`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `玻璃短边边长`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `\r\n   b\: 玻璃长边边长\: ${bl}m`
- `ISDOUBLEW` 运算 `*` → `t\: 玻璃板块厚度\: ${to}mm`
- `ISDOUBLEW` 运算 `+` → `ti\:  ${GLASSSTRUCTNAME}内侧玻璃厚度为\: ${ti}(mm) \r\n`
- `ISDOUBLEW` 运算 `+` → `to\:  ${GLASSSTRUCTNAME}外侧玻璃厚度为\: ${to}(mm)`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `ISDOUBLEW` 运算 `+` → `\r\n   荷载分配计算\r\n   qo=${ISHOLW:+1.1×}q×to^3/(to^3+ti^3)\r\n     =${ISHOLW:+1.1×}${qw}×${t`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISDOUBLEW` 运算 `*` → `θ`
- `ISDOUBLEW` 运算 `+` → `θo`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `\r\n   θi=qi×${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}^4×10^9/E/ti^4\r\n     =${`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `η${ISDOUBLEW:+o}×`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwo)}×`
- `ISDOUBLEW` 运算 `+` → `\r\n   σwi=6×m×${Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):*ηi×}qi×${IsNEqual(PRJGLASS,2`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηi×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwi)}×`
- `ISDOUBLEW` 运算 `+` → `\r\n    ${σwi}N/mm^2${GetLess(FWILESS)}ｆg=${fgwi}N/mm^2`
- `FWLESS` 运算 `*` → `不`

普通变量（20）：`Ew`, `FWLESS`, `GLASSDESC`, `GLASSSTRUCTNAME`, `ISDOUBLEW`, `ISHOLW`, `al`, `awl`, `bl`, `fgwi`, `fgwo`, `qw`, `qwi`, `qwo`, `ti`, `to`, `θwi`, `θwo`, `σwi`, `σwo`

## `WSTRENGTHYPTHREELAYER`（iid 363，3182 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 19 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `IsNLess` | 2 | [2] | None | 否 | `None` |
| `Mul` | 13 | [2] | None | 否 | `None` |

条件块：
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNLess(tml,3)` 运算 `+` → `1.1×${IsNLess(tm,3):+0.95^3×}`
- `IsNLess(tm,3)` 运算 `+` → `0.95^3×`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwo×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `${GetNg(θwo)}×`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwm×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `ηwi×`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `FWLESS` 运算 `*` → `不`

普通变量（24）：`Ew`, `FWLESS`, `GLASSDESC`, `GLASSSTRUCTNAME`, `al`, `awl`, `bl`, `fgwi`, `fgwm`, `fgwo`, `qw`, `qwi`, `qwm`, `qwo`, `ti`, `tmg`, `to`, `ζto`, `θwi`, `θwm`, `θwo`, `σwki`, `σwkm`, `σwko`

## `MG_WSTRENGTHYP`（iid 364，3018 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetEQFormat` | 24 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 10 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `Mul` | 5 | [2] | None | 否 | `None` |

条件块：
- `ISDOUBLEW` 运算 `*` → `=${fgwo}N/mm^2`
- `IsEqual(PRJGLASS,1)` 运算 `+` → `玻璃计算跨度`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `玻璃短边边长`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `\r\n   b\: 玻璃长边边长\: ${bl}m`
- `ISDOUBLEW` 运算 `*` → `t\: 玻璃板块厚度\: ${to}mm`
- `ISDOUBLEW` 运算 `+` → `ti\:  ${GLASSSTRUCTNAME}内侧玻璃厚度为\: ${ti}(mm) \r\n`
- `ISDOUBLEW` 运算 `+` → `to\:  ${GLASSSTRUCTNAME}外侧玻璃厚度为\: ${to}(mm)`
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `ISDOUBLEW` 运算 `+` → `\r\n   荷载分配计算\r\n   qo=${ISHOLW:+1.1×}q×${GetEQFormat(0)}\\f(to^3,to^3+ti^3)${GetEQFormat(`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISHOLW` 运算 `+` → `1.1×`
- `ISDOUBLEW` 运算 `*` → `θ`
- `ISDOUBLEW` 运算 `+` → `θo`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `\r\n   θi=qi×${GetEQFormat(0)}\\f(${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}^4×10`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `ISDOUBLEW` 运算 `+` → `o`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×η${ISDOUBLEW:+o}`
- `ISDOUBLEW` 运算 `+` → `o`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwo)}`
- `ISDOUBLEW` 运算 `+` → `\r\n   σwi=${GetEQFormat(0)}\\f(6×m×qi×${IsNEqual(PRJGLASS,2):+a}${IsEqual(PRJGLASS,2):+b}`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηi`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwi)}`
- `ISDOUBLEW` 运算 `+` → `\r\n    ${σwi}N/mm^2${GetLess(FWILESS)}ｆg=${fgwi}N/mm^2`
- `FWLESS` 运算 `*` → `不`

普通变量（20）：`Ew`, `FWLESS`, `GLASSDESC`, `GLASSSTRUCTNAME`, `ISDOUBLEW`, `ISHOLW`, `al`, `awl`, `bl`, `fgwi`, `fgwo`, `qw`, `qwi`, `qwo`, `ti`, `to`, `θwi`, `θwo`, `σwi`, `σwo`

## `MG_WSTRENGTHYPTHREELAYER`（iid 365，3646 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetEQFormat` | 24 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 19 | [2] | None | 否 | `None` |
| `IsNEqual` | 7 | [2] | None | 否 | `None` |
| `IsNLess` | 2 | [2] | None | 否 | `None` |
| `Mul` | 13 | [2] | None | 否 | `None` |

条件块：
- `IsNEqual(PRJGLASS,1)` 运算 `+` → `,按边长比a/b查表${IsEqual(PRJGLASS,0):+6.1.2-1}${Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2)):+8`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `6.1.2-1`
- `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `+` → `8.1.5-1`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNLess(tml,3)` 运算 `+` → `1.1×${IsNLess(tm,3):+0.95^3×}`
- `IsNLess(tm,3)` 运算 `+` → `0.95^3×`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `0.95^3×(`
- `Mul(IsNLess(tm,3),IsNLess(tml,3))` 运算 `+` → `)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-3)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-4)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwo`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×${GetNg(θwo)}`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwm`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `IsNEqual(PRJGLASS,2)` 运算 `+` → `a`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `b`
- `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` 运算 `*` → `×ηwi`
- `IsEqual(PRJGLASS,0)` 运算 `+` → `(JGJ102-2003  6.1.2-1)`
- `IsEqual(PRJGLASS,2)` 运算 `+` → `(JGJ102-2003  8.1.5-1)`
- `FWLESS` 运算 `*` → `不`

普通变量（24）：`Ew`, `FWLESS`, `GLASSDESC`, `GLASSSTRUCTNAME`, `al`, `awl`, `bl`, `fgwi`, `fgwm`, `fgwo`, `qw`, `qwi`, `qwm`, `qwo`, `ti`, `tmg`, `to`, `ζto`, `θwi`, `θwm`, `θwo`, `σwki`, `σwkm`, `σwko`

## `WSTRENGTHXZPS`（iid 496，2835 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 3 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 11 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `=${GLSPS_fgwo}N/mm^2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `to\:外层玻璃厚度\: ${GLSPS_to}mm    ti\:内层玻璃厚度\: ${GLSPS_ti}mm`
- `LNot(LOr(GLSPS_tmg,GLSPS_ti))` 运算 `+` → `to\:玻璃板块厚度为\: ${GLSPS_to}(mm)`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\: 折减系数,根据参数θ查表6.1.2-2    `
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `    荷载分配计算\:    qo=${IsLarge(GLSPS_tm,3.0):+1.1×}q×to^3/(to^3+ti^3)      =${IsLarge(GLS`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `1.1×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    θ${GLSPS_ti:+o}=qk${GLSPS_ti:+o}×b^4×10^9/E/t${GLSPS_ti:+o}^4      (JGJ102-200`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `    θi=qki×b^4×10^9/E/ti^4      =${GLSPS_qwki}×${GLSPS_awl}^4×10^9/${GetE(GLOB_BOARDMATE`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η${GLSPS_ti:+o}`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}×${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `×${Div(GLSPS_awl,2.0)}`
- `GLSPS_ti` 运算 `+` → `    σwi=6×m×qi${IsEqual(GLSPS_LINKNUM,4):+×ηi}×b^2×1000/ti^2          =6×${GetSMr(GLSPS_`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×ηi`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwi)}×${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `×${Div(GLSPS_awl,2.0)}`
- `GLSPS_ti` 运算 `+` → `    ${GLSPS_STRESSI}N/mm^2${GetLess(IsNLarge(GLSPS_STRESSI,GLSPS_fgwi))}ｆg=${GLSPS_fgwi}N`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（22）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_STRESSI`, `GLSPS_STRESSO`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwko`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwo`

## `WSTRENGTHXZPSJD`（iid 497，2519 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 2 | [2] | None | 否 | `None` |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 3 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 9 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `=${GLSPS_fgwo}N/mm^2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `to\:${GLSPS_STRUCT}外层玻璃厚度\: ${GLSPS_to}mm    ti\:${GLSPS_STRUCT}内层玻璃厚度\: ${GLSPS_ti}mm`
- `LNot(LOr(GLSPS_tmg,GLSPS_ti))` 运算 `+` → `to\:${GLSPS_STRUCT}玻璃板块厚度为\: ${GLSPS_to}(mm)`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\: 折减系数,根据参数θ查表6.1.2-2    `
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `    荷载分配计算\:    qo=${IsLarge(GLSPS_tm,3.0):+1.1×}q×to^3/(to^3+ti^3)      =${IsLarge(GLS`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `1.1×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    θ${GLSPS_ti:+o}=qk${GLSPS_ti:+o}×b^4×10^9/E/t${GLSPS_ti:+o}^4      (JGJ102-200`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `    θi=qki×b^4×10^9/E/ti^4      =${GLSPS_θwi}    查表6.1.2-2 得ηi = ${GetNg(GLSPS_θwi)} `
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η${GLSPS_ti:+o}`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}×${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `×${Div(GLSPS_awl,2.0)}`
- `GLSPS_ti` 运算 `+` → `    σwi=6×m×qi${IsEqual(GLSPS_LINKNUM,4):+×ηi}×b^2×1000/ti^2          =${GLSPS_σwi}N/mm^`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×ηi`
- `GLSPS_ti` 运算 `+` → `    ${GLSPS_STRESSI}N/mm^2${GetLess(IsNLarge(GLSPS_STRESSI,GLSPS_fgwi))}ｆg=${GLSPS_fgwi}N`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（23）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_STRESSI`, `GLSPS_STRESSO`, `GLSPS_STRUCT`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwko`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwo`

## `WSTRENGTHTHREELAYERPS`（iid 498，5589 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 2 | [2] | None | 否 | `None` |
| `GetE` | 4 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 11 | [2] | None | 否 | `None` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\:折减系数,根据参数θ查表6.1.2-2     `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =t1^3/(t1^3+t2^3+t3^3)       =${GLSPS_to}^3/(${GL`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑外层夹胶先组合然后与内层再组合的原则,    tew\:外层夹胶组合等效厚度    tew=(t1^3+t2^3)^(1`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ten\:内层夹胶组合等效厚度    ten=(t2^3+t3^3)^(`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC}    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =1.1×t1^3/(t1^3+t2^3+t3^3`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    风荷载标准值作用下    θ1=qk1×a^4×10^9/E/t1^4      (JGJ102-2003  8.1.5-4)     =${GLSPS`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η3`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（32）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_RGLASS0`, `GLSPS_RGLASS1`, `GLSPS_RGLASS2`, `GLSPS_STRESSI`, `GLSPS_STRESSM`, `GLSPS_STRESSO`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwm`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwkm`, `GLSPS_qwko`, `GLSPS_qwm`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwm`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwm`, `GLSPS_σwo`

## `WSTRENGTHTHREELAYERPSJD`（iid 499，4873 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 2 | [2] | None | 否 | `None` |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 11 | [2] | None | 否 | `None` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\:折减系数,根据参数θ查表6.1.2-2     `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =t1^3/(t1^3+t2^3+t3^3)       =${GLSPS_to}^3/(${GL`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑外层夹胶先组合然后与内层再组合的原则,    tew\:外层夹胶组合等效厚度    tew=(t1^3+t2^3)^(1`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ten\:内层夹胶组合等效厚度    ten=(t2^3+t3^3)^(`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC}    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =1.1×t1^3/(t1^3+t2^3+t3^3`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    风荷载标准值作用下    θ1=qk1×a^4×10^9/E/t1^4      (JGJ102-2003  8.1.5-4)     =${GLSPS`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η3`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（32）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_RGLASS0`, `GLSPS_RGLASS1`, `GLSPS_RGLASS2`, `GLSPS_STRESSI`, `GLSPS_STRESSM`, `GLSPS_STRESSO`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwm`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwkm`, `GLSPS_qwko`, `GLSPS_qwm`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwm`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwm`, `GLSPS_σwo`

## `MG_WSTRENGTHXZPS`（iid 508，3399 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 3 | [2] | None | 否 | `None` |
| `GetE` | 3 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 24 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 3 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 13 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `=${GLSPS_fgwo}N/mm^2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `to\:${GLSPS_STRUCT}外层玻璃厚度\: ${GLSPS_to}mm    ti\:${GLSPS_STRUCT}内层玻璃厚度\: ${GLSPS_ti}mm`
- `LNot(LOr(GLSPS_tmg,GLSPS_ti))` 运算 `+` → `to\:${GLSPS_STRUCT}玻璃板块厚度为\: ${GLSPS_to}(mm)`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\: 折减系数,根据参数θ查表6.1.2-2    `
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `    荷载分配计算\:    qo=${IsLarge(GLSPS_tmg,3.0):+1.1×}q×${GetEQFormat(0)}\\f(to^3,to^3+ti^3)`
- `IsLarge(GLSPS_tmg,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLSPS_tmg,3.0)` 运算 `+` → `1.1×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    θ${GLSPS_ti:+o}=${GetEQFormat(0)}\\f(qk${GLSPS_ti:+o}×a^4×10^9,E×t${GLSPS_ti:+`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `    θi=${GetEQFormat(0)}\\f(qki×a^4×10^9,E×ti^4)${GetEQFormat(1)}      =${GetEQFormat(0)`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η${GLSPS_ti:+o}`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}`
- `GLSPS_ti` 运算 `+` → `    σwi=${GetEQFormat(0)}\\f(6×m×qi×b^2×1000,ti^2)${GetEQFormat(1)}${IsEqual(GLSPS_LINKNU`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×ηi`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwi)}`
- `GLSPS_ti` 运算 `+` → `    ${GLSPS_STRESSI}N/mm^2${GetLess(IsNLarge(GLSPS_STRESSI,GLSPS_fgwi))}ｆg=${GLSPS_fgwi}N`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（23）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_STRESSI`, `GLSPS_STRESSO`, `GLSPS_STRUCT`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwko`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwo`

## `MG_WSTRENGTHXZPSJD`（iid 509，2876 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 2 | [2] | None | 否 | `None` |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 18 | [1] | 1 | 是 | `FUN_180252770` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 3 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `IsEqual` | 10 | [2] | None | 否 | `None` |
| `IsLarge` | 2 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLSPS_ti` 运算 `*` → `=${GLSPS_fgwo}N/mm^2`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `to\:${GLSPS_STRUCT}外层玻璃厚度\: ${GLSPS_to}mm    ti\:${GLSPS_STRUCT}内层玻璃厚度\: ${GLSPS_ti}mm`
- `LNot(LOr(GLSPS_tmg,GLSPS_ti))` 运算 `+` → `to\:${GLSPS_STRUCT}玻璃板块厚度为\: ${GLSPS_to}(mm)`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\: 折减系数,根据参数θ查表6.1.2-2    `
- `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` 运算 `+` → `    荷载分配计算\:    qo=${IsLarge(GLSPS_tm,3.0):+1.1×}q×${GetEQFormat(0)}\\f(to^3,to^3+ti^3)$`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLSPS_tm,3.0)` 运算 `+` → `1.1×`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    θ${GLSPS_ti:+o}=${GetEQFormat(0)}\\f(qk${GLSPS_ti:+o}×a^4×10^9,E×t${GLSPS_ti:+`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `    θi=${GetEQFormat(0)}\\f(qki×a^4×10^9,E×ti^4)${GetEQFormat(1)}      =${GLSPS_θwi}   `
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×η${GLSPS_ti:+o}`
- `GLSPS_ti` 运算 `+` → `o`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}`
- `GLSPS_ti` 运算 `+` → `    σwi=${GetEQFormat(0)}\\f(6×m×qi×b^2×1000,ti^2)${GetEQFormat(1)}${IsEqual(GLSPS_LINKNU`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×ηi`
- `GLSPS_ti` 运算 `+` → `    ${GLSPS_STRESSI}N/mm^2${GetLess(IsNLarge(GLSPS_STRESSI,GLSPS_fgwi))}ｆg=${GLSPS_fgwi}N`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（25）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_STRESSI`, `GLSPS_STRESSO`, `GLSPS_STRUCT`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwko`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwo`, `ti`, `to`

## `MG_WSTRENGTHTHREELAYERPS`（iid 510，12064 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 2 | [2] | None | 否 | `None` |
| `GetE` | 4 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 96 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 73 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `GetSSubFormat` | 101 | [3] | 3 | 是 | `FUN_180254620` |
| `IsEqual` | 11 | [2] | None | 否 | `None` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\:折减系数,根据参数θ查表6.1.2-2     `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},${GetEQSSubFormat('r','`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑外层夹胶先组合然后与内层再组合的原则    ${GetEQSSubFormat('t','','ew')}\:外层夹胶组合`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ${GetEQSSubFormat('t','','en')}\:内层夹胶`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC}    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    风荷载标准值作用下    ${GetEQSSubFormat('θ','','1')}=${GetEQFormat(0)}\\f(${GetSSubFor`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetEQSSubFormat('η','','1')}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetEQSSubFormat('η','','2')}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetEQSSubFormat('η','','3')}`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（32）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_RGLASS0`, `GLSPS_RGLASS1`, `GLSPS_RGLASS2`, `GLSPS_STRESSI`, `GLSPS_STRESSM`, `GLSPS_STRESSO`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwm`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwkm`, `GLSPS_qwko`, `GLSPS_qwm`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwm`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwm`, `GLSPS_σwo`

## `MG_WSTRENGTHTHREELAYERPSJD`（iid 511，11179 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `Div` | 2 | [2] | None | 否 | `None` |
| `GetE` | 2 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 80 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 73 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetNg` | 4 | [1] | 1 | 是 | `FUN_1802980c0` |
| `GetSMr` | 2 | [4] | 2 | 是 | `FUN_180298f50` |
| `GetSSubFormat` | 101 | [3] | 3 | 是 | `FUN_180254620` |
| `IsEqual` | 11 | [2] | None | 否 | `None` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `${GLSPS_bl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_bl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `8.1.5-1`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `η\:折减系数,根据参数θ查表6.1.2-2     `
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},${GetEQSSubFormat('r','`
- `LAnd(IsNLarge(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑外层夹胶先组合然后与内层再组合的原则    ${GetEQSSubFormat('t','','ew')}\:外层夹胶组合`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ${GetEQSSubFormat('t','','en')}\:内层夹胶`
- `LAnd(IsNLess(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLSPS_DESC}    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `参数θ计算\:    风荷载标准值作用下    ${GetEQSSubFormat('θ','','1')}=${GetEQFormat(0)}\\f(${GetSSubFor`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetEQSSubFormat('η','','1')}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GLSPS_awl}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `*` → `${Div(GLSPS_awl,2.0)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetNg(GLSPS_θwo)}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetEQSSubFormat('η','','2')}`
- `IsEqual(GLSPS_LINKNUM,4)` 运算 `+` → `×${GetEQSSubFormat('η','','3')}`
- `GLSPS_FWLESS` 运算 `*` → `不`

普通变量（32）：`GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_RGLASS0`, `GLSPS_RGLASS1`, `GLSPS_RGLASS2`, `GLSPS_STRESSI`, `GLSPS_STRESSM`, `GLSPS_STRESSO`, `GLSPS_Sh`, `GLSPS_Sv`, `GLSPS_al`, `GLSPS_awl`, `GLSPS_bl`, `GLSPS_fgwi`, `GLSPS_fgwm`, `GLSPS_fgwo`, `GLSPS_qwi`, `GLSPS_qwki`, `GLSPS_qwkm`, `GLSPS_qwko`, `GLSPS_qwm`, `GLSPS_qwo`, `GLSPS_ti`, `GLSPS_tmg`, `GLSPS_to`, `GLSPS_θwi`, `GLSPS_θwm`, `GLSPS_θwo`, `GLSPS_σwi`, `GLSPS_σwm`, `GLSPS_σwo`

## `WSTRENGTHTWOSIDEXZ`（iid 1089，1702 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `IsLarge` | 4 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `=${GLS_fgwo}N/mm^2`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `t1\:${GLS_STRUCTDESC}外层玻璃厚度\: ${GLS_to}mm    t2\:${GLS_STRUCTDESC}内层玻璃厚度\: ${GLS_ti}mm`
- `LNot(LOr(GLS_tmg,GLS_ti))` 运算 `+` → `t1\:${GLS_STRUCTDESC}玻璃板块厚度为\: ${GLS_to}(mm)`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `    荷载分配计算\:    q1=${IsLarge(GLS_tm,3.0):+1.1×}q×t1^3/(t1^3+t2^3)      =${IsLarge(GLS_t`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `1`
- `GLS_ti` 运算 `+` → `    σw2=6×m×q2×a^2×1000/t2^2          =6×0.125×${GLS_qwi}×${GLS_awl}^2×1000/${GLS_ti}^2`
- `GLS_ti` 运算 `+` → `    ${GLS_STRESSI}N/mm^2${GetLess(IsNLarge(GLS_STRESSI,GLS_fgwi))}ｆg=${GLS_fgwi}N/mm^2`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（18）：`GLS_COMP`, `GLS_COMPK`, `GLS_DESC`, `GLS_FWLESS`, `GLS_STRESSI`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwko`, `GLS_qwo`, `GLS_ti`, `GLS_to`, `GLS_σwi`, `GLS_σwo`

## `MG_WSTRENGTHTWOSIDEXZ`（iid 1090，3065 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 26 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 6 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 2 | [1] | 2 | 是 | `FUN_180254010` |
| `GetSSubFormat` | 26 | [3] | 3 | 是 | `FUN_180254620` |
| `IsLarge` | 4 | [2] | None | 否 | `None` |
| `LAnd` | 2 | [2] | None | 否 | `None` |
| `LNot` | 1 | [1] | None | 否 | `None` |

条件块：
- `GLS_ti` 运算 `*` → `=${GLS_fgwo}N/mm^2`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `${GetEQSSubFormat('t','','1')}\:${GLS_STRUCTDESC}外层玻璃厚度\: ${GLS_to}mm    ${GetEQSSubForma`
- `LNot(LOr(GLS_tmg,GLS_ti))` 运算 `+` → `${GetEQSSubFormat('t','','1')}\:${GLS_STRUCTDESC}玻璃板块厚度为\: ${GLS_to}(mm)`
- `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` 运算 `+` → `    荷载分配计算\:    ${GetEQFormat(0)}${GetSSubFormat('q','','1')}=${IsLarge(GLS_tm,3.0):+1.1`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `IsLarge(GLS_tm,3.0)` 运算 `+` → `1.1×`
- `GLS_ti` 运算 `*` → `${GetSSubFormat('σ','','w')}`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('σ','','w1')}`
- `GLS_ti` 运算 `*` → `q`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('q','','1')}`
- `GLS_ti` 运算 `*` → `t`
- `GLS_ti` 运算 `+` → `${GetSSubFormat('t','','1')}`
- `GLS_ti` 运算 `+` → `    ${GetEQFormat(0)}${GetSSubFormat('σ','','w2')}=\\f(6×m×${GetSSubFormat('q','','2')}×a`
- `GLS_ti` 运算 `+` → `    ${GLS_STRESSI}N/mm^2${GetLess(IsNLarge(GLS_STRESSI,GLS_fgwi))}${GetEQSSubFormat('f','`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（18）：`GLS_COMP`, `GLS_COMPK`, `GLS_DESC`, `GLS_FWLESS`, `GLS_STRESSI`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwko`, `GLS_qwo`, `GLS_ti`, `GLS_to`, `GLS_σwi`, `GLS_σwo`

## `WSTRENGTHTWOSIDETHREELAYER`（iid 1093，4118 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =t1^3/(t1^3+t2^3+t3^3)       =${GLS_to}^3/(${GLS_`
- `LAnd(IsNLarge(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑外层夹胶先组合然后与内层再组合的原则,    tew\:外层夹胶组合等效厚度    tew=(t1^3+t2^3)^(1/3`
- `LAnd(IsNLess(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ten\:内层夹胶组合等效厚度    ten=(t2^3+t3^3)^(1/`
- `LAnd(IsNLess(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC}    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =1.1×t1^3/(t1^3+t2^3+t3^3)`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（26）：`GLS_COMP`, `GLS_DESC`, `GLS_FWLESS`, `GLS_RGLASS0`, `GLS_RGLASS1`, `GLS_RGLASS2`, `GLS_STRESSI`, `GLS_STRESSM`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwm`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwkm`, `GLS_qwko`, `GLS_qwm`, `GLS_qwo`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_σwi`, `GLS_σwm`, `GLS_σwo`

## `MG_WSTRENGTHTWOSIDETHREELAYER`（iid 1094，9919 B）

| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |
| --- | --- | --- | --- | --- | --- |
| `GetE` | 1 | [1] | 1 | 是 | `FUN_180271340` |
| `GetEQFormat` | 84 | [1] | 1 | 是 | `FUN_180252770` |
| `GetEQSSubFormat` | 62 | [3] | 3 | 是 | `FUN_180252940` |
| `GetLess` | 3 | [1] | 2 | 是 | `FUN_180254010` |
| `GetMax` | 1 | [2] | None | 否 | `None` |
| `GetMin` | 1 | [2] | None | 否 | `None` |
| `GetSSubFormat` | 95 | [3] | 3 | 是 | `FUN_180254620` |
| `LAnd` | 4 | [2] | None | 否 | `None` |

条件块：
- `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},${GetEQSSubFormat('r','`
- `LAnd(IsNLarge(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑外层夹胶先组合然后与内层再组合的原则    ${GetEQSSubFormat('t','','ew')}\:外层夹胶组合等效`
- `LAnd(IsNLess(GLS_tm,3),IsNLarge(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ${GetEQSSubFormat('t','','en')}\:内层夹胶组合`
- `LAnd(IsNLess(GLS_tm,3),IsNLess(GLS_tml,3))` 运算 `+` → `    当前玻璃结构为${GLS_DESC}    ${GetEQSSubFormat('r','','1')},${GetEQSSubFormat('r','','2')},`
- `GLS_FWLESS` 运算 `*` → `不`

普通变量（26）：`GLS_COMP`, `GLS_DESC`, `GLS_FWLESS`, `GLS_RGLASS0`, `GLS_RGLASS1`, `GLS_RGLASS2`, `GLS_STRESSI`, `GLS_STRESSM`, `GLS_STRESSO`, `GLS_STRUCTDESC`, `GLS_awl`, `GLS_fgwi`, `GLS_fgwm`, `GLS_fgwo`, `GLS_qwi`, `GLS_qwki`, `GLS_qwkm`, `GLS_qwko`, `GLS_qwm`, `GLS_qwo`, `GLS_ti`, `GLS_tmg`, `GLS_to`, `GLS_σwi`, `GLS_σwm`, `GLS_σwo`

## 未解析（需继续取证）

- `IsEqual`：not in registry (MG_WSTRENGTH)；not in registry (MG_WSTRENGTHJD)；not in registry (MG_WSTRENGTHTHLAYERCG)；not in registry (MG_WSTRENGTHTHLAYERCGJD)；not in registry (MG_WSTRENGTHTHREELAYERPS)；not in registry (MG_WSTRENGTHTHREELAYERPSJD)；not in registry (MG_WSTRENGTHXZPS)；not in registry (MG_WSTRENGTHXZPSJD)；not in registry (MG_WSTRENGTHYP)；not in registry (MG_WSTRENGTHYPTHREELAYER)；not in registry (WSTRENGTH)；not in registry (WSTRENGTHJD)；not in registry (WSTRENGTHTHLAYERCG)；not in registry (WSTRENGTHTHLAYERCGJD)；not in registry (WSTRENGTHTHREELAYERPS)；not in registry (WSTRENGTHTHREELAYERPSJD)；not in registry (WSTRENGTHXZPS)；not in registry (WSTRENGTHXZPSJD)；not in registry (WSTRENGTHYP)；not in registry (WSTRENGTHYPTHREELAYER)（全库出现 916 次）
- `IsNEqual`：not in registry (MG_WSTRENGTH)；not in registry (MG_WSTRENGTHJD)；not in registry (MG_WSTRENGTHTHLAYERCG)；not in registry (MG_WSTRENGTHTHLAYERCGJD)；not in registry (MG_WSTRENGTHYP)；not in registry (MG_WSTRENGTHYPTHREELAYER)；not in registry (WSTRENGTH)；not in registry (WSTRENGTHJD)；not in registry (WSTRENGTHTHLAYERCG)；not in registry (WSTRENGTHTHLAYERCGJD)；not in registry (WSTRENGTHYP)；not in registry (WSTRENGTHYPTHREELAYER)（全库出现 789 次）
- `Mul`：not in registry (MG_WSTRENGTH)；not in registry (MG_WSTRENGTHJD)；not in registry (MG_WSTRENGTHTHLAYERCG)；not in registry (MG_WSTRENGTHTHLAYERCGJD)；not in registry (MG_WSTRENGTHYP)；not in registry (MG_WSTRENGTHYPTHREELAYER)；not in registry (WSTRENGTH)；not in registry (WSTRENGTHJD)；not in registry (WSTRENGTHTHLAYERCG)；not in registry (WSTRENGTHTHLAYERCGJD)；not in registry (WSTRENGTHYP)；not in registry (WSTRENGTHYPTHREELAYER)（全库出现 787 次）
- `GetMin`：not in registry (MG_WSTRENGTHTHREELAYER)；not in registry (MG_WSTRENGTHTHREELAYERJD)；not in registry (MG_WSTRENGTHTWOSIDETHREELAYER)；not in registry (MG_WSTRENGTHXZ)；not in registry (MG_WSTRENGTHXZJD)；not in registry (WSTRENGTHTHREELAYER)；not in registry (WSTRENGTHXZ)；not in registry (WSTRENGTHXZJD)（全库出现 328 次）
- `GetMax`：not in registry (MG_WSTRENGTHTHREELAYER)；not in registry (MG_WSTRENGTHTHREELAYERJD)；not in registry (MG_WSTRENGTHTWOSIDETHREELAYER)；not in registry (MG_WSTRENGTHXZ)；not in registry (MG_WSTRENGTHXZJD)；not in registry (WSTRENGTHTHREELAYER)；not in registry (WSTRENGTHXZ)；not in registry (WSTRENGTHXZJD)（全库出现 85 次）
- `LAnd`：not in registry (MG_WSTRENGTHTHREELAYER)；not in registry (MG_WSTRENGTHTHREELAYERJD)；not in registry (MG_WSTRENGTHTHREELAYERPS)；not in registry (MG_WSTRENGTHTHREELAYERPSJD)；not in registry (MG_WSTRENGTHTWOSIDETHREELAYER)；not in registry (MG_WSTRENGTHTWOSIDEXZ)；not in registry (MG_WSTRENGTHXZ)；not in registry (MG_WSTRENGTHXZJD)；not in registry (MG_WSTRENGTHXZPS)；not in registry (MG_WSTRENGTHXZPSJD)；not in registry (WSTRENGTHTHREELAYER)；not in registry (WSTRENGTHTHREELAYERJD)；not in registry (WSTRENGTHTHREELAYERPS)；not in registry (WSTRENGTHTHREELAYERPSJD)；not in registry (WSTRENGTHTWOSIDETHREELAYER)；not in registry (WSTRENGTHTWOSIDEXZ)；not in registry (WSTRENGTHXZ)；not in registry (WSTRENGTHXZJD)；not in registry (WSTRENGTHXZPS)；not in registry (WSTRENGTHXZPSJD)（全库出现 271 次）
- `LNot`：not in registry (MG_WSTRENGTHTWOSIDEXZ)；not in registry (MG_WSTRENGTHXZ)；not in registry (MG_WSTRENGTHXZPS)；not in registry (MG_WSTRENGTHXZPSJD)；not in registry (WSTRENGTHTWOSIDEXZ)；not in registry (WSTRENGTHXZ)；not in registry (WSTRENGTHXZPS)；not in registry (WSTRENGTHXZPSJD)（全库出现 15 次）
- `IsLarge`：not in registry (MG_WSTRENGTHTWOSIDEXZ)；not in registry (MG_WSTRENGTHXZ)；not in registry (MG_WSTRENGTHXZJD)；not in registry (MG_WSTRENGTHXZPS)；not in registry (MG_WSTRENGTHXZPSJD)；not in registry (WSTRENGTHTWOSIDEXZ)；not in registry (WSTRENGTHXZ)；not in registry (WSTRENGTHXZJD)；not in registry (WSTRENGTHXZPS)；not in registry (WSTRENGTHXZPSJD)（全库出现 387 次）
- `IsNLess`：not in registry (MG_WSTRENGTHTHLAYERCG)；not in registry (MG_WSTRENGTHTHLAYERCGJD)；not in registry (MG_WSTRENGTHYPTHREELAYER)；not in registry (WSTRENGTHTHLAYERCG)；not in registry (WSTRENGTHTHLAYERCGJD)；not in registry (WSTRENGTHYPTHREELAYER)（全库出现 42 次）
- `Div`：not in registry (MG_WSTRENGTHTHREELAYERPS)；not in registry (MG_WSTRENGTHTHREELAYERPSJD)；not in registry (MG_WSTRENGTHXZPS)；not in registry (MG_WSTRENGTHXZPSJD)；not in registry (WSTRENGTHTHREELAYERPS)；not in registry (WSTRENGTHTHREELAYERPSJD)；not in registry (WSTRENGTHXZPS)；not in registry (WSTRENGTHXZPSJD)（全库出现 134 次）

## 可变参数节点（形参个数不参与判定）

- `GetSMr`：4 args in MG_WSTRENGTH (registry arity 2)；4 args in MG_WSTRENGTHJD (registry arity 2)；4 args in MG_WSTRENGTHTHLAYERCG (registry arity 2)；4 args in MG_WSTRENGTHTHLAYERCGJD (registry arity 2)
- `GetLess`：1 args in MG_WSTRENGTH (registry arity 2)；1 args in MG_WSTRENGTHJD (registry arity 2)；1 args in MG_WSTRENGTHTHLAYERCG (registry arity 2)；1 args in MG_WSTRENGTHTHLAYERCGJD (registry arity 2)

## 输入面（按前缀归类）

| 前缀 | 不同符号数 | 符号 |
| --- | --- | --- |
| `other` | 36 | `Ew`, `FWLESS`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME`, `ISDOUBLEW`, `ISHOLW`, `IsLPeak` … |
| `GLSPS` | 33 | `GLSPS_COMP`, `GLSPS_DESC`, `GLSPS_FWLESS`, `GLSPS_RGLASS0`, `GLSPS_RGLASS1`, `GLSPS_RGLASS2`, `GLSPS_STRESSI`, `GLSPS_STRESSM` … |
| `GLS` | 32 | `GLS_COMP`, `GLS_COMPK`, `GLS_DESC`, `GLS_FWLESS`, `GLS_RGLASS0`, `GLS_RGLASS1`, `GLS_RGLASS2`, `GLS_STRESSI` … |

## 分支面（条件块按判定函数归类）

| 判定 | 出现次数 | 例 |
| --- | --- | --- |
| `IsEqual(PRJGLASS,2)` | 108 | `+` b |
| `ISDOUBLEW` | 102 | `*` =${fgwo}N/mm^2 |
| `IsEqual(GLSPS_LINKNUM,4)` | 87 | `+` ${GLSPS_bl} |
| `GLS_ti` | 70 | `*` =${GLS_fgwo}N/mm^2 |
| `IsEqual(PRJGLASS,0)` | 60 | `+` 6.1.2-1 |
| `IsNEqual(PRJGLASS,2)` | 60 | `+` a |
| `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` | 48 | `*` η${ISDOUBLEW:+o}× |
| `Mul(IsNLess(tm,3),IsNLess(tml,3))` | 48 | `+` 0.95^3×( |
| `GLSPS_ti` | 48 | `*` =${GLSPS_fgwo}N/mm^2 |
| `IsNEqual(PRJGLASS,1)` | 24 | `+` 玻璃短边边长 |
| `IsLPeak` | 24 | `*` 风荷载与地震荷载 |
| `IsLarge(GLS_tm,3.0)` | 16 | `+` 1.1× |
| `Mul(IsNEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` | 12 | `+` 8.1.5-1 |
| `ISHOLW` | 12 | `+` 1.1× |
| `FWLESS` | 12 | `*` 不 |
| `GLS_FWLESS` | 12 | `*` 不 |
| `LAnd(IsEqual(GLS_tmg,0),GLS_ti)` | 10 | `+` t1\:${GLS_STRUCTDESC}外层玻璃厚度\: ${GLS_to}mm    t2\:${GLS_STRU |
| `LAnd(IsEqual(GLSPS_tmg,0),GLSPS_ti)` | 8 | `+` to\:外层玻璃厚度\: ${GLSPS_to}mm    ti\:内层玻璃厚度\: ${GLSPS_ti}mm |
| `GLSPS_FWLESS` | 8 | `*` 不 |
| `IsEqual(PRJGLASS,1)` | 6 | `+` 玻璃计算跨度 |
| `IsLarge(GLS_tmg,3.0)` | 6 | `+` 1.1× |
| `LAnd(IsNLarge(GLS_tm,3),IsNLarge(GLS_tml,3))` | 6 | `+`     r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =t1^3/(t1^3+t2^3+t3^ |
| `LAnd(IsNLarge(GLS_tm,3),IsNLess(GLS_tml,3))` | 6 | `+`     当前玻璃结构为${GLS_DESC},考虑外层夹胶先组合然后与内层再组合的原则,    tew\:外层夹胶组 |
| `LAnd(IsNLess(GLS_tm,3),IsNLarge(GLS_tml,3))` | 6 | `+`     当前玻璃结构为${GLS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ten\:内层夹胶 |
| `LAnd(IsNLess(GLS_tm,3),IsNLess(GLS_tml,3))` | 6 | `+`     当前玻璃结构为${GLS_DESC}    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数     |
| `IsNLess(tml,3)` | 6 | `+` 1.1×${IsNLess(tm,3):+0.95^3×} |
| `IsNLess(tm,3)` | 6 | `+` 0.95^3× |
| `IsLarge(GLSPS_tm,3.0)` | 6 | `+` 1.1× |
| `LNot(LOr(GLS_tmg,GLS_ti))` | 4 | `+` t1\:${GLS_STRUCTDESC}玻璃板块厚度为\: ${GLS_to}(mm) |
| `LNot(LOr(GLSPS_tmg,GLSPS_ti))` | 4 | `+` to\:玻璃板块厚度为\: ${GLSPS_to}(mm) |
| `LAnd(IsNLarge(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` | 4 | `+`     r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数    r1 =t1^3/(t1^3+t2^3+t3^ |
| `LAnd(IsNLarge(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` | 4 | `+`     当前玻璃结构为${GLSPS_DESC},考虑外层夹胶先组合然后与内层再组合的原则,    tew\:外层夹 |
| `LAnd(IsNLess(GLSPS_tm,3),IsNLarge(GLSPS_tml,3))` | 4 | `+`     当前玻璃结构为${GLSPS_DESC},考虑内层夹胶先组合然后与外层中空再组合的原则    ten\:内层 |
| `LAnd(IsNLess(GLSPS_tm,3),IsNLess(GLSPS_tml,3))` | 4 | `+`     当前玻璃结构为${GLSPS_DESC}    r1,r2,r3\:外层、中间层、内层玻璃荷载分配系数   |
| `IsLarge(GLSPS_tmg,3.0)` | 2 | `+` 1.1× |

## 节点库的调用面（同一次统计）

- 379 个注册节点里，**293 个在全部 2079 条公式模板中一次都没被调用**
- 关注节点的模板调用次数：`CalGlassStress`=0、`CalGlassPSStress`=0

即：模板层与节点层是**两套各自实现同一物理量的机制**，模板不走这些算量节点。

## 这一步能证明什么、不能证明什么

- 能证明：这些模板里出现的引擎调用名，哪些确实是注册节点、实参个数与注册元数对不对得上。
- 不能证明：调用顺序、默认值注入、查表数据来源，以及**这份模板是否就是运行时真正走的那条路**
  （同一物理量还存在于节点 `CalGlassDisp` 的自有算式中，两者参数化不同，谁被调用需另行取证）。
