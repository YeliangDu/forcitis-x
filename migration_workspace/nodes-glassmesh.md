# 节点 eval 摘要 — glassmesh

- 命中节点：14；成功：14；失败：0
- 提取规则：参名取 `look_string` 之前的字符串字面量；常量与表达式行按字面匹配，未做语义推断。

| 节点 | eval | 参数名 | 数值常量 |
| --- | --- | --- | --- |
| `GetDSlopeShapeRatio` | `0x18026d310` | `rtype`, `H`, `D`, `angle`, `FM`, `DM` | `0.0`, `0.01333333333333333`, `0.013333333333333334`, `0.019999999999999997`, `0.02`, `0.030000000000000006` |
| `GetDSlopeShapeRatioRegionText` | `0x18026e5d0` | `rtype` | — |
| `GetGlassDesc` | `0x18029c6e0` | `xdata`, `wo`, `wm`, `wi` | `1191.0`, `200`, `3.0` |
| `GetGlassLayerDesc` | `0x1802be560` | `$0` | `200` |
| `GetGlassLayerThickness` | `0x1802beb70` | `$0` | `0.0` |
| `GetGlassName` | `0x18025a110` | `ta` | `3.0` |
| `GetGlassRatioMat` | `0x18025a580` | `ta`, `prefix` | `0.0`, `1.0`, `1.1`, `200`, `3.0` |
| `GetGlassThickMat` | `0x18025af20` | `ta`, `prefix` | `200` |
| `GetGlassThickMatT` | `0x18025b5a0` | `ta` | — |
| `GetGlassXDesc` | `0x18029ef70` | `xo`, `xm`, `xi`, `wm`, `nm`, `ish` | `0.99999`, `1.00001`, `1.99999`, `1191.0`, `2.00001`, `2.99999` |
| `GetLayoutCenter` | `0x18002fe20` | `$0` | `0.0`, `289.0` |
| `GetLayoutRR` | `0x180031a00` | `$0` | `189.0` |
| `GetLayoutRRzox` | `0x180031de0` | `$0` | — |
| `GetLayoutS2` | `0x180032160` | `$0`, `$1` | `189.0` |

### `GetDSlopeShapeRatio` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar18;
v = (**(code **)(*plVar6 + 0x20))();
v = *(longlong *)pCVar18;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar18;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar18;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar18;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar18;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
```

### `GetDSlopeShapeRatioRegionText` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar5;
v = (**(code **)(*plVar3 + 0x20))(plVar3);
v = (**(code **)(*plVar3 + 0xa8))(plVar3);
```

### `GetGlassDesc` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar11 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar10 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = (**(code **)(*plVar12 + 0xa8))(plVar12);
v = *(double *)(lVar13 + 8);
v = (**(code **)(*plVar12 + 0xa8))(plVar12);
v = *(double *)(lVar13 + 8);
```

### `GetGlassLayerDesc` 赋值表达式（原文，未化简）

```c
v = *plVar7;
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *plVar7;
v = (int)pCVar6 + 1;
v = *(longlong *)pCVar6;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
```

### `GetGlassLayerThickness` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = dVar3 + *(double *)(lVar9 + 8);
v = (int)pCVar10 + 1;
v = *(longlong *)pCVar11;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
```

### `GetGlassName` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar7;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar9 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar9 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar9 + 8);
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
```

### `GetGlassRatioMat` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = (**(code **)(*plVar11 + 0xa8))(plVar11);
v = *(double *)(lVar12 + 8);
v = (**(code **)(*plVar11 + 0xa8))(plVar11);
v = *(double *)(lVar12 + 8);
v = (**(code **)(*plVar11 + 0xa8))(plVar11);
v = *(double *)(lVar12 + 8);
v = (**(code **)(*plVar11 + 0xa8))(plVar11);
v = *(double *)(lVar12 + 8);
```

### `GetGlassThickMat` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(undefined8 *)(lVar8 + 8);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(double *)(lVar8 + 8);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = (undefined4)*(undefined8 *)(lVar8 + 8);
v = (undefined4)((ulonglong)*(undefined8 *)(lVar8 + 8) >> 0x20);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
```

### `GetGlassThickMatT` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(undefined8 *)(lVar8 + 8);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(double *)(lVar8 + 8);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = (undefined4)*(undefined8 *)(lVar8 + 8);
v = (undefined4)((ulonglong)*(undefined8 *)(lVar8 + 8) >> 0x20);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(undefined8 *)(lVar8 + 8);
v = (**(code **)(*plVar5 + 0xa8))(plVar5);
```

### `GetGlassXDesc` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar14;
v = (**(code **)(*(longlong *)local_200 + 0x20))();
v = *(longlong *)pCVar14;
v = (**(code **)(*(longlong *)local_210 + 0x20))();
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
```

### `GetLayoutCenter` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar12 + 0xa8))(plVar12);
v = (double)iVar20 * dVar3;
```

### `GetLayoutRR` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(undefined8 *)(lVar11 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(undefined8 *)(lVar11 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(double *)(lVar11 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(double *)(lVar11 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(undefined8 *)(lVar11 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(undefined8 *)(lVar11 + 8);
```

### `GetLayoutRRzox` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(undefined8 *)(lVar10 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(undefined8 *)(lVar10 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar10 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar10 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(undefined8 *)(lVar10 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(undefined8 *)(lVar10 + 8);
```

### `GetLayoutS2` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(double *)(lVar10 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(double *)(lVar10 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(double *)(lVar10 + 8);
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(double *)(lVar10 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = (double)((int)dVar2 + -1) * dVar15;
v = (double)((int)dVar1 + -1) * dVar3;
v = *(longlong *)pCVar11;
```
