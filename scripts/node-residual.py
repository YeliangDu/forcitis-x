#!/usr/bin/env python3
"""把 `nodes-expr` 里尚未闭合的节点逐条列成待办清单（L5/A 路线收尾用）。

对每个 `PARTIAL`/`SELECTED` 节点，找出表达式里仍未绑定的符号（`p[…]`、`sel(…)`、残留 `dVar/uVar`），
并回溯它在反编译里的**赋值来源语句**，便于逐条人工收尾。

输出：`migration_workspace/nodes-residual.md` + `raw/nodes-residual.json`
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
NODES = RAW / 'nodes'

UNBOUND = re.compile(r'p\[([^\]]+)\]')
REST = re.compile(r'\b([dfu]Var\d+|local_[0-9a-f]+)\b')
SEL = re.compile(r'sel\(([^)]*)\)')


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
            out += [part.strip() for part in joined.split(';') if part.strip()]
            buf = []
    return out


def origin(stmts, symbol):
    """该符号在伪代码里的第一个赋值语句（截断保存）。"""
    pat = re.compile(rf'^(?:\(?\s*{re.escape(symbol)}\s*=|.*\(\s*{re.escape(symbol)}\s*=)')
    for st in stmts:
        if pat.match(st):
            return st[:160]
    for st in stmts:
        if re.search(rf'(?<![\w$]){re.escape(symbol)}(?![\w$])\s*=', st):
            return st[:160]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=str(RAW / 'nodes-residual.json'))
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'nodes-residual.md'))
    args = ap.parse_args()

    try:
        data = json.loads((RAW / 'nodes-expr.json').read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'cannot read nodes-expr.json: {exc}') from exc
    kinds = {}
    kinds_path = RAW / 'node-kinds.json'
    if kinds_path.exists():
        try:
            kinds = {r['name']: r['kind'] for r in json.loads(kinds_path.read_text()).get('rows', [])}
        except json.JSONDecodeError:
            kinds = {}
    rows = []
    for row in data['rows']:
        if row['status'] == 'EXPR':
            continue
        # 非算术且非 ARITH 类的节点不属于"算式待收尾"，见 node-kinds.md
        if row['status'] == 'NO_ARITH' and kinds.get(row['name']) != 'ARITH':
            continue
        fused = row.get('fused') or ''
        missing = sorted(set(UNBOUND.findall(fused)))
        extra = sorted(set(REST.findall(fused)))
        sels = list(SEL.findall(fused))
        if not (missing or extra or sels or (row['status'] == 'NO_ARITH' and kinds.get(row['name']) == 'ARITH')):
            continue
        pseudo = ''
        node_path = NODES / f"{row['name']}.rea.json"
        if node_path.exists():
            try:
                pseudo = json.loads(node_path.read_text()).get('normalized_result') or ''
            except json.JSONDecodeError:
                pseudo = ''
        stmts = statements(pseudo)
        rows.append({
            'name': row['name'],
            'status': row['status'],
            'expr': fused[:400],
            'unbound': [{'symbol': s, 'origin': origin(stmts, s.strip('()'))} for s in missing],
            'residual_vars': [{'symbol': s, 'origin': origin(stmts, s)} for s in extra],
            'selects': sels,
            'select_note': row.get('select_note'),
        })

    Path(args.json).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n')

    with_unbound = sum(1 for r in rows if r['unbound'])
    with_residual = sum(1 for r in rows if r['residual_vars'])
    md = ['# 节点算式收尾清单（L5/A 路线）', '',
          f'- 待收尾节点：{len(rows)}（`PARTIAL` + `SELECTED` + 抽不出步骤的 `ARITH`）',
          f'- 含未绑定取值 `p[…]`：{with_unbound}',
          f'- 含残留寄存器变量：{with_residual}',
          '',
          '每条给出「未绑定符号 + 它在反编译里的赋值来源」，按来源分类即可收尾。',
          '']
    for row in rows:
        md.append(f"## `{row['name']}` — {row['status']}")
        md.append('')
        md.append(f"表达式：`{row['expr'] or '—'}`")
        md.append('')
        for item in row['unbound']:
            md.append(f"- 未绑定 `{item['symbol']}` ← `{item['origin'] or '未找到赋值语句'}`")
        for item in row['residual_vars']:
            md.append(f"- 残留变量 `{item['symbol']}` ← `{item['origin'] or '未找到赋值语句'}`")
        for sel in row['selects']:
            md.append(f'- 数据相关选择 `sel({sel})`（候选顺序 = 条件里 `SUB84` 出现顺序）')
            if row.get('select_note'):
                md.append(f"  - 条件原文：`{row['select_note']}`")
        if not (row['unbound'] or row['residual_vars'] or row['selects']):
            md.append('- 该节点被判定有算术，但数学写在被调函数里（需反编译该函数才能闭合）')
        md.append('')
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'rows={len(rows)} unbound={with_unbound} residual={with_residual} -> {args.md}')


if __name__ == '__main__':
    sys.exit(main())
