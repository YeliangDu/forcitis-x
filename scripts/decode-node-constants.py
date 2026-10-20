#!/usr/bin/env python3
"""批量解码节点 eval 里的「常量表」（L5/L7 交叉用）。

很多节点（如 `GetKk`）没有算术，而是按输入分支返回常量；这些常量在反编译里写成
两条相邻的 `uVarX = 0x…;`（低/高 32 位），拼回才是 double。本脚本机械解码并标注
最近的条件（`operator==("A")` / `param_2 <= 2.6` 等）。

输出：`migration_workspace/node-constants.md` + `raw/node-constants.json`
只做机械解码与就近条件标注，**不命名常量语义**。
"""
import argparse
import json
import math
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
NODES = RAW / 'nodes'

HEX_ASSIGN = re.compile(r'^(\w+)\s*=\s*(0x[0-9a-f]{1,8});$')
STR_EQ = re.compile(r'operator==\(\s*\(?String \*\)?\s*\w+\s*,\s*"([^"]+)"')
NUM_COND = re.compile(r'if \(\s*param_(\d+)\s*([<>=!]+)\s*(-?[\d.]+)\s*\)')
RET_HEX = re.compile(r'return (0x[0-9a-f]{16});')


def decode(lo, hi):
    if hi < 0x3f000000:
        return None
    value = struct.unpack('<d', struct.pack('<II', lo & 0xffffffff, hi & 0xffffffff))[0]
    if math.isnan(value) or math.isinf(value) or not (1e-9 < abs(value) < 1e12):
        return None
    return round(value, 6)


def scan(pseudo):
    lines = [ln.strip() for ln in pseudo.splitlines()]
    cond = None
    rows = []
    for i, line in enumerate(lines):
        m = STR_EQ.search(line)
        if m:
            cond = f'== "{m.group(1)}"'
        m = NUM_COND.search(line)
        if m:
            cond = f'param_{m.group(1)} {m.group(2)} {m.group(3)}'
        m = RET_HEX.search(line)
        if m:
            raw = int(m.group(1), 16)
            lo, hi = raw & 0xffffffff, raw >> 32
            value = decode(lo, hi)
            if value is not None:
                rows.append({'cond': cond, 'value': value, 'form': 'return-hex'})
            continue
        m = HEX_ASSIGN.match(line)
        if not m:
            continue
        lo = int(m.group(2), 16)
        for j in range(i + 1, min(i + 4, len(lines))):
            m2 = HEX_ASSIGN.match(lines[j])
            if not m2 or m2.group(1) == m.group(1):
                continue
            value = decode(lo, int(m2.group(2), 16))
            if value is not None:
                rows.append({'cond': cond, 'value': value, 'form': 'u32-pair',
                             'vars': [m.group(1), m2.group(1)]})
            break
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'node-constants.md'))
    ap.add_argument('--json', default=str(RAW / 'node-constants.json'))
    args = ap.parse_args()

    out, errors = [], []
    for path in sorted(NODES.glob('*.rea.json')):
        name = path.stem.replace('.rea', '')
        try:
            pseudo = json.loads(path.read_text()).get('normalized_result') or ''
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({'name': name, 'error': str(exc)})
            continue
        rows = scan(pseudo)
        if rows:
            out.append({'name': name, 'constants': rows})

    Path(args.json).write_text(json.dumps({'nodes': out, 'errors': errors}, ensure_ascii=False, indent=1) + '\n')
    md = ['# 节点常量表解码（机械）', '',
          f'- 扫描 `raw/nodes/*.rea.json`；有常量的节点：**{len(out)}** 个',
          '- 解码规则：相邻两条 `uVarX = 0x…` 拼成 double；标注最近的条件（不命名语义）', '',
          '| 节点 | 常量数 | 条件 → 值（前 6） |', '| --- | --- | --- |']
    for row in sorted(out, key=lambda r: -len(r['constants'])):
        pairs = '；'.join(
            f"{c['cond'] or '无条件'}→{c['value']:g}" for c in row['constants'][:6])
        md.append(f"| `{row['name']}` | {len(row['constants'])} | {pairs} |")
    if errors:
        md += ['', '## 失败', ''] + [f"- `{e['name']}`：{e['error']}" for e in errors]
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'nodes_with_constants={len(out)} errors={len(errors)}')


if __name__ == '__main__':
    sys.exit(main())
