# `.cwx` 字段边界与宽度（动态差分实测）

- 日期：2026-10-19
- 方法：在测试机 `C:\hwk-modern\run-20261019-cwx`（**只操作副本**）用隔离客户端
  `C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe`（pid 157264 / session 4）打开、改一个输入、
  另存为新文件，再把文件拉回本地逐字节比对。
- 证据目录：`migration_workspace/raw/cwx-diff-20261019/`
- 复现脚本：`scripts/cwx-frame.py`、`scripts/cwx-diff-fields.py`、`scripts/cwx-diff-run.py`

## 1. 本轮文件与哈希（实测，SHA-256 全量）

| 文件 | 字节 | SHA-256 | 产生方式 |
| --- | --- | --- | --- |
| `a.cwx` | 7,318,303 | `7F79C6F3…F508BF` | 从 `C:\Program Files\HWKSoft\XWallClient\示例\各种栏杆样例.cwx` 只读复制（原件未改） |
| `b.cwx` | 823,355 | `7C69C00D…019A97B` | 打开 `a.cwx` 后原样「另存为」 |
| `c.cwx` | 823,355 | `5109D1F3…6C62CABF` | 在 `b.cwx` 上把「城市基本雪压」0.4 改为 0.5 后另存 |
| `d.cwx` | 823,355 | `825AF59C…40FB9A6` | 在 `c.cwx` 上把「城市基本风压」0.45 改为 0.55 后另存 |
| `e.cwx` | 823,357 | `CC85E5C8…098916B` | 在 `d.cwx` 上把「工程名称」`各种样式栏杆计算样例` 改为 `…样例X` 后另存 |

`a.cwx` 在全部操作前后哈希不变（原件与副本均未被写）。GUI 操作路径与控件级证据见
`saveas-open/`、`saveas-inspect/`、`saveas-fill/`、`cell-f2/`、`menu-item/`、`saveas-fill2/` 子目录的
`*.json`（含控件 handle、class、rect、读回文本）与 `*.png` 截图。

## 2. 容器框架（实测，10 个样例中 9 个一致）

```text
0x00  ff fe                      UTF-16LE BOM
0x02  ff                         标记字节（样例全部相同，语义未知）
0x03  u8 0x0e                    产品名字符数（14）
0x04  "HWKSoft XWall "           UTF-16LE，14 字符 = 28 字节
0x20  u32 02 00 00 00            归档版本 = 2（9 个样例一致）
0x24  u32                        payloadTotal；实测恒等于 文件长度 − 40
0x28  ← 记录流起点

记录头（实测）：
  u16  tag = 0x8000 | strlen(name)
  u16*strlen(name)  UTF-16LE 类型名（如 "HWKWallContext"）
  u32  A
  ...  载荷（紧接 A，无独立长度字段）
```

验证范围（`scripts/cwx-frame.py`）：`a/b/c/d` + `左右面板不同热工`、`连续梁立柱计算示例`、
`索桁架结构`、`热工计算例子`、`石材幕墙示例1`、`门窗计算示例1` —— 共 9 个文件
`declared_payload == size − 40` 全部成立。

例外：`玻璃优化示例.cwx` 无 `ff fe` 头（与 `cwx-format.md` 记录的「6 个优化类样例无 HKW* 类型」
一致）→ 优化类工程是**另一种容器**，不适用本节结论。

### 2.1 尚未解明的两项（保留未知，不猜）

| 项 | 实测事实 | 结论 |
| --- | --- | --- |
| `u32 A` 语义 | 同一构建里同一个类 `HWKWallContext` 在 `a.cwx` 中 A=773、在 `b/c/d` 中 A=1058；同一文件内大量不同类共用同一 A（`a`：6/399/773；`b`：6/597/1058） | **既不是载荷长度，也不是类常量**；含义未知 |
| 记录载荷长度 | 记录头里找不到能落位的长度字段；按 A 做算术推进会立刻错位 | 载荷长度可能由各类 `Serialize` 隐含决定（与静态结论一致），**未解** |

因此本脚本用「扫描下一个合法 tag」定位记录，不用算术推进；字段偏移一律按**绝对偏移**给出。

## 3. 已量出的字段（两次单字段差分，均只有 1 处差异）

| 语义（原版属性面板列） | 绝对偏移 | 相对 `HWKWallContext` 载荷 | 宽度 | 实测变化 |
| --- | --- | --- | --- | --- |
| 城市基本雪压 | `0x5E` | `+0x14` | 8 字节 IEEE754 LE double | `0.4` → `0.5` |
| 城市基本风压 | `0xA0` | `+0x56` | 8 字节 IEEE754 LE double | `0.45` → `0.55` |
| 工程名称 | `0x66`（字符数）+ `0x6A`（正文） | `+0x1C` / `+0x20` | u32 字符数 + UTF-16LE（变长） | 10 字符 → 11 字符（文件 +2 字节） |

