#!/usr/bin/env python3
"""把 5285 个公式数据符号按"族"归类（L7 第 3 步第 1 小步）。

族规则（机械、可复核）：
- `XXX_yy` → 取前缀 `XXX_`（如 `GLS_to` → `GLS_`）
- 希腊字母 / 单字母 + 下标（`γwf`、`βE`、`ω0`、`ψE`）→ 取首字符作为族（`γ`、`β`、`ω`、`ψ`）
- 其余按首字母大写化归族，避免族数爆炸

输出：`migration_workspace/formula-symbols.md` + `raw/formula-symbols.json`
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
GREEK = set('αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ')
PREFIXED = re.compile(r'^([A-Za-z]{2,}_)')


def family(symbol):
    m = PREFIXED.match(symbol)
    if m:
        return m.group(1)
    if symbol and symbol[0] in GREEK:
        return f'{symbol[0]}(希腊字母族)'
    return f'{symbol[:1].upper()}…'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'formula-symbols.md'))
    ap.add_argument('--json', default=str(RAW / 'formula-symbols.json'))
    args = ap.parse_args()

    try:
        data = json.loads((RAW / 'formula-bindings.json').read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'cannot read formula-bindings.json: {exc}') from exc
    rows = data['rows']

    counts = Counter()
    formulas_by_symbol = defaultdict(set)
    for row in rows:
        for sym in row['params']:
            counts[sym] += 1
            formulas_by_symbol[sym].add(row['symbol'])
    fam_counts = Counter()
    fam_members = defaultdict(list)
    for sym, cnt in counts.items():
        fam = family(sym)
        fam_counts[fam] += cnt
        fam_members[fam].append((sym, cnt))

    out = []
    for fam, total in fam_counts.most_common():
        members = sorted(fam_members[fam], key=lambda kv: -kv[1])
        out.append({'family': fam, 'occurrences': total, 'symbols': len(members),
                    'top': [{'symbol': s, 'count': c} for s, c in members[:8]]})
    Path(args.json).write_text(json.dumps({'total_symbols': len(counts), 'families': out}, ensure_ascii=False, indent=1) + '\n')

    md = ['# 公式数据符号族（L7 第 3 步）', '',
          f'- 数据符号总数：**{len(counts)}**；族数：**{len(out)}**',
          '- 族规则见脚本注释（前缀优先、希腊字母按首字符）；只做机械归并，不解释业务含义', '',
          '| 族 | 符号数 | 出现次数 | 高频成员 |', '| --- | --- | --- | --- |']
    for row in out[:40]:
        top = ', '.join(f"{m['symbol']}({m['count']})" for m in row['top'][:4])
        md.append(f"| `{row['family']}` | {row['symbols']} | {row['occurrences']} | {top} |")
    md += ['', '## 使用面最广的符号（出现在最多公式里）', '', '| 符号 | 公式数 | 出现次数 |', '| --- | --- | --- |']
    for sym, cnt in counts.most_common(30):
        md.append(f"| `{sym}` | {len(formulas_by_symbol[sym])} | {cnt} |")
    md += ['', '## 下一步', '',
           '1. 按族把符号对到 `raw/db/*.json` 的列（风压/强度/密度/系数表）；',
           '2. 挑 `WLD`（风荷载设计值，只依赖 γw 与 Wk）做端到端复算；',
           '3. 与原版界面值对照（L8 最小切片）。']
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'symbols={len(counts)} families={len(out)} -> {args.md}')


if __name__ == '__main__':
    sys.exit(main())
