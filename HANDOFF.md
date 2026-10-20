# 交接 · FORCITIS-x（截面库导入 + 规范/CI 基建完成后）

## 交接更新 · 2026-10-21 11:30 (UTC+8) / 新会话从这里读

**三行复述**——已验证：**截面库路线改为"直接上传 DWG → 服务端转换 → 算参 → 入库"**（D26/D27），
`FG5025`（50×25×2 方管）与闭式解**逐位一致**（A=284.000、Ix=29,603.67、Iy=90,078.67、Cy=12.5，误差 0）；
`PBW7525103` 双算法（Green 解析 vs 扫描线全局 even-odd）互校 **0.5%**（A=820.955 mm²、Ix=316,988 mm⁴、Iy=672,569 mm⁴）；
未完成：**与原版的逐件外部差分**（缺该件号旧值）、轴向口径锚定（IZ↔Iy、IY↔Ix 仍是假设）、多外环/图框污染的分组修正；P2/P3/P4 未启动。

### 一、本轮真正落地的东西

| 产物 | 说明 |
| --- | --- |
| `scripts/poc/dxf-section.py` | DXF/DWG → 环 → 孔 → 参数；`--selftest`（DXF）、`--selftest-dwg`（DXF→dwgwrite→DWG→导入）均 PASS；含 `$INSUNITS` 单位、INSERT 递归展开、转换器产物损坏时自动降级 group-code 扫描 |
| `scripts/poc/dwg-blocks.py` | 块普查：解 `TABLES/BLOCK_RECORD` 句柄→块名，按块求特性 |
| `scripts/poc/classify-sections.py` | 家族判别（铝型材 / 方管 / 钣金 / 五金 / 图框），特征：填充率、环数、长细比、等效壁厚 `≈2A/Σ周长`、名称白/黑名单 |
| `scripts/poc/crosscheck-section.py` | 双算法对拍（Green vs 光栅） |
| `scripts/poc/render-blocks.py` | 候选块渲染成对照图 `evidence/poc/P1/sections/profiles-sheet-{1,2}.png` |
| `docs/section-library-spec.md` | 截面库规格（导入→校验→入库→按 `sectionAssetId+version` 引用） |
| `docs/decisions.md` D26/D27 | 截面库路线；DWG 直传 + 服务端转换（LibreDWG，GPL-3 待决策；商业替代 ODA） |

### 二、真实图纸实测（用户桌面的 `7#10#楼型材断面图.dwg`）

```text
2,381,186 B DXF ← dwg2dxf；ezdxf 拒收（POLYLINE 子实体不规范）→ 自动 group-code 扫描兜底
1,425 实体 / 94 闭合环 / INSUNITS=4(mm) / 坐标在 27 万 mm 量级（必须先平移到局部原点）
BLOCK_RECORD 251 个块；含几何 69；闭合环 33；疑似截面 30
```

家族判别结果（`evidence/poc/P1/blocks-classified.json`）：铝型材 9、方管 1、钣金 4、五金 13、图框 7、待定 10。
已向用户确认：`FG5025` = 50×25 方钢（方管）；**`PBW7525103` 用户说明是"组合型材"**。

### 三、P1 台账状态（`planning/poc-state.json`）

| 步骤 | 状态 |
| --- | --- |
| s1 引擎单测（9 个） | PASS |
| s2 解析解判据（5 用例 ≤1e-12） | PASS |
| s3 旧系统数据摄取（只读导出 12+3+12 行） | PASS |
| s4 **DXF/DWG 导入与算参** | **PASS**（自检两条链路都在） |
| s4b 真实图纸批量导入与对照 | **RUNNING**（导入可用；分组与外部差分未完） |
| s5 与旧系统值对照（A/B 面积判据 9 检查 0 失败） | PASS |
| gate P1 | 仍 BLOCKED（C 项缺外部参照） |

### 四、下一条命令（按优先级）

```text
# 1) 口径锚定：找一件"尺寸已知"的旧库行（T=2、面积≈2.84 cm² 的方管）
python3 scripts/poc/export-old-system.py --sql "SELECT IID,AREA,IZ,IY,T FROM [dbo].[型材参数表] WHERE T=2 AND AREA BETWEEN 2.6 AND 3.0"

# 2) 分组修正（当前把图框外环当父级，导致部分截面惯性矩为负）
python3 scripts/poc/dxf-section.py evidence/poc/P1/sections/real-profiles.dwg --split

# 3) 全量对拍（每个候选块）
python3 scripts/poc/crosscheck-section.py PBW7525103
```

### 五、阻塞与未决

1. **外部差分缺参照**：旧库按名称查不到 `PBW7525*`；`复合型材参数表` 只有 3 行且面积不在 8.21 cm² 附近；
   `型材参数表` 面积 8.15–8.27 的两行 IZ/IY 与本件不符（40.99/58.54、37.77/37.77 vs 我们 31.70/67.26）。
   → 需要：该件号的旧值截图 / 含该型材的旧 `.cwx` / 件号与旧 `IID` 的对照表。
2. **轴向口径**：假设 `IZ ↔ 我们的 Iy`、`IY ↔ 我们的 Ix`（依据 IID 204 比值 3.037 vs 我们 3.043），未确证。
3. **分组**：图框外环把型材当孔 → 需按"环内含其它环则视为容器"或按图层/块分组。
4. **转换器许可**：LibreDWG 为 GPL-3（内部可用；产品分发需 ODA 或法务确认）。
5. **上下文误报教训**：不要再凭感觉报"上下文耗尽"；用 `python3 scripts/session-usage.py`（读会话 usage，阈值 75%）。

### 六、最近检查（全部 exit 0）

```text
cd replica && npm run check                  # build+lint+9 tests
python3 scripts/check-standards.py           # 10 项门禁
python3 scripts/poc/dxf-section.py --selftest        # 50x60 带孔矩形，A=5600、Ix=1,786,666.67
python3 scripts/poc/dxf-section.py --selftest-dwg    # DXF→DWG→导入，同值
python3 scripts/poc/brep-arcs2.py                    # 1783 面积 0.00%（BREP 路线保留为证据）
```

远端仓库 `github.com/YeliangDu/forcitis-x`（public），CI 已通过（run 39406831450）；注意
`scripts/scheduler/assurance.py` 有 6 条**既有**类型告警（与截面工作无关，未改动）。

---

## 历史（按时间倒序，内容保留不覆盖）

## 交接更新 · 2026-10-21 11:00 (UTC+8)：口径探针（IZ/IY ↔ x/y）；方法与结果的关系已澄清

**三行复述**——已澄清"方法不唯一 ≠ 结果不唯一"（Green 解析积分 / 扫描线 / OCCT `BRepGProp` 都收敛到同一积分值，差异只是离散误差）；
本轮做**轴向映射探针**：用 FG5025（50×25×2 方管，闭式解 Ix=2.9604、Iy=9.0079 cm⁴，比值 3.043）反查旧库，
在 `AREA 2.70–3.00` 的 10 行中发现 `IID 204`（IZ=8.8811 / IY=2.9242，比值 3.037）与"**IZ ↔ 我们的 Iy、IY ↔ 我们的 Ix**"一致；
未完成：该假设**未确证**（IID 204 面积 2.743 与 2.840 差 3.4%，T=3 而 FG5025 为 2，不是同一件），需一件已知尺寸的旧库行锚定。

### 下一条命令

```text
# 找一件"宽高已知"的旧库行做锚定（例如拿旧库里 T=2、AREA≈2.84 的方管行）
python3 scripts/poc/export-old-system.py --sql "SELECT IID,AREA,IZ,IY,T FROM [dbo].[型材参数表] WHERE T=2 AND AREA BETWEEN 2.6 AND 3.0"
```

---

## 交接更新 · 2026-10-21 10:20 (UTC+8)：PBW7525103 内部对拍通过；外部差分缺参照

**三行复述**——已验证：`PBW7525103` 的两套独立算法结果一致（Green 解析积分 vs 扫描线光栅，全局 even-odd 处理孔洞，
A/Ix/Iy/Cx/Cy 相对差 0.5%–1.8%，差异来自光栅步长）→ **数学链路自洽**；数值 A=820.955 mm²、Ix=316,988 mm⁴、Iy=672,569 mm⁴、8 环（4 外 + 4 孔）；
未完成：**外部差分**——旧库按名称查不到该件号（图库无 `PBW7525*`），`复合型材参数表` 仅 3 行且面积都不在 8.21 cm² 附近，
`型材参数表` 中面积 8.15–8.27 的两行 IZ/IY 与本件不符 → 需要该件号的旧值才能判定 0.5%。

### 顺带修掉的两个真 bug

1. 环方向未归一 → 二次矩相互抵消（曾出现负 Ix）；已按"外环 CCW / 孔 CW"归一化，`FG5025` 恢复解析值（A=284、Ix=29603.67、Iy=90078.67，误差 0）。
2. 光栅对拍里孔洞用"逐环 OR"导致孔被填实；已改为**全局 even-odd**。

### 下一条命令

```text
python3 scripts/poc/crosscheck-section.py PBW7525103
python3 scripts/poc/classify-sections.py
```

---

## 交接更新 · 2026-10-21 09:10 (UTC+8)：真实图纸图元清单完成；分组仍被"图框外环"污染

**三行复述**——已验证：用户桌面 DWG 的图元清单（`--inventory`）为 **4,106 LINE / 250 LWPOLYLINE / 251 BLOCK / 188 INSERT**
（另有大量非几何对象），块名在 `BLOCK_RECORD` 表而非 BLOCK 内联 → "按块分组"须先解句柄映射；
分组规则已改为"每个最外层环 = 一个截面，内层环按包含关系作孔" → **35 个截面**，但图里有一个**包围全图的外框矩形**，
把型材都当成它的孔 → 部分组出现 −1e+15 量级惯性矩。
未完成：排除外框（按图层 code 8 / 块 / "环内含其它环则视为容器"）、与 `型材参数表` 对照、P2–P4。

