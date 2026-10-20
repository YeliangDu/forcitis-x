# 数据库结构（实机只读导出）

来源：实机 LocalDB `(localdb)\v11.0`（SQL Server 11.00.7001）上的**副本库**
`HWKCOPY_XWallTem` / `HWKCOPY_XWall` / `HWKCOPY_UserGlazing`，
仅执行 `select … from sys.tables / sys.columns / sys.partitions`，**未写入、未改动**原库。

| 库标签 | 表数 | 列数 |
| --- | --- | --- |
| `glazing` | 21 | 135 |
| `main` | 8 | 81 |
| `tem` | 56 | 492 |

## `glazing` 库

| 表 | 行数 | 列数 |
| --- | --- | --- |
| `dbo.SpectralData` | 195775 | 9 |
| `dbo.GlazingProperties` | 548 | 45 |
| `dbo.Coatings` | 396 | 7 |
| `dbo.NominalThicknessLookup` | 79 | 6 |
| `dbo.Manufacturers` | 73 | 6 |
| `dbo.GlazingTypes` | 8 | 2 |
| `dbo.Materials` | 7 | 4 |
| `dbo.NominalThicknessStandards` | 6 | 2 |
| `dbo.DataSources` | 4 | 3 |
| `dbo.Regions` | 4 | 2 |
| `dbo.Uses` | 4 | 2 |
| `dbo.DataSourceCategories` | 3 | 2 |
| `dbo.GlazingUses` | 3 | 2 |
| `dbo.CoatingTypes` | 1 | 2 |
| `dbo.DatabaseInfo` | 1 | 5 |
| `dbo.DepositionMethods` | 1 | 2 |
| `dbo.LaminateStructures` | 1 | 7 |
| `dbo.GlazingAvailability` | 0 | 3 |
| `dbo.InterlayerLookup` | 0 | 11 |
| `dbo.InterlayerUses` | 0 | 2 |
| `dbo.udbAction` | 0 | 11 |

### 列明细

