# 交接：离线分析流水线（下一轮直接从这里继续）

更新时间：2026-10-18。总纲见 `MASTER-PLAN.md`，验证台账见 `VERIFICATION.md`。

## 1. 当前状态一句话

离线分析已覆盖：安装包 / 体系 / 模块 / 引擎 / 节点定位 / 公式库 / 数据库 / `.cwx` 文件格式；
**未覆盖**：379 节点的算法语义（84/379）、FE 求解链、`.cwx` 数值字段语义、优化类工程格式、实机数值对照。

## 2. 正在后台跑

```sh
sh scripts/offline-advance.sh      # 379 节点批量反编译，断点续跑，幂等
```
产出：`migration_workspace/raw/nodes/*.rea.json`（已完成 84）、`nodes-<族>.md`
日志：`migration_workspace/UNATTENDED.log`；状态：`UNATTENDED.state`

## 3. 已完成且可复核的产物

| 文件 | 内容 |
| --- | --- |
| `install-package.md` | 458 MSI 条目 / 506.6 MB / 139 PE / 3 CAD 插件族 |
| `calculation-systems.md` | 74 体系 / 19 大类 / 157 构件类 |
| `calculation-core.md` | 引擎机制 9 节 + `CalGlassDisp` 完整算法 |
| `node-vtables.md` | 379 类 / vtable / eval 地址全表 |
| `formulas.md` + `formulas.json` | 2,079 条公式（GBK 明文）+ 58 规范号 |
| `db-schema.md` | 3 库 85 表 / 708 列 + 材料/规范字段样例 |
| `cwx-format.md` | `.cwx` 头部、216 类型、记录格式 |
| `cwx-crosscheck.md` | 跨源一致性 9 PASS / 6 N/A / 0 FAIL |
| `units-candidates.md` | 公式→候选单元切分（12,176 个） |
| `VERIFICATION.md` | PASS/PARTIAL/NOT_RUN 台账 |

## 4. 本轮四个可复用的关键事实

1. **`.cwx` 记录格式**：`<类型名 UTF-16><u32 a><u32 b><8 字节零><double 序列>`。
   已用它读出圆弧对象：`−π/4, 4.0, +π/4, −12.0, −22.0, …`（角度/半径/圆心）。
2. **`.cwx` 有两种格式**：优化类工程（6/15 样例）不含任何 `HWK*` 类型，走另一套序列化。
3. **版本门控**：`HWKProjectInfo::Serialize` 用 `0x28` / `0x2e3` 两个阈值决定是否读新字段。
4. **参数名判定规则**：只有"构造后 4 行内被 `look_string` 当字典键用"的字面量才是参数名，
   否则会把 Ghidra 占位符、错误提示文案当成参数（实测污染率曾达 43%）。

## 5. 下一条命令（按优先级）

```sh
# 1) 继续节点批次（若已停）
sh scripts/offline-advance.sh

# 2) 记录级读取（看某类型的 double 序列）
python3 scripts/cwx-read.py <cwx> --type HWKCalc_LoadWinStand

# 3) 跨源一致性（改动类表/体系清单后重跑）
python3 scripts/cwx-crosscheck.py --out migration_workspace/cwx-crosscheck.md \
        --json migration_workspace/raw/cwx-crosscheck.json

# 4) 公式解码 / 单元切分
python3 scripts/decode-formulas.py --hex migration_workspace/raw/db-schema/formula-hex.csv \
        --out-json migration_workspace/formulas.json --out-md migration_workspace/formulas.md
python3 scripts/split-formula-units.py --formulas migration_workspace/formulas.json \
        --out migration_workspace/units-candidates.md
```

## 6. 下一轮该做的三件事（按信息量排序）

1. **`.cwx` 二次切分**：当前按"下一个类型名"截断，`HWKCADGraphArc` 中位 370 个 double
   说明跨了记录。应按头部 `a`/`b` 字段界定，然后对 `HWKCalc_*` 记录取值做 G3 数值闸门。
2. **优化类工程格式**：6 个样例无 `HKW*` 类型，需单独取证（可能不是 CbArchive）。
3. **FE 求解链**：114 个 `FEAdd*` 参数表已随批次产出，下一步对照 `HWKFeUtil.dll` / `Structmodule.dll`。

## 7. 阻塞与边界

