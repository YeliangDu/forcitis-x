#!/usr/bin/env python3
"""给每个节点写一句「结构描述」（L5/A 路线第 4 步：文字面）。

只描述**结构**，不解释业务含义：
- 入参：`String::String(local,"名")` + `look_string(...)` 两跳绑定到的参数名（按出现顺序）
- 主要动作：反编译里出现的高层调用（`look_string`/`CXStringDefine`/`NCollection_*`/`HWKPlot`/`FE*`…）
- 返回：eval 签名里的返回类型

输出：`migration_workspace/node-descriptions.md` + `raw/node-descriptions.json`
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
NODES = RAW / 'nodes'

STR_CREATE = re.compile(r'XYUtil::String::String\(\s*(\w+)\s*,\s*L?"([^"]+)"\s*\)')
SIG = re.compile(r'^([\w \*]+?)\s+FUN_[0-9a-f]+\(([^)]*)\)', re.M)
CALL = re.compile(r'\b([A-Z][A-Za-z0-9_]*(?:::[A-Za-z0-9_]+)+)\s*\(')
ACTION_HINTS = (
    'look_string', 'CXStringDefine', 'CXConstant::CXConstant', 'CXParameter',
    'CXMapVariableArguments', 'NCollection_', 'HWKPlot', 'g_bEmfOut',
    'FEAdd', 'FEDel', 'FESet', 'FEGet', 'MMgt::Allocate', 'GetHMMxValue',
)


def params_in_order(pseudo):
    by_local = {m.group(1): m.group(2) for m in STR_CREATE.finditer(pseudo)}
    out = []
    for m in re.finditer(r'(\w+)\s*=\s*[^;]*?look_string\(([^;]*?)\);', pseudo):
        args = m.group(2)
        for local, name in by_local.items():
            if re.search(rf'(?<![\w$]){re.escape(local)}(?![\w$])', args) and name not in out:
                out.append(name)
    return out


GENERIC = ('look_string', 'CXConstant::CXConstant', 'CXMapVariableArguments', 'CXParameter',
           'MMgt::Allocate', 'NCollection_', 'HWKPlot', 'g_bEmfOut')


def actions(pseudo):
    """返回 (业务相关调用, 基础设施调用)。业务相关指非 String/CXGDict/容器/分派 的调用。"""
    specific, generic = [], []
    for hint in ACTION_HINTS:
        if hint in pseudo:
            generic.append(hint)
    for m in CALL.finditer(pseudo):
        name = m.group(1)
        if name.startswith(('XYUtil::String::', 'XYUtil::CXGDict::', 'XYUtil::CXMap::', 'XYUtil::Time::')):
            continue
        if any(name.startswith(g) for g in ('CXConstant', 'CXParameter', 'CXMapVariableArguments', 'MMgt', 'NCollection')):
            continue
        if name not in specific:
            specific.append(name)
        if len(specific) >= 6:
            break
    return specific[:4], generic[:4]


def returns(pseudo):
    m = SIG.search(pseudo)
    return m.group(1).strip() if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=str(RAW / 'node-descriptions.json'))
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'node-descriptions.md'))
    args = ap.parse_args()

    kinds = {}
    kinds_path = RAW / 'node-kinds.json'
    if kinds_path.exists():
        try:
            kinds = {r['name']: r['kind'] for r in json.loads(kinds_path.read_text()).get('rows', [])}
        except json.JSONDecodeError:
            kinds = {}
    expr = {}
    expr_path = RAW / 'nodes-expr.json'
    if expr_path.exists():
        try:
            expr = {r['name']: r['status'] for r in json.loads(expr_path.read_text()).get('rows', [])}
        except json.JSONDecodeError:
            expr = {}

    rows = []
    for path in sorted(NODES.glob('*.rea.json')):
        name = path.stem.replace('.rea', '')
        try:
            pseudo = json.loads(path.read_text()).get('normalized_result') or ''
        except (OSError, json.JSONDecodeError):
            continue
        params = params_in_order(pseudo)
        acts, generic = actions(pseudo)
        rows.append({
            'name': name,
            'kind': kinds.get(name),
            'expr_status': expr.get(name),
            'params': params,
            'actions': acts,
            'generic_actions': generic,
            'branches': pseudo.count('if ('),
            'returns': returns(pseudo),
        })

    Path(args.json).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n')

    md = ['# 节点结构描述（L5/A 路线第 4 步）', '',
          f'- 覆盖：{len(rows)} 个节点全部',
          '- 内容只描述**结构**（入参、主要动作、返回类型），**不含业务语义推断**',
          '',
          '| 节点 | 类别 | 算式 | 入参 | 业务相关调用 | 分支数 | 返回 |',
          '| --- | --- | --- | --- | --- | --- | --- |']
    for row in rows:
        params = ', '.join(row['params'][:6]) or '—'
        acts = ', '.join(f'`{a}`' for a in row['actions'][:3]) or '—'
        md.append(f"| `{row['name']}` | {row['kind'] or '—'} | {row['expr_status'] or '—'} | "
                  f"{params} | {acts} | {row['branches']} | `{row['returns'] or '—'}` |")
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'rows={len(rows)} -> {args.md}')


if __name__ == '__main__':
    sys.exit(main())
