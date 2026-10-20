#!/usr/bin/env python3
"""解码 `计算模板` 表的公式文本（CONTEXT 为 GBK/cp936 明文，不是加密）。

数据来源：实机 LocalDB 副本库 `HWKCOPY_XWallTem` 的只读导出
  `CONVERT(varchar(max), CONTEXT, 2)` → `migration_workspace/raw/db-schema/formula-hex.csv`
解码结论（实测）：字节流按 cp936 解码即可读，SQL 里 `cast to nvarchar` 出现乱码只是因为
先按 UTF-16 解释了 GBK 字节。

输出：`migration_workspace/formulas.json`（全量）+ `migration_workspace/formulas.md`（摘要与样例）
"""
import argparse
import binascii
import collections
import csv
import json
import re
import sys
from pathlib import Path

VAR = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\b')
FN = re.compile(r'\b([A-Z][A-Za-z0-9_]{2,})\(')
CODE = re.compile(r'\b(GB\s?\d{5}[-–]\d{4}|JGJ\s?\d{3}[-–]\d{4}|JG\s?\d{3}[-–]\d{4}|CECS\s?\d+[:\-]\d{4}|GB/T\s?\d+[-–]\d{4})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hex', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md', required=True)
    ap.add_argument('--sample', type=int, default=3)
    a = ap.parse_args()

    rows = []
    try:
        with open(a.hex, newline='', encoding='utf-8-sig') as fh:
            for r in csv.DictReader(fh):
                h = (r.get('hex') or '').strip()
                if len(h) < 8 or len(h) % 2:
                    continue
                try:
                    raw = binascii.unhexlify(h)
                except (binascii.Error, ValueError):
                    continue
                rows.append({'iid': r.get('IID'), 'symbol': r.get('SYMBOL'),
                             'bytes': len(raw),
                             'text': raw.decode('cp936', errors='replace')})
    except OSError as exc:
        raise SystemExit(f'无法读取 CSV：{a.hex}（{exc}）') from exc

    vars_ = collections.Counter()
    fns = collections.Counter()
    codes = collections.Counter()
    for r in rows:
        vars_.update(VAR.findall(r['text']))
        fns.update(FN.findall(r['text']))
        codes.update(m.group(0) for m in CODE.finditer(r['text']))

    Path(a.out_json).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n')
    md = ['# 公式库解码结果（`计算模板` 表）', '',
          f'- 条目：{len(rows)}；原始字节：{sum(r["bytes"] for r in rows)}',
          '- 编码：**GBK / cp936 明文**（非加密）。未做任何改写，按原样解码。',
          f'- 引用的模板变量：{len(vars_)} 种；函数：{len(fns)} 种；规范号：{len(codes)} 种', '',
          '## 1. 最常见模板变量', '', '| 变量 | 出现条目数 |', '| --- | --- |']
    for k, v in vars_.most_common(25):
        md.append(f'| `${k}` | {v} |')
    md += ['', '## 2. 最常见函数', '', '| 函数 | 出现条目数 |', '| --- | --- |']
    for k, v in fns.most_common(25):
        md.append(f'| `{k}()` | {v} |')
    md += ['', '## 3. 出现过的规范号（原文）', '']
    md += [f'- `{k}`（{v} 条）' for k, v in codes.most_common(30)] or ['无']

    md += ['', '## 4. 样例（原文照录）', '']
    for r in rows[:a.sample]:
        md += [f"### `{r['symbol']}`（IID {r['iid']}，{r['bytes']} 字节）", '', '```text',
               r['text'].rstrip(), '```', '']
    md += ['## 5. 口径与限制', '',
           '- 只解码 `计算模板.CONTEXT`；`REMARK` 未取。',
           '- 公式里的 `${...}` 是模板占位符，具体取值来自工程数据与节点计算，**未验证**。',
           '- 未验证任何一条公式的计算正确性；此处只是"可读"。']
    Path(a.out_md).write_text('\n'.join(md) + '\n')
    print(f'{a.out_md}  rows={len(rows)} vars={len(vars_)} fns={len(fns)} codes={len(codes)}')


if __name__ == '__main__':
    sys.exit(main())
