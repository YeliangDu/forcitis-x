# 公式 ↔ 函数 ↔ 数据符号绑定（L7 第 2 步）

- 公式条目：**2082**（`计算模板`，`CONTEXT` 按 GBK 解码）
- 出现的调用型占位：**250** 个不同函数，其中 **81** 个命中 379 个 CXMap 注册名
- 出现的数据符号占位：**5285** 个不同符号；其中命中注册名的：**0** 个

> 结论：**公式里的"函数"才是节点，"符号"是数据**。379 个注册名中有 300 个从未在公式里以函数出现（多为内部/FE/绘图节点）。

## 命中注册名的公式函数（81 个，按次数）

| 函数 | 次数 |
| --- | --- |
| `GetEQFormat` | 9832 |
| `GetEQSSubFormat` | 7490 |
| `GetSSubFormat` | 5330 |
| `GetLess` | 1667 |
| `GetOKStr` | 1596 |
| `GetE` | 1081 |
| `GetFt` | 422 |
| `XDrawProfileEX` | 404 |
| `GetNg` | 284 |
| `GetM` | 226 |
| `GetDfnum` | 156 |
| `GetSMr` | 142 |
| `GetVr` | 119 |
| `GetUmax` | 106 |
| `GetDe` | 103 |
| `GetPoleDfnum` | 95 |
| `GetSDr` | 89 |
| `GetGama` | 81 |
| `GetBoltNumber` | 48 |
| `GetRecip` | 41 |
| `GetAlpha` | 40 |
| `GetI10` | 40 |
| `GetFp` | 36 |
| `GetLMCDfnum` | 32 |
| `GetBeamDfnum` | 29 |
| `GetLambda` | 28 |
| `GetSNRatio` | 26 |
| `GetBeamUmax` | 20 |
| `GetFyk` | 20 |
| `GetKk` | 20 |
| `GetBoltNvb` | 18 |
| `GetBackSlotStressRatio` | 16 |
| `GetBoltLinkDrawing` | 16 |
| `GetBoltNcb` | 16 |
| `GetSFAlpha1` | 16 |
| `GetWeldNASK` | 16 |
| `GetMidLayerANoise` | 14 |
| `DoDrawVSec` | 12 |
| `GetDesity` | 12 |
| `GetPoleLambda` | 12 |
| `GetWeldNMVI` | 12 |
| `GetBoardType` | 10 |
| `GetFc` | 10 |
| `GetFstk` | 10 |
| `GetAntiEQLevelString` | 9 |
| `GetAr` | 9 |
| `GetPoleDflim` | 9 |
| `GetBoltShearDesc` | 8 |
| `GetFcuk` | 8 |
| `GetSFAlpha2` | 8 |
| `GetSFAlpha3` | 8 |
| `GetTFromDB` | 8 |
| `XDrawProfile` | 8 |
| `GetAVmax` | 6 |
| `GetAmax` | 6 |
| `GetDSlopeShapeRatioRegionText` | 6 |
| `GetArchSnowRatio` | 4 |
| `GetBeamWTMax` | 4 |
| `GetCommonBoltDrawing` | 4 |
| `GetF02` | 4 |
| `GetFvk` | 4 |
| `GetLMCBeamDfnum` | 4 |
| `GetSlopeSnowRatio` | 4 |
| `GetWeldFa` | 4 |
| `GetWeldNASF` | 4 |
| `XDrawProMetalSheet_Wire` | 4 |
| `GetGlassXDesc` | 3 |
| `GetLarge` | 3 |
| `GetProjCodeInfo` | 3 |
| `GetBoltLength` | 2 |
| `GetEarBoardDrawing` | 2 |
| `GetEarthQuakeLevelString` | 2 |
| `GetGlassLayerDesc` | 2 |
| `GetHasAirLayer` | 2 |
| `GetSteelShapeRatio` | 2 |
| `GetWeldNASDesc` | 2 |
| `IsLargeConLevel` | 2 |
| `XDrawWeldNAS` | 2 |
| `XDrawWeldNMV1` | 2 |
| `XDrawWeldNV` | 2 |
| `GetRGlass` | 1 |

## 数据符号（Top 30，来自数据表或用户输入，不是节点）

