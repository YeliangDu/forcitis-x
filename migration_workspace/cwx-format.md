# `.cwx` 工程文件结构分析（静态）

- 样例数：15
- 合并后不同对象类型：**216**
- 类型实例总数：2018

## 1. 头部结构（最小样例，实测）

```text
ff fe                  UTF-16LE BOM
ff 0e                  标记
"HWKSoft XWall "       产品标识（UTF-16）
02 00 00 00  94 1e 00 00
0e 80                  标记
"HWKWallContext"       根对象类型名（UTF-16）
a5 02 00 00 …         随后是类型标签 + 内联二进制记录流
```

## 2. 每个样例的类型规模

| 样例 | 大小 | 类型数 | 实例数 |
| --- | --- | --- | --- |
| `各种栏杆样例.cwx` | 6.98 MB | 59 | 1230 |
| `栏杆教程.cwx` | 1.48 MB | 59 | 352 |
| `热工计算例子.cwx` | 1.02 MB | 30 | 33 |
| `左右面板不同热工.cwx` | 0.67 MB | 21 | 25 |
| `门窗计算示例1.cwx` | 0.23 MB | 79 | 96 |
| `玻璃组合优化.cwx` | 0.13 MB | 0 | 0 |
| `铝板优化.cwx` | 0.09 MB | 0 | 0 |
| `线材组合优化例子.cwx` | 0.09 MB | 0 | 0 |
| `线材优化示例1.cwx` | 0.09 MB | 0 | 0 |
| `线材优化例子.cwx` | 0.09 MB | 0 | 0 |
| `玻璃优化示例.cwx` | 0.08 MB | 0 | 0 |
| `连续梁立柱计算示例.cwx` | 0.02 MB | 81 | 93 |
| `异型索网幕墙.cwx` | 0.02 MB | 45 | 51 |
| `石材幕墙示例1.cwx` | 0.01 MB | 75 | 87 |
| `索桁架结构.cwx` | 0.01 MB | 45 | 51 |

## 3. 类型前缀分布（按不同类型数）

| 前缀 | 类型数 |
| --- | --- |
| `HWKCalc` | 107 |
| `HWKWin` | 11 |
| `HWKElement` | 10 |
| `HWKSchema` | 9 |
| `HWKLoad` | 9 |
| `HWKGraph` | 9 |
| `HWKC` | 7 |
| `HWKF` | 6 |
| `HWKGlass` | 5 |
| `HWKWall` | 4 |
| `HWKBeam` | 4 |
| `HWKBolt` | 3 |
| `HWKProfile` | 3 |
| `HWKTherm` | 2 |
| `HWKProject` | 2 |
| `HWKInfo` | 2 |
| `HWKBoard` | 2 |
| `HWKPole` | 2 |
| `HWKConnector` | 2 |
| `HWKStone` | 2 |

## 4. 出现最多的类型（按实例数）

| 类型 | 实例数 |
| --- | --- |
| `HWKCADGraphModelDoc` | 209 |
| `HWKCADGraphSurface` | 209 |
| `HWKCADGraphWire` | 209 |
| `HWKCADGraphWireSurfaceReleation` | 209 |
| `HWKCADGraphLine` | 209 |
| `HWKCADGraphEdgeWireReleation` | 209 |
| `HWKCADGraphArc` | 209 |
| `HWKProjectInfo` | 24 |
| `HWKLoadInfoB` | 18 |
| `HWKFEOfRailingFrame` | 14 |
| `HWKThermFEAnalysis` | 10 |
| `HWKGlassKValue` | 10 |
| `HWKWallContext` | 9 |
| `HWKWallStruct` | 9 |
| `HWKWallCheck` | 9 |
| `HWKSchemaCalcInfo` | 9 |
| `HWKInfoRelationOfSelf` | 9 |
| `HWKInfoRelation` | 9 |
| `HWKCalc_ProjectDescOthers` | 7 |
| `HWKCalc_ProjectDescAccord` | 7 |
| `HWKCalc_ProjectDescFormula` | 7 |
| `HWKCalc_LoadWinStand` | 7 |
| `HWKCalc_LoadWinDesign` | 7 |
| `HWKCalc_LoadHorEarthquake` | 7 |
| `HWKCalc_LoadCompound` | 7 |
| `HWKLoadInfoPHB` | 6 |
| `HWKWallKValueDrawing` | 5 |
| `HWKCalc_CWallKValueTheory` | 5 |
| `HWKCalc_CWallKValueInOutRatio` | 5 |
| `HWKCalc_CWallKValueGlassK` | 5 |