`HWKWallContext` 记录本轮实测位置：tag `0x800e` @`0x28`，名字 14 字符，A=1058（`b/c/d`），
载荷起点 `0x4A`；载荷头部 `+0x00` = double `80.0`，`+0x08` = double `3027.6`，`+0x10` = int32 `2`。

### 3.1 差分结果（可复核）

```text
b.cwx -> c.cwx : 823355 -> 823355 bytes, 1 diff run
  off=0x00005e len=7 double 0.4 -> 0.5
c.cwx -> d.cwx : 823355 -> 823355 bytes, 1 diff run
  off=0x0000a0 len=7 double 0.45 -> 0.55
d.cwx -> e.cwx : 823355 -> 823357 bytes, 172804 diff runs
  off=0x000024 len=1  文件头 payloadTotal +2
  off=0x000066 len=1  u32 字符数 0x0a -> 0x0b
  off=0x00007e len=11 插入 58 00（UTF-16LE 'X'）→ 其后全部右移 2 字节
```

两次同长度编辑都只有 1 段差异、文件长度不变、且差异只落在 8 字节 double 的尾 7 字节（最高字节
`0x3f` 相同）——说明：

1. 该输入字段就是**原位 8 字节 double**，不是字符串或变长编码；
2. 该类对象**不做字节对齐**（`0x5E % 8 == 6`、`0xA0 % 8 == 0`），与 MFC `CArchive` 的紧凑写入一致；
3. 保存路径对未改动内容**逐字节确定**（无时间戳/随机量/指针值写入），这是后续所有差分的前提。

### 3.2 字符串编码（`工程名称` 实测，`d → e`）

```text
0x66  u32  字符数（不含结尾）        10 -> 11
0x6A  ...  UTF-16LE 正文，无结尾符   各=04 54、样=37 68 ……
```

同一规则在 `城市基本信息` 上也成立：`0x92` = u32 `3`，`0x96` 起 UTF-16LE `北京市`。
→ 工程文件内的文本一律 **u32 字符数 + UTF-16LE 紧凑排列**，不是 GBK（早前把 `04 54`
误读成 GBK 双字节，`04` 其实是「各」U+5404 的低字节）。

### 3.3 变长编辑的判读规则（本轮踩到）

变长字段（字符串）一改，插入点之后**整段右移**，逐字节差分会出现十几万段“差异”（`d→e` 172,804 段），
不能按“段数少=单字段”判断。判读顺序应为：

1. 先看文件长度差（`e` 比 `d` 大 2 → 只可能插入了 1 个 UTF-16 字符）；
2. 找**最早**的插入点（`0x7E`），插入内容 `58 00` 与输入一致；
3. 差异总数只作“有变长字段被改写”的指示，不作字段计数。

## 4. 「原样另存」为什么小 8.9 倍（`a` → `b`）

`a.cwx` 7,318,303 B → `b.cwx` 823,355 B，差异是全文件级重排，不适合当字段证据；但类清单差是可靠的：

- 仅存在于 `a`：`HWKElementOfBeam/Node/SubBeam/SubNode`、`HWKFEResultOfNode/SubBeam/LoadCombination`、
  `HWKLoadCoordInfo`、`HWKLoadOfBeamDistributeExForce`、`HWKLoadOfNodeForce`（10 个，全部是**有限元结果/节点荷载**）
- 仅存在于 `b`：`HWKCalc_GlassDisp/GlassStrength/GlassArea/GlassWeight`、`HWKGlass`、
  `HWKCalc_ChmABolt*`（14 个）、`HWKCalc_ExpaBolt*`（13 个）、`HWKExpandAnchorBolt`、`HWKChemAnchorBolt`、
  `HWKChmABoltLayout`、`HWKCommonBoltLayout`、`HWKEmbeddingAnchorArea*`、`HWKGlassDrawing`、`HWKUDataInfos` 等（45 个）

即：样例里 6.5 MB 是**已算过的有限元结果**，另存时被丢弃并补上锚栓/玻璃类计算对象。
**推断（非结论）**：结果不入库（只入运行期），这一点在 §5 有独立证据。

## 5. 计算节点没有把数值写进工程文件（负面结论）

`c.cwx` 中计算类记录的载荷实测：

| 记录 | 载荷字节 | 内容 |
| --- | --- | --- |
| `HWKCalc_GlassDisp` | 4 | `05 00 00 00` |
| `HWKCalc_GlassArea` | 8 | 全 0 |
| `HWKCalc_GlassStrength` | 8 | `00 00 00 00 04 00 00 00` |

没有 8 字节结果数值。配合下一项，说明**计算结果不持久化**。

## 6. 公式参数名不在工程文件里（负面结论）

在 `a.cwx` / `b.cwx` 全文检索（ASCII 与 UTF-16LE 两种编码）：