- `dbo.SpectralData`：GlazingID:int, WavelengthIndex:int, AngleIndex:int, Wavelength:real, Angle:real, T:real, Rf:real, Rb:real, SSMA_TimeStamp:timestamp
- `dbo.GlazingProperties`：GlazingID:int, FileName:nvarchar, ProductName:nvarchar, NFRC_ID:int, GlazingTypeID:int, Thickness:real, Conductivity:real, Appearance:nvarchar, ManufacturerID:int, CoatingID:int, Coated_Side:nvarchar, Film_Filename:nvarchar, Substrate_FileName:nvarchar, MaterialID:int, Acceptance:nvarchar, TIR:real, ef:real, Source_ef:nvarchar, eb:real, Source_eb:nvarchar, DataSourceID:int, Time_Created:datetime2, Database_Version:nvarchar, Checksum_Date:datetime2, IGDB_Checksum:int, Hidden:bit, Time_LastEdited:datetime2, Precalc_StandardName:nvarchar, Precalc_Time:datetime2, Precalc_Tsol:real, Precalc_Rfsol:real, Precalc_Rbsol:real, Precalc_Tvis:real, Precalc_Rfvis:real, Precalc_Rbvis:real, Precalc_TCIEX:real, Precalc_TCIEY:real, Precalc_TCIEZ:real, Precalc_RfCIEX:real, Precalc_RfCIEY:real, Precalc_RfCIEZ:real, Precalc_Tdw:real, Precalc_Tuv:real, Precalc_TSPF:real, SSMA_TimeStamp:timestamp
- `dbo.Coatings`：CoatingID:int, Coating_Name:nvarchar, Coating_TypeID:int, Deposition_MethodID:int, Reference_FileName:nvarchar, Time_Created:datetime2, Time_LastEdited:datetime2
- `dbo.NominalThicknessLookup`：NominalThicknessBracketID:int, NominalThicknessStandardID:int, Low_Limit:real, High_Limit:real, Designation:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.Manufacturers`：ManufacturerID:int, Manufacturer:nvarchar, Contact Person:nvarchar, Measurement_Facilities:nvarchar, File_Extension:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.GlazingTypes`：GlazingTypeID:int, Type:nvarchar
- `dbo.Materials`：MaterialID:int, MaterialName:nvarchar, SurfaceEmittance:real, SSMA_TimeStamp:timestamp
- `dbo.NominalThicknessStandards`：StandardID:int, StandardName:nvarchar
- `dbo.DataSources`：DataSourceID:int, DataSource:nvarchar, DataSourceCategoryID:int
- `dbo.Regions`：RegionID:int, Region:nvarchar
- `dbo.Uses`：UseID:int, Use:nvarchar
- `dbo.DataSourceCategories`：DataSourceCategoryID:int, DataSourceCategory:nvarchar
- `dbo.GlazingUses`：GlazingID:int, UseID:int
- `dbo.CoatingTypes`：Coating_TypeID:int, Coating_Type:nvarchar
- `dbo.DatabaseInfo`：Version_ID:nvarchar, Version_Date:datetime2, Version_Description:nvarchar, Last_Edited:datetime2, SSMA_TimeStamp:timestamp
- `dbo.DepositionMethods`：Deposition_MethodID:int, Deposition_Method:nvarchar
- `dbo.LaminateStructures`：LaminateStructureID:int, GlazingID:int, Layer_Number:smallint, Layer_FileName:nvarchar, Layer_Thickness:real, Layer_Flipped:bit, SSMA_TimeStamp:timestamp
- `dbo.GlazingAvailability`：GlazingID:int, RegionID:int, AlternativeProductName:nvarchar
- `dbo.InterlayerLookup`：InterlayerID:int, ProductName:nvarchar, Reference_FileName:nvarchar, ManufacturerID:int, Nominal_Thickness:real, Code:nvarchar, Appearance:nvarchar, MaterialID:int, Time_Created:datetime2, Time_Edited:datetime2, SSMA_TimeStamp:timestamp
- `dbo.InterlayerUses`：InterlayerID:int, UseID:int
- `dbo.udbAction`：udbActionID:int, udbAction:nvarchar, udbDB_Version:nvarchar, udbRefNr1:int, udbRefNr2:int, udbRefNr3:int, udbRefNr4:int, udbRefText1:nvarchar, udbRefText2:nvarchar, udbRefText3:nvarchar, udbRefText4:nvarchar

## `main` 库

| 表 | 行数 | 列数 |
| --- | --- | --- |
| `dbo.图库数据表` | 3808 | 10 |
| `dbo.型材参数表` | 681 | 27 |
| `dbo.图库目录表` | 107 | 6 |
| `dbo.词条表` | 11 | 3 |
| `dbo.词条目录表` | 6 | 4 |
| `dbo.材料特性表` | 5 | 5 |
| `dbo.复合型材参数表` | 3 | 21 |
| `dbo.版本描述表` | 1 | 5 |

### 列明细