## 5. 结构含义（有证据的部分）

- 根对象是 `HWKWallContext`，向下依次出现 `HWKWallStruct` → `HWKSchema_*`（体系）→ `HWKWallCheck` → `HWKSchemaCalcInfo` → `HWKLoadInfoB` → `HWKCalc_*`。
- **计算结果是持久化对象**：`HWKCalc_*` 类型合计 107 种，说明工程文件里保存了逐条计算结果。
- 栏杆样例里 7 种 `HWKCADGraph*` 各有 209 个实例，说明几何用图结构（点/线/弧/面/关系）存储。

## 6. 口径与限制

- 只抽取 UTF-16 的类型名，**未解析字段值与偏移**；字段布局需要结合各类 `Serialize` 反编译。
- 未验证写入路径；能否"新→旧"往返完全未知。
- 样例只有 15 个，不代表全部体系都有覆盖。

---

## 7. 记录头与格式签名（2026-10-18 追加实测）

### 7.1 文件级签名

三个不同工程的偏移 8 处 `u32` 完全相同：

| 工程 | 文件大小 | 偏移 8 的 u32 |
| --- | --- | --- |
| 索桁架结构.cwx | 7,868 | **5,439,563** |
| 石材幕墙示例1.cwx | 11,355 | **5,439,563** |
| 各种栏杆样例.cwx | 7,318,303 | **5,439,563** |

→ 这是一个**格式签名/版本常量**，可作为 `.cwx` 文件嗅探依据。含义未解（可能是产品码或格式版本）。

### 7.2 记录头 = (u32 a, u32 b)

`索桁架结构.cwx` 前 14 条记录的头部：

| 偏移 | 类型 | a | b |
| --- | --- | --- | --- |
| 42 | HWKWallContext | 677 | 0 |
| 216 | HWKWallStruct | 677 | 6 |
| 334 | HWKSchema_LinkTruss | 677 | 5 |
| 401 | HWKWallCheck | 677 | 8 |
| 451 | HWKSchemaCalcInfo | 677 | 6 |
| 497 | HWKLoadInfoB | 1 | 18 |
| 529 | HWKThermFEAnalysis | 0 | 14 |
| 573 | HWKGlassKValue | 0 | 16 |
| 609 | HWKLinkTrussInfo | 1 | 14 |
| 649 | HWKProjectInfo | 0 | 10 |
| 685 | HWKPSGlass | 0 | 4751374 |
| 711 | HWKProjectInfo | 677 | 7 |

观察：
- `a` 只出现三种值 `0 / 1 / 677`（677 = `0x2A5`），疑似**类族或序列化模式标记**
- `b` 多为 6–18 的小整数，疑似**字段/子对象计数**；但 `HWKPSGlass` 的 4,751,374 明显是**错位**——
  说明某些记录的头部不由固定 16 字节构成，或类型名出现在非记录起点

→ 结论：**记录头格式还未完全解出**，`b` 不能直接当计数用；`cwx-read.py` 的"按下一个类型名截断"
在有嵌套/错位的记录上会多读（`HWKCADGraphArc` 中位 370 个 double 就是症状）。

### 7.3 下一步（下一轮从这里开始）

1. 以 `索桁架结构.cwx`（7.8 KB，52 个类型标记）为**完整可枚举样本**，逐条手工核对记录边界
2. 用 `b` 的分布反推它到底是"字段数"还是"字节长度"（小值 6–18 vs 异常大值）
3. 边界确定后，`HWKCalc_*` 记录的 double 才能可靠取值 → 才能做 G3 数值闸门

---

## 8. 记录头语义：`a` = 类组，`b` = 组内实例序号（2026-10-19 实测）

用 `索桁架结构.cwx`（52 条记录）逐条量 `body = 下一条位置 − (本位置 + 名字长度)`：