- 实机数值对照（G3 的最终形态）需要 Windows 运行；离线只能做到"文件内自洽"。
- 数据库只用副本库 `HWKCOPY_*` 只读；未写入、未 attach 新库。
- `vendor/` 未修改；其他卡的文件（如 `scripts/collect-b02-ui-46.py`）不代改。

---

## 8. `.cwx` 载荷编码：改走动态差分（用户已同意，2026-10-19）

静态路线已到头：`CbArchive::operator<<` 是跳转表分派的重载集合，Ghidra 解不出具体重载
（反编译里反复出现 `Could not recover jumptable … Treating indirect jump as call`），
因此"每次写多少字节"静态拿不到。

### 8.1 方案：另存差分（不注入、不改原工程）

1. 在测试机 `C:\hwk-modern\run-<日期>-cwx` 下**复制**一个样例工程（不改原文件）
2. 用 XWall 打开副本 → **另存为** `b.cwx` → 关闭
3. 把原副本 `a.cwx` 与 `b.cwx` 拉回本地，逐字节比对：
   - 完全相同 → 说明另有随机/时间字段（先看差异位置是否在小块区域）
   - 有差异 → **差异位置就是数值字段边界**，据此量出字段宽度与对齐
4. 再做一次"改一个输入再算"的差分：只改一个参数，观察哪几个 8 字节变化 → 直接对应公式输入
5. 用 `CalGlassDisp` 的公式（`ms×qwk×aw⁴÷dw×theta×1e9`）复核变化量，完成 G3

### 8.2 安全边界

- 只操作 `C:\hwk-modern\` 下的副本；不碰 `C:\Program Files\HWKSoft` 原件
- 不 attach 新数据库、不改 `HWKCOPY_*`；读取只用副本库
- 若需重启 XWall，先确认无未保存工程；许可状态前后各截一次本地记录

### 8.3 备选（若 GUI 操作受限）

直接读实机上已存在的两个同类工程（如同为 `HWKSchema_LinkTruss`）做差分，
不需要打开应用；只是无法控制"只改一个输入"。

### 8.4 预期产出

- `migration_workspace/cwx-field-widths.md`：字段边界与宽度表
- `migration_workspace/cwx-g3.md`：G3 数值闸门结果（PASS/FAIL + 误差）

### 8.5 实机准备已完成（2026-10-19）

| 项 | 值 |
| --- | --- |
| 本轮目录 | `C:\hwk-modern\run-20261019-cwx` |
| 样例副本 | `a.cwx`（7,318,303 字节，sha256 `7F79C6F3…F508BF`） |
| 源文件 | `C:\Program Files\HWKSoft\XWallClient\示例\各种栏杆样例.cwx`（**只读复制，未改原件**） |
| XWall 进程 | 本轮新起 pid=157264 / session 4，标题 `豪沃克幕墙工程软件XWall  - [d.cwx]`（8.6 全部完成后仍存活） |

### 8.6 下一步自动化步骤（下一轮直接执行）

> **2026-10-19 本轮已全部执行完**（下方原计划保留，实际结果见 §9）。

1. 让 XWall 打开 `C:\hwk-modern\run-20261019-cwx\a.cwx`（若支持命令行参数直接传路径；
   否则用 UIA 找"打开"菜单，或 SendKeys `Ctrl+O` + 输入路径）
2. `Ctrl+Shift+S` 另存为 `b.cwx` 到同一目录；确认覆盖提示时选"是"
3. 关闭该文档（不保存再次改动），把 `a.cwx` / `b.cwx` 一起拉回本地
4. 本地比对：`python3` 逐字节 diff → 差异偏移即字段边界
5. 再做一次"改一个输入 → 另存"的差分，定位公式输入字段
6. 用 `CalGlassDisp` 公式复核，产出 `cwx-field-widths.md` 与 `cwx-g3.md`

风险控制：只操作副本；若打开时提示许可/工程升级，**记录弹窗原文并停止**，不要确认升级。

---

## 9. 8.6 执行结果（2026-10-19 续跑，已完成）

结论一句话：**动态差分方法成立且干净；字段宽度量出 2 个；G3 在文件侧不可能闭合，需回到原版运行。**

### 9.1 实际做了什么

| 原计划 | 实际结果 |
| --- | --- |
| 1 打开 `a.cwx` | `Start-Process XWall.exe "<a.cwx>"` 直接传路径即可（无需 `Ctrl+O`）；pid 157264 / session 4 |
| 2 `Ctrl+Shift+S` | **该快捷键无效**；改为点菜单栏「文件」→ 按项坐标点「另存为(A)…」→ 系统 `#32770` 对话框，`WM_SETTEXT` 写全路径 + `BM_CLICK` 点「保存」 |
| 3 关闭文档 | 未关闭；文档依次变为 `b→c→d.cwx`，进程保持存活供下轮继续 |
| 4 逐字节 diff | `a→b` 为全文件重排（7,318,303→823,355）；真正可用于量字段的是 `b→c`、`c→d` |
| 5 改一个输入 | 城市基本雪压 0.4→0.5、城市基本风压 0.45→0.55，各一次 |
| 6 公式复核 | **失败且已定性**：公式参数名与计算结果都不落盘，`.cwx` 侧无法复核 `CalGlassDisp` |

