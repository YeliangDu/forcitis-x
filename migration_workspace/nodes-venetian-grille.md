# 节点 eval 摘要 — venetian-grille

- 命中节点：2；成功：2；失败：0
- 提取规则：参名取 `look_string` 之前的字符串字面量；常量与表达式行按字面匹配，未做语义推断。

| 节点 | eval | 参数名 | 数值常量 |
| --- | --- | --- | --- |
| `FEDoGrilleVPole` | `0x180160c20` | `hand`, `sec`, `loads`, `poleinfo` | `1000` |
| `FEDoGrilleVPoleDraw` | `0x1801614a0` | `hand`, `sec`, `loads`, `poleinfo`, `drawbz`, `drawsize`, `ratio` | `100`, `100.0`, `1000`, `2000` |

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