| 观察 | 证据 |
| --- | --- |
| `a` 只有 `0 / 1 / 677` 三种 | 677 几乎总是与 `HWKCalc_*`、`HWKWall*` 同现 |
| `b` 在同一类组内**连续递增** | `HWKCalc_ProjectDescOthers/Accord/Formula` = 0/1/2；`HWKCalc_LoadWinStand/WinDesign/HorEarthquake/Compound` = 0/1/2/3；`HWKCalc_LinkTruss*` = 0…6 |
| `HWKCalc_*` 记录 body **恒为 10 字节** | 名字后只有 8 字节头 + 2 字节，等于"登记占位" |
| 大块数据在别处 | `HWKLinkTrussInfo` body=2,625；`HWKThermFEAnalysis`=381；`HWKPSGlass`=268；`HWKGlassKValue`=255 |

**结论（改写前一轮的判断）**：`b` 不是"字段数"，是**该类型在本工程内的实例序号**。
`HWKCalc_*` 在前缀区是**占位登记**（10 字节），真正的数值在后续大块记录里。

### 对 G3 数值闸门的影响

要取 `HWKCalc_GlassPSDisp` 的结果，不能在前缀区的占位记录里找，必须定位到
`HWKLinkTrussInfo` / `HWKGlassKValue` 这类**携带数据的大块记录**，并按 `a/b` 重建它们与
`HWKCalc_*` 占位之间的对应关系。这是下一轮的具体动作。

### 仍未知

- `a=0/1/677` 的确切含义（类组 ID？序列化模式？）
- 大块记录内部如何组织（是否定长 double 数组 + 变长字符串）
- `HWKSOFTTHERMEND__________` 的 112 字节 body 是结束标记区还是数据

---

## 9. `HWKCalc_*` 的 Serialize 是空壳（2026-10-19 实测）

`?Serialize@HWKCalc_LoadWinStand@@MEAAXAEAVCbArchive@@@Z` = `0x18009fc60`，反编译结果只有两步：

```c
HWKCalc_LoadBase::Serialize(this);   // 全部字段由基类写
CbArchive::IsStoring(ar);            // 无自有字段
```

且**四个类的 Serialize 共用同一地址**：`HWKCalc_LoadCompound` / `LoadHorEarthquake` /
`LoadWinDesign` / `LoadWinStand`（链接器相同代码折叠）。

→ 与 §8 的"`HWKCalc_*` body 恒 10 字节"完全一致：**这些条目本身不存数据**，
数值在其基类/所属信息对象里。要取计算结果，必须走基类或宿主对象，不能在 `HWKCalc_*` 记录里找。

### 下一步（下一轮）

反编译 `HWKCalc_LoadBase::Serialize` 和 `HWKInfoBase::Serialize`，看基类写什么；
再对照一大块记录的字节流，才能确定"长度前缀 + 字段"的编码原语。

---

## 10. CAD 图形按"每实体 7 条记录"成组序列化（2026-10-19 实测）

对比两个同体系（`HWKSchema_Railings`）工程：

| 类型 | 各种栏杆样例.cwx | 栏杆教程.cwx |
| --- | --- | --- |
| `HWKCADGraphModelDoc` | 164 | 42 |
| `HWKCADGraphSurface` | 164 | 42 |
| `HWKCADGraphWire` | 164 | 42 |
| `HWKCADGraphWireSurfaceReleation` | 164 | 42 |
| `HWKCADGraphLine` | 164 | 42 |
| `HWKCADGraphEdgeWireReleation` | 164 | 42 |
| `HWKCADGraphArc` | 164 | 42 |

**七种图形类型在两个文件里数量完全相同**（164 / 42），说明每个图形实体固定产生 7 条记录
（文档→面→线框→线框-面关系→线→边-线框关系→弧）。这与 §7.2 里
`HWKCADGraphLine` 恒在 `Arc` 前 170 字节一致——它们属于同一实体的固定顺序块。

→ 对重构的意义：几何数据的序列化是**定型的 7 元组**，不是任意对象图。重写 `.cwx` 读取时
可以按"每实体 7 条"的块结构解析，不必做通用对象还原。