### 9.1b 续跑增量（同一轮内追加，2026-10-19 20:0x）

- 第 3 个字段量出：`工程名称` = `u32 字符数 @0x66` + `UTF-16LE 正文 @0x6A`；改名 10→11 字符 → 文件 +2 字节。
- 字符串编码规则因此定案：**u32 字符数 + UTF-16LE 紧凑排列**（`北京市`：count=3 @0x92、正文 @0x96）。
- 新增 `e.cwx`（823,357 B，sha256 `CC85E5C8…098916B`）；差分 `d→e` 172,804 段但只是**单点插入**后的整体右移。
- 新增探针 `scripts/cwx-probes/cell-edit.ps1`（字符串单元格）、`click-then-dump.ps1`（提交并回读）。
- 坑：字符串单元格 `ENTER` 不提交，需点别处（本轮点左侧树 `(120,131)`）才提交；提交后用 UIA 顶部 `ComboBox` 名字核验。

### 9.2 关键实测数字

```text
b.cwx -> c.cwx : 823355 -> 823355, 1 diff run, off=0x5E  double 0.4 -> 0.5    (城市基本雪压)
c.cwx -> d.cwx : 823355 -> 823355, 1 diff run, off=0xA0  double 0.45 -> 0.55  (城市基本风压)
d.cwx -> e.cwx : 823355 -> 823357, 插入点 0x7E 插入 58 00 (UTF-16 'X')      (工程名称)
                 同时 0x66 的 u32 字符数 0x0a -> 0x0b
```

- 记录头：`u16(0x8000|名字长度)` + UTF-16 名字 + `u32 A` + 载荷（**无独立长度字段**）。
- 文件头 40 字节，`u32@0x24 == 文件长度 − 40`，9 个样例全部成立；`玻璃优化示例.cwx` 是另一种容器（无 BOM）。
- `u32 A` 语义未知：同类 `HWKWallContext` 在 `a` 中 773、在 `b/c/d` 中 1058；同文件内多类共用同一 A（`a`：6/399/773；`b`：6/597/1058）。**既不是长度也不是类常量**。
- 保存对未改动内容逐字节确定（同长度差分都只有 1 段差异，无时间戳噪声）。
- 文本字段编码已实测：**u32 字符数 + UTF-16LE 紧凑排列**（`工程名称` 10→11 字符文件 +2 字节；`北京市` count=3 @0x92、正文 @0x96）。早前当 GBK 读的 `04 54` 其实是「各」(U+5404) 低字节。
- 变长字段一改，插入点之后整段右移（`d→e` 出现 172,804 段差异），判读靠文件长度差 + 最早插入点，不靠段数。
- `a→b` 丢掉的 10 个类全是有限元结果/节点荷载；新增的 45 个类是玻璃/锚栓计算对象。
- 计算类记录载荷只有 4–8 字节且无 double → 结果不持久化；`qwk/theta/CalGlassDisp` 在文件中 0 次命中 → 公式图不持久化。

产出：`migration_workspace/cwx-field-widths.md`（PASS/PARTIAL 混合，见其 §8）、`migration_workspace/cwx-g3.md`（BLOCKED：方法不适用）。
脚本：`scripts/cwx-frame.py`、`scripts/cwx-diff-fields.py`、`scripts/cwx-diff-run.py`、`scripts/cwx-probes/*.ps1`。
证据：`migration_workspace/raw/cwx-diff-20261019/`（4 个 cwx、7 个样例副本、diff json、各探针 json+png）。

### 9.3 操作坑（下轮直接用）