| 符号 | 出现次数 |
| --- | --- |
| `GLS_to` | 302 |
| `γwf` | 267 |
| `GLS_ti` | 249 |
| `βE` | 244 |
| `γEf` | 230 |
| `ψE` | 202 |
| `ω0` | 184 |
| `γGf` | 182 |
| `GLS_tmg` | 180 |
| `LEANGLS_to` | 178 |
| `GLSPS_to` | 159 |
| `LEANGLS_ti` | 158 |
| `EqAMax` | 155 |
| `BEAM_Bh` | 136 |
| `GLSPS_ti` | 122 |
| `LEANGLS_tmg` | 112 |
| `GLUE_Hw` | 102 |
| `GLS_awl` | 91 |
| `REGION` | 90 |
| `WINFAN_Height` | 90 |
| `SGPGLS_H1` | 88 |
| `GLSPS_tmg` | 86 |
| `STONE_COMP` | 84 |
| `BREASTGLS_to` | 84 |
| `GLS_COMPK` | 80 |
| `μh` | 76 |
| `α2` | 76 |
| `SGPGLS_H2` | 76 |
| `BREASTGLS_ti` | 76 |
| `to` | 74 |

## 模板函数使用频次（Top 25）

| 函数 | 次数 |
| --- | --- |
| `GetEQFormat` | 9832 |
| `GetEQSSubFormat` | 7490 |
| `GetSSubFormat` | 5330 |
| `GetLess` | 1667 |
| `GetOKStr` | 1596 |
| `GetE` | 1081 |
| `GetFa` | 741 |
| `Mul` | 618 |
| `IsEqual` | 493 |
| `GetFt` | 422 |
| `XDrawProfileEX` | 404 |
| `GetMin` | 328 |
| `IsNEqual` | 289 |
| `IsNLarge` | 285 |
| `GetNg` | 284 |
| `Sub` | 254 |
| `GetM` | 226 |
| `IsLarge` | 167 |
| `GetDfnum` | 156 |
| `GetSMr` | 142 |
| `Div` | 134 |
| `GetVr` | 119 |
| `IFValue` | 114 |
| `GetUmax` | 106 |
| `GetDe` | 103 |

## 公式样例（前 12 条，含函数与符号）

| IID | SYMBOL | 标题 | 函数 | 数据符号（前 4） |
| --- | --- | --- | --- | --- |
| 1 | `WLS` | 风荷载标准值 | `GetBoardType`, `GetKk`, `IsNEqual` | `REGION`, `z`, `α`, `α2` |
| 2 | `WLD` | 风荷载设计值 | — | `γwf`, `ω`, `ωkt`, `ωktx` |
| 3 | `WLSJD` | 风荷载标准值 | `GetKk`, `IsNEqual` | `α`, `α2`, `βgz`, `γ0` |
| 4 | `WLDJD` | 风荷载设计值 | — | `γwf`, `ω`, `ωkt`, `ωktx` |
| 5 | `WLGD` | 风荷载标准值(指定) | — | `ωk` |
| 6 | `WAREA` | 玻璃面积 | `XDrawProfileEX` | `GLS_AREA`, `GLS_Bw`, `GLS_DRAWDESC`, `GLS_Hw` |
| 7 | `WAREAJD` | 玻璃面积 | `XDrawProfileEX` | `GLS_AREA`, `GLS_Bw`, `GLS_DRAWDESC`, `GLS_Hw` |
| 8 | `WWEIGHT` | 玻璃板块自重 | `GetM`, `Mul` | `GLS_AREA`, `GLS_GAK`, `GLS_GLS4`, `GLS_STRUCTDESC` |
| 9 | `WWEIGHTJD` | 玻璃板块自重 | `GetM`, `Mul` | `GLS_AREA`, `GLS_GAK`, `GLS_GLS4`, `GLS_STRUCTDESC` |
| 10 | `WHQUAKE` | 分布水平地震作用计算 | `GetAmax`, `IsNEqual` | `GAK`, `qEA`, `qEk`, `βE` |
| 11 | `WHQUAKEJD` | 分布水平地震作用计算 | `GetAmax`, `IsNEqual` | `GAK`, `qEA`, `qEk`, `βE` |
| 12 | `WSTRENGTH` | 玻璃强度计算 | `GetLess`, `GetNg`, `GetSMr` | `Ew`, `GAK`, `GLASSDESC`, `GLASSSTRUCTNAME` |

## 下一步

1. 未注册符号逐个判定：是"节点名"（应出现在 379 名单里但没匹配上）、"数据列"还是"中间量"；
2. 把已绑定公式的参数映射到 `raw/db/*.json` 的列（风压/强度/密度/系数）；
3. 取一条公式做端到端复算（L8 最小切片）。