- `dbo.图库数据表`：IID:int, 名称:nvarchar, 目录ID:int, SLD:varbinary, DWG:varbinary, BREP:varbinary, CANDEL:int, ISDEL:int, REMARK:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.型材参数表`：IID:int, 图形ID:int, 标志:nvarchar, IZ:float, IY:float, WZ1:float, WZ2:float, WY1:float, WY2:float, SZ:float, SY:float, AREA:float, T:float, CX:float, CY:float, PERIM:float, JA:float, CJ:float, CJY:float, CJZ:float, TCX:float, TCY:float, CRTY:float, CRTZ:float, SCX:float, SCY:float, SSMA_TimeStamp:timestamp
- `dbo.图库目录表`：IID:int, 名称:nvarchar, PARENTIID:int, CANDEL:int, ISDEL:int, TYPE:int
- `dbo.词条表`：IID:int, DIRID:int, CONTEXT:nvarchar
- `dbo.词条目录表`：IID:int, PARENTID:int, DIRNAME:nvarchar, REMARK:nvarchar
- `dbo.材料特性表`：IID:int, NAME:nvarchar, DENSITY:float, REMARK:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.复合型材参数表`：IID:int, MAINID:int, SUBID1:int, SUBID2:int, SUBID3:int, LENGTH:float, IZ:float, IY:float, WZ1:float, WZ2:float, WY1:float, WY2:float, SZ:float, SY:float, AREA:float, T:float, CX:float, CY:float, PERIM:float, REMARK:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.版本描述表`：ID:int, 主版本:int, 版本字串:nvarchar, 版本描述:nvarchar, SSMA_TimeStamp:timestamp

## `tem` 库

| 表 | 行数 | 列数 |
| --- | --- | --- |
| `dbo.计算模板` | 2082 | 6 |
| `dbo.风压数据` | 767 | 19 |
| `dbo.风压数据OLD` | 665 | 12 |
| `dbo.更新记录表` | 549 | 4 |
| `dbo.dcsval` | 465 | 9 |
| `dbo.dxqb` | 139 | 18 |
| `dbo.材料导热系数表` | 132 | 8 |
| `dbo.标准规范表` | 93 | 7 |
| `dbo.玻璃参数` | 56 | 12 |
| `dbo.铝材强度表` | 41 | 16 |
| `dbo.拉索参数表` | 40 | 11 |
| `dbo.幕墙类别码表` | 40 | 3 |
| `dbo.省表` | 34 | 2 |
| `dbo.铆钉参数表` | 27 | 8 |
| `dbo.结构胶参数` | 25 | 8 |
| `dbo.花岗石板强度表` | 24 | 10 |
| `dbo.玻璃强度表` | 22 | 12 |
| `dbo.钢材强度表` | 22 | 15 |
| `dbo.软件发布版本表` | 22 | 6 |
| `dbo.抗滑移系数` | 21 | 5 |
| `dbo.金属板参数` | 20 | 13 |
| `dbo.拉杆参数表` | 20 | 13 |
| `dbo.气体特性表` | 20 | 8 |
| `dbo.墙体材料表` | 19 | 6 |
| `dbo.不锈钢螺栓表` | 18 | 9 |
| `dbo.常用材料特性表` | 18 | 8 |
| `dbo.焊缝强度表` | 17 | 5 |
| `dbo.混凝土强度表` | 14 | 11 |
| `dbo.连接构件承压强度表` | 14 | 7 |
| `dbo.塑性发展系数表` | 14 | 7 |
| `dbo.板材分析数据表` | 12 | 8 |
| `dbo.高强度螺栓预拉力` | 12 | 5 |
| `dbo.类别码信息表` | 12 | 3 |
| `dbo.gas2` | 9 | 17 |
| `dbo.不锈钢锚栓表` | 9 | 9 |
| `dbo.材料类别表` | 9 | 4 |
| `dbo.螺栓强度表` | 8 | 8 |
| `dbo.复合金属板参数` | 7 | 12 |
| `dbo.碳素钢及合金钢锚栓表` | 7 | 7 |
| `dbo.规范表` | 6 | 8 |
| `dbo.图库数据表` | 6 | 10 |
| `dbo.gas` | 5 | 19 |
| `dbo.材料安全系数表` | 5 | 6 |
| `dbo.气体热物理特性` | 5 | 12 |
| `dbo.GasProperties` | 4 | 9 |
| `dbo.金属板类别` | 3 | 3 |
| `dbo.复合金属板` | 2 | 4 |
| `dbo.锚栓强度表` | 2 | 7 |
| `dbo.热轧钢筋强度表` | 2 | 12 |
| `dbo.gaslist` | 1 | 7 |
| `dbo.建筑胶参数表` | 1 | 5 |
| `dbo.木材强度表` | 1 | 12 |
| `dbo.塑料强度表` | 1 | 11 |
| `dbo.GasMixtures` | 0 | 5 |
| `dbo.sysdiagrams` | 0 | 5 |
| `dbo.拉索截面表` | 0 | 6 |

### 列明细

- `dbo.计算模板`：IID:int, TITLE:nvarchar, SYMBOL:nvarchar, CONTEXT:varbinary, REMARK:varbinary, SSMA_TimeStamp:timestamp
- `dbo.风压数据`：IID:int, SID:int, 城市:nvarchar, 海拔:float, R10风压:float, 基本风压:float, 百年风压:float, R10雪压:float, 雪荷载:float, 百年雪压:float, 冬季温度:float, 夏季温度:float, 雪荷载分区:nvarchar, 年温差:float, 气候分布:nvarchar, 设防烈度:int, 加速度:float, 热工分布:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.风压数据OLD`：IID:int, 城市:nvarchar, 基本风压:float, 年温差:float, 雪荷载:float, 雪荷载分区:smallint, 百年风压:float, 气候分布:nvarchar, 冬季温度:float, 夏季温度:float, 设防烈度:int, SSMA_TimeStamp:timestamp
- `dbo.更新记录表`：IID:int, VERSIONID:int, MODIFYCONTEXTS:nvarchar, MODIFYTIME:datetime2
- `dbo.dcsval`：fbz:nvarchar, fmw:nvarchar, fwhere:nvarchar, fvalue:float, fvalue1:float, fvalue2:float, fsm:nvarchar, myid:int, SSMA_TimeStamp:timestamp
- `dbo.dxqb`：fbz:nvarchar, fxcbh:nvarchar, fname:nvarchar, fbt:float, fky:float, fkj:float, fxz:float, fsc:float, fdr:float, fv:float, fkl:float, fkj_:float, fe:float, fp:float, fh:float, fw:float, myid:int, SSMA_TimeStamp:timestamp
- `dbo.材料导热系数表`：ID:int, 名称:nvarchar, 目录ID:int, 导热系数:float, 表面发射率:float, 调整系数:real, Frequency:int, SSMA_TimeStamp:timestamp
- `dbo.标准规范表`：IID:int, CODENAME:nvarchar, CODENUMBER:nvarchar, CODEYEAR:int, OPERWORD:int, REMARK:nvarchar, LOCALCODE:int
- `dbo.玻璃参数`：名称:nvarchar, 厚度:float, 面强度:float, 边强度:float, FAA1:float, FA0:float, FK3:float, FK3_SC:float, FTT0:float, FRR0:float, IID:int, SSMA_TimeStamp:timestamp
- `dbo.铝材强度表`：IID:int, CODEID:int, 牌号:nvarchar, 状态:nvarchar, 最小厚度:float, 最大厚度:float, f:float, fv:float, fce:float, E:float, v:float, G:float, a:float, midu:float, SSMA_TimeStamp:timestamp, f02:float
- `dbo.拉索参数表`：IID:int, 名称:nvarchar, 弹性模量:float, 膨胀系数:float, 泊松比:float, 安全系数:float, 金属面积:float, 钢丝直径:float, 绞线直径:float, 破断拉力:float, SSMA_TimeStamp:timestamp
- `dbo.幕墙类别码表`：IID:int, CLASSNAME:nvarchar, TYPEID:int
- `dbo.省表`：IID:int, 省名:nvarchar
- `dbo.铆钉参数表`：IID:int, LEVEL:nvarchar, MATERIAL:nvarchar, DIAMETER:float, ft:float, fv:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.结构胶参数`：IID:int, 名称:nvarchar, 温差变位:float, 地震变位:float, 变位:float, 短期强度:float, 长期强度:float, SSMA_TimeStamp:timestamp
- `dbo.花岗石板强度表`：IID:int, 类别:nvarchar, 名称:nvarchar, ft:float, fv:float, E:float, a:float, v:float, density:float, SSMA_TimeStamp:timestamp
- `dbo.玻璃强度表`：IID:int, CODEID:int, NAME:nvarchar, 最小厚度:real, 最大厚度:real, f:real, fce:real, E:real, v:real, a:real, midu:real, fsd:real
- `dbo.钢材强度表`：IID:int, 牌号:nvarchar, 最小厚度:float, 最大厚度:float, 压弯拉强度:float, 抗剪强度:float, 端面承压:float, E:float, G:float, midu:float, v:float, a:float, fyk:float, fstk:int, SSMA_TimeStamp:timestamp
- `dbo.软件发布版本表`：IID:int, XWALLVER:nvarchar, VERSION:nvarchar, RELEASE:datetime2, LASTUPDATE:datetime2, REMARK:nvarchar
- `dbo.抗滑移系数`：IID:int, TREATMENT:nvarchar, FELEVEL:nvarchar, miu:float, SSMA_TimeStamp:timestamp
- `dbo.金属板参数`：IID:int, TID:int, 名称:nvarchar, 成分:nvarchar, 抗拉强度:float, 抗剪强度:float, 弹性模量:float, 屈服强度:float, 膨胀系数:float, 泊松比:float, 密度:float, CODEINFO:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.拉杆参数表`：IID:int, 名称:nvarchar, 抗拉强度:float, 抗剪强度:float, 弹性模量:float, 屈服强度:float, 膨胀系数:float, 泊松比:float, 安全系数:float, ASTM:nvarchar, GBNUM:nvarchar, 端面承压:float, 规范:nvarchar
- `dbo.气体特性表`：IID:int, 气体:nvarchar, 温度:float, 密度:float, 动态黏度:float, 热导率:float, 比热:float, SSMA_TimeStamp:timestamp
- `dbo.墙体材料表`：IID:int, NAME:nvarchar, TYPE:nvarchar, MIDU:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.不锈钢螺栓表`：IID:int, TYPE:nvarchar, LEVEL:nvarchar, CNAME:nvarchar, ft:float, fv:float, E:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.常用材料特性表`：IID:int, MNAME:nvarchar, E:float, V:float, a:float, M:float, CODENAME:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.焊缝强度表`：IID:int, STYPE:nvarchar, WTYPE:nvarchar, Fwf:float, REMARK:nvarchar
- `dbo.混凝土强度表`：IID:int, 名称:nvarchar, fc:float, ft:float, fcuk:float, E:float, a:float, v:float, midu:float, G:float, SSMA_TimeStamp:timestamp
- `dbo.连接构件承压强度表`：IID:int, TYPE:nvarchar, LEVEL:nvarchar, LTYPE:nvarchar, fcb:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.塑性发展系数表`：IID:int, SECTYPE:int, rx1:float, rx2:float, ry:float, HARDEN:bit, SSMA_TimeStamp:timestamp
- `dbo.板材分析数据表`：ID:int, NAME:nvarchar, E:float, NU:float, RHO:float, ALPHA:float, REMARK:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.高强度螺栓预拉力`：IID:int, LEVEL:nvarchar, DIAMETER:int, P:float, SSMA_TimeStamp:timestamp
- `dbo.类别码信息表`：IID:int, TYPENAME:nvarchar, BITVALUE:int
- `dbo.gas2`：GasID:int, Status:int, Timestamp:int, Name:nvarchar, MixtureType:smallint, Conductivity:real, dConductivity:real, Viscosity:real, dViscosity:real, MolecularWeight:real, Cp:real, dCp:real, AirFraction:real, SF6Fraction:real, ArgonFraction:real, KryptonFraction:real, SSMA_TimeStamp:timestamp
- `dbo.不锈钢锚栓表`：IID:int, TYPE:nvarchar, LEVEL:nvarchar, lwdiam:int, fstk:float, fyk:float, delta:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.材料类别表`：ID:int, 名称:nvarchar, 备注:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.螺栓强度表`：IID:int, TYPE:nvarchar, LEVEL:nvarchar, ft:float, fv:float, LINKSTEEL:nvarchar, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.复合金属板参数`：IID:int, TID:int, 厚度:float, 抗拉强度:float, 抗剪强度:float, 截面模量:float, 弯曲刚度:float, 弹性模量:float, 泊松比:float, 膨胀系数:float, 自重标准值:float, REMARK:nvarchar
- `dbo.碳素钢及合金钢锚栓表`：IID:int, LEVEL:nvarchar, fstk:float, fyk:float, delta:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.规范表`：IID:int, 名称:nvarchar, 标准号:nvarchar, ALUM:bit, GLASS:bit, STONE:bit, 备注:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.图库数据表`：IID:int, 名称:nvarchar, 目录ID:int, SLD:varbinary, DWG:varbinary, BREP:varbinary, CANDEL:int, ISDEL:int, REMARK:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.gas`：ID:int, Name:nvarchar, nGasses:smallint, ConductivityA:real, ConductivityB:real, ConductivityC:real, ViscosityA:real, ViscosityB:real, ViscosityC:real, MolecularWeight:real, CpA:real, CpB:real, CpC:real, Color:int, Comment:nvarchar, Certification:nvarchar, Status:int, Timestamp:int, SSMA_TimeStamp:timestamp
- `dbo.材料安全系数表`：IID:int, MNAME:nvarchar, KBM:real, KCM:real, LOCALCODE:int, REMARK:nvarchar
- `dbo.气体热物理特性`：ID:int, ANAME:nvarchar, LAMBDAA:float, LAMBDAB:float, INTERLAMBDA0:real, INTERLAMBDA10:real, MIUA:float, MIUB:float, CPAIRA:float, CPAIRB:float, MOL:float, SSMA_TimeStamp:timestamp
- `dbo.GasProperties`：ID:int, Name:nvarchar, Type:nvarchar, Conductivity:real, Viscosity:real, Cp:real, Density:real, Prandtl:real, SSMA_TimeStamp:timestamp
- `dbo.金属板类别`：IID:int, TNAME:nvarchar, REMARK:nvarchar
- `dbo.复合金属板`：IID:int, 材料名:nvarchar, 厚度折算系数:float, REMARK:nvarchar
- `dbo.锚栓强度表`：IID:int, TYPE:nvarchar, LEVEL:nvarchar, ft:float, fv:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.热轧钢筋强度表`：IID:int, 牌号:nvarchar, 压弯拉强度:float, 抗剪强度:float, fyk:float, fstk:float, E:float, G:float, midu:float, v:float, a:float, SSMA_TimeStamp:timestamp
- `dbo.gaslist`：ParentID:int, Index:smallint, ID:int, GasTimestamp:int, Thickness:real, Keff:real, SSMA_TimeStamp:timestamp
- `dbo.建筑胶参数表`：IID:int, GLUE:nvarchar, fvk:float, remark:nvarchar, SSMA_TimeStamp:timestamp
- `dbo.木材强度表`：IID:int, 名称:nvarchar, fls:float, flh:float, fy:float, fv:float, E:float, v:float, G:float, a:float, midu:float, SSMA_TimeStamp:timestamp
- `dbo.塑料强度表`：IID:int, 名称:nvarchar, f:float, fv:float, fce:float, E:float, v:float, G:float, a:float, midu:float, SSMA_TimeStamp:timestamp
- `dbo.GasMixtures`：ParentID:int, Index:smallint, GasID:int, Percentage:real, SSMA_TimeStamp:timestamp
- `dbo.sysdiagrams`：name:sysname, principal_id:int, diagram_id:int, version:int, definition:varbinary
- `dbo.拉索截面表`：IID:int, 直径:float, 有效面积:float, 破断力:float, 描述:nvarchar, SSMA_TimeStamp:timestamp