1. **不要按 `Ctrl+Shift+S`**：无效。走菜单点击：菜单栏 `(18,35)` → 弹出菜单项「另存为(A)…」`(60,136)`（菜单弹窗 rect `10,44,218,266`）。
2. **不要 SendKeys `a` 选菜单项**：IME 候选窗会吃掉按键（实测出现 `CandidateWindow`）。
3. **属性网格单元格要双击**（两次 click 间隔 ~120ms）才进 `Edit`；单击只落到 `AfxWnd140u`。改完按 `ENTER` 提交。
4. 网格**点击行号与可见标签错位一行**：要按单元格当前值守卫（`编辑框名字 == 期望值`）再输入，别按标签位置点。
5. SSH stdin 一次性上传较大 `.ps1` 会随机卡死（远端 powershell 卡在 `CopyTo`，并留下 0 字节文件锁）。改用 `scripts/cwx-diff-run.py` 的分块 `upload_chunked`（每块 768B，`WriteAllText`/`AppendAllText`），并给 `.ps1` 加 UTF-8 BOM（否则 PS 5.1 按 ANSI 解码，中文字面量直接语法错）。
6. 卡死的上传进程要按命令行里的 `OpenStandardInput` 找出来杀掉，否则文件锁 + CPU 空转。

### 9.4 下一条命令（下一轮）

同一存活进程（pid 157264，当前文档 `e.cwx`）可继续量字段；两个推荐目标：

```bash
# A) 整数型字段：风压设计年限 50 -> 60（先核对当前值，网格行与标签错位一行）
python3 scripts/cwx-diff-run.py run cell-edit 890 249 '50' '60'
# B) 玻璃/荷载页面上的尺寸类输入（需先导航），量到 double 后可直接对公式输入定位
python3 scripts/cwx-diff-run.py run menu-item f-open 60 136
python3 scripts/cwx-diff-run.py run saveas-fill2 f-fill 'C:\hwk-modern\run-20261019-cwx\f.cwx'
scp -i ~/.ssh/hwk-win-test 'Administrator@8.149.129.78:C:/hwk-modern/run-20261019-cwx/f.cwx' \
    migration_workspace/raw/cwx-diff-20261019/files/f.cwx
python3 scripts/cwx-diff-fields.py migration_workspace/raw/cwx-diff-20261019/files/e.cwx \
    migration_workspace/raw/cwx-diff-20261019/files/f.cwx --max-print 5
```

G3 改道：需要在 B02 环境读界面值 + 原版计算结果，步骤见 `cwx-g3.md` §3；本卡不得以文件自洽替代。

### 9.5 机器状态提醒（2026-10-19 14:20 实测）

- 测试机 4 核、系统 CPU **100%**：占用者是 **3 个非本项目进程**
  `powershell 12756 / 34968 / 44368`（命令行指向 `C:\DSM-REA-Test\morden-office`、操作 `WINWORD`），
  各累计 3.3 万 CPU 秒；**不是本轮 HWK 自动化**，未杀、未改。
- XWall 自身累计 CPU 仅 20.9 秒、工作集 38.5 MB、句柄 931 → 应用空闲，自动化开销可忽略。
- 因此本轮所有 GUI 探针都按「单次短任务」执行，未做轮询式截图。


---

## 10. L5 / A 路线：节点算式抽取（2026-10-19 新增，可续跑）

一句话：**三步已完成——379/379 个节点全部反编译并分类；47 个算式完全可读、39 个有骨架、293 个已归类为非算术（UNKNOWN=0）。**

### 10.1 产物

| 文件 | 内容 |
| --- | --- |
| `scripts/extract-node-expr.py` | 机械替换抽取器（参名两跳绑定 + 数值对象取用 + 逐语句代入） |
| `migration_workspace/nodes-expr.md` | 生成的逐节点表（状态 / 参名 / 代入后算式） |
| `migration_workspace/raw/nodes-expr.json` | 同内容机器可读版（含每步 `steps` 与 `ctor_args`） |

### 10.2 分布（379 个节点，`raw/nodes/*.rea.json`）

算式抽取（`nodes-expr.md`）：

