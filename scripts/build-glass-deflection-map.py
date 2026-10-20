"""Build the glass-deflection orchestration map (symbol -> engine node) from the formula library.

Inputs (all already collected, no ECS access):
  migration_workspace/formulas.json           2,079 decoded formula templates
  migration_workspace/raw/cxmap-arity.json    registered node names (+ arity when known)
  migration_workspace/raw/cxmap-bindings.json node name -> constructor implementation function
  migration_workspace/raw/nodes/*.rea.json    per-node decompilation (presence check only)

Output:
  migration_workspace/glass-deflection-map.md
  migration_workspace/raw/glass-deflection-map.json

The script only reports what the bytes say: a call is "resolved" only when the name exists in
the registry; the arity is reported as a check, never corrected. Anything unmatched stays
unresolved with the raw text so it can be chased later.
"""
import json
import re
import sys
from pathlib import Path

WS = Path('migration_workspace')
FAMILY = re.compile(r'^(MG_)?(WDISPLACEMENT[A-Z]*|GLASSRIBDISP[A-Z]*|GLASSFEDISPMENT[A-Z]*)$')


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'cannot read {path}: {error}') from error


def split_args(body):
    """Split a call argument list on top-level commas, keeping nested lists intact."""
    parts, depth, current, i = [], 0, [], 0
    while i < len(body):
        ch = body[i]
        if body.startswith('${', i):
            depth += 1
            current.append('${')
            i += 2
            continue
        if ch == '}' and depth:
            depth -= 1
            current.append('}')
            i += 1
            continue
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    if current or parts:
        parts.append(''.join(current).strip())
    return [p for p in parts if p != '']


def iid_key(formula):
    try:
        return int(formula['iid'])
    except (KeyError, TypeError, ValueError):
        return -1


