# 公式符号 → 数据列 候选匹配（L7 第 3 步）

- 数据符号：**5285**；数据库列：**708**（85 张表）
- 置信分桶：`none`=4329、`contains`=537、`exact_generic`=295、`exact_weak`=88、`exact`=28、`token`=8
- `exact_weak` = 去前缀后 ≤3 字符的精确撞名；`exact_generic` = 撞上通用列名（IZ/AREA/NAME…）——两者**都不可直接采信**；
- **候选不等于绑定**：`contains`/`token` 两桶仍需人工确认（列名是中文/英文缩写，符号是公式记号）

## 精确命中（可直接核对）

| 符号 | 次数 | 表.列 |
| --- | --- | --- |
| `REGION` | 78 | `HWKCOPY_UserGlazing.Regions.Region` |
| `CHMBOLT_fcuk` | 8 | `HWKCOPY_XWallTem.混凝土强度表.fcuk` |
| `LOADSSLOP_ANGLE` | 6 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `WATERTIGHT_MIDU` | 6 | `HWKCOPY_XWallTem.玻璃强度表.midu` |
| `LOADDSLOP_ANGLE` | 4 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `EXABOLT_fcuk` | 4 | `HWKCOPY_XWallTem.混凝土强度表.fcuk` |
| `LINKPOLE_CRTY` | 4 | `HWKCOPY_XWall.型材参数表.CRTY` |
| `LINKPOLE_CRTZ` | 4 | `HWKCOPY_XWall.型材参数表.CRTZ` |
| `TROEMB_fcuk` | 4 | `HWKCOPY_XWallTem.混凝土强度表.fcuk` |
| `ALUS_GBNUM` | 3 | `HWKCOPY_XWallTem.拉杆参数表.GBNUM` |
| `ALUC_GBNUM` | 3 | `HWKCOPY_XWallTem.拉杆参数表.GBNUM` |
| `CHMBOLT_ANGLE` | 3 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `WELDNV_Angle` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `KVALUE_AName` | 2 | `HWKCOPY_XWallTem.气体热物理特性.ANAME` |
| `KVALUE_Angle` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `EARBOARD_MATERIAL` | 2 | `HWKCOPY_XWallTem.铆钉参数表.MATERIAL` |
| `CHEMBOLT_ANGLE` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `CHEMBOLT_GLUE` | 2 | `HWKCOPY_XWallTem.建筑胶参数表.GLUE` |
| `EXABOLT_ANGLE` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `LINKPOLE_MATERIAL` | 2 | `HWKCOPY_XWallTem.铆钉参数表.MATERIAL` |
| `HOLDBLOCK_MATERIAL` | 2 | `HWKCOPY_XWallTem.铆钉参数表.MATERIAL` |
| `SSLOPEFRAME_ANGLE` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `UGLASS_Midu` | 2 | `HWKCOPY_XWallTem.玻璃强度表.midu` |
| `LEANGLS_Angle` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `SGPGLS_Angle` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `SANDWICHPANEL_Midu` | 2 | `HWKCOPY_XWallTem.玻璃强度表.midu` |
| `MSGPGLS_Angle` | 2 | `HWKCOPY_UserGlazing.SpectralData.Angle` |
| `ARCHCIRC_ANGLE` | 1 | `HWKCOPY_UserGlazing.SpectralData.Angle` |

## 包含命中（前 40，需人工确认）