| 串 | a.cwx | b.cwx |
| --- | --- | --- |
| `qwk` | 0 | 0 |
| `theta` | 0 | 0 |
| `ms\0` | 2 | 0 |
| `aw\0`, `dw\0` | 各 1 | 0 |
| `CalGlassDisp` | 0 | 0 |

即 `calculation-core.md` §9 的 7 个具名形参（`ms/qwk/aw/dw/theta/prefix/def`）**不随工程文件持久化**，
公式图是运行期由计算体系构建的。→ 字段级 G3 无法只靠 `.cwx` 闭合，见 `cwx-g3.md`。

另：上表 `a.cwx` 中 `ms\0`/`aw\0`/`dw\0` 的 1–2 次命中位于二进制载荷中部，不是
“u32 字符数 + UTF-16LE”结构的文本字段（对照 §3.2），因此**不得**当作参数名落盘证据。

## 7. 复现命令

```bash
F=migration_workspace/raw/cwx-diff-20261019/files
python3 scripts/cwx-frame.py $F/a.cwx $F/b.cwx $F/c.cwx $F/d.cwx $F/e.cwx \
        --json migration_workspace/raw/cwx-diff-20261019/frame-ab.json
python3 scripts/cwx-diff-fields.py $F/b.cwx $F/c.cwx --json migration_workspace/raw/cwx-diff-20261019/diff-b-c.json
python3 scripts/cwx-diff-fields.py $F/c.cwx $F/d.cwx --json migration_workspace/raw/cwx-diff-20261019/diff-c-d.json
python3 scripts/cwx-diff-fields.py $F/d.cwx $F/e.cwx --json migration_workspace/raw/cwx-diff-20261019/diff-d-e.json --max-print 3
```

实机侧探针：`scripts/cwx-probes/*.ps1`，运行器 `scripts/cwx-diff-run.py`（通过 `HWKModern-20261019-CWX`
计划任务在 session 4 执行，产物落 `migration_workspace/raw/cwx-diff-20261019/<probe>/`）。

## 8. 状态

| 项 | 状态 | 说明 |
| --- | --- | --- |
| 记录头/文件头框架 | PARTIAL | 头 40 字节与记录头已实测；载荷长度规则未知 |
| 字段宽度测量方法 | PASS | 同长度单字段差分各只 1 段差异；变长编辑按插入点判读 |
| 已测字段 | 3 | 城市基本雪压、城市基本风压（8 字节 double）、工程名称（u32 字符数 + UTF-16LE） |
| 字符串编码规则 | PASS | u32 字符数 + UTF-16LE（工程名称、城市名两处互证） |
| 其他字段 | NOT_RUN | 需继续「改一个输入→另存→差分」 |
| 字段语义归属 | PARTIAL | 语义来自原版属性面板列名 + 值命中，未做规范/计算书对照 |

## 9. 新发现：工程文件里有「参数绑定表」（`HWKInfoRelation`，2026-10-19）

在 `a.cwx` / `b.cwx` 里都有两个相关记录，**实测格式（已解析成功）**：

| 记录 | 载荷结构 |
| --- | --- |
| `HWKInfoRelationOfSelf` | `u32 A` + [可选 `u32 0`] + `u32 对数` + 每对：`u32 长度 + UTF-16 名`、`u32 长度 + UTF-16 值` |
| `HWKInfoRelation` | `u32 A` + `u32 个数` + 每个：`u32 长度 + UTF-16 名`（纯名字列表） |

实测解析结果（两个文件一致）：

```text
HWKInfoRelationOfSelf (A=0x305 / 0x422)
  LOAD_GIVEWK  → GLOB_GIVEWK      # 取全局量的值
  LOAD_BWEIGHT → 0.5              # 取常量

HWKInfoRelation (A=0x305 / 0x422)
  RAILINGFRAME_W …                # 名字列表
```

注意：**长度前缀是 `u32`（不是 u16）**；`b.cwx` 在 `A` 后多一个 `u32 0`（估计是分区/标志），
解析时用"两种偏移各试一次、取能完整解出且字符串合法的那次"即可（脚本已按此实现）。

**为什么重要**：上一轮统计出 5285 个公式符号里 82% 在数据库里找不到（`none`），当时判断是"构件输入"。
这张表说明——**它们的取值来源就写在工程文件里**（全局量 / 常量 / 另一参数），属有结构的绑定表。

样例里只出现 2 对（该样例的绑定很少），但格式与解析路径已打通，换更复杂的工程即可规模化。

### 下一步（机器恢复前后都可做）

1. ~~解出记录格式~~ 已完成（`u32` 长度前缀；两种偏移自动试解析）；
2. 把这张绑定表与 `formula-symbol-map.json` 的 4329 个 `none` 符号对照，看覆盖率；
3. 若覆盖率高，则"可执行公式"的门槛从"需要 UI 输入"降为"需要解析关系表 + 少量真实输入"。
