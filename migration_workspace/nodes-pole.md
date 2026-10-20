# 节点 eval 摘要 — pole

- 命中节点：22；成功：22；失败：0
- 提取规则：参名取 `look_string` 之前的字符串字面量；常量与表达式行按字面匹配，未做语义推断。

| 节点 | eval | 参数名 | 数值常量 |
| --- | --- | --- | --- |
| `CheckPoleIsSimpleSup` | `0x1801a3800` | `poleinfo` | `0.0`, `1.0`, `200` |
| `FEDoArchPole` | `0x1800e2910` | `hand`, `sec`, `loads`, `poleinfo` | `145.0`, `200` |
| `FEDoCPole` | `0x1801441a0` | `hand`, `model`, `loads`, `drawsize`, `polepos` | `545.0` |
| `FEDoGrilleVPole` | `0x180160c20` | `hand`, `sec`, `loads`, `poleinfo` | `1000` |
| `FEDoGrilleVPoleDraw` | `0x1801614a0` | `hand`, `sec`, `loads`, `poleinfo`, `drawbz`, `drawsize`, `ratio` | `100`, `100.0`, `1000`, `2000` |
| `FEDoLGAPole` | `0x18016c800` | `hand`, `sec1`, `sec2`, `pos`, `loads`, `poleinfo`, `polepos` | `1e-05`, `245.0` |
| `FEDoPXTPole` | `0x1801b3480` | `hand`, `sec`, `loads`, `poleinfo`, `polepos` | `445.0` |
| `FEDoPole` | `0x1801a3bb0` | `hand`, `sec`, `loads`, `poleinfo`, `polepos` | `1000`, `545.0` |
| `FEDoVOLGPole` | `0x1801e3aa0` | `hand`, `sec`, `sec2`, `loads`, `height`, `poleinfo`, `polepos` | `1e-05`, `245.0` |
| `FEDoVPXTPole` | `0x1801f6ef0` | `hand`, `sec`, `loads`, `poleinfo`, `polepos` | `245.0` |
| `FEDoXTPole` | `0x180203e20` | `hand`, `sec`, `loads`, `polelength` | `0.001`, `345.0` |
| `FELGAPoleDraw` | `0x18016d240` | `hand`, `sec1`, `sec2`, `loads`, `pos`, `beaminfo`, `drawbz`, `drawsize`, `prefix` | `100.0`, `189.0` |
| `FEPXTPoleDraw` | `0x1801b3d00` | `hand`, `sec`, `loads`, `beaminfo`, `drawbz`, `drawsize` | `100.0`, `189.0` |
| `FEPoleDraw` | `0x1801a45a0` | `hand`, `sec`, `loads`, `poleinfo`, `drawbz`, `drawsize`, `ratio` | `100`, `100.0`, `1000`, `199`, `200`, `2000` |
| `FEVOLGPoleDraw` | `0x1801e44b0` | `hand`, `sec`, `sec2`, `loads`, `height`, `beaminfo`, `drawbz`, `drawsize`, `prefix` | `100`, `100.0`, `189.0`, `199`, `200`, `299` |
| `FEVPXTPoleDraw` | `0x1801f7720` | `hand`, `sec`, `loads`, `beaminfo`, `drawbz`, `drawsize` | `100`, `100.0`, `189.0` |
| `FEXTPoleDraw` | `0x180204630` | `hand`, `sec`, `loads`, `poleinfo`, `drawbz`, `drawsize`, `ratio` | `100.0`, `389.0` |
| `GetCPoleReaction` | `0x180144b90` | `hand`, `model`, `loads`, `nodeindex` | — |
| `GetPoleCalcStab` | `0x1801a58e0` | `poleinfo` | `0.0`, `1.0`, `10000.0`, `145.0`, `1e-05`, `200` |
| `GetPoleDflim` | `0x1802872c0` | `$0`, `$1`, `$2` | `0.002`, `0.004`, `0.0044444444444444444`, `0.005555555555555556`, `0.006666666666666667`, `0.008333333333333333` |
| `GetPoleDfnum` | `0x180287a50` | `$0`, `$1`, `$2` | `0.8999999999999999`, `15.0`, `180.0`, `200`, `225.0`, `250.0` |
| `GetPoleLambda` | `0x180288130` | `L`, `Ix`, `Iy`, `A`, `Mat`, `sectype` | `0.152`, `0.215`, `0.3`, `0.302`, `0.41`, `0.432` |

