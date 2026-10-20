#!/usr/bin/env python3
"""批量把 379 个 CXMap 节点的 eval 反编译结果整理成"参名表 + 算术摘要"。

输入：`migration_workspace/raw/node-vtables.json`（名字 → 构造/vtable/eval）
      已存在的 `migration_workspace/raw/nodes/<名字>.rea.json`（有则复用，不重复反编译）
输出：`migration_workspace/nodes-<族>.md` + `raw/nodes-summary.json`

提取规则（全部是字面量匹配，不做语义推断）：
 - 参数名：`String::String(...,"xxx")` 之后紧跟 `look_string` 的字符串
 - 数值常量：形如 `* 1000000000.0`、`pow(x, 4.0)`、`1000000000.0` 的字面量
 - 表达式行：含 `dVar`/`fVar` 且含 `=` 的行，去掉 Ghidra 变量名后保留运算结构
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
NODES = RAW / 'nodes'
STR = re.compile(r'XYUtil::String::String\(\w+,\s*"([^"]+)"\)')
LOOK = re.compile(r'look_string\(')
NUM = re.compile(r'(?<![\w.])(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)')
EXPR = re.compile(r'^\s*(dVar\d+|fVar\d+|uVar\d+|lVar\d+)\s*=\s*(.+);\s*$')


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        raise SystemExit(f'无法读取 JSON：{path}（{exc}）') from exc


def decompile(eval_va, out_json, ghidra):
    if out_json.exists():
        data = read_json(out_json)
        if data.get('normalized_result'):
            return data
    env = os.environ.copy()
    if ghidra:
        env['GHIDRA_INSTALL_DIR'] = str(ghidra)
    proc = eval_va if isinstance(eval_va, str) else hex(eval_va)
    cmd = ['rea', 'decompile', str(ROOT / 'evidence/baseline/extracted/cab/_1D7374B2004D4FE39A79BCDFC9340FB8'),
           '--procedure', proc, '--provider', 'ghidra',
           '--snapshot', str(ROOT / 'migration_workspace/.cache/snap-hwkwallutil'),
           '--format', 'json']
    run = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    text = run.stdout.strip()
    if not text.startswith('{'):
        return {'error': (run.stderr or text)[:300]}
    try:
        data = json.loads(text)
    except Exception as exc:
        return {'error': f'JSON 解析失败：{exc}'}
    if not data.get('normalized_result'):
        return {'error': data.get('message') or data.get('code') or 'unknown'}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data


KEYUSE = re.compile(r'look_string\([^,]*,\s*(\w+)')
# `$0`/`$1` 是可变参数节点（CXMapVariableArguments）自己的位置参数名，属合法参数名
NAME_OK = re.compile(r'\$?[A-Za-z_0-9][A-Za-z0-9_]{0,30}|\$\d+')


def summarise(pseudo):
    """只把"构造后立刻作为 CXGDict 键查表"的字面量当参数名。

    旧的宽松做法会把 Ghidra 占位符（`$0`）、"Come Here 17" 跳转标记、错误提示文案
    （`loadcase is empty! ...`）都当成参数名；实测污染率 43%。改为要求：
    该 `String` 局部变量在后续 4 行内被 `look_string` 使用，且名字形如标识符。
    """
    lines = pseudo.splitlines()
    params = []
    for i, line in enumerate(lines):
        m = STR.search(line)
        if not m:
            continue
        lm = re.search(r'String::String\((\w+),\s*"', line)
        if not lm:
            continue
        local = lm.group(1)
        window = "\n".join(lines[i:i + 4])
        if not re.search(rf'look_string\([^\n]*\b{re.escape(local)}\b', window):
            continue
        name = m.group(1)
        if not NAME_OK.fullmatch(name):
            continue
        if name not in params:
            params.append(name)
    used = params
    consts = sorted({m.group(1) for m in NUM.finditer(pseudo)
                     if len(m.group(1)) >= 3 and not m.group(1).startswith('0x')})
    exprs = []
    for line in pseudo.splitlines():
        m = EXPR.match(line)
        if m and re.search(r'[-+*/]|pow\(', m.group(2)):
            exprs.append(m.group(2).strip())
    return {'params': used, 'consts': consts[:20], 'exprs': exprs[:12]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', required=True, help='该批次的族名/正则，用于文件命名与筛选')
    ap.add_argument('--pattern', required=True, help='名字正则，如 ^CalGlass')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--ghidra', default=os.environ.get('GHIDRA_INSTALL_DIR'))
    a = ap.parse_args()

    rows = read_json(RAW / 'node-vtables.json')['rows']
    pat = re.compile(a.pattern)
    todo = [r for r in rows if pat.search(r['name'])]
    if a.limit:
        todo = todo[:a.limit]
    print(f'族 {a.family}: 命中 {len(todo)} 个节点')

    results, errors = [], []
    for i, r in enumerate(todo, 1):
        out_json = NODES / f"{r['name']}.rea.json"
        data = decompile(r['eval'], out_json, a.ghidra)
        if 'error' in data:
            errors.append({'name': r['name'], 'error': data['error']})
            print(f"  [{i}/{len(todo)}] {r['name']}: 失败 {data['error'][:80]}")
            continue
        s = summarise(data['normalized_result'])
        results.append({'name': r['name'], 'eval': r['eval'],
                        'evidence_id': data.get('evidence_id'), **s})
        print(f"  [{i}/{len(todo)}] {r['name']}: params={s['params']}")

    md = [f'# 节点 eval 摘要 — {a.family}', '',
          f'- 命中节点：{len(todo)}；成功：{len(results)}；失败：{len(errors)}',
          '- 提取规则：参名取 `look_string` 之前的字符串字面量；常量与表达式行按字面匹配，未做语义推断。',
          '', '| 节点 | eval | 参数名 | 数值常量 |', '| --- | --- | --- | --- |']
    for r in results:
        md.append(f"| `{r['name']}` | `{r['eval']}` | "
                  f"{', '.join(f'`{p}`' for p in r['params']) or '—'} | "
                  f"{', '.join(f'`{c}`' for c in r['consts'][:6]) or '—'} |")
    for r in results:
        if not r['exprs']:
            continue
        md += ['', f"### `{r['name']}` 赋值表达式（原文，未化简）", '', '```c']
        md += [f'v = {e};' for e in r['exprs']]
        md += ['```']
    if errors:
        md += ['', '## 失败项', ''] + [f"- `{e['name']}`：{e['error'][:200]}" for e in errors]
    out_md = ROOT / 'migration_workspace' / f'nodes-{a.family}.md'
    out_md.write_text('\n'.join(md) + '\n')
    out_json = RAW / f'nodes-summary-{a.family}.json'
    out_json.write_text(json.dumps({'family': a.family, 'pattern': a.pattern,
                                    'results': results, 'errors': errors},
                                   ensure_ascii=False, indent=1) + '\n')
    print(f'{out_md}  ok={len(results)} err={len(errors)}')


if __name__ == '__main__':
    sys.exit(main())