## 口径与限制

- 这是**副本库**的结构，与安装目录里的 `*.mdf` 是否逐字节一致未验证；
  同名库在主库路径下也存在（`C:\Users\administrator\AppData\Local\HWKSoft\XWall\*.mdf`）。
- 只取结构与行数，**未取任何业务数据行**。
- 行数来自 `sys.partitions` 统计，可能滞后于实际提交。
- 表名与列名为数据库原文（含中文），未做翻译或改名。

---

## 字段语义样例（实机只读导出，原文照录）

### 标准规范表（93 行）

| 规范名 | 编号 | 年 |
| --- | --- | --- |
| 《玻璃幕墙工程技术规范》 | `JGJ 102` | 2003 |
| 《铝合金结构设计规范》 | `GB 50429` | 2007 |
| 《建筑玻璃应用技术规程》 | `JGJ 113` | 2015 |
| 《建筑幕墙》 | `GB/T 21086` | 2007 |
| 《金属与石材幕墙工程技术规范》 | `JGJ 133` | 2001 |
| 《混凝土结构设计标准》(2024版) | `GB/T 50010` | 2010 |
| 《建筑结构荷载规范》 | `GB 50009` | 2012 |
| 《建筑门窗玻璃幕墙热工计算规程》 | `JGJ/T 151` | 2008 |
| 《不锈钢棒》 | `GB/T 1220` | 2007 |
| 《混凝土用机械锚栓》 | `JG/T 160` | 2017 |
| 《建筑陶瓷薄板应用技术规程》 | `JGJ/T 172` | 2012 |
| 《建筑玻璃采光顶技术要求》 | `JG/T 231` | 2018 |