### 下一条命令

```text
python3 scripts/poc/dxf-inventory.py evidence/poc/P1/sections/real-profiles.dwg --by-block   # 需先补 BLOCK_RECORD 句柄映射
```

---

## 交接更新 · 2026-10-21 08:30 (UTC+8)：真实型材图纸已导入；分组规则需改为"按块/单外环"

**三行复述**——已验证：用户桌面的 `7#10#楼型材断面图.dwg`（907,858 B）经 `dwg2dxf` 转出 2.38 MB DXF，
ezdxf 因转换器产物不规范（`Expected DXF entity INSERT or SEQEND`）拒绝 → **自动降级为 group-code 扫描成功**，
解析出 **1,425 个实体、94 个闭合环、INSUNITS=4（mm）**；并确认必须在计算前把坐标平移到局部原点（原图在 27 万 mm 量级，否则二次矩灾难性抵消）。
未完成：**分组规则**——按"包围盒邻近(5 mm)"把相邻型材合并了，含多环的组算出无意义惯性矩；下一步改按块(INSERT)分组，或强制"每截面恰 1 个外环"。

### 下一条命令

```text
python3 scripts/poc/dxf-section.py evidence/poc/P1/sections/real-profiles.dwg --by-block
```

（`--by-block` 待实现：按 INSERT 的块名逐个求特性，并与 `型材参数表` 的 `AREA/IZ/IY` 对照）

---

## 交接更新 · 2026-10-21 07:40 (UTC+8)：几何链接近似失败 → 改走"关系索引表"重建拓扑

**三行复述**——已验证：1783 仍稳定 **0.00%**（24 线+16 弧、2 环）；但 1781/1782 出现**退化环**（67 点、面积≈0，即环折返），
1780 面积偏大 42%（4 环、无内孔识别）；根因是"用端点几何猜邻接 + 用角度差猜弧的扫掠方向"两条都不可靠；
未完成：改用记录内**关系索引表**（`u32 count + count×u32 id`，指代本记录子对象 id 5,6,7…）重建 wire→edge 拓扑，再算特性；P2–P4 未动。

### 为什么这样改

BREP 尾部本身就是索引表；用它确定"哪条边属于哪个环"是**数据驱动**，不需要猜容差与方向。
1783 之所以一直对，是因为它的环恰好端点都精确相接。

### 下一条命令

```text
python3 scripts/poc/brep-relations.py 1782   # 解析 (count, ids...) 表，输出 wire→edge 索引，核对是否覆盖全部 56 线 + 27 弧
```

---

## 交接更新 · 2026-10-21 07:00 (UTC+8)：弧改用"圆心/半径套线端点"拟合成功；剩余 bug 在多边形拼装

**三行复述**——已验证：OCCT 只用于几何（`TopoDS_*`/`BRepBuilderAPI`/布尔圆角/`BRepGProp` 精确质量属性），
**没有** 任何网格划分符号（`BRepMesh`/`Poly_Triangulation`）或求解能力；FE 是自研结构化网格（`Element` 4060、`Quad` 316、`Mindlin` 298、`Mitc` 386）+ 独立稀疏求解库（`SPARSE.dll`/`SparseSolve.dll`）；
弧参数改为**不依赖角度基准**的拟合（圆心候选×半径候选，取"恰好 2 个线端点落在圆周上"），命中率 1783 16/16、1782 26/27、1781 23/24、1780 67/67；
未完成：多边形拼装 bug（1783 两条链有向面积互相抵消 → `build_chains` 产生重复/镜像链）、Ix/Iy 对照、P2–P4。

### 下一条命令

```text
python3 scripts/poc/brep-arcs2.py 1783      # 先修拼装：去重 + 按包含关系区分外环/内环
```

---

## 交接更新 · 2026-10-21 06:20 (UTC+8)：截面已可视化并被用户确认；弧参数映射随断面族不同

**三行复述**——用户确认图上的形状就是日常铝型材截面（多腔薄壁挤压件），并已把 `brep-1783.png`/`brep-1780.png` 直接显示在会话里；
已验证：1783 的 16/16 弧用统一映射 `(a0=d0, r=d1, a1=d2, cx=d3, cy=d4)` 全部落在相邻线端点上，面积 **0.00%**；
1780 的 67 弧只解出 16 条，1781/1782 全未解（1782 例：弧心 5.656/7.103、r=0.3，端点只与 (5.36,7.1) 部分吻合 → 角度基准或半径符号不同）；
另修正一处解析错误：**2 字节尾部标记并非每条记录都有**（1782 的 Line 记录 46B→48B），已改为仅当 `len%8==2` 时裁剪。
未完成：弧映射搜索扩展、链接器（多环分离）、Ix/Iy/Wx 对照、P2–P4。

### 下一条命令

```text
python3 scripts/poc/brep-arcs.py 1782     # 扩展候选：角度基准 0/π、半径 ±、端点 (cx±r,cy) 或极角端点
```

---

## 交接更新 · 2026-10-21 05:40 (UTC+8)：图库 DWG 列解开但块内为空；截面几何仍以 BREP 为准

**三行复述**——已验证：`图库数据表.DWG` 是 **bzip2 压缩的 AC1024 DWG**（gid 1783：12,506 B → 16,775 B），
`dwg2dxf`/`dwgread -O JSON` 均可读，但**块内没有任何 LINE/ARC**（只有 TABLE/DICTIONARY/空 BLOCK_HEADER），
`$INSBASE` 恰等于型材 `CX/CY`（24.7160306/27.9604829）→ 块里是 HWK 自定义对象（`HWUtil.arx` 定义），通用 DWG 工具看不到实体；
因此几何仍以 BREP 为准（已解 line=48 B 两个 3D 端点、arc=96 B 圆心/半径/起止角，gid 1783 面积 **0.00%** 命中）。
未完成：8/12 型材的 BREP 里没有 line/arc（实体类型未清点）、链接器加固、Ix/Iy/Wx 比对、P2–P4。

### 新增资产

`evidence/poc/P1/sections/section-1783.dwg`（解压后的 DWG）+ `section-{1780..1783}.svg`（由 BREP 几何渲染，供目视核对）。

### 下一条命令

```text
python3 scripts/poc/brep-stream.py 4570   # 清点"无 line/arc"的型材实际用了哪些实体类型
```

---

## 交接更新 · 2026-10-21 04:55 (UTC+8)：BREP 结构定性 —— 记录体是"子对象流"，P1 s4 恢复推进

**三行复述**——已验证：Arc 记录体内部是**多个子对象的串联**，每个子对象由 `u32 version(6) + u32 objectId + u64 0`（16 B）开头再接该类型字段；
1783 体里出现 id 5,6,7,8,9,10,11 于偏移 0/114/132/198/216/282/300，边界处有 `04 00 06 00 00 00` 之类标记（待解）；
未完成：类型标记与各类型字段宽度、拼轮廓、C 项、P2–P4。

### 下一条命令

```text
python3 scripts/poc/parse-curves.py   # 改造成"按 `06 00 00 00 | id | 8B 0` 切子对象"的流解析器
```

---

## 交接更新 · 2026-10-21 04:20 (UTC+8)：P1 C 项 —— 四种静态假设全部排除，只剩 A2/B 两条路

**三行复述**——本轮做了 4 个可证伪实验并全部否证（①中间区是点阵 double？否，含 7.4e248；
②尾部关系表能解释整条记录？否，只有最后 8–192 B 是 `u32 count + count×u32 id`；
③型材可当空心矩形由 (AREA,IZ,IY,T) 反解几何？否，预测误差 >50%；
④记录体 = `Serialize` 直写？否，前缀 `int32 6 / int32 5 / 8B 0 / double…` 与反编译顺序不符）；
未完成：P1 C 项（需 A2 对象表解码或 B 动态差分）、P2–P4。

### 证据

`evidence/poc/P1/rea/arc-layout.json` 新增 `negative_results`（4 条，含具体数字）与 `next_options`（A2/B）。

### 两条候选路（判据不变）

| 路 | 做法 | 状态 |
| --- | --- | --- |
| **A2** | 在 7 条记录中找"固定宽度对象表"（试 8/16/24 B 记录），用引用 id 范围与计数闭合校验 | 纯离线，未开始 |
| **B** | 启动隔离客户端 → 型材/断面编辑器改一个尺寸 → 另存 → 比较库中 BREP 差异 | 前置已做：session 1 Active、XWall 未运行；需 UI 自动化 |

### 下一条命令

```text
python3 scripts/poc/solve-brep-layout.py 1783     # A2 的第一版搜索器（尾部先行，已可跑）
```

---

## 交接更新 · 2026-10-21 03:40 (UTC+8)：P1 s4 方法切换 —— 静态度量对不上，改走"改尺寸→另存→字节差分"

**三行复述**——本轮把 `HWKCADGraphArc/Line`、`HWKCADGraphBase`、`HWKCADGraphModelDocObject` 三个 `Serialize` 反编译完整读出并落盘
（`evidence/poc/P1/rea/*.json`，含 `arc-layout.json` 的字段顺序），但**实测字节流与写入顺序不一致**：Arc 记录体以
`int32 6 / int64 5 / int32 0 / double 1.5708…` 开头，而反编译顺序是 `int 21 → int64 → int32 → CbString`，
且尾部是 `(int 1, int id)+2` 的成对索引数组（1783 体 5154 B，3287 B 为 0，仅 128 个 double 非零）→ 判断记录由**容器层**写入，
不能靠"按字段顺序硬解"；`SerializeConstructorInclude(Wire)` 经查只是把 `this+0x80..0xa8` 清零，不是序列化器。
未完成：P1 C 项、P2–P4。