### `CheckPoleIsSimpleSup` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
```

### `FEDoArchPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar15;
v = (**(code **)(*(longlong *)local_108 + 0x20))();
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = (uint)*(double *)(lVar12 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
```

### `FEDoCPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(double *)(lVar13 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = (uint)*(double *)(lVar13 + 8);
v = (**(code **)(*(longlong *)local_108 + 0xa8))();
v = (**(code **)(*plVar11 + 0xb8))(plVar11);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
```

### `FEDoGrilleVPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar13;
v = (**(code **)(*local_d8 + 0x20))();
v = *(longlong *)pCVar18;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar18;
```

### `FEDoGrilleVPoleDraw` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar7 + 0xa8))();
v = (**(code **)(*plVar11 + 0xa8))();
v = (**(code **)(*plVar7 + 0xa8))();
v = (uint)*(double *)(lVar14 + 8);
v = (**(code **)(*plVar13 + 0xa8))();
v = (undefined4)*(undefined8 *)(lVar14 + 8);
v = (uint)((ulonglong)*(undefined8 *)(lVar14 + 8) >> 0x20);
v = *(undefined4 *)g_uPaperSize_exref;
v = (**(code **)(*plVar12 + 0xa8))();
v = *(longlong *)pCVar19;
v = (**(code **)(*plVar7 + 0x20))();
v = *(longlong *)pCVar19;
```

### `FEDoLGAPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*local_120 + 0xa8))();
v = *(longlong *)local_130;
v = (**(code **)(*local_120 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar17;
v = (**(code **)(*local_b0 + 0x20))();
v = *(longlong *)pCVar17;
```

### `FEDoPXTPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(longlong *)pCVar16;
v = (**(code **)(*local_b8 + 0x20))();
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
v = *(longlong *)pCVar16;
v = (**(code **)(*(longlong *)local_118 + 0x20))();
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
```

### `FEDoPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)local_138;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)local_138;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)local_138;
v = (**(code **)(*local_110 + 0x20))();
v = *(longlong *)local_138;
v = (**(code **)(*local_108 + 0x20))();
v = *(longlong *)pCVar18;
```

### `FEDoVOLGPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*local_120 + 0xa8))();
v = *(longlong *)local_130;
v = (**(code **)(*local_120 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar17;
v = (**(code **)(*local_b0 + 0x20))();
v = *(longlong *)pCVar17;
```

### `FEDoVPXTPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(longlong *)pCVar16;
v = (**(code **)(*local_b0 + 0x20))();
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
v = *(longlong *)pCVar16;
v = (**(code **)(*(longlong *)local_110 + 0x20))();
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
```

### `FEDoXTPole` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(longlong *)local_f8;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = (uint)*(double *)(lVar12 + 8);
v = (**(code **)(*plVar11 + 0xa8))(plVar11);
```

### `FELGAPoleDraw` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*local_130 + 0xa8))();
v = *(longlong *)pCVar13;
v = (**(code **)(*local_130 + 0x20))();
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar13;
v = (**(code **)(*(longlong *)pSVar9 + 0x20))(pSVar9);
v = *(longlong *)pCVar13;
v = (**(code **)(*local_138 + 0x20))();
v = *(longlong *)pCVar13;
```

### `FEPXTPoleDraw` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = *(longlong *)pCVar5;
v = (**(code **)(*local_138 + 0x20))();
v = *(longlong *)pCVar5;
v = (**(code **)(*(longlong *)pcVar7 + 0x20))(pcVar7);
v = *(longlong *)pCVar5;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar5;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar5;
v = (**(code **)(*local_e0 + 0x20))();
v = *(longlong *)pCVar5;
```

### `FEPoleDraw` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = (**(code **)(*local_e0 + 0xa8))();
v = (uint)*(double *)(lVar12 + 8);
v = (**(code **)(*(longlong *)local_1e8 + 0xa8))();
v = (undefined4)*(undefined8 *)(lVar12 + 8);
v = (uint)((ulonglong)*(undefined8 *)(lVar12 + 8) >> 0x20);
v = (**(code **)(*local_1d8 + 0xa8))();
v = *(longlong *)pCVar17;
v = (**(code **)(*local_e0 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
```

### `FEVOLGPoleDraw` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*local_170 + 0xa8))();
v = *(longlong *)pCVar16;
v = (**(code **)(*local_170 + 0x20))();
v = *(longlong *)pCVar16;
v = (**(code **)(*(longlong *)pcVar7 + 0x20))(pcVar7);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar16;
v = (**(code **)(*local_188 + 0x20))();
v = *(longlong *)pCVar16;
```

### `FEVPXTPoleDraw` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = *(longlong *)pCVar5;
v = (**(code **)(*local_148 + 0x20))();
v = *(longlong *)pCVar5;
v = (**(code **)(*(longlong *)pcVar7 + 0x20))(pcVar7);
v = *(longlong *)pCVar5;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar5;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar5;
v = (**(code **)(*local_f0 + 0x20))();
v = *(longlong *)pCVar5;
```

### `FEXTPoleDraw` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*(longlong *)pCVar6 + 0xa8))(pCVar6);
v = *(longlong *)pCVar12;
v = (**(code **)(*(longlong *)local_a0 + 0x20))();
v = *(longlong *)pCVar12;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar12;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar12;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar12;
v = (**(code **)(*local_128 + 0x20))();
v = *(longlong *)pCVar12;
```

### `GetCPoleReaction` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(double *)(lVar11 + 8);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = (uint)*(double *)(lVar11 + 8);
v = (**(code **)(*plVar9 + 0xb8))(plVar9);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar17;
```

### `GetPoleCalcStab` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar12;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = -10000.0;
v = *(double *)(local_310 + (longlong)pCVar10 * 8);
```

### `GetPoleDflim` 赋值表达式（原文，未化简）

```c
v = 1.0 / dVar17;
v = *(longlong *)pCVar9;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar9;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar11 + 8);
v = 1.0 / (((dVar17 - 3.6) * 45.0) / 0.8999999999999999 + 180.0);
v = *(longlong *)pCVar9;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar9;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
```

### `GetPoleDfnum` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar12 + 8);
v = ((dVar1 - 3.6) * 45.0) / 0.8999999999999999 + 180.0;
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar14;
```

### `GetPoleLambda` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar13;
v = (**(code **)(*local_a0 + 0x20))();
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar13;
v = (**(code **)(*(longlong *)local_a8 + 0x20))();
```