| 状态 | 数量 |
| --- | --- |
| `EXPR`（参名全绑、无残留中间变量） | 52 |
| `SELECTED`（含 `sel(…)` 数据相关选择） | 1 |
| `TABLE_LOOKUP`（规范查表函数） | 13 |
| `INTERPOLATION`（调用方传入的表做线性查表） | 4 |
| `STRING_TABLE`（字符串键常量表） | 2 |
| `FE_OP`（FE 建模/求解动作） | 13 |
| `EXTERNAL_CALL`（未定性外部函数） | 3 |
| `PARTIAL`（有算式骨架、来源未定） | 30 |
| `NO_ARITH`（反编译里没有数值算术） | 260 |

节点头分类（`node-kinds.md`，`UNKNOWN`=0）：`GETTER` 115、`ARITH` 95、`STRING` 69、
`FE_DATA` 47、`COLLECTION` 45、`DRAW` 7、`PREDICATE` 1。

辅助函数（`raw/helpers/*.rea.json`，31 个）：`GLOBAL_GETTER` 1（`FUN_180279d50` → `GLOB_STEELLIMIT`，已代入）、
`RNG` 1（`FUN_180331b80`，许可校验伪随机）、`ARITH` 7（已归档未内联）、`OTHER` 22。

自检：`CalGlassDisp` 输出
`((qwk * ms * (pow(aw,4.0))) / dw) * theta * 1000000000.0`，与 `calculation-core.md` §9 人工核对结论逐字一致。

### 10.3b 四件收尾（2026-10-19 完成）

1. `FUN_180251270` 反编译结果证伪了"代理取参"假设 → 它是 `GetAVmax` 的构造函数；
   节点 eval 里这类调用属**符号回退分支**，已用 `numeric_block()` 排除。
2. `CONCAT44(hi,lo)` 还原已加（18 类节点受益）；`OTHER` 类辅助函数不再当数值来源。
3. `helper-tables.md`：11 个查表函数的「条件 → 常量」已提取（未命名系数，规范依据仍未知）。
4. `GetACFt` 的 `sel(H|W)` 已定位条件（`dVar5≈2.0 → dVar2`、`dVar5≈0 → dVar3`），存 `select_note`。
5. `node-descriptions.md`：379 个节点逐个给结构描述（入参/业务调用/分支数/返回类型）。

### 10.3 已知缺口（2026-10-19 第 1 轮执行后）

1. `FEDelCBProb` 已补齐 → **379/379 个节点都有反编译**。
2. 33 个待收尾节点已逐条列进 `nodes-residual.md`（未绑定符号 + 赋值来源）：`p[…]` 8、残留变量 23、`sel(…)` 1；
   另 13 个 `TABLE_LOOKUP`、4 个 `INTERPOLATION`（`FUN_180299d50` 线性查表）、2 个 `STRING_TABLE`
   （`FUN_180276de0` 字符串键常量）、13 个 `FE_OP`、3 个 `EXTERNAL_CALL` 待定性。
3. 新发现模式：部分节点参数不经 `look_string`，而经代理函数 `FUN_180251270(local_48,&local_68)` 取，
   导致参名绑不上（`GetAVmax`/`GetAmax` 等）→ 下一轮先反编译该代理函数。
4. `ARITH` 95 个里仍有 9 个抽不出步骤（数学在被调函数里）。
4. 283 个非算术节点只有类别标签，逐节点"做了什么"的自然语言说明还没写（A 路线的文字面）。
5. 抽取只给算术结构；**单位、规范依据、物理含义仍为未知**，不得由结构反推语义。

### 10.4 下一条命令

```bash
GHIDRA_INSTALL_DIR=$HOME/Tools/ghidra_12.1.4_PUBLIC python3 scripts/decompile-helpers.py  # 幂等
python3 scripts/extract-node-expr.py    # -> nodes-expr.md + raw/nodes-expr.json
python3 scripts/classify-node-kind.py   # -> node-kinds.md + raw/node-kinds.json
python3 scripts/node-residual.py        # -> nodes-residual.md（36 条待办）
python3 scripts/helper-tables.py        # -> helper-tables.md
python3 scripts/node-describe.py        # -> node-descriptions.md
```

续跑优先级：① 内联 7 个 ARITH 辅助函数并把 `f[addr](…)` 替换成算式；② `PARTIAL` 39 → 逐个收尾；
③ 283 个非算术节点逐类写"做了什么"。

---

## 11. L7 数据层与公式链（2026-10-19 一大轮，交接）

### 11.1 这一轮做成了什么