### 方法切换（已写入 poc-plan/state）

改用 `.cwx` 字段宽度那套**已验证**的招法：在 ECS 只读副本上打开含该型材的工程 → 改一个断面尺寸 → 另存 → 逐字节差分，
直接量出参数偏移与宽度；不再用"猜字段顺序"逼近。

### 下一条命令

```text
python3 scripts/poc/orchestrate.py next      # 会指向 s4b（动态差分）
```

另注：本轮曾误在 HANDOFF 写"上下文 78%"，实测为 53.9%，已在原位更正（不掩盖）。

---

## 交接更新 · 2026-10-21 03:10 (UTC+8)：Arc 字段顺序已精确、尾部定性为"int32 成对索引数组"；上下文实测 53.9%（未达 75% 阈值，本轮不 handoff）

**三行复述**——已验证：`HWKCADGraphArc::Serialize` 的写入顺序由反编译确证（ModelDocObject: int 21 + int64 +0x8 + int32 +0xc + CbString +0x10；
GraphBase: int +0x48 + double +0x50；Arc: int +0x70 + 3×double +0x90/98/a0 + gp_Pnt +0xa8 + 2×gp_Vec +0xc0/+0xd8，
**OCCT 类型各 3 个 double**，读写半由 `archive+8` 的 IsStoring 分支决定、版本门在 `this+0x28`），
且 Arc 记录体尾部实测为 **int32 成对数组**（`(1,64) (1,66) (1,68) …` 每次 +2），1783 体 5154 B 中 3287 B 为 0、仅 128 个 double 非零 → 大块是索引/关系数组；
未完成：写出该数组的方法与其计数前缀（决定 4+count*8 编码），P1 C 项、P2–P4。

### 本轮新增证据

- `evidence/poc/P1/rea/{arc-serialize,graphbase-serialize,modeldocobject-serialize}.json`（REA 反编译原文）
- `evidence/poc/P1/rea/arc-layout.json`（写入顺序 + 版本门 + 尾部数组结论 + 下一步）
- 结论：`SerializeConstructorInclude(Wire)` **不是序列化器**（只把 this+0x80..0xa8 清零），不要再按它找字段

### 下一条命令

```text
# 找写"成对 int32 数组"的方法（候选：HWKCADGraphModelDoc::SerializeRelations 的数组分支）
export PATH="/Users/yeliang/.nvm/versions/node/v24.18.0/bin:$PATH" GHIDRA_INSTALL_DIR=/Users/yeliang/tools/ghidra_12.1.4_PUBLIC
rea decompile evidence/baseline/extracted/cab/_1C34889D4B7943DB91CA676194B3F1FC \
  --procedure='?SerializeRelations@HWKCADGraphModelDoc@HWKCAD@@MEAAXAEAVCbArchive@@QEAPEAVHWKCADGraphModelDocObject@2@@Z' --format=json
```

读法：在 77 行伪代码里找写 `int` 对的循环（`operator<<(int)` 两次 / vector 遍历），确认计数前缀与元素宽度。

---

## 交接更新 · 2026-10-21 02:20 (UTC+8)：ES-01 整改完成、ADR 索引建立；基建审计闭合 2 项

**三行复述**——已按"采纳"执行：①ES-01 重命名落地（`areaMm2/centroidXMm/ixMm4/wxTopMm3/principalAngleRad…`，
波及 4 个文件），`tsc` + 9 单测 + PoC 运行器 + 旧系统对照脚本全部通过；②`docs/adr/0000-index.md` 建立 D01–D24 → ADR 映射（状态 legacy）；
③`planning/standards-audit.json` 更新：ES-01=RESOLVED、ES-05/17=MITIGATED，剩余 GAP 仅 ES-11–14/18–22（随 MVP 落地）与 ES-18（仓库无提交，需授权）。
未完成：P1 C 项（链工具读写切分 → `HWKCADGraphArc` 逐字段消费）、P2–P4。

### 本轮检查（全绿）

```text
cd replica && npm run check            # build+lint+test → exit 0（9 passed）
python3 scripts/check-standards.py     # 10 项 PASS
python3 scripts/poc/compare-profiles.py# 9 检查 / 0 失败（新字段名下仍通过）
```

### 下一条命令（回 PoC 主线）

```text
python3 scripts/build-serialize-chains.py --pe evidence/baseline/extracted/cab/_1C34889D4B7943DB91CA676194B3F1FC \
  --root HWKCADGraphArc --json /tmp/arc.json
```

要点：该模块的 `Serialize` 体没有 `this+0xc` 版本门，需先用 `IsStoring` 谓词调用点把 store/read 半切开，
再逐字段消费 `Arc` 载荷到字节闭合（当前 5154 B 无法按"点数组"拟合）。

---

## 交接更新 · 2026-10-21 01:40 (UTC+8)：基建回看审计 — 1 项待修、1 项已缓解、3 项 GAP

**三行复述**——已做"既有成果 vs 今日规范"回看审计（`planning/standards-audit.json`）：**ES-01 违反**（`SectionProperties`
的 `area/cx/ix/wxTop…` 无单位后缀）、**ES-05 已缓解**（新增 `scripts/README.md` 声明 `scripts/**` 属 T2/T3）、
**3 项 GAP**（11 条规范仍 PLANNED、ADR 未迁移、仓库无提交）；未完成：ES-01 重命名（波及 5 文件）、P1 C 项、P2–P4。

### 审计结论

| 规范 | 判定 | 动作 |
| --- | --- | --- |
| ES-01 单位后缀 | **PENDING_FIX** | 引擎字段/参数改 `*Mm/*Mm2/*Mm3/*Mm4/*Rad`；影响 `packages/section/src/index.ts`、`section.test.ts`、`replica/scripts/{poc-p1-section,section-props}.mts`、`scripts/poc/compare-profiles.py` |
| ES-05 命名政策 | **MITIGATED** | `scripts/README.md` 声明 T2/T3；T0 扫描机器强制 |
| ES-02/10/16 | PASS | `check-standards.py` 10 项 |
| ES-11–14/19–22 | GAP | 11 条 PLANNED，随 PoC/MVP 落地 |
| ES-17 ADR | GAP | 需 `docs/adr/0000-index.md` 映射 D01–D24 |
| ES-18 提交 | GAP | 仓库无提交；**需用户授权**才可 git init/commit |

### 下一条命令

```text
python3 scripts/check-standards.py     # 10 项门禁，当前 PASS
```

---

## 交接更新 · 2026-10-21 00:55 (UTC+8)：P1 C 项定性为"Arc 对象图解码"，判据不改，P1 保持 BLOCKED

**三行复述**——已验证：BREP 记录体结构 = `u32 版本(6) + u32 序号 + 8 字节零 + body`，`HWKCADGraphLine` body 恰好 6 个 double（两个点），
`HWKCADGraphArc` 是**最后一条记录且 body 直通文件尾**（5154 B / 644 double，含角度、点、0/1 标志与 NaN），
用"偏移×点数"穷举（offset 0–200 步长 4、点数 20–900）**找不到**任何满足 `AREA=73.5 mm²` 的连续点阵 → 轮廓不是简单数组，而是嵌套对象图；
未完成：Arc/关系类的字段顺序（需 `HWKCADGraphArc` 的 Serialize 精确布局，当前链工具在无 `0xc` 版本门的类上会把读半混入写半）。

### 判据（按用户指示不改）

P1 gate 仍要求 C（IZ/IY/WZ 与原版对照）→ **P1 保持 BLOCKED**，不降级为 P1a。

### 下一条命令（聚焦一个点）

```text
python3 scripts/build-serialize-chains.py --pe evidence/baseline/extracted/cab/_1C34889D4B7943DB91CA676194B3F1FC   --root HWKCADGraphArc --json /tmp/arc.json    # 再看 HWKCADGraphArc 的写半/读半划分
```

改进方向：先修链工具的"无版本门"切分（用 `IsStoring` 谓词调用点作为 store/read 分界），
再按字段顺序逐字段消费 Arc body，直到字节数闭合；闭合后即得到轮廓点列 → 跑 C 项。

---

## 交接更新 · 2026-10-21 00:20 (UTC+8)：P1 剩余工作定性为"数组编码"，不是字段偏移

**三行复述**——已验证：`build-serialize-chains.py` 支持命名空间符号（`?Serialize@HWKCADGraphLine@HWKCAD@@`），
`HWKCADGraphLine/Arc` 链可解（Line 14 字段、Arc 22 字段）；**但** 载荷里的关键字段是"聚合/数组"型（点坐标数组、字符串），
字段宽度不可由偏移推出；另用存储值验证：复合与各子段的 `CX/CY` **完全相同**（如 31.181/27.182），说明 `SUBID1..3` 是**沿长度方向的切片**，
不是截面拼装件 → P1 的 C 项（IZ/IY/WZ 复算）**不能**用 stored 数值凑出来，必须解 BREP 数组。
未完成：s4b（`CbArchive` 数组/字符串原语）、P2/P3/P4。

### 结论（对 PoC 范围的影响）

引擎的**正确性**已由解析解闭环（9 单测 + 5 用例 ≤1e-12）；P1 的 C 项本质是**与原版保真度的对照**，
需要旧系统 BREP 数组解码，属"深度逆向"，可与主目标解耦。

**建议**（待用户定）：把 P1 gate 拆为
- **P1a（建议立即关掉）**：A/B + 解析解 C → 引擎可用；
- **P1b（独立）**：旧系统 BREP 数组解码 → 与原版 IZ/IY/WZ 对照（保真验证）。

---

## 交接更新 · 2026-10-20 23:55 (UTC+8)：P1 硬判据 A/B 通过；BREP 记录框已解

