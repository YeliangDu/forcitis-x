#!/usr/bin/env python3
"""把 raw/db/*.json 汇总成 db-dump.md（L7 数据层第 1 步的交付物）。

只做汇总与样本展示：**不推断单位、不解释业务语义**。
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw' / 'db'


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'cannot read {path}: {exc}') from exc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'db-dump.md'))
    args = ap.parse_args()

    dbs = {}
    for path in sorted(RAW.glob('*.json')):
        dbs[path.stem] = load(path)

    md = ['# 数据层导出（L7 第 1 步）：表结构 + 样本行', '',
          '- 来源：`HWKCOPY_*` 只读副本库（`SELECT` only，未 attach 新库、未写入）',
          '- 方式：`scripts/dump-db.py`（每表：列名/类型/可空 + 行数 + 前 3 行样本）',
          '- 边界：**只记录结构与样本，不推断单位与业务语义**', '']

    total_tables = 0
    total_rows = 0
    for db, tables in dbs.items():
        rows = sum(t['rows'] for t in tables)
        total_tables += len(tables)
        total_rows += rows
        md += [f'## `{db}`：{len(tables)} 张表 / {rows} 行', '',
               '| 表 | 行数 | 列数 |', '| --- | --- | --- |']
        for t in sorted(tables, key=lambda x: -x['rows']):
            md.append(f"| `{t['name']}` | {t['rows']} | {len(t['columns'])} |")
        md.append('')

    md += ['## 合计', '', f'- 表总数 **{total_tables}**，行总数 **{total_rows}**', '']

    # 列类型分布
    types = Counter()
    for tables in dbs.values():
        for t in tables:
            for c in t['columns']:
                types[c['type']] += 1
    md += ['## 列类型分布', '', '| 类型 | 列数 |', '| --- | --- |']
    for name, count in types.most_common():
        md.append(f'| `{name}` | {count} |')
    md.append('')

    # 数值列样本：给出量级观察，不命名单位
    md += ['## 数值列样本（量级观察，不推断单位）', '']
    for db, tables in dbs.items():
        for t in tables:
            numeric = [c['name'] for c in t['columns'] if c['type'] in ('float', 'real', 'int', 'bigint', 'smallint', 'tinyint', 'decimal', 'numeric')]
            if not numeric or not t['sample']:
                continue
            row = t['sample'][0]
            vals = []
            for col in numeric[:6]:
                if col in row and row[col] is not None:
                    vals.append(f'{col}={row[col]}')
            if vals:
                md.append(f"- `{db}`.`{t['name']}`：{'，'.join(vals)}")
    md.append('')
    md.append('## 下一步')
    md.append('')
    md.append('1. 把 `计算模板`（2082 条公式）里的符号与 `raw/cxmap-entries.json` 的 379 个参名对齐；')
    md.append('2. 再把参名对到本文件的数据列（风压/强度/密度/系数），产出"可执行公式"清单；')
    md.append('3. 选一条业务链做原版对照（L8 最小切片）。')
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'tables={total_tables} rows={total_rows} -> {args.md}')


if __name__ == '__main__':
    sys.exit(main())