| 主题 | 结果 | 产物 |
| --- | --- | --- |
| 数据层可读性 | `XWallTem.mdf`+`_log.ldf` 复制件 attach 成功，56 表 | `db-access.md` |
| 数据全量导出 | 3 个 `HWKCOPY_*` 库 = **85 表 / 207,105 行**（列名/类型/行数/前 3 行） | `raw/db/*.json`、`db-dump.md` |
| 公式取回 | `计算模板` **2082 条**，`CONTEXT`(varbinary) 按 **GBK** 解码 | `raw/db/formulas-raw.json` |
| 公式↔注册名 | 250 个函数占位中 **81** 命中 379 个 CXMap 注册名；5285 个符号 **0** 个是注册名 | `formula-bindings.md` |
| 符号→列 | 高置信 `exact` **28**、族内短名命中 **88 族**、`none` 4329 | `formula-symbol-map.md`、`formula-family-tables.md` |
| 节点常量 | 26 个节点解出常量表（含 `GetAlpha`/`GetBgzcal`/`IsBgzTruncHigh`） | `node-constants.md` |
| 风荷载链 | `WLS`/`WLD` 原文 + `α`/`I10`/`Kk` 反编译双源印证；βgz 新旧两种形式都已实现 | `formula-chains.md` §1–§12 |
| 玻璃自重链 | `WWEIGHT` 原文 + DB ρ=25.6，三分支实现 | 同上 §10 |
| 回归断言 | 7 项（玻璃 3 + 风荷载 2 + `CalGlassDisp` 逐字 2），全绿 | `replica/scripts/test-calc-chains.py` |

### 11.2 当前数字

- 节点算式：`EXPR` 51、`SELECTED` 1、`TABLE_LOOKUP` 15、`INTERPOLATION` 4、`STRING_TABLE` 3、
  `TABLE_BUILDER` 2、`VARARG_GET` 1、`FE_OP` 12、`PARTIAL` 31、`NO_ARITH` 259（合计 379）
- 辅助函数分类：`COEF_TABLE` 7、`VARARG_GET` 5、`OTHER` 6、`ARITH` 4、`NODE_CTOR` 4、
  `STRING_TABLE` 3、`TABLE_BUILDER` 3、`GLOBAL_GETTER` 1、`INTERPOLATE` 1、`RNG` 1（合计 35）
- 计算链常量：`α`=0.12/0.16/0.22/0.30、`I10`=0.12/0.14/0.23/0.39、`Kk`=0.92/0.89/0.85/0.80

### 11.3 阻塞

1. **测试机 `8.149.129.78` 不可达**：`ping` 100% 丢包、22 端口 refused → L8 数值对照无法进行。
   恢复后先只读刷新进程/页面状态，**不假定 XWall 仍在运行**（上次 pid 157264 / `d.cwx`）。
2. **小表只有 3 行样本**：`常用材料特性表`(18)、`抗滑移系数`(21)、`塑性发展系数表`(14)、
   `风压数据`(767) 需要全量导出才能接进计算器 —— 也要机器。
3. `GLOB_g`（峰值因子）在 85 张表里没有对应列，来源待查。
4. `μz` 的 `μh/α2` 值仍是"推得"（原文只说"查表或公式二选一"）。

### 11.4 下一条命令（机器可用时）

```bash
# 1) 全量导出小表（复用 dump-db 的查询口径，只 SELECT）
python3 scripts/dump-db.py HWKCOPY_XWallTem      # 已含 56 表结构与样本
# 2) 用《计算模板》对照一次原版读数（新增脚本未写，按 formula-chains.md §4 步骤）
# 3) 回归断言（任何改动后必跑）
python3 replica/scripts/test-calc-chains.py
```

### 11.5 纪律记录（这一轮踩过的坑）

1. 我给抽取器加"括号整理"，把 `CalGlassDisp` 的运算符分组改坏 → 靠逐字断言发现并回滚；
2. 写测试时按空格切列，把标签里的数字当数值 → 2 项假失败，改为从行尾倒取；
3. 一度把 `fun_180255170` 的 `1.65/1.78` 当 μh 候选，后来证明是**钳制上下界**；
4. 一度按"参数名=注册名"去绑公式符号，实测 0 命中，改为"函数=节点、符号=数据"。

→ 共同教训：**每个机械结论都要有一个能证伪的对照**（已知算式、行尾数值、原文出处）。

### 11.6 机器恢复与 GUI 环境重建（2026-10-19 夜）

