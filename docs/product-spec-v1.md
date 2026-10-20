# 产品规格 V1（冻结契约）

状态：**V1 已冻结（用户 2026-10-20 确认）**。本文只写"不该变的东西"；实现细节、图形样式、SDK 选型、
排期数字一律不在本文固定。变更必须走 §8。

定位一句话：**中心化薄客户端工程计算协作平台**——以几何为源头、以规范为正确性权威、以"数值+文本+图形"
三元组为交付物、以不可变规范包与审计链保证可复现，替代旧系统在日常工作中的角色。

依据（仓库内可查）：`docs/decisions.md` D01–D20、`AGENTS.md`、`migration_workspace/` 下的取证产物
（`coefficient-tables.md`、`lookup-tables.md`、`serialize-fields.md`、`modules/*`）。

---

## 1. 定位与范围

| 项 | 内容 |
| --- | --- |
| 使用者 | 公司内部，8 城，300 人（200 人日常），域账号 |
| 形态 | 中心化 Web 薄客户端（无离线）；服务端负责计算、存储、渲染、PDF |
| 输入 | 参数化几何（分格/断面）、计算信息、材料/型材、规范包；可选 DWG/DXF 参照 |
| 输出 | 计算书 PDF（含分析图）、方案对比表、图纸（PDF/DXF；DWG 待定） |
| 兼容 | 历史工程仍由旧系统处理；新系统只处理新项目（`.cwx` 仅可选只读参照） |
| 并发 | 100 在线、20 并发重算（另设 FE/PDF 独立队列） |

## 2. 冻结契约（S1–S9）

| # | 契约 | 内容 | 校验方式 |
| --- | --- | --- | --- |
| **S1** | 形态 | 中心化薄客户端；AD SSO（域组→角色）；不提供离线；无本地工程文件流通 | 登录态测试；离线场景应显式不可用 |
| **S2** | 正确性权威 | 以规范为准（`code_profile`）；与旧系统每处差异进差异台账；黄金回归防漂移 | 每条公式/参数可追溯到条文；差异台账非空项均有裁决记录 |
| **S3** | 数据主干 | `Project / Scheme(不可变快照) / Geometry(参数化) / Member / Section / CalcCase / ResultBundle / RulePack / Deviation / Figure / AuditEvent` | 实体与不变量见 §4；任何计算必须可定位到 Scheme 快照 + RulePack 版本 |
| **S4** | 引擎边界 | 几何→构件→断面→荷载→内力→验算→产物；**求解器可插拔**；计算为纯函数（无随机、无时钟、无 IO） | 单测：同输入两次结果字节一致；代码扫描禁止 `Date.now`/随机 |
| **S5** | 结果三元组 | 每个计算点产出 `数值 + 文本要素 + 图形规格(数据)`；图形渲染独立于计算 | ResultBundle schema 校验；图形数据不含样式常量 |
| **S6** | 证据链 | PDF 内嵌 RulePack 指纹、引擎版本、figure hash、审计号；签章层可后置插入 | PDF 元数据/附件可读回并复算指纹 |
| **S7** | 规范治理 | RulePack 不可变；项目钉版本；升级=新包 + 重算 + 差异报告 | 历史包 hash 不变；升级产出差异报告 |
| **S8** | 图形范围 | 参数化单一真源 + 派生计算模型；**不做通用 CAD/BRep 内核** | 无自由绘制命令；几何输入仅参数与目录化图元 |
| **S9** | 边界外 | 离线、`.cwx` 写回、旧 UI 复刻、加密狗协议、CAD 插件（`.arx`）兼容 | 需求评审时显式拒绝 |

## 3. 待定项（不阻塞 MVP，各自绑定 gate）

| 待定 | 决定者 | Gate（触发条件） | 默认路径 |
| --- | --- | --- | --- |
| DWG 写入 / 识别导入 | 用户（下游需求） | 提供 ≥20 张真实图纸样本 + 明确下游要 DWG | 先 PDF/DXF；导入只做 L1 参照 |
| 签章供应商/格式 | 用户调研 | 结论落地（CA/格式/时间戳） | PDF 留签名占位 + 内容 hash |
| FE 首批体系清单 | 统计 + 用户 | 完成"哪些体系必须 FE"统计（POC-4） | 只对必要体系上 FE |
| 分析图清单与色标 | 用户/企业图例规范 | 提供图例规范或确认 6 类通用模板 | 6 类模板可配置 |
| 断面特性精度 | POC-1 结论 | 与旧系统/手算对照结果 | 精确多边形优先，薄壁近似作校验 |
| 偏差裁决责任链 | 用户 + 注册工程师 | 指定签字人与流程 | 每处修正需签署记录，否则不进发布 |

