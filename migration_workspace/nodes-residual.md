# 节点算式收尾清单（L5/A 路线）

- 待收尾节点：30（`PARTIAL` + `SELECTED` + 抽不出步骤的 `ARITH`）
- 含未绑定取值 `p[…]`：5
- 含残留寄存器变量：20

每条给出「未绑定符号 + 它在反编译里的赋值来源」，按来源分类即可收尾。

## `FEAddMat` — TABLE_LOOKUP

表达式：`table[fun_1802798d0](uVar14) + table[fun_1802793c0](uVar14,3) + table[fun_180276eb0](uVar14,3)`

- 残留变量 `uVar14` ← `uVar14 = (**(code **)(*plVar7 + 0x20))(plVar7)`

## `FESetSec` — TABLE_LOOKUP

表达式：`table[fun_1802798d0](uVar17) + table[fun_1802793c0](uVar17,3) + table[fun_180276eb0](uVar17,3)`

- 残留变量 `uVar17` ← `uVar17 = (**(code **)(*plVar4 + 0x20))(plVar4)`

## `FESetSecMat` — TABLE_LOOKUP

表达式：`table[fun_1802798d0](uVar15) + table[fun_1802793c0](uVar15,3) + table[fun_180276eb0](uVar15,3)`

- 残留变量 `uVar15` ← `uVar15 = (**(code **)(*plVar7 + 0x20))(plVar7)`

## `FESetSecN` — TABLE_LOOKUP

表达式：`table[fun_1802798d0](uVar19) + table[fun_1802793c0](uVar19,3) + table[fun_180276eb0](uVar19,3)`

- 残留变量 `uVar19` ← `uVar19 = (**(code **)(*plVar6 + 0x20))(plVar6)`

## `GetACFt` — SELECTED

表达式：`(((H) * (q) * (W) * 0.5) / (((double)sel(H|W) * (q) * 0.5) / (t))) / ((W) + (H))`

- 数据相关选择 `sel(H|W)`（候选顺序 = 条件里 `SUB84` 出现顺序）
  - 条件原文：`if (((1.99999 < dVar5) && (uVar17 = SUB84(dVar2,0), uVar18 = (int)((ulonglong)dVar2 >> 0x20), dVar5 < 2.00001)) || ((-1e-05 < dVar5 && (uVar17 = SUB84(dVar3,0), uVar18 = (int)((ulonglong)dVar3 >> 0x20), dVar5 < 1e-05))))`

## `GetAl` — TABLE_LOOKUP

表达式：`table[fun_180276990](uVar8)`

- 残留变量 `uVar8` ← `uVar8 = (**(code **)(*plVar6 + 0x20))(plVar6)`

## `GetBgz` — TABLE_LOOKUP

表达式：`table[fun_180255170](local_60,*(($1) + 8), *(($2) + 8),1)`

- 残留变量 `local_60` ← `未找到赋值语句`

## `GetBoltAn` — NO_ARITH

表达式：`—`

- 该节点被判定有算术，但数学写在被调函数里（需反编译该函数才能闭合）

## `GetBoltNvb` — TABLE_LOOKUP

表达式：`table[fun_180278990](uVar11,0)`

- 残留变量 `uVar11` ← `uVar11 = (**(code **)(*plVar9 + 200))(plVar9)`

## `GetBoltTForceTable` — TABLE_BUILDER

表达式：`table[fun_18002c040](dVar2)`

- 残留变量 `dVar2` ← `dVar2 = *(double *)(lVar10 + 8)`

## `GetCBoltLayoutRR` — PARTIAL

表达式：`(0.0) + (($0 - ((0.0) / (double)(iVar2))) * (p[plVar14] - ((0.0) / (double)(iVar2))))`

- 未绑定 `plVar14` ← `plVar14 = (longlong *)(**(code **)(*plVar10 + 0xb8))(plVar10)`

## `GetCBoltTForceTable` — TABLE_BUILDER

表达式：`table[fun_180058f10](dVar3)`

- 残留变量 `dVar3` ← `dVar3 = *(double *)(lVar12 + 8)`

## `GetCommonLayoutRRzox` — PARTIAL

表达式：`(0.0) + (($0 - ((0.0) / (double)(iVar2))) * (p[plVar14] - ((0.0) / (double)(iVar2))))`

- 未绑定 `plVar14` ← `plVar14 = (longlong *)(**(code **)(*plVar9 + 0xb8))(plVar9)`

## `GetE` — TABLE_LOOKUP

表达式：`table[fun_180276eb0](uVar7,0) + table[fun_180276eb0](uVar7,*(($1) + 8))`

- 残留变量 `uVar7` ← `uVar7 = (**(code **)(*plVar3 + 200))(plVar3)`

## `GetFt` — TABLE_LOOKUP