| 步骤 | 结果 |
| --- | --- |
| 重启后控制台会话 | 原本是 `s4test`（该本地账户已不存在）→ 计划任务（Administrator/Interactive）**无法运行**，XWall 起不来 |
| 处置 | 用户确认该 ECS 为专用测试机；在远端**生成新口令**写 `C:\hwk-modern\.pw-rotated`（不回显），`Set-LocalUser` 轮换 Administrator，并配置 `Winlogon\AutoAdminLogon=1` + 重启 |
| 现状 | 控制台 session 1 = **Administrator**（explorer 在 session 1），XWall **pid 4568** 已用 `a.cwx` 启动，标题 `[a.cwx]`，UI 文本可读（`RICHEDIT50W` TextPattern 正常） |

排障记录（避免下轮重复踩）：

1. `ping` 100% 丢包**不代表**机器不可达（阿里云安全组默认禁 ICMP），应以 TCP 22 为准；
2. 计划任务 `-LogonType Interactive` 要求该用户**有交互会话**，否则 `LastTaskResult=267011`（从未运行）；
3. 自建探针若用 `$args[0]` 当输出文件名，调度器必须传参，否则写出的文件名是 `.json`（本轮踩过一次）；
4. `sed` 把 `-or $p.SessionId -ne 4` 替换成 `-or false` 会语法错（应为 `$false` 或整段删除）。

下一步（GUI 已就绪）：导航「工程控制 → 强度计算信息 → 荷载计算」，读出 B 区 80 m 的 `μz/βgz/Wk`，
与 `calc-wind.py` 的两个候选（`α2=2α` → Wk 1.315；`α2=α` → 0.959）对照。

---

## 12. 本轮结束状态（2026-10-19 夜，供新会话直接接手）

### 12.1 一句话

数据层与公式侧已打通到"可执行"门槛，两条计算链有断言保护；**环境已恢复**（控制台 Administrator、XWall 运行中），
只剩 L8 一次读数把 `μz` 的最后一个"推得"消掉。

### 12.2 机器现状（重启后已重建）

| 项 | 值 |
| --- | --- |
| 控制台会话 | session 1 = **Administrator**（`AutoAdminLogon=1`，重启后自动登录） |
| XWall | **pid 4568**，`C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe`，文档 `a.cwx` |
| 口令 | 已轮换；**新口令只在远端** `C:\hwk-modern\.pw-rotated`（本机 `.hwk_ecs_admin_pw` 仍是旧值，勿用） |
| 计划任务 | `HWKModern-20261019-CWX`（Administrator/Interactive）——需要交互会话，现已可用 |
| SSH | 正常（`ping` 不通属正常，安全组禁 ICMP，以 TCP 22 为准） |

### 12.3 已完成（本轮累计，均可复核）

| 领域 | 内容 | 关键产物 |
| --- | --- | --- |
| L5 节点 | 379/379 反编译 + 分类；`EXPR` 51、`TABLE_LOOKUP` 15、`INTERPOLATION` 4、`STRING_TABLE` 3、`TABLE_BUILDER` 2、`VARARG_GET` 1、`FE_OP` 12、`PARTIAL` 31、`NO_ARITH` 259 | `nodes-expr.md`、`node-kinds.md`、`node-descriptions.md`、`nodes-residual.md` |
| 节点常量 | 26 个节点解出常量表（`GetAlpha`/`GetBgzcal`/`IsBgzTruncHigh`…） | `node-constants.md` |
| L7 数据 | 85 表 / 207,105 行结构 + 11 张参数表全量 1065 行 | `raw/db/*.json`、`db-dump.md`、`db-access.md` |
| 公式 | `计算模板` 2082 条（GBK）；250 个函数里 81 命中注册名；5285 符号分族/映射 | `formula-bindings.md`、`formula-symbol-map.md`、`formula-family-tables.md` |
| `.cwx` | 记录头/字符串编码/3 个字段偏移 + **参数绑定表格式**（`HWKInfoRelation*`） | `cwx-field-widths.md`、`scripts/parse-info-relation.py` |
| 计算链 | 风荷载 `WLS/WLD`（α=0.12/0.16/0.22/0.30、I10=0.12/0.14/0.23/0.39、Kk=0.92/0.89/0.85/0.80）；玻璃自重 `WWEIGHT` | `replica/scripts/calc-wind.py`、`calc-glass-weight.py` |
| 回归 | 7 条断言全绿 | `replica/scripts/test-calc-chains.py` |

