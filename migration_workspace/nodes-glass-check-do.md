# 节点 eval 摘要 — glass-check-do

- 命中节点：17；成功：17；失败：0
- 提取规则：参名取 `look_string` 之前的字符串字面量；常量与表达式行按字面匹配，未做语义推断。

| 节点 | eval | 参数名 | 数值常量 |
| --- | --- | --- | --- |
| `CalGlassDisp` | `0x1803081c0` | `ms`, `qwk`, `aw`, `dw`, `theta`, `prefix`, `def` | `1000000000.0`, `200`, `4.0`, `89.0` |
| `CalGlassPSDisp` | `0x1803087b0` | `ms`, `qwk`, `aw`, `dw`, `theta`, `num`, `prefix`, `def` | `0.5`, `1000000000.0`, `189.0`, `200`, `4.0` |
| `CalGlassPSStress` | `0x180308f90` | `sw`, `qw`, `aw`, `tw`, `num`, `theta`, `prefix`, `def` | `0.25`, `1000.0`, `189.0`, `200`, `6.0` |
| `CalGlassStress` | `0x1803097c0` | `sw`, `qw`, `aw`, `tw`, `theta`, `prefix`, `def` | `1000.0`, `189.0`, `200`, `6.0` |
| `CalcGlassShadeCoef` | `0x1800419d0` | `handle`, `calcinfo`, `calrad`, `layids`, `thicks`, `gopparam` | `0.0`, `289.0` |
| `CalcGlassUFactor` | `0x180042070` | `handle`, `calcinfo`, `calrad`, `layids`, `thicks`, `gopparam` | `0.0`, `289.0` |
| `CheckHasHollowBeforeLayer` | `0x180256800` | `ta`, `layer` | `3.0` |
| `CheckPoleIsSimpleSup` | `0x1801a3800` | `poleinfo` | `0.0`, `1.0`, `200` |
| `DoCalcAwning3d` | `0x1800210f0` | `hand`, `loads`, `GAK`, `model`, `drawsize`, `material`, `bz` | `100`, `46.0` |
| `DoCalcClayPlate3d` | `0x180054a00` | `hand`, `loads`, `model`, `drawsize`, `material`, `bz` | `100`, `200`, `46.0` |
| `DoCalcRailing3d` | `0x180305d70` | `hand`, `loads`, `model`, `drawsize`, `hmaterial`, `vmaterial`, `bz` | `100`, `200`, `46.0` |
| `DoCalcShell` | `0x180249bc0` | `hand`, `thickinfo`, `shellinfo`, `bz` | `100`, `136`, `200`, `46.0` |
| `DoDrawVSec` | `0x180061760` | `secdata`, `bz` | `334.0` |
| `DoGetAwning3dReaction` | `0x180021960` | `hand`, `loads`, `GAK`, `model`, `gkindex`, `material`, `nodeindex` | `100` |
| `DoGetAwning3dReactionInfo` | `0x180022010` | `hand`, `loads`, `GAK`, `model`, `material` | `100` |
| `DoGetAwning3dReactionMatrix` | `0x180022590` | `hand`, `loads`, `GAK`, `model`, `material` | `100` |
| `GetRGlass` | `0x18025ec40` | `ta`, `prefix` | `0.0`, `1.0`, `1.1`, `200`, `3.0` |

### `CalGlassDisp` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar15;
v = (**(code **)(*local_108 + 0x20))();
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar4 + 0x20))(plVar4);
v = *(longlong *)pCVar15;
v = (**(code **)(*(longlong *)local_100 + 0x20))();
v = *(longlong *)pCVar15;
v = (**(code **)(*(longlong *)pcVar6 + 0x20))(pcVar6);
v = *(longlong *)pCVar15;
v = (**(code **)(*local_b0 + 0x20))();
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
```

### `CalGlassPSDisp` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar17;
v = (**(code **)(*local_128 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = *(longlong *)pCVar17;
v = (**(code **)(*(longlong *)pcVar6 + 0x20))(pcVar6);
v = *(longlong *)pCVar17;
v = (**(code **)(*local_b8 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*local_120 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*(longlong *)local_130 + 0x20))();
```