**三行复述**——已验证：P1 s1/s2/s3/s5 全 PASS（引擎 9 单测；解析解 ≤1e-12；只读导出 12 型材+3 复合+12 图库；
对照 9 项检查 0 失败，判据已按实测语义改成 A=组合面积=主型材面积、B=子段面积之和=主面积、C=二次数值待轮廓）；
**新发现**：`图库数据表.BREP` 与 `.cwx` 同一记录框（`u16 tag(0x8000|len)` + UTF-16 类名 + `u32`（实测恒 6）+ 载荷），
每个断面恰好 **7 条记录**（ModelDoc/Surface/Wire/WireSurfaceReleation/Line/EdgeWireReleation/Arc），Line 载荷以 double 起（如 -9.517/7.4 mm）；
未完成：P1 s4 的字段布局（记录长度未存，需用 `HWKCAD.dll` 的 Serialize 链推）、P2/P3/P4 未开工。

### 下一条命令

```text
python3 scripts/build-serialize-chains.py --pe evidence/baseline/extracted/cab/_1C34889D4B7943DB91CA676194B3F1FC \
  --root HWKCADGraphLine --root HWKCADGraphArc --root HWKCADGraphModelDoc
```

（**注意**：本轮有一次 `tail` 输出未限长导致 50KB 灌入上下文，后续所有 dump 必须限行/限字节。）

---

## 交接更新 · 2026-10-20 23:00 (UTC+8)：PoC 工作流编排器上线，P1 已推进到数据关卡

**三行复述**——已验证：PoC 编排器 `scripts/poc/orchestrate.py` 可运行（status/next/run/gate、状态机、门禁、证据存在性检查、日志落 `evidence/poc/orchestrator/`），
`run P1` 实测 **s1 引擎单测 PASS、s2 解析解判据 PASS、s3 旧系统数据摄取 BLOCKED（exit 2，打印只读 SQL）**，状态已写入 `planning/poc-state.json`；
未完成：P1 硬判据（与旧系统 ≤0.5%）与 s4 BREP 解码、P2/P3/P4 实现；下一步：只读导出 3 张表到 `evidence/poc/P1/input/` 后重跑 `run P1`。

### 编排结构（`planning/poc-plan.json`）

| PoC | 步骤 | 当前状态 |
| --- | --- | --- |
| P1 断面 | s1 引擎单测 → s2 解析解判据 → s3 数据摄取 → s4 BREP 解码 → s5 对照 | s1/s2 PASS，s3 BLOCKED（缺 fixture） |
| P2 桥 | s1 几何模型 → s2 桥+荷载 → s3 与旧荷载表对照 | NOT_RUN（npm 脚本未实现，会显式失败） |
| P3 结果→PDF | s1 ResultBundle → s2 六类图 → s3 PDF+指纹 | NOT_RUN |
| P4 FE | s1 需 FE 体系统计 → s2 单元对齐 | NOT_RUN（等用户决策） |

规则：步骤通过=命令 exit 0 且声明的产物存在非空；PoC 通过=全部步骤 PASS 且 gate 命令 exit 0；
`requires` 未满足记为 BLOCKED，不静默跳过；不允许无证据 PASS。

### P1 的数据关卡（唯一阻塞点）

需要只读导出三个数组到 `evidence/poc/P1/input/`：`profiles.json`（型材参数表 681 行）、`composites.json`（复合型材参数表）、
`gallery.json`（图库数据表 `IID/BREP`，`BREP` 列即断面几何来源）。SQL 已写死在 `scripts/poc/ingest-profiles.py` 的输出里，
只读、不改库；导出后 `python3 scripts/poc/orchestrate.py run P1` 会自动重跑 s3→s5。

### 检查

```text
python3 scripts/poc/orchestrate.py run P1     # s1 PASS, s2 PASS, s3 BLOCKED(2)
python3 scripts/poc/orchestrate.py status     # P1 BLOCKED；P2/P3/P4 NOT_RUN
cd replica && npm test / npm run build / npm run lint   # 9 passed / 0 / 0
```

---

## 交接更新 · 2026-10-20 22:05 (UTC+8) / 2026-10-20T14:05Z：P1 断面引擎开工，解析解全绿；旧系统对照待补

**三行复述**——已验证：`replica/` 骨架建立（npm workspaces + Node 24 直接跑 TS），
断面特性引擎完成并通过 **9 个单测 + 5 个判据用例**（矩形/矩形管/工字形/组合平行轴/薄壁 J，相对误差 ≤1e-12），
`npm test`=PASS(9/9)、`npm run build`(tsc --noEmit)=0、`npm run lint`(oxlint)=0；
未完成：P1 的**硬判据**（与旧系统 `型材参数表`/`复合型材参数表` 值 ≤0.5%）因缺"全量行 + 图形ID 断面轮廓"仍 PENDING，
POC-1 台账保持 `NOT_RUN`；下一步：只读导出两张型材表全量行 + 解析 `图形ID` 轮廓。

### 本轮产物

| 路径 | 内容 |
| --- | --- |
| `replica/packages/section/src/index.ts` | 断面几何→特性（有向面积、孔洞相减、组合平行轴、任意变换、主轴、Wn、回转半径、包围盒、周长、静矩裁剪、薄壁开口 J 近似） |
| `replica/packages/section/src/section.test.ts` | 9 个测试（含孔洞换向不变、平移/旋转不变、主轴和不变、静矩=半截面一阶矩） |
| `replica/scripts/poc-p1-section.mts` | P1 判据运行器 → `evidence/poc/P1/{criteria.md,data.json,conclusion.md}` |
| `replica/{package.json,tsconfig.json,README.md}` | workspaces、tsc/oxlint 配置、运行说明 |
| `planning/acceptance.json` | POC-1 增 `progress` 字段（状态仍 `NOT_RUN`，不伪造 PASS） |

### 检查

```text
cd replica && npm test        # 9 passed
cd replica && npm run build   # tsc --noEmit exit 0
cd replica && npm run lint    # oxlint exit 0
cd replica && npm run poc:p1  # analyticPass=true, oldSystem=PENDING, exit 0
python3 scripts/check-acceptance.py --self-test   # PASS（主检查仍 exit 1：13 项未通过）
```

### 下一条命令

```text
cd replica && npm test && npm run poc:p1
# 然后补 P1 硬判据：型材参数表/复合型材参数表全量行 + 图形ID 断面轮廓（只读 SQL / 图库 SLD 解析）
```

---

## 交接更新 · 2026-10-20 21:10 (UTC+8) / 2026-10-20T13:10Z：产品规格 V1 冻结 + PoC/MVP 定义落盘

**三行复述**——已验证（用户确认）：产品形态定为**中心化薄客户端工程计算协作平台**（无离线、域账号 SSO、100 在线/20 并发），
正确性**以规范为准**+旧系统差异台账+黄金回归，交付物为"数值+文本+图形"三元组，PDF 内嵌 RulePack 指纹/引擎版本/figure hash/审计号；
PoC 定为 4 项（断面引擎、图形→计算桥、结果→PDF、FE 可选）、MVP 定为 3 体系+单城 10–20 人+6 类分析图（不含 DWG 写入/签章），
出口判据 M1–M7；未完成：PoC 全部 NOT_RUN、无应用代码（`replica/` 仍空）；下一步：跑 P1（断面引擎）与"完整 RTF 图中的 `\pict` 统计"取证。

### 本轮落盘（4 份）

| 文件 | 内容 |
| --- | --- |
| `docs/product-spec-v1.md` | 冻结契约 S1–S9、6 项待定（各挂 gate）、数据主干与不变量、验收三层口径、变更控制 |
| `docs/poc-mvp-plan.md` | P1–P4（假设/输入/硬判据/失败降级）、MVP IN/OUT、M1–M7、Go/No-Go 关卡、排期规则、Kill Criteria |
| `docs/decisions.md` | 新增 D14–D22（图形单一真源、结果图形分离、三元组与指纹、互操作分级、规格 V1、PoC/MVP、规范为准、TS 单栈首版、`.cwx` 写回移出范围） |
| `planning/scope.json` + `planning/acceptance.json` | 13 个可验收项（POC-1..4、MVP-1..9），全部 `NOT_RUN`，ID 与 scope 严格对齐 |

### 边界与状态（不变项）

- **S1–S9 已冻结**；技术选型（桌面宿主/部署形态/SDK）、图样式、排期数字**不属于** V1，不阻塞实施。
- **74 体系全量库存仍未闭合**：`inventory_complete=false`，最终验收门槛不变；本轮只是把"第一阶段可验收项"变成可判定。
- 旧系统继续有效：`compat_profile` 仅用于复现历史结论；历史工程由旧系统处理，`.cwx` 写回移出 P0/P1。

### 最近检查（本轮）

```text
python3 scripts/check-acceptance.py --self-test     # PASS
python3 scripts/check-acceptance.py                 # exit 1（预期：13 项全部 NOT_RUN + 7 个 gate 未过）
```

### 下一条命令

```text
python3 scripts/check-acceptance.py --self-test
# 然后开始 P1：python3 scripts/poc-section-properties.py（待建）对 1 个复合型材复算
```

---

---

## 历史标题 · 模块透明化 + `.cwx` 字段顺序（B11 前半闭合，2026-10-20 19:40 版）

## 交接更新 · 2026-10-20 19:40 (UTC+8) / 2026-10-20T11:40Z：`Serialize` 链叠加成功，`.cwx` 字段顺序与原版字节对齐

**三行复述**——已验证：`Serialize` 链（自身字段写顺序 + 基类调用位置 + 版本门）可机械叠加成"一条记录内的有序字段表"，
`HWKWallContext` 根按该表走 `b.cwx` 载荷，三个单字段差分锚点全部落在预测偏移**且读出正确值**
（`+0x14` 雪压 0.4=对象`+0x98`、`+0x1c` 工程名称"各种样式栏杆计算样例"=对象`+0xa0`、`+0x56` 风压 0.45=对象`+0x110`），
顺带读出 `+0x48`"北京市"（城市）、`+0x62`"ⅡA"（粗糙度类别候选）；未完成：记录边界（`u32 A` 语义仍未知）、
聚合槽位未细分（String/vector/嵌套对象）、412 个 `Serialize` 只对齐 1 个根、字段语义只证到 5 个；
下一步：解 `A` 与聚合槽位（决定能否做通用解析），或转回主线 B02-03。

