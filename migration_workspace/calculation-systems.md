# 计算体系清点（安装包静态实测）

- 清单文件：`HWKSchemaList.xml`（8750 字节）
- **有效体系条目：74 个**，分 19 个大类
- 体系 Schema 文件：70 个
- 被注释禁用：0 个

## 1. 按大类统计

| 大类（StructDesc） | 体系数 |
| --- | --- |
| 幕墙 | 24 |
| 雨蓬 | 14 |
| 框架幕墙 | 4 |
| 采光顶 | 4 |
| 热工U值计算 | 4 |
| 栏杆 | 3 |
| 平面结构 | 3 |
| 百叶计算 | 3 |
| 格栅计算 | 3 |
| 压型金属屋面板 | 2 |
| 吊顶 | 2 |
| 门窗 | 1 |
| 框架雨蓬 | 1 |
| 平面应力 | 1 |
| 三维结构 | 1 |
| 焊缝连接 | 1 |
| 螺栓连接 | 1 |
| 板块分析 | 1 |
| 杂项计算 | 1 |

## 2. 体系清单

| # | 大类 | 体系（CheckDesc） | Schema 类 |
| --- | --- | --- | --- |
| 1 | 幕墙 | 明框幕墙 | `HWKSchema_MKMQ` |
| 2 | 幕墙 | 隐框幕墙 | `HWKSchema_YKMQ` |
| 3 | 幕墙 | 横明竖隐幕墙 | `HWKSchema_HMSYMQ` |
| 4 | 幕墙 | 横隐竖明幕墙 | `HWKSchema_HYSMMQ` |
| 5 | 幕墙 | 全玻幕墙 | `HWKSchema_QBMQ` |
| 6 | 幕墙 | U玻幕墙 | `HWKSchema_UGlass` |
| 7 | 幕墙 | 石材幕墙 | `HWKSchema_StoneBoard` |
| 8 | 幕墙 | 石材蜂窝板幕墙 | `HWKSchema_StoneHoneyCombPanel` |
| 9 | 幕墙 | 微晶玻璃板幕墙 | `HWKSchema_GlassCeramicsPanel` |
| 10 | 幕墙 | 瓷板幕墙 | `HWKSchema_PorcelainPlate` |
| 11 | 幕墙 | 纤维水泥板幕墙 | `HWKSchema_FiberCementFlatSheet` |
| 12 | 幕墙 | 木纤维板幕墙 | `HWKSchema_HighPressureLaminatesSheet` |
| 13 | 幕墙 | 单层铝板幕墙 | `HWKSchema_AluSBoard` |
| 14 | 幕墙 | 复合铝板幕墙 | `HWKSchema_AluCBoard` |
| 15 | 幕墙 | 复合板幕墙 | `HWKSchema_CompMetalPlate` |
| 16 | 幕墙 | 金属板幕墙 | `HWKSchema_MetalPlate` |
| 17 | 幕墙 | 蜂窝铝板幕墙 | `HWKSchema_AluHoneyCombPanel` |
| 18 | 幕墙 | 夹芯墙板 | `HWKSchema_SandwichPanel_Wall` |
| 19 | 幕墙 | 单元体幕墙 | `HWKSchema_CellUnit` |
| 20 | 幕墙 | 单元体幕墙2 | `HWKSchema_CellUnitEx` |
| 21 | 幕墙 | 单层索网幕墙 | `HWKSchema_LinkNet` |
| 22 | 幕墙 | 异型索网幕墙 | `HWKSchema_UnregLinkNet` |
| 23 | 幕墙 | 点式幕墙 | `HWKSchema_PSWall` |
| 24 | 幕墙 | 点式索桁架 | `HWKSchema_LinkTruss` |
| 25 | 框架幕墙 | 倾斜明框幕墙 | `HWKSchema_LEAN_MKMQ` |
| 26 | 框架幕墙 | 倾斜隐框幕墙 | `HWKSchema_LEAN_YKMQ` |
| 27 | 框架幕墙 | 明框框架幕墙 | `HWKSchema_Frame_MKMQ` |
| 28 | 框架幕墙 | 隐框框架幕墙 | `HWKSchema_Frame_YKMQ` |
| 29 | 门窗 | 普通门窗 | `HWKSchema_NormalMC` |
| 30 | 采光顶 | 单坡采光顶 | `HWKSchema_LPEAK_DPCGD` |
| 31 | 采光顶 | 双坡采光顶 | `HWKSchema_LPEAK_DualSlope` |
| 32 | 采光顶 | 单坡车棚 | `HWKSchema_LPEAK_SSlopeCarport` |
| 33 | 采光顶 | 双坡车棚 | `HWKSchema_LPEAK_DualSlopeCarport` |
| 34 | 压型金属屋面板 | 金属屋面梯形板计算 | `HWKSchema_RoofPlate_Trapezoidal` |
| 35 | 压型金属屋面板 | 金属屋面直立锁边板计算 | `HWKSchema_RoofPlate_VerticalLocking` |
| 36 | 雨蓬 | 悬挑雨蓬 | `HWKSchema_AWNING_XTYP` |
| 37 | 雨蓬 | 点式悬挑雨蓬 | `HWKSchema_AWNING_DSXTYP` |
| 38 | 雨蓬 | 拉索雨蓬 | `HWKSchema_AWNING_LGYP` |
| 39 | 雨蓬 | 点式拉索雨蓬 | `HWKSchema_AWNING_DSLGYP` |
| 40 | 雨蓬 | 拉杆雨蓬 | `HWKSchema_AWNING_YGYP` |
| 41 | 雨蓬 | 点式拉杆雨蓬 | `HWKSchema_AWNING_DSYGYP` |
| 42 | 雨蓬 | 变截面悬挑雨蓬 | `HWKSchema_AWNINGV_XTYP` |
| 43 | 雨蓬 | 变截面点式悬挑雨蓬 | `HWKSchema_AWNINGV_DSXTYP` |
| 44 | 雨蓬 | 变截面拉索雨蓬 | `HWKSchema_AWNINGV_LGYP` |
| 45 | 雨蓬 | 点式变截面拉索雨蓬 | `HWKSchema_AWNINGV_DSLGYP` |
| 46 | 雨蓬 | 变截面拉杆雨蓬 | `HWKSchema_AWNINGV_YGYP` |
| 47 | 雨蓬 | 点式变截面拉杆雨蓬 | `HWKSchema_AWNINGV_DSYGYP` |
| 48 | 雨蓬 | 三维雨蓬 | `HWKSchema_AWNING3D` |
| 49 | 雨蓬 | 点式三维雨蓬 | `HWKSchema_AWNINGP3D` |
| 50 | 框架雨蓬 | 平面框架雨蓬 | `HWKSchema_Frame_YP` |
| 51 | 栏杆 | 玻璃栏板 | `HWKSchema_BreastBoard` |
| 52 | 栏杆 | 无面板三维栏杆 | `HWKSchema_RailingsNB` |
| 53 | 栏杆 | 三维栏杆 | `HWKSchema_Railings` |
| 54 | 吊顶 | 简单吊顶 | `HWKSchema_CeilingFrame2D` |
| 55 | 吊顶 | 三维吊顶 | `HWKSchema_CeilingFrame` |
| 56 | 平面应力 | 平面应力分析 | `HWKSchema_PlaneStressAnalysis` |
| 57 | 平面结构 | 二维平面结构 | `HWKSchema_PlaneFrame` |
| 58 | 平面结构 | 幕墙挑出雨蓬结构 | `HWKSchema_CompPlaneFrame_CanopyWall` |
| 59 | 平面结构 | 双层雨蓬结构 | `HWKSchema_CompPlaneFrame_DoubleCanopy` |
| 60 | 三维结构 | 通用三维结构 | `HWKSchema_GeneralFrame` |
| 61 | 百叶计算 | 水平百叶相关强度计算 | `HWKSchema_VenetianHorizon` |
| 62 | 百叶计算 | 竖向百叶相关强度计算 | `HWKSchema_VenetianVertical` |
| 63 | 百叶计算 | 顶部百叶相关强度计算 | `HWKSchema_VenetianTop` |
| 64 | 格栅计算 | 水平格栅相关强度计算 | `HWKSchema_GrilleHorizon` |
| 65 | 格栅计算 | 竖向格栅相关强度计算 | `HWKSchema_GrilleVertical` |
| 66 | 格栅计算 | 顶部格栅相关强度计算 | `HWKSchema_GrilleTop` |
| 67 | 焊缝连接 | 普通焊缝 | `HWKSchema_Welding` |
| 68 | 螺栓连接 | 普通螺栓连接 | `HWKSchema_BoltLink` |
| 69 | 板块分析 | 各种板块分析计算 | `HWKSchema_GlassCalc` |
| 70 | 热工U值计算 | U值有限元分析计算 | `HWKSchema_TTherm` |
| 71 | 热工U值计算 | U值有限元分析计算（左右不同面板） | `HWKSchema_ThermEx` |
| 72 | 热工U值计算 | 幕墙/门窗体系U值计算 | `HWKSchema_Therm` |
| 73 | 热工U值计算 | 玻璃光学特性分析 | `HWKSchema_GOP` |
| 74 | 杂项计算 | 独立计算条目 | `HWKSchema_SingleCalc` |

