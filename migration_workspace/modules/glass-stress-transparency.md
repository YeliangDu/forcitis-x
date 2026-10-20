# 玻璃面板强度（跨中应力）模块：打透结果（2026-10-20）

对象：**玻璃面板强度/跨中应力**（`WSTRENGTH` 族，规范 JGJ102-2003 6.1.2-1 / 8.1.5-1 查表、6.1.2-2 折减）。

| # | 判定项 | 状态 | 关键证据 |
| --- | --- | --- | --- |
| ① | 调用关系 | **部分** | 模板调用面穷举（1,937 命中 / 0 形参不一致）；`CalGlassStress`/`CalGlassPSStress` 模板调用 **0** 次 |
| ② | 算式与对应 | **闭合** | 模板算术逐字 + 节点算式 `sw×qw×aw⁴…` 族，见 §2 |
| ③ | 输入来源与查表 | **闭合** | 101 个输入符号归类；`GetSMr` 为代码内嵌分段表，非 DB；轴表与分支映射已解出（`coefficient-tables.md`、`lookup-tables.md`） |
| ④ | 分支与异常 | **闭合** | 849 个条件块，含 PRJGLASS/LINKNUM 双维度切换 |
| ⑤ | 中间量 + 数值一致 | **闭合** | q1/q2/qk1/qk2、θ1/θ2、η1/η2、σ1/σ2 全链复现；σ1=6.726054 差 9.8e-8（η、m 均来自解出的表） |

复现命令：

```text
python3 scripts/build-module-transparency.py --slug glass-stress \
  --title "玻璃面板强度（跨中应力）" --pattern '^(MG_)?WSTRENGTH[A-Z]*$' \
  --watch 'CalGlassStress,CalGlassPSStress'
python3 scripts/check-module-numeric.py glass-stress
```

生成物：`migration_workspace/modules/glass-stress.md` / `.json`。
同一脚本已用同一口径重跑玻璃跨中挠度（`modules/glass-disp.*`，25 条模板 / 555 调用 / 434 命中 / 0 不一致，与首轮完全一致），证明流水线可复用。

## 1. 调用关系（①，部分）

- **32 条模板**，**2,532 处节点调用**：命中 379 注册名 **1,937**（形参一致 1,809、可变参数节点 128、**真正不一致 0**）。
- 实际被调用的节点是取值/查表类，核心是 `GetSMr(al, bl, PRJGLASS, LINKNUM)`——玻璃板面跨中弯曲系数，**按 PRJGLASS 与 LINKNUM 双维度选规范表**（6.1.2-1 / 8.1.5-1）。
- 算量节点 `CalGlassStress`、`CalGlassPSStress` 在 2,079 条模板中 **0** 次调用；379 个注册节点里 293 个从未被模板调用（与挠度模块同一结论）。
- 模板里出现的 10 个名字不是节点而是模板函数：`IsEqual`、`IsNEqual`、`Mul`、`GetMin`、`GetMax`、`LAnd`、`LNot`、`IsLarge`、`IsNLess`、`Div`。

## 2. 算式（②，闭合）

```text
选定面板材料:${GLASSDESC}
判据: σ ≤ fg[wo]
q  = 组合荷载(设计值)  = ${IsLPeak:*W+ψE×qEA}${IsLPeak:+γg×GAk×cosα+0.9×(W+S)}
a  = ${IsEqual(PRJGLASS,1):+计算跨度}${IsNEqual(PRJGLASS,1):+短边边长}
m  = GetSMr(al, bl, PRJGLASS, LINKNUM)     查表 6.1.2-1（或 8.1.5-1）
η  = GetNg(θ)                              查表 6.1.2-2
荷载分配(中空):
  q1 = [1.1×] q × t1³/(t1³+t2³)
  q2 =       q × t2³/(t1³+t2³)
应力:
  σ  = 6 × m × q × a² × 1000 / t² × η
```

节点侧同族（`VERIFICATION.md` A6/A9）：`CalGlassStress` 参数 `sw, qw, aw, tw, theta, prefix, def`，常量含 `1000.0 / 6.0`；`CalGlassPSDisp` 另有 `0.5 / 189.0`。

## 3. 输入面（③，闭合）

| 前缀 | 不同符号数 | 说明 |
| --- | --- | --- |
| `other` | 36 | 结构性/环境符号：`Ew`、`GAK`、`GLASSDESC`、`GLASSSTRUCTNAME`、`ISDOUBLEW`、`ISHOLW`、`IsLPeak`、`PRJGLASS`、`LINKNUM`、`FWLESS` 等 |
| `GLSPS_*` | 33 | PS（夹层/点支）玻璃计算信息 |
| `GLS_*` | 32 | 常规/中空玻璃计算信息 |