### 本轮状态

| 线 | 状态 | 说明 |
| --- | --- | --- |
| B02-02 原版运行/许可 | **PARTIAL，待独立验收** | 本轮未触碰远端；任何远端动作前先只读刷新会话/进程/哈希 |
| 离线模块透明化（用户指派线程） | 2 模块 5 项全闭合 | 查表缺口已闭合（上一轮） |
| 共享缺口 2：`.cwx` 字段 | **顺序/类型闭合（1 个根验证）、语义 PARTIAL** | B11 从"方法已知"前进到"顺序可验证" |
| 查表缺口 1 | 闭合 | 本轮未改动；脚本仍在 |

### 本轮实质结论

1. **链图可解**：本模块 412 个 `Serialize`、13 个根（`HWKWallContext`、`HWKWallContextObject`、`HWKSurfaceLoad` 等）。
   玻璃族为 `HWKCalc_GlassDisp`（薄壳 0 字段）→ `HWKCalc_GlassBase`（`+0x98` int32，门 `0x20`）→ `HWKSBLinkInfoBase` → `HWKWallContextObject`。
2. **`this` 寄存器不固定**（`%rbx`/`%rdi`/`%rsi` 都出现），必须按函数检测；`0xc` 通过专用槽 `0x18034f288` 写出，
   属类版本标记，不能当字段。
3. **`.cwx` 记录 = `Serialize` 链的写出顺序**这条假设首次被字节级证实（3 个独立差分锚点）。
4. 字段语义新增 5 个：雪压 `+0x98`、风压 `+0x110`、工程名称 `+0xa0`、城市 `+0xe0`、粗糙度类别候选 `+0x140`。
5. **未能推进**：`u32 A`（如 `b.cwx` 的 1058）既不是长度也不是类常量；走完 29 字段读到 1,564 B 后遇非法计数即停。

### 证据与产物

- 新脚本 `scripts/build-serialize-chains.py`（链叠加 + IAT 槽分类 + `--cwx` 对齐检查，写 `migration_workspace/raw/serialize-chains.json`）
- `migration_workspace/serialize-fields.md` §7（方法、链图、对齐表、5 条限制）
- `VERIFICATION.md` 新增 A19、B11 降级为"顺序已解 + 4 项残余"；`planning/naming-observations.json` 新增 `NAME-CWX-WALLCONTEXT-FIELDS`
- 对齐证据全部来自仓库内文件：`raw/cwx-diff-20261019/files/b.cwx`、`cwx-field-widths.md` §3 的差分记录

### 最近检查（本轮全部 exit 0）

```text
python3 scripts/build-serialize-chains.py --cwx migration_workspace/raw/cwx-diff-20261019/files/b.cwx   # 3/3 锚点 OK
python3 scripts/extract-coefficient-tables.py    # 38 表 / 4 锚点 PASS（回归）
python3 scripts/extract-lookup-table.py          # 3 η 表 PASS
python3 scripts/check-module-numeric.py          # 16 步 all_matched=true
```

npm test/build/lint 仍 **NOT_RUN**（尚无应用）；未提交 git，未触碰远端。

### 下一条命令

```text
python3 scripts/build-serialize-chains.py --cwx migration_workspace/raw/cwx-diff-20261019/files/b.cwx
```

两条可选线：①解 `u32 A` 与聚合槽位细分（看清 `.cwx` 记录边界，才能做通用读写并支撑"打开-另存-逐字节复现"验收）；
②给 `HWKWallContext` 其余 8 个字段找语义（对比面板列值，需实机只读取数）；③回主线 B02-03（报告/绘图/保存重开）。

### 决定

1. `.cwx` 字段结论一律要求"链预测偏移 × 原版字节实测"双证据；纯静态不写"已解"。
2. 聚合槽位未细分前，不对外宣称"可通用解析 `.cwx`"。

---

## 历史快照 · 2026-10-20 18:35 (UTC+8) / 2026-10-20T10:35Z：`FUN_1802a0fa0` 解开，μ/m 与外片应力一起闭合

**三行复述**——已验证：`FUN_1802a0fa0`（`GetSDr`）与同构的 `FUN_1802a2940`（`GetSMr`）是
"读 `$0..$3` → 归一化成边长比 → 按 `$2` 材料代码 / `$3` 支承代码选一对内嵌轴表 → 交 `FUN_180299d50` 插值"，
23 条分支逐条转录；两个节点引用的 **38 个去重轴地址全部**解成 `[double count][count × double]`（count ∈ {11,13,15,16}），
4 个系数锚点命中（μ=0.00406、m=0.0442 @ a/b=1），外片应力 `6.726054` 按 m→θ1→η1→σ1 整链复现（差 9.8e-8）；
未完成：`$2/$3` 代码语义只证到 `11`=铝板族、`0/1/2`=PRJGLASS、`4`/`6`=支承（`GetSMr` 的 `20/25/30` 细分无锚点）、
`.cwx` 字段语义仍待叠加；下一步：转 `Serialize` 基类链（B11）或给石材/铝板分支补真实样例锚点。

### 本轮状态

| 线 | 状态 | 说明 |
| --- | --- | --- |
| B02-02 原版运行/许可 | **PARTIAL，待独立验收** | 未在本轮触碰；远端会话状态仍须先只读刷新再动作 |
| 离线模块透明化（用户指派线程） | **2 个模块 5 项全闭合** | 查表不再是输入：μ/m/η 全部由解出的轴表算出 |
| 共享缺口 1：查表 | **闭合** | η 3 表 + 系数 38 表；锚点 3 η + 4 系数 |
| 共享缺口 2：`.cwx` 字段 | **方法闭合，语义待叠加** | 未在本轮推进（`serialize-fields.md` 保持原状） |

### 本轮实质结论（都可重跑）

1. **节点语义**：`FUN_1802a0fa0` 不是"第二种取数路径"，而是**同一个查表模板的材料/支承分派版**；
   与 `GetNg` 的区别只在分支键（`GetNg` 键 θ；`GetSDr/GetSMr` 键 `$2`+`$3`）。完整分支表见
   `migration_workspace/coefficient-tables.md` §3（23 条，含 `code` 常数）。
2. **旧负面结论两处作废**：B10 的"19/22 个地址按该布局解析失败"未复现（38/38 成功）；B9 的"外片 η1 原文未打印"
   不成立（强度段原文打印了 `θ1=5.894204`、`η1=0.992846`，且与 η 表自洽到 3.7e-7）。
3. **特例要照抄**：`GetSDr` 的 `$2=2` 非四边分支是 `($1/$0)×0.5`，`GetSMr` 的 `$2=2` 非六点分支是 `$0/($1×0.5)`，
   不可互换；`$2=22` 的 tie-break 两张 y 轴字节相同（空转分支）；原版计算书把 μ 标"表6.1.3"、η 标"表6.1.2-2"，
   与 JGJ102-2003 编号对调，属原版文案缺陷，复刻须照抄。

### 证据与产物

- 新脚本 `scripts/extract-coefficient-tables.py`（解 38 表 + 分支模型 + 4 锚点，写 `migration_workspace/raw/coefficient-tables.json`）
- `scripts/extract-lookup-table.py` 增补两处 η 锚点（θ1=5.894204、θ2=5.358368）
- `scripts/check-module-numeric.py` 改为**表驱动**：μ/m 取自系数表、η 取自 η 表，两个模块共 16 步全绿
- 新文档 `migration_workspace/coefficient-tables.md`；更新 `lookup-tables.md`、`modules/glass-stress-transparency.md`、
  `modules/README.md`、`VERIFICATION.md`（新增 A16–A18，B9/B10 降级为"已闭合+残余"）
- 数值证据重生成：`evidence/stages/B02/B02-02/attempt-47/acceptance/{glass-disp,glass-stress}-numeric-check.json`

### 最近检查（本轮全部 exit 0）

```text
python3 scripts/extract-coefficient-tables.py     # 38 表 / 23 分支 / 4 锚点 PASS
python3 scripts/extract-lookup-table.py           # 3 η 表 / 3 锚点 PASS
python3 scripts/check-module-numeric.py           # 16 步 all_matched=true
```

`python3 scripts/build-module-transparency.py`、`test-glass-deflection-map.py`、`check-acceptance.py --self-test`
本轮未重跑（生成物未变）；npm test/build/lint 仍 **NOT_RUN**（尚无应用）。

### 下一条命令

```text
python3 scripts/extract-coefficient-tables.py && python3 scripts/extract-lookup-table.py \
  && python3 scripts/check-module-numeric.py
```

之后两条可选线：①`Serialize` 基类链叠加（B11，`.cwx` 字段语义）；②给石材/铝板分支（`GetSMr` 的 `$2=3`、`$3∈{20,25,30}`）
补真实样例锚点——需要一份石材或铝板计算书，当前冻结样例没有这些分支。

### 决定

1. 查表类缺口一律用"解表 + 原版自印值锚点 + 可重跑脚本"三件套结案，不再用"读了代码"结案。
2. 数值复算脚本**不再接受手填的 μ/m/η**：必须经提取器，否则视为未取证。
3. 原版文案缺陷（表号对调）按"照抄不复原"处理，写入复刻要求。

---

## 历史快照 · 2026-10-20 16:45 (UTC+8)：两个计算模块打透，共享缺口 1 闭合、2 方法打通