表达式：`table[fun_180278990](uVar6,0) + table[fun_180278990](uVar6,*(($1) + 8))`

- 残留变量 `uVar6` ← `uVar6 = (**(code **)(*plVar3 + 200))(plVar3)`

## `GetGlassLayerThickness` — PARTIAL

表达式：`(0.0) + p[plVar8]`

- 未绑定 `plVar8` ← `plVar8 = (longlong *)(**(code **)(*plVar6 + 0x180))(plVar6,pCVar10)`

## `GetGlassRatioMat` — PARTIAL

表达式：`(ta[6]) / (((((((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1)) * 1.1) * 1.1) * (((((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1)) * 1.1) * 1.1) * (((((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1)) * 1.1) * 1.1)) + ((((((dVar22 * 1.1) * 1.1) * ((dVar22 * 1.1) * 1.1) * ((dVar22 * 1.1) * 1.1)) * 1.1) * 1.1) * (((((dVar22 * `

- 残留变量 `dVar21` ← `dVar21 = *(double *)(lVar12 + 8)`
- 残留变量 `dVar22` ← `dVar22 = *(double *)(lVar12 + 8)`

## `GetKuzcal` — TABLE_LOOKUP

表达式：`table[fun_180255450](local_88,*(($1) + 8))`

- 残留变量 `local_88` ← `未找到赋值语句`

## `GetLayoutCenter` — PARTIAL

表达式：`((double)iVar19 * (p[plVar14]) + dVar6 + (p[plVar14])) - (dVar5 - (0.0))`

- 未绑定 `plVar14` ← `plVar14 = (longlong *)(**(code **)(*plVar12 + 0x180))(plVar12,0)`
- 残留变量 `dVar5` ← `dVar5 = 0.0`
- 残留变量 `dVar6` ← `dVar6 = 0.0`

## `GetLayoutS2` — NO_ARITH

表达式：`—`

- 该节点被判定有算术，但数学写在被调函数里（需反编译该函数才能闭合）

## `GetM` — TABLE_LOOKUP

表达式：`table[fun_1802793c0](uVar8,0) + table[fun_1802793c0](uVar8,*(($1) + 8))`

- 残留变量 `uVar8` ← `uVar8 = (**(code **)(*plVar4 + 200))(plVar4)`

## `GetMaxBoltPullForce` — NO_ARITH

表达式：`—`

- 该节点被判定有算术，但数学写在被调函数里（需反编译该函数才能闭合）

## `GetNu` — PARTIAL

表达式：`(pow((pow(p[plVar3],3.0)) * (p[dVar19]) * 0.0001,(double)0.31)) * (double)0.1`

- 未绑定 `dVar19` ← `dVar19 = (double)FUN_1802bc2d0(plVar6)`
- 未绑定 `plVar3` ← `未找到赋值语句`
- 残留变量 `dVar19` ← `dVar19 = (double)FUN_1802bc2d0(plVar6)`

## `GetPoleCalcStab` — NO_ARITH

表达式：`—`

- 该节点被判定有算术，但数学写在被调函数里（需反编译该函数才能闭合）

## `GetPoleLambda` — PARTIAL

表达式：`(((((L * 100.0) / (Ix)) / *(double *)PI_exref) * (table[fun_180277390](local_f8,4))) * ((((L * 100.0) / (Ix)) / *(double *)PI_exref) * (table[fun_180277390](local_f8,4)))) * 0.65`

- 残留变量 `local_f8` ← `未找到赋值语句`

## `GetRMidHollowGlass` — PARTIAL

表达式：`(ta[4]) / (ta[6]) + dVar21 / (ta[6]) + ((dVar21 * 1.1) / (ta[6]) + (ta[4]) / (ta[6]) + ((dVar19 * 1.1) / (ta[6])))`

- 残留变量 `dVar19` ← `dVar19 = dVar3 * dVar3 * dVar3`
- 残留变量 `dVar21` ← `dVar21 = dVar2 * dVar2 * dVar2`

## `GetSABFt` — NO_ARITH

表达式：`—`

- 该节点被判定有算术，但数学写在被调函数里（需反编译该函数才能闭合）

## `GetSCBFt` — NO_ARITH

表达式：`—`

- 该节点被判定有算术，但数学写在被调函数里（需反编译该函数才能闭合）

## `GetTroembS` — PARTIAL

表达式：`(double)(int)((uVar15 ^ uVar13) - uVar13) * S`

- 残留变量 `uVar13` ← `uVar13 = (int)uVar15 >> 0x1f`
- 残留变量 `uVar15` ← `uVar15 = (int)dVar16 - (int)dVar1`

## `GetVr` — TABLE_LOOKUP

表达式：`table[fun_1802798d0](uVar7)`

- 残留变量 `uVar7` ← `uVar7 = (**(code **)(*plVar5 + 200))(plVar5)`