## 3. 清单与文件的一致性

- 清单引用但目录中无同名文件：5 个 — `HWKSchema_CeilingFrame2D`, `HWKSchema_CompMetalPlate`, `HWKSchema_LPEAK_DualSlope`, `HWKSchema_MetalPlate`, `HWKSchema_UGlass`
- 目录中存在但清单未引用：1 个 — `HWKSchema_CeilingFrame2d`
- 说明：文件名大小写差异（如 `CeilingFrame2d` vs `CeilingFrame2D`）在 Windows 上等价，此处按字节比较。

## 4. 构件类引用

- schema 文件中出现的不同 `ClassName`：157 个
- 引用总次数：929
- 单个体系类数：中位 12，最多 66（HWKSchema_SingleCalc）

| 构件类 | 出现体系数 |
| --- | --- |
| `HWKProjectInfo` | 61 |
| `HWKEmbeddingAnchorArea` | 51 |
| `HWKChemAnchorBolt` | 51 |
| `HWKExpandAnchorBolt` | 51 |
| `HWKLinkPoleWeld` | 36 |
| `HWKDewInfo` | 26 |
| `HWKGlass` | 25 |
| `HWKWaterSealInfo` | 24 |
| `HWKTroughEmbeddedInfo` | 22 |
| `HWKLoadInfoPHB` | 21 |
| `HWKLinkPole` | 21 |
| `HWKPole` | 18 |
| `HWKConnectorOfStruct` | 18 |
| `HWKBeamInfo` | 18 |
| `HWKConnectorOfBeam` | 18 |
| `HWKRetractileGap` | 18 |
| `HWKGlassKValue` | 18 |
| `HWKBoltAnchorNMV` | 17 |
| `HWKChemicalBolt` | 17 |
| `HWKAntiNoise` | 17 |

## 5. 口径与未验项

- 本表是**安装包声明的体系清单**，不等于"实际能算通"：每个体系的计算正确性、计算书输出、异常分支均未验证。
- `Support/*.xdf`（106 个数据定义文件）实测为**加密/压缩二进制**（头部 `\x00 36 00 00 <count> … 38 00 00 00`，可打印率约 36%），内容未解密，因此材料/型材/规范数据层仍是 NOT_RUN。
- 体系与 `HWKCalc_*` 实现类的映射（哪个体系用哪些计算类）未建立。
- 与 SQL 库 `XWall.mdf` / `XWallTem.mdf` 的表结构关系未验证。
