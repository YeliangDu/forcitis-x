#!/usr/bin/env python3
"""把公式数据符号与数据库列做**候选匹配**（L7 第 3 步核心）。

思路：符号（如 `GLS_to`）与列名（如 `玻璃参数.厚度` 或 `材料特性表.DENSITY`）都不是同一种语言，
所以只做**候选 + 置信度分桶**，不宣布绑定成立：

| 桶 | 规则 |
| --- | --- |
| `exact` | 符号（去前缀、小写）与列名（小写）完全相同 |
| `contains` | 一方包含另一方，且较短一方长度 ≥ 3 |
| `token` | 符号按 `_` 切分后，至少一个 ≥3 字符的 token 出现在列名里 |
| `none` | 都不命中 |

输出：`migration_workspace/formula-symbol-map.md` + `raw/formula-symbol-map.json`
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
DB = RAW / 'db'


def load_columns():
    cols = []
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
            for col in table.get('columns', []):
                cols.append({'db': path.stem, 'table': table['name'], 'column': col['name'],
                             'type': col['type']})
    return cols


# 通用列名：任何体系的符号都可能撞上，不能算"证据"
GENERIC = {'name', 'area', 'type', 'remark', 'iid', 'thickness', 'g', 'iz', 'iy',
           'wz1', 'wz2', 'wy1', 'wy2', 'id', 'code', 'level', 'num', 'count',
           'len', 'length', 'width', 'height', 'w', 'h', 'b', 't', 'd'}


def stem(symbol):
    return re.sub(r'^[A-Z]+_', '', symbol)


def classify(symbol, columns):
    core = stem(symbol).lower()
    tokens = [t for t in re.split(r'_+', core) if len(t) >= 3]
    hits = []
    for col in columns:
        name = col['column'].lower()
        if core and core == name:
            if core in GENERIC:
                hits.append((1, 'exact_generic', col))
            elif len(core) < 4:
                hits.append((1, 'exact_weak', col))
            else:
                hits.append((3, 'exact', col))
        elif core and (core in name or name in core) and min(len(core), len(name)) >= 3:
            hits.append((2, 'contains', col))
        elif any(t in name for t in tokens):
            hits.append((1, 'token', col))
    hits.sort(key=lambda h: -h[0])
    return hits[:3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'formula-symbol-map.md'))
    ap.add_argument('--json', default=str(RAW / 'formula-symbol-map.json'))
    args = ap.parse_args()

    try:
        data = json.loads((RAW / 'formula-bindings.json').read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'cannot read formula-bindings.json: {exc}') from exc
    counts = Counter()
    for row in data['rows']:
        for sym in row['params']:
            counts[sym] += 1
    columns = load_columns()

    buckets = Counter()
    rows = []
    for sym, freq in counts.most_common():
        hits = classify(sym, columns)
        bucket = hits[0][1] if hits else 'none'
        buckets[bucket] += 1
        rows.append({'symbol': sym, 'occurrences': freq, 'bucket': bucket,
                     'candidates': [{'table': f"{h[2]['db']}.{h[2]['table']}",
                                     'column': h[2]['column'], 'type': h[2]['type']} for h in hits]})

    Path(args.json).write_text(json.dumps({'columns': len(columns), 'buckets': dict(buckets),
                                           'symbols': rows}, ensure_ascii=False, indent=1) + '\n')
    md = ['# 公式符号 → 数据列 候选匹配（L7 第 3 步）', '',
          f'- 数据符号：**{len(rows)}**；数据库列：**{len(columns)}**（85 张表）',
          '- 置信分桶：' + '、'.join(f'`{k}`={v}' for k, v in buckets.most_common()),
          '- `exact_weak` = 去前缀后 ≤3 字符的精确撞名；`exact_generic` = 撞上通用列名（IZ/AREA/NAME…）——两者**都不可直接采信**；',
          '- **候选不等于绑定**：`contains`/`token` 两桶仍需人工确认（列名是中文/英文缩写，符号是公式记号）',
          '', '## 精确命中（可直接核对）', '', '| 符号 | 次数 | 表.列 |', '| --- | --- | --- |']
    for r in rows:
        if r['bucket'] == 'exact':
            c = r['candidates'][0]
            md.append(f"| `{r['symbol']}` | {r['occurrences']} | `{c['table']}.{c['column']}` |")
    md += ['', '## 包含命中（前 40，需人工确认）', '', '| 符号 | 次数 | 候选列 |', '| --- | --- | --- |']
    shown = 0
    for r in rows:
        if r['bucket'] != 'contains':
            continue
        c = r['candidates'][0]
        md.append(f"| `{r['symbol']}` | {r['occurrences']} | `{c['table']}.{c['column']}` ({c['type']}) |")
        shown += 1
        if shown >= 40:
            break
    md += ['', '## 未命中（前 30，多为构件输入而非表数据）', '', '| 符号 | 次数 |', '| --- | --- |']
    for r in [x for x in rows if x['bucket'] == 'none'][:30]:
        md.append(f"| `{r['symbol']}` | {r['occurrences']} |")
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'symbols={len(rows)} columns={len(columns)} buckets={dict(buckets)}')


if __name__ == '__main__':
    sys.exit(main())
