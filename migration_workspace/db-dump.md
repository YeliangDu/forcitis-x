# 数据层导出（L7 第 1 步）：表结构 + 样本行

- 来源：`HWKCOPY_*` 只读副本库（`SELECT` only，未 attach 新库、未写入）
- 方式：`scripts/dump-db.py`（每表：列名/类型/可空 + 行数 + 前 3 行样本）
- 边界：**只记录结构与样本，不推断单位与业务语义**

## `HWKCOPY_UserGlazing`：21 张表 / 196914 行

| 表 | 行数 | 列数 |
| --- | --- | --- |
| `SpectralData` | 195775 | 9 |
| `GlazingProperties` | 548 | 45 |
| `Coatings` | 396 | 7 |
| `NominalThicknessLookup` | 79 | 6 |
| `Manufacturers` | 73 | 6 |
| `GlazingTypes` | 8 | 2 |
| `Materials` | 7 | 4 |
| `NominalThicknessStandards` | 6 | 2 |
| `DataSources` | 4 | 3 |
| `Regions` | 4 | 2 |
| `Uses` | 4 | 2 |
| `DataSourceCategories` | 3 | 2 |
| `GlazingUses` | 3 | 2 |
| `CoatingTypes` | 1 | 2 |
| `DatabaseInfo` | 1 | 5 |
| `DepositionMethods` | 1 | 2 |
| `LaminateStructures` | 1 | 7 |
| `GlazingAvailability` | 0 | 3 |
| `InterlayerLookup` | 0 | 11 |
| `InterlayerUses` | 0 | 2 |
| `udbAction` | 0 | 11 |

## `HWKCOPY_XWall`：8 张表 / 4622 行

| 表 | 行数 | 列数 |
| --- | --- | --- |
| `图库数据表` | 3808 | 10 |
| `型材参数表` | 681 | 27 |
| `图库目录表` | 107 | 6 |
| `词条表` | 11 | 3 |
| `词条目录表` | 6 | 4 |
| `材料特性表` | 5 | 5 |
| `复合型材参数表` | 3 | 21 |
| `版本描述表` | 1 | 5 |

## `HWKCOPY_XWallTem`：56 张表 / 5569 行

| 表 | 行数 | 列数 |
| --- | --- | --- |
| `计算模板` | 2082 | 6 |
| `风压数据` | 767 | 19 |
| `风压数据OLD` | 665 | 12 |
| `更新记录表` | 549 | 4 |
| `dcsval` | 465 | 9 |
| `dxqb` | 139 | 18 |
| `材料导热系数表` | 132 | 8 |
| `标准规范表` | 93 | 7 |
| `玻璃参数` | 56 | 12 |
| `铝材强度表` | 41 | 16 |
| `拉索参数表` | 40 | 11 |
| `幕墙类别码表` | 40 | 3 |
| `省表` | 34 | 2 |
| `铆钉参数表` | 27 | 8 |
| `结构胶参数` | 25 | 8 |
| `花岗石板强度表` | 24 | 10 |
| `玻璃强度表` | 22 | 12 |
| `钢材强度表` | 22 | 15 |
| `软件发布版本表` | 22 | 6 |
| `抗滑移系数` | 21 | 5 |
| `金属板参数` | 20 | 13 |
| `拉杆参数表` | 20 | 13 |
| `气体特性表` | 20 | 8 |
| `墙体材料表` | 19 | 6 |
| `不锈钢螺栓表` | 18 | 9 |
| `常用材料特性表` | 18 | 8 |
| `焊缝强度表` | 17 | 5 |
| `混凝土强度表` | 14 | 11 |
| `连接构件承压强度表` | 14 | 7 |
| `塑性发展系数表` | 14 | 7 |
| `板材分析数据表` | 12 | 8 |
| `高强度螺栓预拉力` | 12 | 5 |
| `类别码信息表` | 12 | 3 |
| `gas2` | 9 | 17 |
| `不锈钢锚栓表` | 9 | 9 |
| `材料类别表` | 9 | 4 |
| `螺栓强度表` | 8 | 8 |
| `复合金属板参数` | 7 | 12 |
| `碳素钢及合金钢锚栓表` | 7 | 7 |
| `规范表` | 6 | 8 |
| `图库数据表` | 6 | 10 |
| `gas` | 5 | 19 |
| `材料安全系数表` | 5 | 6 |
| `气体热物理特性` | 5 | 12 |
| `GasProperties` | 4 | 9 |
| `金属板类别` | 3 | 3 |
| `复合金属板` | 2 | 4 |
| `锚栓强度表` | 2 | 7 |
| `热轧钢筋强度表` | 2 | 12 |
| `gaslist` | 1 | 7 |
| `建筑胶参数表` | 1 | 5 |
| `木材强度表` | 1 | 12 |
| `塑料强度表` | 1 | 11 |
| `GasMixtures` | 0 | 5 |
| `sysdiagrams` | 0 | 5 |
| `拉索截面表` | 0 | 6 |

