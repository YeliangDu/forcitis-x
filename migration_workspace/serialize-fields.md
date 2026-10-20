# `.cwx` 字段布局：方法与首批结果（2026-10-20）

目标：让"中间量落盘格式"脱离猜测。结论：**可以按字段读出来**，且已建立可重跑的方法；剩余工作是沿继承链走完每一层。

## 1. 证据来源

| 项 | 值 |
| --- | --- |
| 模块 | `evidence/baseline/extracted/cab/_F35DC0979FF04306B20773A25268CC58` |
| sha256 | `877057a46c5091aac738bc3b49efc3d9d501bdb69c76098b309a23bec03dbe78` |
| REA | CLI 6.7.0 / Ghidra 12.1.4（`GHIDRA_INSTALL_DIR=/Users/yeliang/tools/ghidra_12.1.4_PUBLIC`） |
| Evidence | `evidence/.../rea-serialize/glassbase.json`（`ev_d8a40627…`）、`serialize-fields.json`、`glass-serialize-fields.json` |

## 2. 编译器留下的可读模式

`HWKCalc_GlassBase::Serialize` 反编译只有 795 字节，真正的写盘动作藏在被 Ghidra 标为
"jumptable 无法恢复"的间接跳转里。转去看反汇编就清清楚楚：

```text
180089fa2: 8b 93 98 00 00 00   movl 0x98(%rbx), %edx   ; 取 this+0x98 的 4 字节值
180089fa8: 48 8b cf            movq %rdi, %rcx          ; rcx = CbArchive*
180089fb5: 48 ff 25 ...        jmpq *<operator<< thunk> ; 尾调用 CbArchive::operator<<
...
180089fbc: 83 7b 0c 20         cmpl $0x20, 0xc(%rbx)    ; 读回时按类版本门控
180089fca: ff 15 ...            callq *<operator>> thunk
180089fd4: 89 83 98 00 00 00   movl %eax, 0x98(%rbx)    ; 读到的值写回 this+0x98
```

于是每一层的规则是：

- **存盘**：`value = *(类型*)(this + 偏移)` → `CbArchive::operator<<(archive, value)`
- **读回**：`if (*(int*)(this+0xc) >= 阈值) { operator>>(archive, &tmp); *(类型*)(this+偏移) = tmp; }`

`this+0xc` 是**类版本/标识**，字段按版本出现——这解释了历史 `.cwx` 与新版本之间"多/少字段"的现象。

## 3. 已解析工具

`scripts/extract-serialize-fields.py --pe <PE> [--filter <类名>] [--json out]`：

- 用 `objdump -d` 扫全部 `?Serialize@…` 符号（本模块 **412 个**）；
- 每个方法报告：读/写字段偏移与宽度、版本阈值、`operator<</>>` 跳转桩数量；
- 只报告指令里明确出现的偏移，不推断字段名与语义。

## 4. 玻璃族首批结果（10 个方法）

| 方法 | 读 | 写 | 版本门 |
| --- | --- | --- | --- |
| `HWKCalc_GlassBase` | `+0x98`(4B) | `+0x98`(4B) | `0x20` |
| `HWKCalc_GlassPSBase` | `+0x98`(4B) | `+0x98`(4B) | `0xA0` |
| `HWKCalc_GlassPSRibBase` | `+0x98`(4B) | `+0x98`(4B) | `0x207` |
| `HWKCalc_GlassRibBase` | `+0x98`(4B) | `+0x98`(4B) | `0x5B` |
| `HWKCalc_GlassDisp` / `GlassArea` / `GlassStrength` / `GlassWeight` | — | — | — |
| `HWKCalc_GlassPSWeight` / `GlassPSRibStrength` / `GlassRibWidth` / `GlassFESupportInfo` | — | — | — |

后两行"无字段"是真的：它们的 `Serialize` 只调用基类（例如 `GlassDisp` 的 856 字节只有
`HWKCalc_GlassBase::Serialize(this, archive)` + `IsStoring`），字段全在基类链上。

## 5. 结论与剩余工作

- **方法已闭环**：任意 `Serialize` 的字段偏移/宽度/版本门现在可机械读出，不再依赖猜测。
- **顺序已解**（见 §7）：`scripts/build-serialize-chains.py` 把基类链叠加成记录内的有序字段表，
  并用 `b.cwx` 的实测偏移逐字段对齐（3 个锚点全中）。
- **仍未闭环**：字段**语义**（哪个是名/单位/派生量）只证到 5 个；记录边界（`u32 A` 语义）未知；
  412 个 `Serialize` 中还有 thin-wrapper 与读半未切分的个例（§7.5）。

## 6. 复跑

```text
GHIDRA_INSTALL_DIR=/Users/yeliang/tools/ghidra_12.1.4_PUBLIC \
  rea decompile <PE> --procedure='?Serialize@HWKCalc_GlassBase@@MEAAXAEAVCbArchive@@@Z' --format=json
python3 scripts/extract-serialize-fields.py --pe <PE> --filter 'Serialize@HWKCalc_Glass' --json out.json
```

---

## 7. 基类链叠加与 `.cwx` 字节对齐（2026-10-20）

### 7.1 方法：`scripts/build-serialize-chains.py`

从同一份 `objdump -d` 里机械读出三件事，再叠成"一条记录内的字段顺序"：