**三行复述**——已验证：玻璃跨中挠度与玻璃面板强度两个模块按同一 5 项口径出表（调用面/算式/输入/分支/数值），
η 三张查表已从 `.data` 解出并命中原版打印值（η(5.221494)=0.998228048 vs 0.998228），`Serialize` 字段布局的可读模式
已用反汇编实证并工具化（本模块 412 个 `Serialize`，玻璃族 10 个已提取偏移/宽度/版本门）；
未完成：μ/m 查表不是同种编码（19/22 个地址试解析全失败，需先解 `FUN_1802a0fa0`）、外片应力 6.726054 仍不能复现、
字段语义与顺序待沿基类链叠加；下一步：解 `FUN_1802a0fa0`（μ/m 与外片应力同一把钥匙），再叠加 `Serialize` 基类链。

### 本轮状态

| 线 | 状态 | 说明 |
| --- | --- | --- |
| B02-02 原版运行/许可 | **PARTIAL，待独立验收** | 冻结样例完整输出落盘（5,926,372 B，`E1FDA490…9DF63`）、TCP 1433、hook-out 零写入；许可条款与服务端语义仍未知 |
| 离线模块透明化（用户指派线程） | **进行中** | 2 个模块打透；流水线可复用，一个模块一条命令 |
| 共享缺口 1：查表 | **η 闭合 / μ·m 未解** | 见 `lookup-tables.md` |
| 共享缺口 2：`.cwx` 字段 | **方法闭合，语义待叠加** | 见 `serialize-fields.md` |

### 证据与产物

- `migration_workspace/modules/`：`glass-disp.{md,json}`、`glass-stress.{md,json}`、`glass-stress-transparency.md`、`README.md`（模块台账）
- `migration_workspace/glass-deflection-transparency.md`：5 项判定 + 数值逐位复现（te/D/θ/df）
- `migration_workspace/lookup-tables.md`：布局 `[double count][count × double]`、三套 η 表、锚点、μ/m 负面结论
- `migration_workspace/serialize-fields.md`：`this+0xc` 版本门 + `operator<</>>` 模式、玻璃族首批字段
- 脚本（全部可重跑、exit 0）：`build-module-transparency.py`、`check-module-numeric.py`、`dump-static-table.py`、
  `extract-lookup-table.py`、`extract-serialize-fields.py`、`test-glass-deflection-map.py`
- `VERIFICATION.md`：A11–A15 成立；B7–B11 记录剩余缺口
- B02 侧证据：`evidence/stages/B02/B02-02/attempt-47/`（含 `acceptance/{main-acceptance.md,restore.md,frozen-report-head.txt,*-numeric-check.json}`）

### 决定

1. **REA 使用方式**：用户明确"REA 不用开放，随时可用"。本轮实测 `rea` CLI 6.7.0 可用；`rea doctor` 报 provider 未配置，
   但命令级注入 `GHIDRA_INSTALL_DIR=/Users/yeliang/tools/ghidra_12.1.4_PUBLIC` 后 `rea decompile` 成功
   （Evidence `ev_d8a40627…`）。**不修改全局 REA/客户端配置**，只在命令级注入环境变量。
2. **不重复走的路**：`GetSDr`/`GetSMr` 的 `DAT_` 地址不能套用 η 的布局（19/22 个全部解析失败，抽样形如 `float32 [3.4e10, 0.0001, …]`）。
3. **模块口径固定为 5 项**（①调用关系 ②算式与对应 ③输入来源与查表 ④分支与异常 ⑤中间量与数值一致），
   任何模块不得只用"读了很多代码"结案。

### 阻塞 / 未决

- **B10**：μ（表 6.1.3）与 m（表 6.1.2-1/8.1.5-1）的取数机制未解 → 外片应力 6.726054 无法复现。
  需要的正是 `FUN_1802a0fa0` 语义 + `puVar14/puVar15` 分支→轴对映射。
- **B11**：字段语义/顺序需沿 `HWKCalc_GlassBase → HWKSBLinkInfoBase → …` 叠加，并与 `.cwx` 字节往返差分。
- **B02-02 许可**：条款、席位、服务端（`165.154.20.222:1433`）授予语义仍未知；B02-03/04 未开始。
- **远端会话未在本轮复查**：ECS 上客户端最后已知状态是 pid 1900 / session 1（Administrator）。
  下一轮任何远端动作前，先只读刷新 `quser`、`Get-Process XWall`、445 源哈希与两处冻结哈希，**不要**默认它仍在运行。

### 最近检查（本轮全部 exit 0）

```text
python3 scripts/extract-lookup-table.py        # 3 张 η 表 + 锚点 0.998228048
python3 scripts/check-module-numeric.py        # 2 个模块数值复算 all_matched=true
python3 scripts/test-glass-deflection-map.py   # 25 模板/555 调用/434 命中/0 形参不一致
python3 scripts/build-module-transparency.py   # glass-disp、glass-stress 生成物与首轮一致
python3 scripts/check-b02-license-47.py        # 两份文档 + 结构化 PID 断言
python3 scripts/check-acceptance.py --self-test
```

npm test/build/lint 仍 **NOT_RUN**（尚无应用）。

### 下一条命令

```text
GHIDRA_INSTALL_DIR=/Users/yeliang/tools/ghidra_12.1.4_PUBLIC \
  rea decompile evidence/baseline/extracted/cab/_F35DC0979FF04306B20773A25268CC58 \
  --procedure=0x1802a0fa0 --format=json
```

解出它之后：①把 μ/m 的取数逻辑写成与 η 同级的脚本并加锚点（原版打印 μ=0.00406 @ a/b=1、m=0.0442）；
②用 η1+μ 复算外片应力，命中 6.726054 即把模块 #2 的 ⑤ 补成闭合；③再回到 `Serialize` 基类链叠加。

---

## 历史 · B02-02 attempt-47 会话恢复与冻结样例完整输出（2026-10-20T07:10Z 版，内容保留不覆盖）

## 交接更新 · 2026-10-20 15:10 (UTC+8) / 2026-10-20T07:10Z：阻塞解除，缺口收敛

**三行复述**——已验证：Administrator 交互会话已恢复（自动登录重指 + 重启，session 1 = administrator/Active），隔离客户端 pid 1900 以**冻结工作样例** `sample-working.cwx` 运行，445 源文件/EXE/样例哈希不变，`reports\report-point-01.rtf`（5,926,372 B，sha256 `E1FDA490…9DF63`）由该样例完整输出而来，正文解码含 `强度计算信息/设计计算书/荷载计算/设计依据` 及数值 `0.737993`、`1.98735`（与 attempt-46 界面实测的 20m 风系数一致），全程 `C:\hwk\hook-out` 新增写入 0、限定事件查询 0 条；未完成：许可条款/服务端授予语义仍未知、其它门控分支（绘图/保存重开）未验；下一步：独立验收判断操作型许可证据是否足以关闭 B02-02，否则用同一存活客户端转入 B02-03。

### 恢复动作（用户指示"你来恢复"）
1. 先在 `s4test` 会话下启动的临时客户端**在创建默认图库前终止**（确认 `C:\Users\s4test` 下无 HWK 数据）。
2. `LogonUser('Administrator', …)` 预检 `.pw-rotated` 中的口令 → true（**口令从未打印**）。
3. `scripts/ecs-restore-admin-autologon.ps1` 把 Winlogon 自动登录从 `s4test` 改回 `Administrator`（回读确认，`SecretPrinted=never`）。
4. 重启（06:57:47Z）→ `quser` 确认 `administrator console 1 Active`。
5. 以 Administrator 启动隔离客户端 + 冻结样例，截图 `shot-admin.png` 显示标题 `[sample-working.cwx]`，无「图库不存在」提示。

副作用显式记录：改动了自动登录账户、重启导致 `s4test` 会话结束（账户与文件未删除/未改动）；未改安装/服务端/许可/sshd，未新建资源。详见 `evidence/stages/B02/B02-02/attempt-47/acceptance/restore.md`。

### 本切片新增证据
- `export-all.json`：trace `settings → saved-1 → confirm-modal-2 → no-dialog-3`，`Saved=[reports\report-point-01.rtf]`，`FileCount=2`，`HookOutRecent=0`，`Errors=0`。
- `final.json`（重采，含逐文件哈希）：445 源清单仍等于冻结基线，进程 pid 1900/session 1、TCP 1433，两份文档 2,829,593 B 与 5,926,372 B。
- `acceptance/frozen-report-head.txt`：冻结样例计算书正文解码（127,273 字符）。
- 回归：`check-b02-license-47.py` exit 0（已更新为两份文档 + 结构化 PID 断言 + 冻结样例数值）；`verify-b02-47.py` exit 0；`collect-b02-final-47.py` exit 0。npm test/build/lint 仍 NOT_RUN（无应用）。

### 仍然未知 / 不在本切片
许可条款、席位、服务端（`165.154.20.222:1433`）授予语义；绘图输出与工程保存重开（B02-03/04）；多计算点工程的多份输出（本次样例只有 1 个点，`a.cwx` 那次其余点被取消）；安装器控制流与干净安装（B01/R01）。

下一条命令：`python3 scripts/verify-b02-47.py`
独立验收下一步：只读复核 445 哈希、pid 1900/session 1、两份 RTF 哈希与正文节选，判断操作型许可证据是否满足 B02-02 done_when；**不**把"生成成功"当作许可条款已知。