## 合计

- 表总数 **85**，行总数 **207105**

## 列类型分布

| 类型 | 列数 |
| --- | --- |
| `float` | 230 |
| `nvarchar` | 161 |
| `int` | 155 |
| `real` | 73 |
| `timestamp` | 55 |
| `datetime2` | 13 |
| `varbinary` | 9 |
| `bit` | 6 |
| `smallint` | 6 |

## 数值列样本（量级观察，不推断单位）

- `HWKCOPY_UserGlazing`.`Coatings`：CoatingID=1，Coating_TypeID=1，Deposition_MethodID=1
- `HWKCOPY_UserGlazing`.`CoatingTypes`：Coating_TypeID=1
- `HWKCOPY_UserGlazing`.`DataSourceCategories`：DataSourceCategoryID=1
- `HWKCOPY_UserGlazing`.`DataSources`：DataSourceID=1，DataSourceCategoryID=1
- `HWKCOPY_UserGlazing`.`DepositionMethods`：Deposition_MethodID=1
- `HWKCOPY_UserGlazing`.`GlazingProperties`：GlazingID=140，NFRC_ID=30000，GlazingTypeID=7，Thickness=0.7656002，Conductivity=0.212，ManufacturerID=25
- `HWKCOPY_UserGlazing`.`GlazingTypes`：GlazingTypeID=1
- `HWKCOPY_UserGlazing`.`GlazingUses`：GlazingID=863，UseID=4
- `HWKCOPY_UserGlazing`.`LaminateStructures`：LaminateStructureID=4，GlazingID=158，Layer_Number=0，Layer_Thickness=2.2352
- `HWKCOPY_UserGlazing`.`Manufacturers`：ManufacturerID=1
- `HWKCOPY_UserGlazing`.`Materials`：MaterialID=1，SurfaceEmittance=0
- `HWKCOPY_UserGlazing`.`NominalThicknessLookup`：NominalThicknessBracketID=1，NominalThicknessStandardID=1，Low_Limit=0.79，High_Limit=1.24
- `HWKCOPY_UserGlazing`.`NominalThicknessStandards`：StandardID=1
- `HWKCOPY_UserGlazing`.`Regions`：RegionID=1
- `HWKCOPY_UserGlazing`.`SpectralData`：GlazingID=140，WavelengthIndex=1，AngleIndex=1，Wavelength=0.3，Angle=0，T=0
- `HWKCOPY_UserGlazing`.`Uses`：UseID=1
- `HWKCOPY_XWall`.`版本描述表`：ID=1，主版本=12
- `HWKCOPY_XWall`.`材料特性表`：IID=1，DENSITY=28.3
- `HWKCOPY_XWall`.`词条表`：IID=1，DIRID=23
- `HWKCOPY_XWall`.`词条目录表`：IID=23，PARENTID=0
- `HWKCOPY_XWall`.`复合型材参数表`：IID=1，MAINID=1780，SUBID1=1781，SUBID2=1783，SUBID3=1782，LENGTH=4
- `HWKCOPY_XWall`.`图库目录表`：IID=1，PARENTIID=0，CANDEL=0，ISDEL=0，TYPE=1
- `HWKCOPY_XWall`.`图库数据表`：IID=44，目录ID=10，CANDEL=1，ISDEL=0
- `HWKCOPY_XWall`.`型材参数表`：IID=97，图形ID=269，IZ=0.400204，IY=0.400204，WZ1=0.286294，WZ2=0.664654
- `HWKCOPY_XWallTem`.`dcsval`：fvalue=0，fvalue1=0，fvalue2=0，myid=1
- `HWKCOPY_XWallTem`.`dxqb`：fbt=2，fky=84.2，fkj=48.9，fxz=0，fsc=0，fdr=2.35e-05
- `HWKCOPY_XWallTem`.`gas`：ID=-1，nGasses=0，ConductivityA=0.002873，ConductivityB=7.76e-05，ConductivityC=0，ViscosityA=3.723e-06
- `HWKCOPY_XWallTem`.`gas2`：GasID=11，MixtureType=0，Conductivity=0.0241，dConductivity=7.6e-05
- `HWKCOPY_XWallTem`.`gaslist`：ParentID=-1，Index=1，ID=1，GasTimestamp=0，Thickness=0，Keff=0
- `HWKCOPY_XWallTem`.`GasProperties`：ID=1，Conductivity=0.02406944，Viscosity=1.721661e-05，Cp=1006.10327，Density=1.29217124，Prandtl=0.7196548
- `HWKCOPY_XWallTem`.`板材分析数据表`：ID=1，E=80000，NU=0.125，RHO=28，ALPHA=1e-05
- `HWKCOPY_XWallTem`.`标准规范表`：IID=1，CODEYEAR=2003，OPERWORD=65535，LOCALCODE=0
- `HWKCOPY_XWallTem`.`玻璃参数`：厚度=3，面强度=28，边强度=19.5，FAA1=0.22，FA0=0.099，FK3=1
- `HWKCOPY_XWallTem`.`玻璃强度表`：IID=1，CODEID=1，最小厚度=3，最大厚度=5，f=28，fce=19.5
- `HWKCOPY_XWallTem`.`不锈钢螺栓表`：IID=1，ft=200，fv=190，E=206000
- `HWKCOPY_XWallTem`.`不锈钢锚栓表`：IID=1，lwdiam=39，fstk=500，fyk=210，delta=0.6
- `HWKCOPY_XWallTem`.`材料安全系数表`：IID=1，KBM=2.15，KCM=4.3，LOCALCODE=8
- `HWKCOPY_XWallTem`.`材料导热系数表`：ID=1，目录ID=1，导热系数=160，表面发射率=0.9，调整系数=1，Frequency=5
- `HWKCOPY_XWallTem`.`材料类别表`：ID=1
- `HWKCOPY_XWallTem`.`常用材料特性表`：IID=1，E=206000，V=0.3，a=1.2，M=78.5
- `HWKCOPY_XWallTem`.`风压数据`：IID=1，SID=1，海拔=54，R10风压=0.3，基本风压=0.45，百年风压=0.5
- `HWKCOPY_XWallTem`.`风压数据OLD`：IID=1，基本风压=0.45，年温差=68.1，雪荷载=0.4，雪荷载分区=2，百年风压=0.5
- `HWKCOPY_XWallTem`.`复合金属板`：IID=1，厚度折算系数=0.8
- `HWKCOPY_XWallTem`.`复合金属板参数`：IID=1，TID=1，厚度=4，抗拉强度=70，抗剪强度=20，截面模量=1.6
- `HWKCOPY_XWallTem`.`钢材强度表`：IID=1，最小厚度=0，最大厚度=16，压弯拉强度=215，抗剪强度=125，端面承压=320
- `HWKCOPY_XWallTem`.`高强度螺栓预拉力`：IID=1，DIAMETER=16，P=80
- `HWKCOPY_XWallTem`.`更新记录表`：IID=1，VERSIONID=1
- `HWKCOPY_XWallTem`.`规范表`：IID=1
- `HWKCOPY_XWallTem`.`焊缝强度表`：IID=1，Fwf=160
- `HWKCOPY_XWallTem`.`花岗石板强度表`：IID=1，ft=2.4，fv=1.2，E=80000，a=8e-06，v=0.125
- `HWKCOPY_XWallTem`.`混凝土强度表`：IID=1，fc=7.2，ft=0.91，fcuk=15，E=22000，a=1e-05
- `HWKCOPY_XWallTem`.`计算模板`：IID=1
- `HWKCOPY_XWallTem`.`建筑胶参数表`：IID=1，fvk=2.3
- `HWKCOPY_XWallTem`.`结构胶参数`：IID=1，温差变位=0.12，地震变位=0.12，变位=0.12，短期强度=0.2，长期强度=0.01
- `HWKCOPY_XWallTem`.`金属板参数`：IID=2，TID=1，抗拉强度=178，抗剪强度=103.4，弹性模量=206000，屈服强度=205
- `HWKCOPY_XWallTem`.`金属板类别`：IID=1
- `HWKCOPY_XWallTem`.`抗滑移系数`：IID=1，miu=0.45
- `HWKCOPY_XWallTem`.`拉杆参数表`：IID=1，抗拉强度=239，抗剪强度=138.7，弹性模量=206000，屈服强度=275，膨胀系数=1.8e-05
- `HWKCOPY_XWallTem`.`拉索参数表`：IID=2，弹性模量=120000，膨胀系数=2e-05，泊松比=0.3，安全系数=1.8，金属面积=21.99
- `HWKCOPY_XWallTem`.`类别码信息表`：IID=1，BITVALUE=1
- `HWKCOPY_XWallTem`.`连接构件承压强度表`：IID=1，fcb=305
- `HWKCOPY_XWallTem`.`铝材强度表`：IID=1，CODEID=2，最小厚度=0，最大厚度=100，f=90，fv=55
- `HWKCOPY_XWallTem`.`螺栓强度表`：IID=1，ft=170，fv=140
- `HWKCOPY_XWallTem`.`锚栓强度表`：IID=1，ft=140
- `HWKCOPY_XWallTem`.`铆钉参数表`：IID=1，DIAMETER=3，ft=460，fv=370
- `HWKCOPY_XWallTem`.`木材强度表`：IID=1，fls=24，flh=24，fy=24，fv=12，E=14000
- `HWKCOPY_XWallTem`.`幕墙类别码表`：IID=1，TYPEID=1
- `HWKCOPY_XWallTem`.`气体热物理特性`：ID=1，LAMBDAA=2.873，LAMBDAB=7.76，INTERLAMBDA0=0.0241，INTERLAMBDA10=0.0249，MIUA=3.723
- `HWKCOPY_XWallTem`.`气体特性表`：IID=1，温度=-10，密度=1.326，动态黏度=1.661，热导率=2.336，比热=1.008
- `HWKCOPY_XWallTem`.`墙体材料表`：IID=1，MIDU=2300
- `HWKCOPY_XWallTem`.`热轧钢筋强度表`：IID=1，压弯拉强度=300，fyk=335，fstk=455，E=200000
- `HWKCOPY_XWallTem`.`软件发布版本表`：IID=1
- `HWKCOPY_XWallTem`.`省表`：IID=1
- `HWKCOPY_XWallTem`.`塑料强度表`：IID=1，f=37，fv=23，fce=35，E=2500，v=0.38
- `HWKCOPY_XWallTem`.`塑性发展系数表`：IID=1，SECTYPE=1，rx1=1，rx2=1，ry=1.05
- `HWKCOPY_XWallTem`.`碳素钢及合金钢锚栓表`：IID=1，fstk=300，fyk=180，delta=0.25
- `HWKCOPY_XWallTem`.`图库数据表`：IID=1，目录ID=1，CANDEL=1，ISDEL=0