### 玻璃强度表（22 行，按厚度分档）

| 名称 | 厚度下限 | 厚度上限 | f | fce | E | v | a | midu | fsd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 浮法玻璃 | 3 | 5 | 28 | 19.5 | 72000 | 0.2 | 1E-05 | 25.6 | 22 |
| 浮法玻璃 | 5.001 | 12 | 28 | 19.5 | 72000 | 0.2 | 1E-05 | 25.6 | 22 |
| 浮法玻璃 | 15 | 19 | 24 | 17 | 72000 | 0.2 | 1E-05 | 25.6 | 19 |
| 浮法玻璃 | 20 | 100 | 20 | 14 | 72000 | 0.2 | 1E-05 | 25.6 | 16 |
| 钢化玻璃 | 3 | 12 | 84 | 58.8 | 72000 | 0.2 | 1E-05 | 25.6 | 67 |
| 钢化玻璃 | 15 | 19 | 72 | 50.4 | 72000 | 0.2 | 1E-05 | 25.6 | 58 |
| 钢化玻璃 | 20 | 100 | 59 | 41.3 | 72000 | 0.2 | 1E-05 | 25.6 | 47 |
| 夹丝磨光玻璃 | 3 | 100 | 21 | 14.7 | 72000 | 0.2 | 1E-05 | 25.6 | 17 |

### 幕墙类别码表（40 行）

把体系 `ClassName` 映射到数值 `TYPEID`（1=幕墙 大类）。

| ClassName | TYPEID |
| --- | --- |
| `HWKSchema_MKMQ` | 1 |
| `HWKSchema_YKMQ` | 1 |
| `HWKSchema_HMSYMQ` | 1 |
| `HWKSchema_HYSMMQ` | 1 |
| `HWKSchema_QBMQ` | 4 |
| `HWKSchema_StoneBoard` | 2 |
| `HWKSchema_AluSBoard` | 3 |
| `HWKSchema_AluCBoard` | 3 |

### 钢材强度表（22 行，列名示例）

```text
IID 牌号 最小厚度 最大厚度 压弯拉强度 抗剪强度 端面承压 E G midu v a fyk fstk
```

口径：以上为数据库原文，**单位未标注**（如 `E=72000` 应为 N/mm²，`midu=25.6` 为 kN/m³，均属推测，未验证）。