### 12.4 下一条命令 / 下一动作

```bash
# 1) 先确认环境还在（不要盲目重跑，避免并发启动）
ssh -i ~/.ssh/hwk-win-test Administrator@8.149.129.78 "powershell -NoProfile -Command "Get-Process XWall | Select Id,SessionId,MainWindowTitle""

# 2) 读原版数值：导航「工程控制 → 强度计算信息 → 荷载计算」，取 B 区 80m 的 μz / βgz / Wk
#    对照：α2=2α → μz≈1.945, Wk≈1.315 ｜ α2=α → μz≈1.395, Wk≈0.959

# 3) 任何改动后必跑
python3 replica/scripts/test-calc-chains.py
```

### 12.5 已知未闭合

1. `μz` 的 `μh/α2`（原文只写"查表或公式二选一"）——等步骤 2 的读数；
2. `GLOB_g`（峰值因子）在 85 表里无对应列，来源未定（`calc-wind.py` 里 `g=2.5` 为候选）；
3. `PARTIAL` 31 条（`nodes-residual.md` 逐条列了未绑定符号与赋值来源）；
4. 259 个 `NO_ARITH` 节点只有结构描述，业务语义仍需规范/原版对照。

### 12.6 本轮踩过的坑（别再踩）

1. `ping` 不通 ≠ 机器不可达（安全组禁 ICMP）；
2. `-LogonType Interactive` 的计划任务要求该用户有交互会话，否则 `LastTaskResult=267011`；
3. 自建探针用 `$args[0]` 作输出名时，调度器必须传参，否则写出 `.json`；
4. `sed` 把 `-or $p.SessionId -ne 4` 换成 `-or false` 会语法错（要 `$false` 或整段删）；
5. 给抽取器加"括号整理"会改坏 `CalGlassDisp` 的运算符分组——已有断言护住。

---

## 13. 增量 · 2026-10-20：查表节点（η / μ / m）全部解出

`FUN_1802a0fa0`（`GetSDr`，挠度系数 μ）与 `FUN_1802a2940`（`GetSMr`，弯矩系数 m）不再是黑箱：

- 语义：读 `$0..$3` → 归一化边长比 → 按 `$2`（材料代码）/`$3`（支承代码）选一对内嵌轴表 →
  `FUN_180299d50(ratio, xAxis, yAxis)`；少数分支直接返回常数。23 条分支逐条转录。
- 数据：两个节点引用的 **38 个去重轴地址全部**解成 `[double count][count × double]`，count ∈ {11,13,15,16}。
- 锚点：μ=0.00406、m=0.0442 @ a/b=1（原版计算书自印），η 三处（0.998228 / 0.992846 / 0.997133）。
- 结果：玻璃强度模块外片应力 `6.726054` 由 m→θ1→η1→σ1 整链复算，差 9.8e-8；两个模块 5 项判定全闭合。

文档 `coefficient-tables.md`（分支/轴表/代码语义边界）、`lookup-tables.md` §3–§5（η）；
脚本 `extract-coefficient-tables.py`、`extract-lookup-table.py`；复算 `check-module-numeric.py`（16 步全绿）。

仍缺：`GetSMr` 的 `$3∈{20,25,30}` 细分表无打印锚点（需石材/铝板样例计算书）；`.cwx` 字段语义（B11）。

## 14. 增量 · 2026-10-20：`.cwx` 字段顺序解出（`Serialize` 链 + 字节对齐）

- 脚本 `scripts/build-serialize-chains.py`：按"字段写顺序 + 基类调用位置 + 版本门"叠加出记录内有序字段表；
  412 个 `Serialize`、13 个根；`this` 寄存器按函数检测，`+0xc` 是类版本标记（专用槽 `0x18034f288`）不进字段表。
- 对齐：`HWKWallContext` 按链走 `b.cwx` 载荷，3 个差分锚点全中且读值正确——`+0x14` 雪压 0.4(对象`+0x98`)、
  `+0x1c` 工程名称(对象`+0xa0`)、`+0x56` 风压 0.45(对象`+0x110`)；另有"北京市"(城市 `+0xe0`)、"ⅡA"(粗糙度类别候选 `+0x140`)。
- 仍缺：`u32 A` 语义（记录边界）、聚合槽位细分（String/vector/嵌套对象）、其余 411 类逐一对齐、字段语义（5/N）。