## 下一步

1. 把 `计算模板`（2082 条公式）里的符号与 `raw/cxmap-entries.json` 的 379 个参名对齐；
2. 再把参名对到本文件的数据列（风压/强度/密度/系数），产出"可执行公式"清单；
3. 选一条业务链做原版对照（L8 最小切片）。

## 关键发现：`计算模板` 就是"可执行公式"的来源

| 列 | 类型 | 含义（实测） |
| --- | --- | --- |
| `IID` | int | 序号 |
| `TITLE` | nvarchar | 公式标题（如「风荷载标准值」） |
| `SYMBOL` | nvarchar | 公式符号（`WLS`/`WLD`/`WLSJD`…） |
| `CONTEXT` | **varbinary** | **GBK 编码的公式正文**（含中文说明 + 算式 + `${参数}` / `${函数(实参)}` 占位） |
| `REMARK` | varbinary | 备注（多为 NULL） |

实测解码（`bytes → GBK`）第 1 条 `WLS`：

```text
Wk: 作用在${GetBoardType(PRJGLASS)}上的风荷载标准值(kN/m^2)
μz: ${z}m高处风压高度变化系数(按${REGION}类区计算): (GB50009-2001  7.2.1)
    μz=${μh}×(z/10)^${α2}=${μzcal}  ${Is...
```