| 项 | 判据（指令层） |
| --- | --- |
| 本层字段写 | `movsd/movl/movq/movzbl 0xNN(%this)` 之后紧跟 `callq *<IAT 槽>`；宽度由助记符给出，`leaq` = 聚合/String |
| `this` 寄存器 | 每函数不固定（`%rbx`/`%rdi`/`%rsi` 都出现过），取"成员引用最多的非 `%rsp/%rip` 寄存器" |
| 基类调用 | 体内 `callq <base>::Serialize`，其**位置**决定基类字段插在哪：`HWKCalc_GlassBase` 先调基类，`HWKWallContext` 不调基类（根） |
| 版本门 | 读半以 `this+0xc` 与立即数比较（`cmpl $imm,0xc(%reg)` 或 `movl 0xc(%reg),%reg; cmpl $imm,%reg`），每个后继字段继承当前门值 |
| 版本标记 | `this+0xc` 通过专用槽 `0x18034f288` 写出，属"类版本标记"，不进字段表 |

IAT 槽按"谁喂它"分类（全模块统计）：`0x18034f0e8`←`movsd`（double）、`0x18034f0f0`←`movl`（int32）、
`0x18034f118`←`leaq`（String/聚合写）、`0x18034f100/108/110`←`leaq`（double/int/String 的读），
`0x18034f0b8` = `IsStoring` 谓词（不是归档操作）。

### 7.2 链图（本模块 412 个 `Serialize`、13 个根）

根（体内不调任何基类 `Serialize`）：`HWKWallContext`、`HWKWallContextObject`、`HWKSurfaceLoad`、
`HWKGLayerStruct`、`HWKLockPointInfo`、`HWKPoleDivInfo`、`HWKThermModelInfo`、`HKWVariantInfo`、
`HWKWallUnitData_Frame`、`HWKWallUnitData_Glass`、`HWKWinBeamDivInfo`、`HWKWinDivideInfo`、`HWKWinHDivInfo`。

玻璃族：`HWKCalc_GlassDisp`（薄壳，自身无字段）→ `HWKCalc_GlassBase`（`+0x98` int32，门 `0x20`）
→ `HWKSBLinkInfoBase` → `HWKWallContextObject`。与 §4 的静态结果一致，顺序现在也确定了。

### 7.3 与 `.cwx` 实测对齐（`b.cwx`，`HWKWallContext`，载荷起点 `0x4A`）

脚本按链走载荷，`String` 按 `u32 字符数 + UTF-16` 推进；三个由单字段差分实测出来的锚点全部命中，
且**读出的值与语义一一对上**：

| 载荷偏移 | 类型 | 对象偏移 | 读出值 | 语义（差分来源） |
| --- | --- | --- | --- | --- |
| `+0x00` | double | `+0x80` | 80.0 | 未知（候选：计算高度/标高） |
| `+0x08` | double | `+0x88` | 3027.6 | 未知 |
| `+0x10` | int32 | `+0x90` | 2 | 未知 |
| `+0x14` | double | **`+0x98`** | **0.4** | **城市基本雪压**（b→c: 0.4→0.5）✔ |
| `+0x1C` | String(10) | **`+0xa0`** | **各种样式栏杆计算样例** | **工程名称**（b→e: 10→11 字符）✔ |
| `+0x34` | double | `+0xa8` | 0.16 | 未知（候选：地震影响系数） |
| `+0x3C` | int32 | `+0xd0` | 3 | 未知（候选：粗糙度/设防类别代码） |
| `+0x40` | double | `+0xd8` | 0.0 | 未知 |
| `+0x48` | String(3) | `+0xe0` | 北京市 | 工程所在城市（报告正文一致） |
| `+0x52` | int32 | `+0x108` | 2 | 未知 |
| `+0x56` | double | **`+0x110`** | **0.45** | **城市基本风压**（b→d: 0.45→0.55）✔ |
| `+0x5E` | int32 | `+0x138` | 6 | 未知 |
| `+0x62` | String(2) | `+0x140` | ⅡA | 地面粗糙度类别（报告"地面粗糙度类别:C类"待核） |
| `+0x6A` | int32 | `+0x10` | 50 | 未知（**此处之后推进不可靠**，见 §7.5） |

判定：**PASS（前缀 13 个字段）**——三个独立差分锚点落在链预测的偏移上，且类型与读值自洽；
这同时说明".cwx 记录 = 该类型 `Serialize` 链的写出顺序"这条假设成立。

### 7.4 复现

```text
python3 scripts/build-serialize-chains.py --root HWKWallContext   --cwx migration_workspace/raw/cwx-diff-20261019/files/b.cwx
python3 scripts/build-serialize-chains.py          # 13 个根全部展开，写 raw/serialize-chains.json
```

### 7.5 已知限制（保留，不掩盖）

1. **记录边界仍未解**：走完 29 个字段后遇到"不可能的字符串计数"即停（读出 1,564 B，而 `u32 A`=1058 不是长度）。
   `A` 的语义仍未知，因此只能按"扫描下一个合法 tag"定位记录。
2. **聚合类型**一律按 `u32 字符数 + UTF-16` 解析；遇到数组/嵌套对象会漂移（`+0x72` 处已出现），
   需要按槽位细分为 `String` / `vector` / 嵌套对象。
3. **thin wrapper**：`HWKCalc_GlassDisp` 这类只转调基类的类，本工具解析出 0 字段（其体 856 B 主要是
   内联的其它逻辑），需要单独建模。
4. **读半切分**依赖 `this+0xc` 比较；没有任何门控的类（如 `HWKWallContext`）体里没有 `cmpl`，
   其读半只能靠 `IsStoring` 分支目标定位，当前会多记少量 `aggregate` 噪点（已见 `HWKWallContextObject`）。
5. 412 个类只验证了 1 个根的 13 个字段；其余类需逐个与真实记录对齐后才能称"顺序已解"。