## 4. 数据主干（冻结的实体与不变量）

```text
Project        { id, 名称, 城市, 基本风压/雪压, 粗糙度, 设防烈度, 成员/角色, rulepack_set }
Scheme         { id, project_id, parent_scheme_id?, 快照(不可变), author, created_at, status: draft|submitted|approved|archived }
Geometry       { scheme_id, 标高[], 轴网, 分格[], 洞口[], 构件布置[] }        // 参数化，单一真源
Member         { id, 类型(立柱/横梁/面板/连接/埋件…), 几何引用, 跨度, 受荷宽度, 从属面积, section_ref, 支座条件 }
Section        { id, 类型(型材/组合/拉索/板材), 断面几何, 材料, 特性快照(A,Ix,Iy,Wx,Wy,S,J), 来源 }
CalcCase       { id, member_id, 体系(system), rulepack_ref, inputs(快照), engine_version }
ResultBundle   { calc_case_id, values{}, text{}, figures[figure_spec], witness{hash}, created_at }
Figure         { id, type, data, template_id, renderer_version, hash }
RulePack       { id, 版本, 生效区间, 条文→公式/参数/表/判据/文本要素, fingerprint }
Deviation      { id, 条文, 旧取值, 新取值, 依据, 影响面, 裁决人, 状态 }
AuditEvent     { id, 谁(域账号), 何时, 动作, 对象, rulepack_fp, figure_hash[], pdf_id }
```

不变量（违反即拒绝写库）：

1. `Scheme` 一经 `submitted` 不可修改，只能派生新快照。
2. `CalcCase` 必须引用**不可变**的 `rulepack_ref` 与 `engine_version`。
3. `ResultBundle` 的 `values` 必须有 `figures[].data` 与之一致（同源）。
4. `Deviation` 未裁决前不得用于对外 PDF。
5. 任何 PDF 必须能由 `(scheme_snapshot, rulepack_fp, engine_version, figure hashes)` 重新生成。

## 5. 结果与计算书契约

- **数值**：存储全精度 double；打印按规范位数（旧系统多为 6 位小数）；比较口径见 §6。
- **文本要素**：条文号、公式、代入过程、中间量、结论（满足/不满足）；措辞模板化、可配置。
- **图形**：仅存数据 + 模板 id（挠度曲线、M/V/N 图、应力云图、变形图、温度场、方案对比）。
- **PDF**：矢量优先；字体固定；元数据含 `rulepack_fp / engine_version / figure_hashes / audit_id`；
  签章位预留（不重排版即可插入）。

## 6. 验收口径（三层，映射到 MVP 判据 M1–M7）

| 层 | 判定 | 对应判据 |
| --- | --- | --- |
| A 规范符合性 | 每条公式/参数/判据可追溯到条文；例外必须有 `Deviation` | M1 |
| B 与旧系统差异 | 所有差异进台账，含条文依据与影响面；禁止"静默不一致" | M1 |
| C 黄金回归 | 已批准的 ResultBundle 作为基线，任何改动必须全绿 | M7 |

数值容差：中间量相对误差 ≤1e-6（打印位数内一致）；图形以数据一致（非像素）为判据。

## 7. 明确不在 V1 范围

离线、`.cwx` 写回与逐字节往返、旧 MFC UI 复刻、加密狗/席位复刻、CAD 插件兼容、
通用 CAD/BRep 内核、3D 自由建模、多语言、移动端。

## 8. 变更控制

V1 只因以下原因升级（写入 `docs/decisions.md` 并说明影响面）：
1. 用户业务规则变化（如必须 DWG、必须离线）；
2. 法规/规范变化（RulePack 不足以覆盖）；
3. PoC 结论推翻契约（例如断面精度不足以支撑 S2，则修 S4/S8）；
4. 安全/合规事件。

技术选型、图样式、SDK、排期数字**不属于 V1**，不进变更流程。