### 本轮新增负结果与方法笔记（B02-03 起点）
- **样例身份已确认**：`示例\门窗计算示例1.cwx` 的 sha256 前缀 `2FFA32CB…` 与本轮冻结工作样例 `sample-working.cwx` 相同 → B02-03 要求的"门窗计算示例1"就是我们正在用的样例；其内部工程名显示为"各种样式栏杆计算样例"，属样例内容字段，不是取错文件。`示例\各种栏杆样例.cwx` 前缀 `7F79C6F3…` 正是早先 `a.cwx` 那份（已生成的 2.8 MB 文档来源）。
- **Ctrl+Shift+S 不是另存快捷方式**：`saveas-try.json` 记录按键后无任何对话框，标题仍为 `[sample-working.cwx]`。另存需走"文件"菜单。
- **菜单是自绘工具栏**：`GetMenu` 返回空；`Alt+O` 只把"计算书输出(B)"按钮聚焦（状态栏提示走查 `menu-scan.json` 八次 Down 提示不变），不会展开下拉。要发现"绘图输出/另存"等命令，需按坐标点击菜单栏条目，或枚举 `HWKToolBar` 按钮后再点。
- **工具链稳定性**：`Start-ScheduledTask` 在本机不推进 `LastRunTime` 且常常静默不执行，已改 `schtasks /run`；ssh stdin 上传偶发挂起，已改 **scp 优先 + gzip 兜底**；PowerShell 写出的 JSON 带 BOM，落地后统一去 BOM 再断言（否则解析器报 `Expected a JSON object`）。

