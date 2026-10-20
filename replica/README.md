# replica/（新实现）

产品规格与 PoC/MVP 见 `../docs/product-spec-v1.md`、`../docs/poc-mvp-plan.md`。

## 现状

- `packages/section`：断面几何 → 特性引擎（PoC P1）。纯函数、无 IO/时钟/随机；解析解对照全绿。
- `scripts/poc-p1-section.mts`：P1 判据运行器，产出 `../evidence/poc/P1/{criteria.md,data.json,conclusion.md}`。

## 检查命令

```sh
npm test          # node --test（Node 24 直接跑 .ts，无需构建）
npm run build     # 当前=类型检查（tsc --noEmit），尚未引入打包器；不要当成产物构建
npm run lint      # oxlint
npm run poc:p1    # P1 判据运行器（解析解对照；旧系统对照仍 PENDING）
```

依赖：`@types/node` / `typescript` / `oxlint`（`npm install` 后可跑上述三项）。

## 约束（摘自规格 V1）

- 计算纯函数：禁止 `Date.now()`、随机数、IO；同输入同输出。
- 单位由调用方保证，引擎内部不做单位换算。
- 薄壁扭转常数 `thinWalledOpenJ` 是显式近似，未与旧系统 `JA` 列对照前不得用于验收。
