#!/usr/bin/env python3
"""把 2082 条公式文本结构化，并与 CXMap 名字表对齐（L7 第 2 步）。

输入：
  `migration_workspace/raw/db/formulas-raw.json`（`计算模板` 全量，CONTEXT 已按 GBK 解码）
  `migration_workspace/raw/cxmap-entries.json`（379 个注册名）

输出：
  `migration_workspace/formula-bindings.md` + `raw/formula-bindings.json`

只做机械切分：`${X}` 视为符号；`${F(a,b):A:B}` 视为条件模板，拆出 F 与两个分支。
不判断公式对错、不给单位。
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
TOKEN = re.compile(r'\$\{([^{}]*)\}')
SIMPLE = re.compile(r'^[A-Za-z_α-ωΑ-Ω][\w.α-ωΑ-Ω]*$')
CALL = re.compile(r'^([A-Za-z_]\w*)\s*\((.*)\)\s*(?::(.*))?$', re.S)


def split_call(inner):
    """`F(a,b):A:B` → (F, 'a,b', 'A:B')；不是调用则返回 None。"""
    m = CALL.match(inner.strip())
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'formula-bindings.md'))
    ap.add_argument('--json', default=str(RAW / 'formula-bindings.json'))
    args = ap.parse_args()

    try:
        formulas = json.loads((RAW / 'db' / 'formulas-raw.json').read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'cannot read formulas-raw.json: {exc}') from exc
    try:
        entries = json.loads((RAW / 'cxmap-entries.json').read_text())['entries']
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f'cannot read cxmap-entries.json: {exc}') from exc

    registered = {e['name'] for e in entries}
    rows, param_counter, func_counter = [], Counter(), Counter()
    unresolved_counter = Counter()
    for f in formulas:
        text = f.get('context_text') or ''
        params, funcs, conditional, unresolved = [], [], [], []
        for inner in TOKEN.findall(text):
            call = split_call(inner)
            if call:
                name, call_args, branches = call
                funcs.append(name)
                func_counter[name] += 1
                if branches is not None:
                    conditional.append(name)
                continue
            token = inner.strip()
            if not token:
                continue
            if SIMPLE.match(token):
                params.append(token)
                param_counter[token] += 1
                if token not in registered:
                    unresolved.append(token)
                    unresolved_counter[token] += 1
        rows.append({
            'iid': f.get('iid'),
            'symbol': f.get('symbol'),
            'title': f.get('title'),
            'params': sorted(set(params)),
            'funcs': sorted(set(funcs)),
            'conditional_funcs': sorted(set(conditional)),
            'unregistered_params': sorted(set(unresolved)),
            'length': len(text),
        })

    covered = [r for r in rows if not r['unregistered_params']]
    with_params = [r for r in rows if r['params']]
    funcs_all = set(func_counter)
    funcs_registered = sorted(funcs_all & registered)
    param_in_registered = sorted(set(param_counter) & registered)
    Path(args.json).write_text(json.dumps({
        'formulas': len(rows),
        'with_params': len(with_params),
        'fully_registered': len(covered),
        'registered_names': len(registered),
        'rows': rows,
    }, ensure_ascii=False, indent=1) + '\n')

    md = ['# 公式 ↔ 函数 ↔ 数据符号绑定（L7 第 2 步）', '',
          f'- 公式条目：**{len(rows)}**（`计算模板`，`CONTEXT` 按 GBK 解码）',
          f'- 出现的调用型占位：**{len(funcs_all)}** 个不同函数，其中 **{len(funcs_registered)}** 个命中 379 个 CXMap 注册名',
          f'- 出现的数据符号占位：**{len(param_counter)}** 个不同符号；其中命中注册名的：**{len(param_in_registered)}** 个',
          '',
          '> 结论：**公式里的"函数"才是节点，"符号"是数据**。'
          f'379 个注册名中有 {len(registered) - len(funcs_registered)} 个从未在公式里以函数出现（多为内部/FE/绘图节点）。',
          '',
          f'## 命中注册名的公式函数（{len(funcs_registered)} 个，按次数）', '',
          '| 函数 | 次数 |', '| --- | --- |']
    for name in sorted(funcs_registered, key=lambda n: -func_counter[n]):
        md.append(f'| `{name}` | {func_counter[name]} |')
    md += ['', '## 数据符号（Top 30，来自数据表或用户输入，不是节点）', '', '| 符号 | 出现次数 |', '| --- | --- |']
    for name, count in param_counter.most_common(30):
        md.append(f'| `{name}` | {count} |')
    md += ['', '## 模板函数使用频次（Top 25）', '', '| 函数 | 次数 |', '| --- | --- |']
    for name, count in func_counter.most_common(25):
        md.append(f'| `{name}` | {count} |')
    md += ['', '## 公式样例（前 12 条，含函数与符号）', '',
           '| IID | SYMBOL | 标题 | 函数 | 数据符号（前 4） |', '| --- | --- | --- | --- | --- |']
    for r in rows[:12]:
        funcs = ', '.join(f'`{f}`' for f in r['funcs'][:3]) or '—'
        params = ', '.join(f'`{p}`' for p in r['params'][:4]) or '—'
        md.append(f"| {r['iid']} | `{r['symbol']}` | {r['title'] or '—'} | {funcs} | {params} |")
    md += ['', '## 下一步', '',
           '1. 未注册符号逐个判定：是"节点名"（应出现在 379 名单里但没匹配上）、"数据列"还是"中间量"；',
           '2. 把已绑定公式的参数映射到 `raw/db/*.json` 的列（风压/强度/密度/系数）；',
           '3. 取一条公式做端到端复算（L8 最小切片）。']
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(f'formulas={len(rows)} funcs={len(funcs_all)} funcs_registered={len(funcs_registered)} '
          f'symbols={len(param_counter)} symbols_in_registered={len(param_in_registered)}')


if __name__ == '__main__':
    sys.exit(main())
