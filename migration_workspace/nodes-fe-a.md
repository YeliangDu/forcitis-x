# 节点 eval 摘要 — fe-a

- 命中节点：17；成功：17；失败：0
- 提取规则：参名取 `look_string` 之前的字符串字面量；常量与表达式行按字面匹配，未做语义推断。

| 节点 | eval | 参数名 | 数值常量 |
| --- | --- | --- | --- |
| `FEAddAnaOfAluBoardProb` | `0x180071a30` | `$0` | `100`, `189.0` |
| `FEAddAnaOfCylinderProb` | `0x18007a900` | `$0` | `100`, `189.0` |
| `FEAddAnaOfQuadMindlinSProb` | `0x1800859d0` | `$0` | `100`, `189.0` |
| `FEAddBDLoad` | `0x18023c230` | `hand`, `lcid`, `BID`, `val`, `spos`, `epos`, `name` | `1289.0` |
| `FEAddBFLoad` | `0x18023cb90` | `hand`, `lcid`, `BID`, `pos`, `val`, `name` | `0.0`, `1289.0` |
| `FEAddBTDLoad` | `0x18023d460` | `hand`, `lcid`, `BID`, `val`, `spos`, `epos`, `name` | — |
| `FEAddBTULoad` | `0x18023dd60` | `hand`, `lcid`, `BID`, `val`, `spos`, `epos`, `name` | — |
| `FEAddBeamExModelProb` | `0x1800eef70` | `$0` | — |
| `FEAddBoardModelProb` | `0x18010b740` | `$0` | — |
| `FEAddCBProb` | `0x1800b6860` | `$0` | `189.0` |
| `FEAddCFrameModelProb` | `0x180133a20` | `$0` | — |
| `FEAddLnkNetProb` | `0x180175160` | — | — |
| `FEAddLnkTrussProb` | `0x180177e60` | — | — |
| `FEAddLoadcase` | `0x180062110` | `hand`, `name` | `144`, `200` |
| `FEAddNode` | `0x1802069c0` | `hand`, `name`, `x`, `y`, `DOF`, `IsCon`, `xg`, `yg`, `rg` | `0.0`, `200` |
| `FEAddPlaneStressProb` | `0x180189210` | `$0` | — |
| `FEAddProb` | `0x180062ba0` | `$0`, `$1` | — |

### `FEAddAnaOfAluBoardProb` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar12;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
```

### `FEAddAnaOfCylinderProb` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar12;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
```

### `FEAddAnaOfQuadMindlinSProb` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar12;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
```

### `FEAddBDLoad` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar5 + 0xa8))(plVar5);
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = *(longlong *)pCVar14;
v = (**(code **)(*local_1d8 + 0x20))();
v = *(longlong *)pCVar14;
v = (**(code **)(*local_1d0 + 0x20))();
v = *(longlong *)pCVar14;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar14;
v = (**(code **)(*local_158 + 0x20))();
v = *(longlong *)pCVar14;
```

### `FEAddBFLoad` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar5 + 0xa8))(plVar5);
v = *(longlong *)pCVar20;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = *(longlong *)pCVar20;
v = (**(code **)(*local_1c8 + 0x20))();
v = *(longlong *)pCVar20;
v = (**(code **)(*local_138 + 0x20))();
v = *(longlong *)pCVar20;
v = (**(code **)(*local_1b8 + 0x20))();
v = *(longlong *)pCVar20;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar20;
```

### `FEAddBTDLoad` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar4 + 0xa8))(plVar4);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar4 + 0x20))(plVar4);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar5 + 0x20))();
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar6 + 0x20))();
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar8 + 0x20))();
v = *(longlong *)pCVar16;
```

### `FEAddBTULoad` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar4 + 0xa8))(plVar4);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar4 + 0x20))(plVar4);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar5 + 0x20))();
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar6 + 0x20))();
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar8 + 0x20))();
v = *(longlong *)pCVar16;
```

### `FEAddBeamExModelProb` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar11;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
```

### `FEAddBoardModelProb` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar11;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
```

### `FEAddCBProb` 赋值表达式（原文，未化简）

```c
v = CCrossBeam::GetHandle((CCrossBeam *)pCVar9);
v = *(longlong *)pCVar10;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
```

### `FEAddCFrameModelProb` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar11;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
```

### `FEAddLnkNetProb` 赋值表达式（原文，未化简）

```c
v = CLinkNetCalc::GetHandle((CLinkNetCalc *)pCVar4);
v = CLinkNetCalc::GetHandle((CLinkNetCalc *)pCVar4);
```

### `FEAddLnkTrussProb` 赋值表达式（原文，未化简）

```c
v = CLinkTrussCalc::GetHandle((CLinkTrussCalc *)pCVar4);
v = CLinkTrussCalc::GetHandle((CLinkTrussCalc *)pCVar4);
```

### `FEAddLoadcase` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = (**(code **)(*plVar6 + 0xa8))(plVar6);
v = *(double *)(lVar8 + 8);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
v = *(longlong *)pCVar16;
v = (**(code **)(*plVar7 + 0x20))(plVar7);
```

### `FEAddNode` 赋值表达式（原文，未化简）

```c
v = (**(code **)(*plVar9 + 0xa8))(plVar9);
v = *(longlong *)pCVar26;
v = (**(code **)(*plVar9 + 0x20))(plVar9);
v = *(longlong *)pCVar26;
v = (**(code **)(*plVar10 + 0x20))(plVar10);
v = *(longlong *)pCVar26;
v = (**(code **)(*plVar11 + 0x20))(plVar11);
v = *(longlong *)pCVar26;
v = (**(code **)(*plVar12 + 0x20))(plVar12);
v = *(longlong *)pCVar26;
v = (**(code **)(*local_80 + 0x20))();
v = *(longlong *)pCVar26;
```

### `FEAddPlaneStressProb` 赋值表达式（原文，未化简）

```c
v = *(longlong *)pCVar11;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
```

### `FEAddProb` 赋值表达式（原文，未化简）

```c
v = CFEProblem::GetHandle((CFEProblem *)pCVar9);
v = CFEProblem::GetHandle((CFEProblem *)pCVar9);
v = CFEProblem::GetHandle((CFEProblem *)pCVar9);
v = *(longlong *)this_00;
v = (**(code **)(*plVar5 + 0x20))(plVar5);
v = *(longlong *)this_00;
v = (**(code **)(*plVar6 + 0x20))(plVar6);
```