| 符号 | 次数 | 候选列 |
| --- | --- | --- |
| `GLS_DESC` | 40 | `HWKCOPY_UserGlazing.DatabaseInfo.Version_Description` (nvarchar) |
| `CITYNAME` | 30 | `HWKCOPY_XWall.材料特性表.NAME` (nvarchar) |
| `LEANGLS_DESC` | 20 | `HWKCOPY_UserGlazing.DatabaseInfo.Version_Description` (nvarchar) |
| `ShapeAngle` | 18 | `HWKCOPY_UserGlazing.SpectralData.Angle` (real) |
| `GLSPS_DESC` | 16 | `HWKCOPY_UserGlazing.DatabaseInfo.Version_Description` (nvarchar) |
| `GLS_RGLASS0` | 14 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `GLS_RGLASS1` | 14 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `GLS_RGLASS2` | 14 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `BOARDFE_BOARDNAME` | 13 | `HWKCOPY_XWall.材料特性表.NAME` (nvarchar) |
| `SHELLT_NAME` | 13 | `HWKCOPY_UserGlazing.Coatings.Coating_Name` (nvarchar) |
| `GLASSDESC` | 12 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `GLASSSTRUCTNAME` | 12 | `HWKCOPY_XWall.材料特性表.NAME` (nvarchar) |
| `GLUE_LONGSIDE` | 12 | `HWKCOPY_XWallTem.风压数据.SID` (int) |
| `LOAD_SUBAREABEAM` | 12 | `HWKCOPY_XWall.复合型材参数表.AREA` (float) |
| `LOAD_SUBAREAPOLE` | 12 | `HWKCOPY_XWall.复合型材参数表.AREA` (float) |
| `EARBOARD_THICKNESS` | 12 | `HWKCOPY_UserGlazing.InterlayerLookup.Nominal_Thickness` (real) |
| `SGPGLS_DESC` | 12 | `HWKCOPY_UserGlazing.DatabaseInfo.Version_Description` (nvarchar) |
| `GLASSCP_Thickness` | 12 | `HWKCOPY_UserGlazing.InterlayerLookup.Nominal_Thickness` (real) |
| `PORCELAIN_Thickness` | 12 | `HWKCOPY_UserGlazing.InterlayerLookup.Nominal_Thickness` (real) |
| `FIBERCFS_Thickness` | 12 | `HWKCOPY_UserGlazing.InterlayerLookup.Nominal_Thickness` (real) |
| `AMJ_CONCRETELEVEL` | 10 | `HWKCOPY_XWallTem.不锈钢螺栓表.LEVEL` (nvarchar) |
| `PROJECTNAME` | 10 | `HWKCOPY_XWall.材料特性表.NAME` (nvarchar) |
| `UXPOLE_RArea` | 10 | `HWKCOPY_XWall.复合型材参数表.AREA` (float) |
| `BOARDMATERIAL` | 9 | `HWKCOPY_XWallTem.铆钉参数表.MATERIAL` (nvarchar) |
| `AMJ_STEELMJLEVEL` | 8 | `HWKCOPY_XWallTem.不锈钢螺栓表.LEVEL` (nvarchar) |
| `STONE_BOARDSMATERIAL` | 8 | `HWKCOPY_XWallTem.铆钉参数表.MATERIAL` (nvarchar) |
| `MCV_DArea` | 8 | `HWKCOPY_XWall.复合型材参数表.AREA` (float) |
| `MCV_DWy1` | 8 | `HWKCOPY_XWall.复合型材参数表.WY1` (float) |
| `MCV_DWy2` | 8 | `HWKCOPY_XWall.复合型材参数表.WY2` (float) |
| `MCV_DWz1` | 8 | `HWKCOPY_XWall.复合型材参数表.WZ1` (float) |
| `MCV_DWz2` | 8 | `HWKCOPY_XWall.复合型材参数表.WZ2` (float) |
| `LOAD_LEVEL` | 8 | `HWKCOPY_XWallTem.抗滑移系数.FELEVEL` (nvarchar) |
| `LEANGLS_RGLASS0` | 8 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `LEANGLS_RGLASS1` | 8 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `LEANGLS_RGLASS2` | 8 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `HPLSHEET_Thickness` | 8 | `HWKCOPY_UserGlazing.InterlayerLookup.Nominal_Thickness` (real) |
| `BREASTGLS_DESC` | 8 | `HWKCOPY_UserGlazing.DatabaseInfo.Version_Description` (nvarchar) |
| `KVALUE_GLASSK` | 7 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `GLSPS_RGLASS1` | 7 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |
| `GLSPS_RGLASS2` | 7 | `HWKCOPY_XWallTem.规范表.GLASS` (bit) |

## 未命中（前 30，多为构件输入而非表数据）

| 符号 | 次数 |
| --- | --- |
| `γGf` | 125 |
| `βE` | 105 |
| `γwf` | 96 |
| `γEf` | 92 |
| `EqAMax` | 90 |
| `ψE` | 89 |
| `ω0` | 84 |
| `α2` | 70 |
| `μh` | 70 |
| `νw` | 60 |
| `GLS_to` | 54 |
| `GLS_ti` | 50 |
| `GLS_STRUCTDESC` | 39 |
| `GLS_awl` | 38 |
| `GLS_tmg` | 36 |
| `GLS_COMPK` | 34 |
| `STONE_COMP` | 34 |
| `γqf` | 34 |
| `GLUE_Hw` | 30 |
| `MCV_FPRATIO1` | 30 |
| `MCV_FPRATIO2` | 30 |
| `GLS_te` | 28 |
| `POLE_Ivz` | 27 |
| `GLS_DFNum` | 26 |
| `LEANGLS_ti` | 26 |
| `LEANGLS_to` | 26 |
| `POLE_γv` | 25 |
| `GLSPS_ti` | 25 |
| `GLSPS_to` | 25 |
| `GLUE_RADLAY` | 24 |

## 结论：符号有三个来源，不是"全都在数据库里"

| 桶 | 符号数 | 判读 |
| --- | --- | --- |
| `exact`（去前缀后 ≥4 字符且非通用名） | **28** | 高置信，可直接核对（如 `CHMBOLT_fcuk` ↔ `混凝土强度表.fcuk`） |
| `exact_weak` / `exact_generic` | 88 / 295 | 撞上 `IZ`/`AREA`/`NAME` 这类通用列名，**不可采信** |
| `contains` | 537 | 候选，需人工确认（列名中文/缩写 vs 公式记号） |
| `none` | **4329** | 数据库里没有对应列 |

`none` 占 82%，这与公式语义一致：绝大多数符号是**工程/构件输入**（`GLS_to` 玻璃厚度、`GLS_awl` 板块边长、
`POLE_*` 立柱截面参数…），来自 `.cwx` 工程文件或界面输入，不是查表数据。

→ 因此"符号 → 数据"的绑定要分三条通路：

1. **数据库**（材料/规范/强度/风压）——`exact` 28 条已有高置信样本，`contains` 537 条待核；
2. **工程文件**（`.cwx` 字段）——已知 3 个字段偏移（雪压 `0x5E`、风压 `0xA0`、工程名 `0x66`），其余待按需扩展；
3. **界面输入**（用户填的构件尺寸、荷载参数）——只能靠 UI 取证或计算书对照。

这条结论对重构很关键：**不能指望"从数据库一键恢复全部输入"**，`.cwx` 与界面输入必须一起实现。