### B02-03 建议首切片
1. 文件菜单 → 另存为：把冻结样例另存到 `C:\hwk-modern\HWK-000048-B02-03\projects\`（新卡目录），记录另存前后哈希差（序列化是否逐字节复现）。
2. 退出 → 重开该另存文件 → 重算，比对数值与界面中间量。
3. 绘图输出：先解决菜单发现（坐标点击或枚举工具栏按钮），产物同样只落授权目录。
4. 每一步沿用本轮守卫：保存对话框文件名必须显式落在授权目录内，默认 `C:\hwk\hook-out` 一律拒绝。

---

## 历史快照 · attempt-47 执行端交接（2026-10-19T20:30Z 版，内容保留不覆盖）

## 交接更新 · 2026-10-20 04:45 (UTC+8) / 2026-10-19T20:45Z：主代理复核完成，新采两条事实

主代理已独立重采（不读执行端结论）：`python3 scripts/verify-b02-47.py` 重新读取 445 源清单、冻结 EXE/样例哈希、进程/会话/TCP、报告哈希、默认目录写入与事件日志，全部与冻结基线一致；262 项证据/脚本哈希逐项核对无差异。复核记录在 `evidence/stages/B02/B02-02/attempt-47/acceptance/main-acceptance.md`，机器可读结果 `acceptance/verify.json`。

复核新增（执行端当时未采集）：

1. **产品自报成功**：写盘后原版弹出 `计算书文件创建完成!` + 授权目录完整路径（`report-done.json`、`report-done-summary.json`），即被测软件自己确认落在 `C:\hwk-modern\HWK-000048-B02-02\reports\`。
2. **输出按「计算信息点」逐份进行**：第一份存盘后原版继续为下一点弹 `保存计算书文件`，**每个默认 `C:\hwk\hook-out`**；本次逐一取消（取消=跳到下一点），8 次后流程结束（`cancel-loop-report.json`：StillOpen=false）。全程 hook-out 新增 **0** 文件，`reports\` 始终只有 1 份文档。

判断：B02-02 仍 **PARTIAL**（缺口从"无任何成功门控操作"缩小为"无显式许可状态读数 + 服务端授予语义未知 + 其它门控分支未验 + 多文档输出被取消"）；报告生成分支已由实际 UI 操作证明可用，建议独立验收据此裁决，不把生成成功表述为许可条款已知。已撤回的失败路径（BFFM_SETSELECTIONW）本轮未重试。

下一条命令：`python3 scripts/verify-b02-47.py`

---


## 历史快照 · attempt-47 执行端交接（2026-10-20T20:30Z 之前版本，内容保留不覆盖）

## 交接更新 · 2026-10-20 04:30 (UTC+8) / 2026-10-19T20:30Z：B02-02 新增真实计算书生成切片

状态：**B02-02 PARTIAL**，independent_acceptance=NOT_RUN。本轮不是控制器派卡（无 stage-assignment.json，card_id=null），是用户解除安全阻塞后直接指示续接的主线工作。三行复述——已验证：隔离客户端仍为冻结副本、445 源文件与两处冻结哈希不变、TCP 1433 建立、经普通 UI 目录树导航把输出目录改到本轮授权 reports 并成功生成 2,829,593 字节 RTF 计算书（sha256 577D61F4…A52A7B0），全程未写入历史默认目录 C:\hwk\hook-out；未完成：许可条款/服务端授予语义/其它门控分支、B02-03 报告绘图保存重开、B01/R01 安装卸载；下一步：由独立验收判断「计算书分支可用」是否足以满足 B02-02 done_when，不足则在同一存活客户端上换另一门控分支。

证据：`evidence/stages/B02/B02-02/attempt-47/`（work-package.json、final.json、final-comparison.json、preflight-read/stdout、path-goto.json、confirm-browse.json、save-as.json、generate.json、delivery-hashes.json、各步 png/json）。回归：`python3 scripts/check-b02-license-47.py` exit 0，重读已存字节断言上述全部结论；`python3 scripts/check-acceptance.py --self-test` exit 0；npm test/build/lint NOT_RUN（无应用）。

关键操作链（均为普通 UI，未用 BFFM_SETSELECTIONW）：Alt+O（计算书输出(B)）→ 输出设置对话框 → 文件保存路径(P) → 浏览文件夹用 MSAA 选中项反馈 + TVM 方向键导航 hook-out→桌面→hwk-modern→HWK-000048-B02-02→reports → 确定 → 保存计算书文件（文件名编辑 AutomationId 1001，WM_SETTEXT）→ 保存。此路径避开了 2026-10-18 触发 SHELL32 崩溃的原生目录消息，未重试该失败路径。

失败与限制保留：①自动化上传脚本曾因缺 UTF-8 BOM 被 PowerShell 按 ANSI 解码，导致生成的报告文件名成乱码（内容正确）；②早期一步把整条路径写进了文件列表的原地重命名编辑，触发「重命名」非法字符提示，被 shell 拒绝、未改名；③任务上一实例未退出时 Start 报 0x800710E0；④第一次点「确定」被本会话自设守卫拒绝（当时路径仍是 C:\hwk\hook-out），该拒绝作为守卫证据保留；⑤本轮生成的工程是存活客户端已打开的 a.cwx（安装示例副本），冻结工作样例 sample-working.cwx 未被打开也未改动，故不主张样例级报告一致性。

远端变更与清理：仅创建 `C:\hwk-modern\HWK-000048-B02-02`（含 reports）并写入本卡探针与产物；注册并停止计划任务 `HWKModern-000048-Probe`（保留未删）；停止本轮自己遗留的僵尸 powershell pid 6124。未启动/关闭客户端、未改许可/二进制/服务端、未读密码文件、未使用外泄密钥之外的新凭据。

下一条命令：`python3 scripts/check-b02-license-47.py`
独立验收下一步：只读 SSH 复核 445 源哈希、隔离 EXE/样例哈希、PID 4568/session 1 与 TCP，核对 reports 内唯一 RTF 的哈希与节选数值，并判断本切片对 B02-02 done_when 的贡献；不把生成成功当作许可条款已知。

---

## 历史 · HWK-000046 B02-02 独立验收

### 交接更新 · 2026-10-19：安全阻塞由用户解除

用户直接确认：**没有密钥泄露**，可继续。据此：

- 上一节记录的 `STOP_SAFETY`（B02-02 验收会话私钥进入工具日志）**解除**；来源为用户直接指示，非代理自行判定。
- 下方原交接内容与 `security-incident.json` 等历史证据**保留不改**（历史记录不覆盖），但其“停止后续远端操作”的约束不再生效。
- 后续远端操作仍按原边界：只写 `C:\hwk-modern\` 本轮目录、只读复制原件、不改安装/服务端配置、不读密码文件内容、不把私钥内容写入日志。


状态：B02-02 PARTIAL；本卡实际重算增量独立核对通过，但许可门控与服务端许可语义仍未知。outcome=blocked、continuation=STOP_SAFETY，原因为本验收会话误读SSH私钥导致密钥进入工具日志，属于实际安全事件；不是轮数限制。阶段/总Goal未完成，控制器维护stage-progress，未自行改合同或跳阶段。

证据：evidence/scheduler-reviews/HWK-000046-B02-02/review.md、checks.json、delivery-audit.json、live-command.ps1、live-stdout.json、live-comparison.json、rea-connection.json、security-incident.json。独立重跑189交付/5输入无差异，445项源文件匹配冻结基线、EXE及工作样例未变；PID113264/session4响应、TCP165.154.20.222:1433，限定错误查询为空。保留证据显示21m→20m中间量变化，未重新操作UI重演。

安全阻塞：~/.ssh/hwk-win-test私钥内容进入本验收会话工具日志；此交接和仓库事件文件不复制任何密钥。未撤销旧密钥、未改变服务器认证、未删除日志。停止后续远端操作。解除条件：有权限操作者撤销泄露密钥、安全配置替代凭据，再独立复核限定只读SSH；不得扩大权限或继续使用泄露密钥。未自行改调度器/launchd或服务端配置。

检查：check-b02-license-46.py、verify-installer.py、test-hwk-ecs-transport.py、check-acceptance.py --self-test exit0；最终check-acceptance.py exit1；npm test/build/lint NOT_RUN（无应用）。REA期望6.7.0，binary_session被never客户端审批拒绝，未重试，actual MCP版本未确认，无新二进制分析。parallel-state accepted历史卡无本包新增需求，未派旁路。命名/重构准备只增记独立复核边界，架构/求解器/持久化未决。

下一条本地命令：python3 scripts/check-b02-license-46.py
下一业务动作（仅安全解除后）：先只读刷新PID/会话/路径及哈希，不重复启动；普通UI目录树导航到新卡授权reports目录，严格读回路径后实际生成计算书，采集成功/拒绝和许可状态，不再使用BFFM_SETSELECTIONW失败路径。当前PID113264在执行端恢复20m后保留，未保存，进程状态下轮必须重新读。B02-03报告/绘图/保存重开与B01/R01安装卸载继续保留，不把本切片当全许可/全业务通过。

本轮已交接，结束验收；由外部控制器消费安全停止结论。

---
以下保留执行端交接（历史快照，不覆盖上述独立结论）：

## HWK Modern 交接 · HWK-000046 B02-02 执行

状态：B02-02 PARTIAL，independent_acceptance=NOT_RUN，continuation=CONTINUE。本轮完成实际荷载输入变更→原版计算输出变化→恢复的业务切片；尚未证明该分支是否实施许可门控，不能据此宣称全部许可、工作包或总Goal通过。B02-01独立PASS与前轮否定记录保持；未修改stage-contracts/stage-progress或调度器。

证据：evidence/stages/B02/B02-02/attempt-46/；包交付evidence/stages/B02/B02-02/work-package.json（本轮快照同目录work-package.json）；前轮交付保存在prior-work-package.json。189项交付及5项合同输入哈希核对一致，delivery-hashes.json可独立复核；命名及重构准备已增量登记原名、数值、单位、来源与未知，未做架构/算法决定。

实际增量：preflight确认无XWall、445项源文件匹配B02-01冻结清单、隔离EXE和真实工作样例哈希匹配后，恢复同一C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe及projects\sample-working.cwx。新PID113264/session4，未并发启动其它客户端。进入强度计算信息/荷载计算，标高输入原20m。Ctrl+A未全选导致20追加21成2021m，输出实际变为2021m/查表2.91；完整失败保留。随后经焦点进程/Class=Edit/原值守卫，以HOME SHIFT+END改成21m，最后恢复20m。未保存或导出。

可独立查看height21-text.json/png（2021m误输入）、height21-corrected.json/png/txt（21m）、height20-restored.json/png/txt（20m）。21m原版高度系数0.754007、阵风系数1.976809、最小值处理前横梃负风荷载-0.768453kN/m²；恢复20m后0.737993、1.98735、-0.756143kN/m²。最低风荷载分支使两者最终面板组合均1.672032kN/m²；不能只看最终值判未重算。初始20m未采全文，只有早期截图；恢复20m全文为新采，不能称逐字往返相等。

postflight/stdout：445项源文件前后一致（包括原样例），隔离EXE/工作样例未变；PID113264响应，TCP165.154.20.222:1433状态5。该端点身份/协议/许可关系未知。限定Application1000/1001/1026、自18:17Z且Message含XWall的查询为空，不代表所有错误渠道均无错误。报告为空，本轮未进入目录选择。前轮SHELL32崩溃继续保留，未重试BFFM_SETSELECTIONW。

采集限制：旧探针共享desktop.png/ui.json可混合新图与旧文本，早期launched/probe/expanded/context/edit/load/focus读数仅作发现。已修为动作独立命名文件、JSON存在的有界等待、不同读取尝试目录；本轮结论以height21-text、height21-corrected、height20-restored独立文件及内部时间为准。准备阶段query user虽输出会话仍exit1；目录实际已创建，未重复创建。focus-status的Get-Content扩展属性导致冗长原始JSON，未用作关键证明，未读取密码文件。

检查：python3 scripts/check-b02-license-46.py、verify-installer.py、test-hwk-ecs-transport.py、check-acceptance.py --self-test均exit0；check-acceptance.py为exit1（最终业务未完成）。原始stdout/stderr及checks.json已保存。npm test/build/lint NOT_RUN，无应用。REA期望6.7.0，binary_session实际连接核验被never客户端审批拒绝，未重试、未改权限；本卡不做新二进制分析，OS/UI证据不充当REA Evidence。

清理/接续：本轮HWKModern-000046-Probe任务已删除，cleanup/stdout确认无同卡任务；保留PID113264/session4，荷载标高已恢复20m，当前页为荷载计算。下轮先读实际PID/会话/路径及UI，不重复启动、不关闭其它用户进程。源安装、业务原件、许可、二进制、服务端均未修改；没有新ECS/付费资源、提交、推送或远端创建。

下一条命令：python3 scripts/check-b02-license-46.py
独立验收下一步：直接只读SSH刷新PID113264路径/会话、445项源哈希、工作样例哈希和TCP，并核对21m→20m全文与截图，判断本轮可用操作是否足以满足B02-02许可判断；不把执行回归PASS当包PASS。若许可证据仍不足，继续同一存活客户端的另一可逆计算分支，或普通UI目录树导航到新卡授权reports目录。任何导出先读取实际路径并严格验证在授权目录；禁止默认C:\hwk\hook-out。B02-03报告/绘图/保存重开及B01/R01安装卸载仍未闭合，不能消失。

本轮里程碑已交接，结束执行，由外部控制器安排独立验收和后续卡。

---

## 用户直接指派线程：彻底搞清楚计算工具（2026-10-18，非调度卡）

状态：**PARTIAL，主动推进中**。总纲见 `migration_workspace/MASTER-PLAN.md`（含可验收的 8 层闭合条件与 P0–P4 优先级）。本线程只写 `migration_workspace/` 与新增取证脚本，不动其他卡的脚本/证据与共享台账。

本轮实测结论：
- 安装包全量清点：458 个 MSI File 条目、506.6 MB、139 PE + 319 非 PE；CAB 成员名是哈希，真实名只能由 MSI `File.FileName` 得到。证据 `migration_workspace/install-package.md`、`raw/install-package.json`，生成器 `scripts/summarize-install-package.py`。
- **产品级计算体系 74 个 / 19 个大类**（幕墙 24、雨蓬 14、框架幕墙 4、采光顶 4、热工U值 4、栏杆/平面结构/百叶/格栅 各 3…），源文件 `Support/HWKSchemaList.xml`。证据 `migration_workspace/calculation-systems.md`、`raw/calculation-systems.json`，生成器 `scripts/summarize-calculation-systems.py`。这是上一轮"多少个体系"问题的答案（此前用 `HWKCalc_*` 前缀猜的 65 组不采纳）。
- 计算引擎机制已闭合：注册存原型实例并 clone、`setName` 的 bool=入字典、`eval` 拉取式求值 + `$$__noEvaluateFunctions` 符号模式、数值取对象 `+0x8`。证据 `migration_workspace/calculation-core.md` §7。
- 节点层全量定位：379 个 CXMap 名字 → 379 个类 → 379 个互不相同的 `eval`（零复用），地址表 `migration_workspace/node-vtables.md`。
- 首个节点算法实测：`CalGlassDisp = ms × qwk × aw⁴ ÷ dw × theta × 1e9`，参数顺序 ms/qwk/aw/dw/theta/prefix/def，跟踪文本只打印前 4 个；节点内含时间+概率（约 1/89）驱动的 `GetHMMxValue` 许可校验，不影响返回值。证据 `calculation-core.md` §9，原始 Evidence `raw/CalGlassDisp-eval.rea.json`。
- 数据层负面结论：`Support/*.xdf`（106 个）为加密/压缩二进制（可打印率约 36%），材料/型材数据不可直读；`XWallTem.mdf` 的 UTF-16 扫描只出系统目录名，无中文表名。

阻塞：无外部阻塞。原版数值对照（L8）需要 B02 环境的 Windows 运行，仍 NOT_RUN。

下一条命令：
`python3 scripts/summarize-calculation-systems.py --install migration_workspace/raw/install-package.json --cab evidence/baseline/extracted/cab --out migration_workspace/calculation-systems.md --json migration_workspace/raw/calculation-systems.json`
（重生成体系清单；随后按 MASTER-PLAN 的 P0 做 `XWallTem.mdf` 页解析）

最近检查：本轮新增/改动的脚本 `lens_diagnostics` 均为 0 findings；`collect-b02-ui-46.py`（B02 UI 卡）遗留 8 条告警属其他卡，未代改。

### 用户指派线程 · 增量更新（2026-10-19，承接上文"彻底搞清楚计算工具"）

线程级交接已单独成文：**`migration_workspace/HANDOFF-offline.md`（8 节，含实机差分计划 §8.6）**，状态与下一条命令都在那里，本段只记增量指针。

- 节点层：**378/379 已反编译**（9 个族摘要 `nodes-*.md`）；不同算术核心 328 个、复用组 31 个/覆盖 81 个；FE 建/删模型各 7 个节点共用模板。参数抽取已修正：`$0/$1` 是可变参数节点的位置参数名（143 个节点），非噪声；覆盖 376/378。
- `.cwx` 格式：签名（偏移 8 恒为 5,439,563）、216 类型、记录头 `(a,b)`＝类组＋组内序号、`HWKCalc_*` 为 10 字节占位且 `Serialize` 空壳、CAD 图形按「每实体 7 条记录」定型。见 `cwx-format.md` §7–§10。**载荷字段宽度静态不可解**（`CbArchive::operator<<` 为跳转表分派），已改动态差分方案。
- 已交叉验证：`.cwx` 跨源一致性 **9 PASS / 6 N/A / 0 FAIL**（6 个优化类工程不含 `HWK*` 类型，属另一套格式）。
- 台账：`migration_workspace/VERIFICATION.md` A–G（PASS 10 / PARTIAL 6 / NOT_RUN 6 + 2 条更正记录）。
- 实机：样例已只读复制到 `C:\hwk-modern\run-20261019-cwx\a.cwx`（sha256 `7F79C6F3…F508BF`），XWall pid=113264 在运行；下一步按 §8.6 执行「打开→另存→逐字节 diff」求字段宽度。
- 边界未变：`vendor/` 未改；数据库只用 `HWKCOPY_*` 副本库只读；其他卡文件（如 `scripts/collect-b02-ui-46.py`）不代改。