第 2 条 `WLD` 里还能看到条件模板 `${IsEqual(PRJGLASS,42):…:…}`。

→ 这意味着 **2082 条公式的符号、算式与规范出处都在库里，且是明文（GBK）**，
  与 `raw/cxmap-entries.json` 的 379 个参名、263 个模板函数可以直接对齐。
  这就是第 2 步"公式 ↔ 参数 ↔ 数据列"绑定的输入。

## 又找到三张"直接可用"的参数表（2026-10-19）

| 表 | 行数 | 列 | 样本 |
| --- | --- | --- | --- |
| `常用材料特性表` | 18 | `MNAME, E, V, a, M, CODENAME` | 钢：E=206000 MPa、V=0.3、M=78.5 kN/m³、CODENAME=`JGJ336-2016` |
| `抗滑移系数` | 21 | `TREATMENT, FELEVEL, miu` | 喷砂(丸)/Q235 → miu=0.45 |
| `塑性发展系数表` | 14 | `SECTYPE, rx1, rx2, ry, HARDEN` | SECTYPE=1 → rx1=1、rx2=1、ry=1.05 |

意义：

1. `常用材料特性表` 就是 `GetE`/`GetM` 这类节点要取的**弹性模量 / 密度 / 泊松比**数据源，而且**带规范号**
   （`JGJ336-2016`）——这填补了"数值 + 规范出处"这一层；
