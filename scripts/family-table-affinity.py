#!/usr/bin/env python3
"""符号族 → 数据表 的亲和矩阵（L7 第 3 步：把 537 条 contains 候选批量收敛）。

做法：复用 `formula-symbol-map.json` 的候选列，按"符号族前缀"统计命中表。
若某族的候选**高度集中**在一两张表，说明该族的绑定是真的（例如 `POLE_*` → 复合型材参数表）；
若分散，则说明是通用名撞车，应判为无绑定。

输出：`migration_workspace/formula-family-tables.md` + `raw/formula-family-tables.json`
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
DB = RAW / 'db'
PREFIX = re.compile(r'^([A-Za-z]{2,}_)')
CONCENTRATION = 0.6   # 单一表占该族候选的比例阈值


def family(symbol):
    m = PREFIX.match(symbol)
    return m.group(1) if m else '其它'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'formula-family-tables.md'))
    ap.add_argument('--json', default=str(RAW / 'formula-family-tables.json'))
    args = ap.parse_args()

    try:
        data = json.loads((RAW / 'formula-symbol-map.json').read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'cannot read formula-symbol-map.json: {exc}') from exc

    # 族内短名精确匹配：去掉族前缀后与列名（忽略大小写）完全相同。
    # 这是比"通用名撞车"更强的证据：短名 Iy/Area 在**指定族的候选表**里才有意义。
    columns = {}
    for path in sorted(DB.glob('*.json')):
        if path.name == 'formulas-raw.json':
            continue
        try:
            tables = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(tables, list):
            continue
        for table in tables:
            columns[f"{path.stem}.{table['name']}"] = {c['name'].lower() for c in table.get('columns', [])}
    fam_short = defaultdict(lambda: defaultdict(list))
    fam_tables = defaultdict(Counter)
    fam_symbols = defaultdict(int)
    fam_matched = defaultdict(int)
    for row in data['symbols']:
        fam = family(row['symbol'])
        fam_symbols[fam] += 1
        short = re.sub(rf'^{re.escape(fam)}', '', row['symbol']).lower()
        if not short:
            continue
        for table, cols in columns.items():
            if short in cols:
                fam_short[fam][table].append(row['symbol'])
        if row['bucket'] in ('none',):
            continue
        if not row['candidates']:
            continue
        fam_matched[fam] += 1
        fam_tables[fam][row['candidates'][0]['table']] += 1

    rows = []
    for fam, total in sorted(fam_symbols.items(), key=lambda kv: -kv[1]):
        tables = fam_tables[fam]
        matched = fam_matched[fam]
        top = tables.most_common(3)
        share = (top[0][1] / matched) if matched and top else 0.0
        rows.append({
            'family': fam, 'symbols': total, 'matched': matched,
            'top_tables': [{'table': t, 'hits': c} for t, c in top],
            'concentration': round(share, 3),
            # 小样本（<5 个候选）即使 100% 集中也不可信：通用名撞车就会这样
            'short_hits': sorted(({'table': t, 'symbols': v} for t, v in
                                   fam_short[fam].items()), key=lambda x: -len(x['symbols']))[:2],
            'verdict': ('样本不足' if matched < 5 else
                        ('绑定可信' if share >= CONCENTRATION else '待人工')) if matched else '无命中',
        })

    Path(args.json).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n')

    md = ['# 符号族 → 数据表 亲和矩阵（L7 第 3 步）', '',
          f'- 族数：**{len(rows)}**；判据：单一表占该族候选比例 ≥ {CONCENTRATION:.0%} 视为"绑定可信"', '',
          '| 族 | 符号数 | 有候选 | Top 表（命中） | 集中度 | 判读 |',
          '| --- | --- | --- | --- | --- | --- |']
    for r in rows[:40]:
        top = '；'.join(f"{t['table']}({t['hits']})" for t in r['top_tables'][:2]) or '—'
        md.append(f"| `{r['family']}` | {r['symbols']} | {r['matched']} | {top} | "
                  f"{r['concentration']:.0%} | {r['verdict']} |")
    trusted = [r for r in rows if r['verdict'] == '绑定可信']
    md += ['', '## 族内短名精确匹配（强证据）', '',
           '| 族 | 表 | 命中符号数 | 例 |', '| --- | --- | --- | --- |']
    for fam, tables in sorted(fam_short.items(), key=lambda kv: -max((len(v) for v in kv[1].values()), default=0)):
        for table, syms in sorted(tables.items(), key=lambda kv: -len(kv[1]))[:1]:
            if len(syms) < 3:
                continue
            md.append(f"| `{fam}` | `{table}` | {len(syms)} | {', '.join(syms[:4])} |")
    md += ['', f'## 绑定可信的族（{len(trusted)} 个）', '']
    for r in trusted:
        md.append(f"- `{r['family']}`：{r['matched']}/{r['symbols']} 有候选，"
                  f"主表 `{r['top_tables'][0]['table']}`（{r['concentration']:.0%}）")
    md += ['', '## 说明', '',
           '- "绑定可信"只表示**候选集中在一张表**，不表示列语义已被确认；',
           '- "待人工"的族要逐条看列名（如 `GLS_to` 是玻璃厚度，`玻璃参数.厚度` 才有意义，'
           '而 `GlazingProperties.Thickness` 是光谱数据库的另一套）。']
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'families={len(rows)} trusted={len(trusted)}')


if __name__ == '__main__':
    sys.exit(main())
