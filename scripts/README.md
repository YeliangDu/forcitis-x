# scripts/ 的作用域声明（T2/T3）

本目录属命名政策 `docs/naming-conventions.md` §5 的 **T2（兼容适配）/ T3（证据）** 层：

- 允许出现旧系统标识（`HWK*`、`XWall`、`型材参数表`、`图库数据表`、`GetSDr` 等），因为它们**只用于读取旧资产、取证与对照**；
- 严禁把这里的旧名复制进 `replica/`（T0 表面积）——`scripts/check-standards.py` 的 ES-05 会对此 FAIL；
- 新增脚本若涉及旧名，头部注释标一行 `scope: T2 legacy adapter` 或 `scope: T3 evidence`；
- 脚本产物进 `evidence/` 或 `migration_workspace/raw/`，不得成为新系统的运行时依赖。

## 子目录

| 路径 | 层 | 用途 |
| --- | --- | --- |
| `scripts/poc/` | T2 | PoC 编排与旧系统 fixture 摄取/对照（只读、可重跑） |
| `scripts/extract-*.py` | T3 | 反编译产物/PE 数据提取（系数表、Serialize 链） |
| `scripts/check-*.py` | T3 | 回归与验收检查器 |
| `scripts/scheduler/` | T3 | 无人值守调度 |