def walk(text):
    """Yield (kind, payload) for every ${...} token, recursing into conditional bodies."""
    i, n = 0, len(text)
    while i < n:
        start = text.find('${', i)
        if start < 0:
            return
        depth, j = 0, start
        while j < n:
            if text.startswith('${', j):
                depth += 1
                j += 2
                continue
            if text[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j >= n:
            yield ('unterminated', text[start:start + 80])
            return
        inner = text[start + 2:j]
        head, sep, body = inner.partition(':')
        head = head.strip()
        if sep:
            operator = ''
            tail = body
            if body[:1] in '+*':
                operator = body[0]
                tail = body[1:]
            yield ('conditional', {'head': head, 'operator': operator, 'body': tail})
            yield from walk(tail)
        call = re.match(r'^([A-Za-z_]\w*)\s*\((.*)\)$', head, re.S)
        if call:
            yield ('call', {'name': call.group(1), 'args': split_args(call.group(2))})
        elif head:
            yield ('variable', head)
        i = j + 1


def main():
    formulas = load(WS / 'formulas.json')
    arity = {row['name']: row.get('arity') for row in load(WS / 'raw/cxmap-arity.json')}
    bindings = load(WS / 'raw/cxmap-bindings.json')['bindings']
    impl = {row['name']: row.get('ctor') for row in bindings}
    node_paths = {p.name[:-len('.rea.json')]: p for p in (WS / 'raw/nodes').glob('*.rea.json')}
    node_files = set(node_paths)
    registry = set(arity) | set(impl) | node_files
    # 143 nodes take positional parameters ($0/$1...), so a call arity that differs from the
    # registry's is not necessarily an error; flag variadic nodes instead of guessing.
    variadic = set()
    for name, path in node_paths.items():
        try:
            body = json.loads(path.read_text(encoding='utf-8')).get('normalized_result') or ''
        except (OSError, json.JSONDecodeError):
            continue
        # only the positional-parameter marker counts as variadic (see VERIFICATION.md B2);
        # "contains look_string" is true for most nodes and would make the bucket meaningless.
        if '$0' in body:
            variadic.add(name)

    selected = [f for f in formulas if FAMILY.match(f['symbol'])]
    if not selected:
        raise SystemExit('no glass-deflection formulas selected')

    report = {'selection_rule': FAMILY.pattern, 'formulas': [], 'unresolved': {}, 'variadic': {},
              'summary': {}}
    totals = {'calls': 0, 'resolved': 0, 'arity_ok': 0, 'arity_mismatch': 0, 'arity_unknown': 0,
              'arity_variadic': 0, 'variables': 0, 'conditionals': 0}
    per_formula = []

    for formula in sorted(selected, key=iid_key):
        calls, variables, conditionals = {}, set(), []
        for kind, payload in walk(formula['text']):
            if kind == 'call':
                name = payload['name']
                got = len(payload['args'])
                entry = calls.setdefault(name, {'count': 0, 'call_arity': set(), 'resolved': name in registry})
                entry['count'] += 1
                entry['call_arity'].add(got)
                totals['calls'] += 1
                if entry['resolved']:
                    totals['resolved'] += 1
                    want = arity.get(name)
                    if want == got:
                        totals['arity_ok'] += 1
                    elif want is None or name in variadic:
                        totals['arity_variadic'] += 1
                        report['variadic'].setdefault(name, set()).add(
                            f'{got} args in {formula["symbol"]} (registry arity {want})')
                    else:
                        totals['arity_mismatch'] += 1
                        report['unresolved'].setdefault(name, set()).add(
                            f'arity {got} in {formula["symbol"]} vs registry {want}')
                else:
                    report['unresolved'].setdefault(name, set()).add(f'not in registry ({formula["symbol"]})')
            elif kind == 'variable':
                variables.add(payload)
                totals['variables'] += 1
            elif kind == 'conditional':
                conditionals.append(payload)
                totals['conditionals'] += 1
            elif kind == 'unterminated':
                report['unresolved'].setdefault('UNTERMINATED_TOKEN', set()).add(payload)
        per_formula.append({
            'iid': formula['iid'], 'symbol': formula['symbol'], 'bytes': formula['bytes'],
            'calls': {k: {'count': v['count'], 'call_arity': sorted(v['call_arity']),
                          'resolved': v['resolved'], 'impl': impl.get(k),
                          'registry_arity': arity.get(k)} for k, v in calls.items()},
            'variables': sorted(variables),
            'conditionals': conditionals,
        })

    report['formulas'] = per_formula
    report['summary'] = totals
    report['unresolved'] = {k: sorted(v) for k, v in report['unresolved'].items()}
    report['variadic'] = {k: sorted(v) for k, v in report['variadic'].items()}
    # how common are the unregistered names across the whole library?
    library = ''.join(f['text'] for f in formulas)
    report['library_occurrences'] = {
        name: library.count('${' + name) for name in report['unresolved']
    }
    (WS / 'raw/glass-deflection-map.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')

    # ---- markdown ----
    lines = ['# 玻璃挠度体系：公式 → 引擎节点 映射（L5/L8 样板，第 1 步）', '',
             f'- 选取规则：`{FAMILY.pattern}`（来自 `formulas.json`，共 {len(selected)} 条模板）',
             f'- 调用总数 {totals["calls"]}：命中注册名 {totals["resolved"]}，'
             f'形参个数与注册元数一致 {totals["arity_ok"]}、可变参数节点 {totals["arity_variadic"]}、'
             f'**真正不一致 {totals["arity_mismatch"]}**',
             f'- 普通变量引用 {totals["variables"]} 次、条件块 {totals["conditionals"]} 个',
             '- 判定口径：**只有名字出现在 379 注册表里才算命中**；形参个数只作为核对，不做纠正。', '']
    for row in per_formula:
        lines += [f'## `{row["symbol"]}`（iid {row["iid"]}，{row["bytes"]} B）', '',
                  '| 节点调用 | 出现次数 | 公式里实参个数 | 注册元数 | 注册表命中 | 构造实现函数 |',
                  '| --- | --- | --- | --- | --- | --- |']
        for name, info in sorted(row['calls'].items()):
            lines.append(f'| `{name}` | {info["count"]} | {info["call_arity"]} | '
                         f'{info["registry_arity"]} | {"是" if info["resolved"] else "否"} | '
                         f'`{info["impl"]}` |')
        if row['conditionals']:
            lines += ['', '条件块：']
            for cond in row['conditionals']:
                body = cond['body'].replace('\n', ' ')[:90]
                lines.append(f'- `{cond["head"]}` 运算 `{cond["operator"] or "-"}` → `{body}`')
        lines += ['', f'普通变量（{len(row["variables"])}）：' +
                  (', '.join(f'`{v}`' for v in row['variables']) if row['variables'] else '无'), '']
    if report['unresolved']:
        lines += ['## 未解析（需继续取证）', '']
        for name, why in report['unresolved'].items():
            occ = report['library_occurrences'].get(name)
            lines.append(f'- `{name}`：' + '；'.join(why) + f'（全库出现 {occ} 次）')
        lines.append('')
    if report['variadic']:
        lines += ['## 可变参数节点（形参个数不参与判定）', '']
        for name, why in report['variadic'].items():
            lines.append(f'- `{name}`：' + '；'.join(sorted(why)[:4]))
        lines.append('')
    # does the node engine get invoked from the templates at all?
    lib_calls = {name: library.count('${' + name) for name in sorted(registry)}
    glass_nodes = ['CalGlassDisp', 'CalGlassPSDisp', 'CalGlassStress', 'CalGlassPSStress']
    never = [n for n in lib_calls if lib_calls[n] == 0]
    report['node_call_sites'] = {n: lib_calls[n] for n in glass_nodes}
    report['nodes_never_called'] = len(never)
    (WS / 'raw/glass-deflection-map.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    # ---- input classification and branch inventory (same pass, reproducible) ----
    prefix = {}
    for row in per_formula:
        for var in row['variables']:
            key = var.split('_')[0] if '_' in var else ('other')
            prefix.setdefault(key, set()).add(var)
    branch_heads = {}
    for row in per_formula:
        for cond in row['conditionals']:
            branch_heads.setdefault(cond['head'], []).append(
                {'symbol': row['symbol'], 'operator': cond['operator'],
                 'body': cond['body'].replace('\n', ' ')[:80]})
    report['input_prefixes'] = {k: sorted(v) for k, v in sorted(prefix.items())}
    report['branch_heads'] = {k: v for k, v in sorted(branch_heads.items(), key=lambda kv: -len(kv[1]))}
    (WS / 'raw/glass-deflection-map.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')

    lines += ['## 输入面（按前缀归类）', '',
              '| 前缀 | 不同符号数 | 符号 |', '| --- | --- | --- |']
    for key, names in sorted(prefix.items(), key=lambda kv: -len(kv[1])):
        ordered = sorted(names)
        shown = ', '.join(f'`{n}`' for n in ordered[:8]) + (' …' if len(ordered) > 8 else '')
        lines.append(f'| `{key}` | {len(names)} | {shown} |')
    lines += ['', '## 分支面（条件块按判定函数归类）', '',
              '| 判定 | 出现次数 | 例 |', '| --- | --- | --- |']
    for head, items in sorted(branch_heads.items(), key=lambda kv: -len(kv[1])):
        example = items[0]
        lines.append(f'| `{head}` | {len(items)} | `{example["operator"] or "-"}` '
                     f'{example["body"][:60]} |')
    lines += ['', '## 节点库的调用面（同一次统计）', '',
              f'- 379 个注册节点里，**{len(never)} 个在全部 {len(formulas)} 条公式模板中一次都没被调用**',
              '- 玻璃四个算量节点的模板调用次数：' +
              '、'.join(f'`{n}`={lib_calls[n]}' for n in glass_nodes), '',
              '即：模板层与节点层是**两套各自实现同一物理量的机制**，模板不走节点。', '',
              '## 这一步能证明什么、不能证明什么', '',
              '- 能证明：这些模板里出现的引擎调用名，哪些确实是注册节点、实参个数与注册元数对不对得上。',
              '- 不能证明：调用顺序、默认值注入、查表数据来源，以及**这份模板是否就是运行时真正走的那条路**',
              '  （同一物理量还存在于节点 `CalGlassDisp` 的自有算式中，两者参数化不同，谁被调用需另行取证）。']
    (WS / 'glass-deflection-map.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(json.dumps({'status': 'OK', 'formulas': len(selected), **totals,
                      'unresolved': list(report['unresolved'])}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
