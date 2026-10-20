# 模块透明化台账

口径见 `migration_workspace/glass-deflection-transparency.md` §0 的 5 项判定：
①调用关系 ②算式与对应 ③输入来源与查表 ④分支与异常 ⑤中间量与数值一致。

每个模块一份生成物（`build-module-transparency.py`）+ 一份透明度结论（`*-transparency.md`）+ 数值复算（`check-module-numeric.py`）。

| 模块 | 模板数 | 调用/命中 | 形参不一致 | 关注节点模板调用 | ① | ② | ③ | ④ | ⑤ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 玻璃跨中挠度 `WDISPLACEMENT*` | 25 | 555 / 434 | 0 | `CalGlassDisp`=0、`CalGlassPSDisp`=0 | 部分 | 闭合 | 闭合 | 闭合 | 闭合（文本侧） |
| 玻璃面板强度 `WSTRENGTH*` | 32 | 2,532 / 1,937 | 0 | `CalGlassStress`=0、`CalGlassPSStress`=0 | 部分 | 闭合 | 闭合 | 闭合 | 闭合 |

共同结论（两模块一致，可作为后续模块的先验假设，仍需逐模块复核）：

1. **模板层不调用算量节点**：379 注册节点中 293 个从未被 2,079 条模板调用；模板把算术写在自己体内。
2. **查表是二进制内嵌分段表**（`GetSDr`/`GetSMr`/`GetNg`），不是 DB 读。`GetSDr`/`GetSMr` 的轴对、
   ratio 变形与“直接返回常数”分支已全部解出（`migration_workspace/coefficient-tables.md`），因此 μ/m 可脱离原版打印值自算。
3. **规范表/公式段由计算信息字段编排**：`PRJGLASS`（玻璃类型）× `LINKNUM`（支承边数）决定走 6.1.x 还是 8.1.5。
4. 模板里的"非节点"名称是模板函数（`IsEqual`/`IsNEqual`/`Mul`/`GetMin`/`LAnd`/`Div` …），不属于 379 注册面。

## 复跑

```text
python3 scripts/build-module-transparency.py --slug glass-disp   --title "玻璃跨中挠度" \
  --pattern '^(MG_)?(WDISPLACEMENT[A-Z]*|GLASSRIBDISP[A-Z]*|GLASSFEDISPMENT[A-Z]*)$' \
  --watch 'CalGlassDisp,CalGlassPSDisp'
python3 scripts/build-module-transparency.py --slug glass-stress --title "玻璃面板强度（跨中应力）" \
  --pattern '^(MG_)?WSTRENGTH[A-Z]*$' --watch 'CalGlassStress,CalGlassPSStress'
python3 scripts/check-module-numeric.py
python3 scripts/test-glass-deflection-map.py
```

## 下一批候选（按共享依赖排序）

1. 玻璃肋 `GLASSRIB*`、`GLASSFE*`（同一 `GLS/GRIB` 输入族，可直接复用）
2. 热工 U 值 `CalcGlassUFactor`（4 个体系，报告文本可作数值锚点）
3. 杆件/立柱 `LINKPOLE_*`、有限元族（`FEAdd*`，需先补 L6）
4. 埋件/焊缝/锚栓（`TROEMB_*`、`WELDNV_*`、`*BOLT_*`）
