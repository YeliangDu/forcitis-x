#!/usr/bin/env python3
"""把从实机 LocalDB 只读导出的 schema CSV 汇总成可读文档。

输入：`migration_workspace/raw/db-schema/schema-<tag>.csv`、`rowcount-<tag>.csv`
（由实机 PowerShell 只读查询 `sys.tables`/`sys.columns`/`sys.partitions` 导出，未写入数据库）
输出：`migration_workspace/db-schema.md` + `raw/db-schema.json`
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    try:
        with open(path, newline='', encoding='utf-8-sig') as fh:
            return list(csv.DictReader(fh))
    except OSError as exc:
        raise SystemExit(f'无法读取 CSV：{path}（{exc}）') from exc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    d = Path(a.dir)
    tags = sorted(p.name[len('schema-'):-len('.csv')] for p in d.glob('schema-*.csv'))
    summary = {}
    for tag in tags:
        cols = read_csv(d / f'schema-{tag}.csv')
        rc_path = d / f'rowcount-{tag}.csv'
        rows = read_csv(rc_path) if rc_path.exists() else []
        rowcount = {}
        for r in rows:
            try:
                rowcount[f"{r['sch']}.{r['tbl']}"] = int(r['rows_'])
            except (TypeError, ValueError, KeyError) as exc:
                raise SystemExit(
                    f'行数 CSV 不可解析：{rc_path}（{exc}）') from exc
        tables = collections.OrderedDict()
        for c in cols:
            key = f"{c['sch']}.{c['tbl']}"
            tables.setdefault(key, []).append(c)
        summary[tag] = {'tables': tables, 'rowcount': rowcount}

    md = ['# 数据库结构（实机只读导出）', '',
          '来源：实机 LocalDB `(localdb)\\v11.0`（SQL Server 11.00.7001）上的**副本库**',
          '`HWKCOPY_XWallTem` / `HWKCOPY_XWall` / `HWKCOPY_UserGlazing`，',
          '仅执行 `select … from sys.tables / sys.columns / sys.partitions`，**未写入、未改动**原库。',
          '', '| 库标签 | 表数 | 列数 |', '| --- | --- | --- |']
    for tag, v in summary.items():
        ncol = sum(len(c) for c in v['tables'].values())
        md.append(f"| `{tag}` | {len(v['tables'])} | {ncol} |")

    for tag, v in summary.items():
        md += ['', f'## `{tag}` 库', '', '| 表 | 行数 | 列数 |', '| --- | --- | --- |']
        order = sorted(v['tables'], key=lambda k: -v['rowcount'].get(k, 0))
        for k in order:
            md.append(f"| `{k}` | {v['rowcount'].get(k, '—')} | {len(v['tables'][k])} |")
        md += ['', '### 列明细', '']
        for k in order:
            cols = ', '.join(f"{c['col']}:{c['typ']}" for c in v['tables'][k])
            md.append(f'- `{k}`：{cols}')

    md += ['', '## 口径与限制', '',
           '- 这是**副本库**的结构，与安装目录里的 `*.mdf` 是否逐字节一致未验证；',
           '  同名库在主库路径下也存在（`C:\\Users\\administrator\\AppData\\Local\\HWKSoft\\XWall\\*.mdf`）。',
           '- 只取结构与行数，**未取任何业务数据行**。',
           '- 行数来自 `sys.partitions` 统计，可能滞后于实际提交。',
           '- 表名与列名为数据库原文（含中文），未做翻译或改名。']
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({
        tag: {'tables': dict(v['tables']), 'rowcount': v['rowcount']}
        for tag, v in summary.items()
    }, ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  dbs={len(summary)}  tables=' +
          ','.join(f"{t}:{len(v['tables'])}" for t, v in summary.items()))


if __name__ == '__main__':
    sys.exit(main())