查表：`GetSMr`（表 6.1.2-1 / 8.1.5-1）与 `GetNg`（表 6.1.2-2）均为**节点内嵌分段表**（边界常量成对出现 `x.99999/x+1.00001`），节点体内无 SQL/记录集标识，不依赖 DB。

## 4. 分支面（④，闭合）

849 个条件块，头部频次前 10：

| 判定 | 次数 | 语义 |
| --- | --- | --- |
| `IsEqual(PRJGLASS,2)` | 108 | 玻璃类型=2（如夹层/中空特定类）时切换文本与公式段 |
| `ISDOUBLEW` | 102 | 是否双层（中空/夹层）→ 输出内外片各自应力 |
| `IsEqual(GLSPS_LINKNUM,4)` | 87 | 四边支承改走 8.1.5 族 |
| `GLS_ti` | 70 | 有内片时输出内片段 |
| `IsEqual(PRJGLASS,0)` | 60 | 门窗类走 6.1.2-1 表 |
| `IsNEqual(PRJGLASS,2)` | 60 | 非该类时输出 a 而非 b |
| `Mul(IsEqual(LINKNUM,6),IsEqual(PRJGLASS,2))` | 48 | 六边支承且特定类型 → 8.1.5-1 |
| `Mul(IsNLess(tm,3),IsNLess(tml,3))` | 48 | 两片都 <3mm 时的 `0.95³×` 组合 |
| `GLSPS_ti` | 48 | PS 版内片 |
| `IsNEqual(PRJGLASS,1)` | 24 | 非"计算跨度"类时输出短边 |

即：**同一模块的规范表与公式段由 `PRJGLASS`（玻璃类型）与 `LINKNUM`（支承边数）两个维度共同编排**，这是本模块最关键的编排事实。

## 5. 数值一致（⑤，部分闭合）

用冻结样例计算书原文（`evidence/stages/B02/B02-02/attempt-47/acceptance/frozen-report-head.txt`，"玻璃强度计算"段）逐项复算：

| 量 | 原版打印 | 复算 | 差 |
| --- | --- | --- | --- |
| q1 = 1.1×q×t1³/(t1³+t2³) | 0.919618 | 0.9196176 | 4.0e-7 |
| q2 = q×t2³/(t1³+t2³) | 0.836016 | 0.836016 | 0 |
| qk1 = 1.1×qk×t1³/(t1³+t2³) | 0.55 | 0.55 | 0 |
| qk2 = qk×t2³/(t1³+t2³) | 0.5 | 0.5 | 0 |
| m = `GetSMr(al,bl,PRJGLASS=0,LINKNUM)` 表 6.1.2-1 | 0.0442 | 0.0442（轴表 a/b=1） | 0 |
| θ1 = qk1×a⁴×10⁹/(E×t1⁴) | 5.894204 | 5.89420439 | 3.9e-7 |
| θ2 | 5.358368 | 5.358367627 | 3.7e-7 |
| η1 = `GetNg(θ1)` 表 6.1.2-2 | 0.992846 | 0.992846365 | 3.7e-7 |
| η2 = `GetNg(θ2)` | 0.997133 | 0.997133059 | 5.9e-8 |
| **σ1** = 6×m×q1×a²×1000/t1²×η1（外片） | **6.726054** | **6.726053902** | **9.8e-8** |
| σ2 = 6×m×q2×a²×1000/t2²×η2（内片） | 6.140995 | 6.140994710 | 2.9e-7 |
| 判据 | 两片均 ≤ fg=28 满足 | 同 | 一致 |

复算不再把 μ/m/η 当输入：m 取自 `GetSMr` 的轴对（`raw/coefficient-tables.json`），
η 取自 `GetNg` 的 η 表（`raw/lookup-tables.json`）——两个提取器的锚点各自先过，再由本表串起来。
外片 6.726054 之所以以前"缺 η1"，是旧记录误判为原文未打印；强度段原文实际打印了 `θ1=5.894204`、
`η1=0.992846`，且两者与 η 表完全自洽。

记录：`evidence/stages/B02/B02-02/attempt-47/acceptance/glass-stress-numeric-check.json`（由 `scripts/check-module-numeric.py` 生成）。

## 6. 仍未闭合

1. **算量节点由谁调用**：同挠度模块，模板不调用；需更大反编译面或实机钩子。
2. **外片应力 η1**：已闭合（θ1/η1 原文有打印且与 η 表自洽，见 §5）；剩余风险只是"原文打印 6 位小数、跨式引用时是否取打印值"，实测取全精度即可复现到 9.8e-8。
3. **中间量落盘格式**（`.cwx` 的 `HWKCalc_*`）：仍未解。

## 7. 口径声明

数字全部来自仓库内可复查文件与两个可重跑脚本；"闭合"指该层能给出可复核的完整清单，不等于原版行为已 100% 还原；数值一致限于本样例、本组参数。