2. `抗滑移系数`、`塑性发展系数表` 是把"规范查表"直接落成数据（对应公式里的 `miu`、`rx/ry` 类符号）；
3. 三张表的行数都不大（14–21），可以整表纳入首版实现，不需要算法。

未定：`GLOB_g`（峰值因子，公式里 `βgz=1+2g·I10·(z/10)^-α` 用到）在已导出的 85 张表里**没有对应列**，
可能是代码常量或未识别表；继续查需新增表查询。

## 第 2 批：11 张参数表已全量落地（2026-10-19，实测 1065 行）

`scripts/fetch-tables.py`（表名+库名双白名单，只 `SELECT *`）→ `raw/db/tables-HWKCOPY_XWallTem.json`

| 表 | 行数 | 关键内容（实测） |
| --- | --- | --- |
| `常用材料特性表` | 18 | `钢 E=206000 V=0.3 M=78.5`、`铝 E=70000 M=28`、`瓷板 E=60000 M=23`，全部带 `CODENAME=JGJ336-2016` |
| `抗滑移系数` | 21 | `喷砂(丸)/Q235 → miu=0.45`、`喷砂后涂无机富锌漆 → 0.35`、`钢丝刷除浮锈 → 0.30` |
| `塑性发展系数表` | 14 | `SECTYPE=1 → rx1=1 rx2=1 ry=1.05`；`SECTYPE=4 → rx1=rx2=ry=1.05` |
| `风压数据` | 767 | 北京：`基本风压 0.45 / 百年 0.5 / R10 0.3 / 雪荷载 0.4 / 雪分区Ⅱ / 冬季-13℃ / 夏季36℃ / 设防烈度3 / 加速度0.2 / 热工2B` |
| `玻璃参数` | 56 | 按厚度给出 `面强度/边强度/FAA1/FA0/FK3/FTT0/FRR0`（浮法 3mm：28/19.5/0.22/0.099/1/0.078/0.844） |
| `钢材强度表` / `铝材强度表` / `玻璃强度表` | 22 / 41 / 22 | 强度取值（按材质+厚度） |
| `材料安全系数表` | 5 | 分项安全系数 |
| `标准规范表` / `规范表` | 93 / 6 | 规范编号与适用材质 |

→ 这些表的行数都很小（5–767），**可直接整表纳入首版实现**，不需要算法推导。

注意：`风压数据` 里北京的 `雪荷载=0.4`、`基本风压=0.45` 与 `.cwx` 字段（`0x5E`/`0xA0`）实测一致，
说明**工程文件里存的是"从该表拷来的副本"**，数据库只提供候选值。