### `CalGlassPSStress` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar21;
v = (**(code **)(*local_128 + 0x20))();
v = *(longlong *)pCVar21;
v = (**(code **)(*local_90 + 0x20))();
v = *(longlong *)pCVar21;
v = (**(code **)(*(longlong *)local_130 + 0x20))();
v = *(longlong *)pCVar21;
v = (**(code **)(*(longlong *)pcVar8 + 0x20))(pcVar8);
v = *(longlong *)pCVar21;
v = (**(code **)(*local_120 + 0x20))();
v = *(longlong *)pCVar21;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
```

### `CalGlassStress` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar19;
v = (**(code **)(*local_108 + 0x20))();
v = *(longlong *)pCVar19;
v = (**(code **)(*local_90 + 0x20))();
v = *(longlong *)pCVar19;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar19;
v = (**(code **)(*(longlong *)local_100 + 0x20))();
v = *(longlong *)pCVar19;
v = (**(code **)(*(longlong *)pcVar8 + 0x20))(pcVar8);
v = *(longlong *)pCVar19;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
```

### `CalcGlassShadeCoef` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar14;
v = (**(code **)(*local_120 + 0x20))();
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar14;
v = (**(code **)(*local_100 + 0x20))();
```

### `CalcGlassUFactor` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar15;
v = (**(code **)(*local_120 + 0x20))();
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar15;
v = (**(code **)(*local_100 + 0x20))();
```

### `CheckHasHollowBeforeLayer` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar9 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar9 + 8);
v = (**(code **)(*plVar8 + 0xa8))(plVar8);
v = *(double *)(lVar9 + 8);
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
```

### `CheckPoleIsSimpleSup` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
```

### `DoCalcAwning3d` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar10 + 0xa8))(plVar10);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar10 + 0xa8))(plVar10);
v = (uint)*(double *)(lVar15 + 8);
v = (**(code **)(*local_130 + 0xa8))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar12 + 0x20))(plVar12);
v = *(longlong *)pCVar17;
```

### `DoCalcClayPlate3d` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*(longlong *)pCVar9 + 0xa8))(pCVar9);
v = *(double *)(lVar13 + 8);
v = (**(code **)(*(longlong *)pCVar9 + 0xa8))(pCVar9);
v = (uint)*(double *)(lVar13 + 8);
v = (**(code **)(*local_110 + 0xa8))();
v = *(longlong *)pCVar23;
v = (**(code **)(*(longlong *)local_f8 + 0x20))();
v = *(longlong *)pCVar23;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar23;
v = (**(code **)(*(longlong *)this_00 + 0x20))(this_00);
v = *(longlong *)pCVar23;
```

### `DoCalcRailing3d` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar10 + 0xa8))(plVar10);
v = *(double *)(lVar14 + 8);
v = (**(code **)(*plVar10 + 0xa8))(plVar10);
v = (uint)*(double *)(lVar14 + 8);
v = (**(code **)(*local_160 + 0xa8))();
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar13;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
v = *(longlong *)pCVar13;
v = (**(code **)(*(longlong *)this_00 + 0x20))(this_00);
v = *(longlong *)pCVar13;
```

### `DoCalcShell` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar10 + 0xa8))(plVar10);
v = (**(code **)(*plVar10 + 0xa8))(plVar10);
v = (uint)*(double *)(lVar14 + 8);
v = (**(code **)(*local_168 + 0xa8))();
v = *(double *)(lVar14 + 8);
v = (**(code **)(*plVar11 + 0xa8))(plVar11);
v = *(double *)(lVar14 + 8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
v = *(longlong *)pCVar15;
```

### `DoDrawVSec` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = (**(code **)(*plVar7 + 0xa8))(plVar7);
v = *(double *)(lVar8 + 8);
v = (**(code **)(*plVar6 + 0xb8))(plVar6);
```

### `DoGetAwning3dReaction` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = *(double *)(lVar13 + 8);
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = (uint)*(double *)(lVar13 + 8);
v = *(longlong *)pCVar17;
v = (**(code **)(*local_60 + 0x20))();
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar17;
v = (**(code **)(*plVar9 + 0x20))();
```

### `DoGetAwning3dReactionInfo` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = *(double *)(lVar11 + 8);
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = (uint)*(double *)(lVar11 + 8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
```

### `DoGetAwning3dReactionMatrix` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = *(double *)(lVar11 + 8);
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = (uint)*(double *)(lVar11 + 8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar8 + 0x20))(plVar8);
v = *(longlong *)pCVar15;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
```

### `GetRGlass` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar19;
v = (**(code **)(*plVar12 + 0x20))(plVar12);
v = *(longlong *)pCVar19;
v = (**(code **)(*plVar13 + 0x20))(plVar13);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
v = (**(code **)(*plVar14 + 0xa8))(plVar14);
v = *(double *)(lVar15 + 8);
```
