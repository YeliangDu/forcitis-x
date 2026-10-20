#!/usr/bin/env python3
"""把辅助函数里的「分支 → 常量」抽成查表（L5/A 路线第 2 步收尾）。

背景：`FUN_180254fd0` 这类函数不是单一算式，而是**按参数值返回不同系数**的规范查表
（例如按场地类别/高度段返回风压系数）。本脚本只做机械提取：

- 条件：`if (param_N <op> 常数)` / `if (param_N == 常数)` / `XYUtil::operator==(param_1,"A")`
- 结果：分支内对 `uVarX = 0x…`（低 32 位）与配对 `uVarY = 0x…`（高 32 位）拼成的 double
- 输出：`raw/helper-tables.json` + `migration_workspace/helper-tables.md`

不做语义推断：不给系数命名，只给「条件 → 值」。
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
HELPERS = RAW / 'helpers'

COND = re.compile(r'(param_\d+)\s*(<=|>=|==|!=|<|>)\s*(-?\d+(?:\.\d+)?)')
COND_STR = re.compile(r'operator==\(\s*(param_\d+)\s*,\s*"([^"]+)"\s*\)')
CONST_HEX = re.compile(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+)$')
CONST_F = re.compile(r'^(\w+)\s*=\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)$')
SIG = re.compile(r'^\s*[\w \*]+?(FUN_[0-9a-f]+)\(([^)]*)\)', re.M)


def statements(pseudo):
    text = pseudo.replace('{', ' ; ').replace('}', ' ; ')
    out, buf = [], []
    for line in text.splitlines():
        code = line.split('//')[0].rstrip()
        if not code.strip():
            continue
        buf.append(code.strip())
        joined = ' '.join(buf)
        if joined.endswith(';'):
            out += [p.strip() for p in joined.split(';') if p.strip()]
            buf = []
    return out


def pair_doubles(stmts):
    """相邻两条 `uVarA = 0x<lo>; uVarB = 0x<hi>;` 拼成一个 double（Ghidra 把 double 拆两个 u32）。"""
    out = []
    for first, second in zip(stmts, stmts[1:], strict=False):
        m1, m2 = CONST_HEX.match(first), CONST_HEX.match(second)
        if not (m1 and m2):
            continue
        if m1.group(1) == m2.group(1):
            continue
        lo, hi = int(m1.group(2), 16), int(m2.group(2), 16)
        if hi == 0 or hi < 0x3f000000:
            continue
        raw = struct.pack('<II', lo & 0xffffffff, hi & 0xffffffff)
        value = struct.unpack('<d', raw)[0]
        if 1e-6 < abs(value) < 1e6:
            out.append(round(value, 10))
    # 去重保序
    seen, uniq = set(), []
    for v in out:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq


def extract(pseudo):
    sig = SIG.search(pseudo)
    params = []
    if sig:
        params = [p.strip() for p in sig.group(2).split(',') if p.strip()]
    stmts = statements(pseudo)
    conds = []
    for st in stmts:
        conds += [f'{m.group(1)} {m.group(2)} {m.group(3)}' for m in COND.finditer(st)]
        conds += [f'{m.group(1)} == "{m.group(2)}"' for m in COND_STR.finditer(st)]
    doubles = pair_doubles(stmts)
    return {'signature_params': params, 'conditions': conds[:40], 'constants': doubles[:40]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=str(RAW / 'helper-tables.json'))
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'helper-tables.md'))
    args = ap.parse_args()

    info_path = RAW / 'helpers.json'
    kinds = {}
    if info_path.exists():
        try:
            kinds = {r['addr'].lower(): r['kind'] for r in json.loads(info_path.read_text()).get('rows', [])}
        except json.JSONDecodeError:
            kinds = {}

    rows = []
    for path in sorted(HELPERS.glob('fun_*.rea.json')):
        addr = path.stem.replace('.rea', '')
        try:
            pseudo = json.loads(path.read_text()).get('normalized_result') or ''
        except (OSError, json.JSONDecodeError):
            continue
        data = extract(pseudo)
        if not (data['conditions'] or data['constants']):
            continue
        rows.append({'addr': addr, 'kind': kinds.get(addr), **data})

    Path(args.json).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n')
    md = ['# 辅助函数查表提取（分支 → 常量）', '',
          f'- 扫描 `raw/helpers/*.rea.json`，命中 {len(rows)} 个含分支或常量的函数',
          '- 只给「条件 → 值」，**不给系数命名**（规范依据仍未知）', '',
          '| 函数 | 类别 | 条件数 | 常量数 |',
          '| --- | --- | --- | --- |']
    for row in rows:
        md.append(f"| `{row['addr']}` | {row['kind'] or '—'} | {len(row['conditions'])} | {len(row['constants'])} |")
    md.append('')
    for row in rows:
        md.append(f"## `{row['addr']}`（{row['kind'] or '—'}）")
        md.append('')
        if row['signature_params']:
            md.append('入参：' + ', '.join(f'`{p}`' for p in row['signature_params']))
            md.append('')
        if row['conditions']:
            md.append('条件：' + '；'.join(row['conditions'][:12]))
            md.append('')
        if row['constants']:
            md.append('常量：' + ', '.join(f'{c:g}' for c in row['constants'][:12]))
            md.append('')
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'helpers_with_table={len(rows)} -> {args.md}')


if __name__ == '__main__':
    sys.exit(main())
