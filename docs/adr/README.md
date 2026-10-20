# ADR（架构决策记录）

规则：一个决策一个文件；`NNNN-title.md`；状态 `proposed | accepted | superseded`；写在决策**当时**，不补写历史结论。

已存在的决策索引在 `docs/decisions.md`（D01–D22）。迁移规则：新决策直接写成 ADR；
`decisions.md` 中尚未迁移的历史条目保持原样，遇到相关改动时再迁成 ADR 并在两处互链。

模板：

```markdown
# NNNN. 标题

- 状态：proposed | accepted | superseded by NNNN
- 日期：YYYY-MM-DD
- 决策者：
- 关联：D## / ES-## / spec §

## 背景
问题、约束、已知证据（标级别）。

## 候选
A / B / C，各自代价与风险。

## 决策
选了哪个，为什么；明确不选哪个及原因。

## 影响
代码/数据/流程/验收的连带变化；失效条件（什么情况下需要重审）。

## 验证
如何证明这个决策是对的（测试、指标、差分样例）。
```
