# 辅助函数查表提取（分支 → 常量）

- 扫描 `raw/helpers/*.rea.json`，命中 11 个含分支或常量的函数
- 只给「条件 → 值」，**不给系数命名**（规范依据仍未知）

| 函数 | 类别 | 条件数 | 常量数 |
| --- | --- | --- | --- |
| `fun_180254fd0` | OTHER | 5 | 0 |
| `fun_180255170` | ARITH | 20 | 21 |
| `fun_180255450` | ARITH | 6 | 6 |
| `fun_180276990` | OTHER | 0 | 1 |
| `fun_180276eb0` | OTHER | 3 | 0 |
| `fun_180277390` | OTHER | 13 | 0 |
| `fun_180278990` | OTHER | 2 | 6 |
| `fun_1802793c0` | OTHER | 2 | 5 |
| `fun_1802798d0` | OTHER | 0 | 3 |
| `fun_1802bbaf0` | ARITH | 12 | 0 |
| `fun_18032e420` | OTHER | 6 | 0 |

## `fun_180254fd0`（OTHER）

入参：`int param_1`, `uint param_2`

条件：param_1 == 6；param_1 == 7；param_1 == 8；param_1 == 9；param_1 == 10

## `fun_180255170`（ARITH）

入参：`String *param_1`, `double param_2`, `double param_3`, `char param_4`

条件：param_1 == "A"；param_2 <= 5.0；param_3 <= 2.6；param_2 < 300.0；param_3 <= 2.6；param_1 == "B"；param_2 <= 10.0；param_3 <= 2.6；param_2 < 350.0；param_3 <= 2.6；param_1 == "C"；param_2 <= 15.0

常量：0.12, 1.65, 1.78, 1.4, 1.48, 0.14, 0.15, 1.7, 1.84, 1.41, 1.49, 0.23

## `fun_180255450`（ARITH）

入参：`String *param_1`, `double param_2`

条件：param_1 == "A"；param_1 == "B"；param_1 == "C"；param_1 == "A"；param_1 == "B"；param_1 == "C"

常量：1.379, 0.616, 0.318, 1.284, 0.544, 0.262

## `fun_180276990`（OTHER）

入参：`String *param_1`

常量：4e-05

## `fun_180276eb0`（OTHER）

入参：`String *param_1`, `double param_2`

条件：param_2 < 20.0；param_2 < 15.0；param_2 <= 5.0

## `fun_180277390`（OTHER）

入参：`String *param_1`, `double param_2`

条件：param_2 <= 2.9；param_2 <= 2.9；param_2 <= 2.9；param_2 <= 12.0；param_2 <= 19.0；param_2 <= 12.0；param_2 <= 12.0；param_2 <= 12.0；param_2 <= 12.0；param_2 <= 12.0；param_2 <= 19.0；param_2 <= 12.0

## `fun_180278990`（OTHER）

入参：`String *param_1`, `double param_2`

条件：param_2 <= 2.9；param_2 <= 2.9

常量：79.2, 107.6, 158.4, 1.4, 2.1, 1.43

## `fun_1802793c0`（OTHER）

入参：`String *param_1`, `double param_2`

条件：param_2 < 20.0；param_2 < 15.0

常量：13.8, 5.3, 4.65, 3.7, 25.6

## `fun_1802798d0`（OTHER）

入参：`String *param_1`

常量：0.33, 0.3, 0.2

## `fun_1802bbaf0`（ARITH）

入参：`double param_1`, `double param_2`, `double param_3`, `double *param_4`, `double *param_5`, `double *param_6`, `double *param_7`, `double *param_8`

条件：param_2 < 0.0；param_2 <= 60.0；param_2 <= 90.0；param_1 <= 50000.0；param_1 <= 10000.0；param_1 <= 10000.0；param_1 <= 50000.0；param_1 <= 10000.0；param_1 <= 10000.0；param_1 <= 50000.0；param_1 <= 10000.0；param_1 <= 10000.0

## `fun_18032e420`（OTHER）

入参：`int param_1`, `int param_2`

条件：param_1 == 0；param_2 == 1；param_1 == 1；param_2 == 1；param_1 != 2；param_2 == 1

