#!/usr/bin/env python3
"""从已归档的节点反编译里抽出「参名 → 算术表达式」(L5 / A 路线)。

输入：`migration_workspace/raw/nodes/<名字>.rea.json`（REA 反编译，`normalized_result` 是 Ghidra 伪代码）
输出：`migration_workspace/raw/nodes-expr.json` + `migration_workspace/nodes-expr.md`

提取是**机械替换**，不做语义推断。规则全部来自模板实测（`CalGlassDisp` 已人工核对）：

1. `XYUtil::String::String(<local>,"<名>")` → `local` ↔ 参数名；
2. 随即 `look_string(..., local, ...)` 的结果变量 `<W>` ↔ 同一个参数名；
3. `X = **(code **)(*W + 0xa8))(…)` 取该参数对象的数值容器，`*(double *)(X + 8)` 即数值；
4. `dVar/fVar = …` 逻辑语句按出现顺序做代入（先做多行拼接）。

状态：
- `EXPR`：解析到 ≥1 个参数名，且存在喂给 `CXConstant::CXConstant` 的赋值；
- `PARTIAL`：有算术但参数名没绑全 / 未定位到 CXConstant 入参；
- `NO_ARITH`：没有 dVar/fVar 赋值（绘图、集合、字符串类节点）。
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
HELPERS_DIR = RAW / 'helpers'

STR_CREATE = re.compile(r'XYUtil::String::String\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)')
LOOK = re.compile(r'(\w+)\s*=\s*[^;]*?look_string\([^,]*,\s*\(?[^,]*?&?\s*(\w+)\s*[,)]')
ALIAS = re.compile(r'^(\w+)\s*=\s*(\w+)$')
FETCH = re.compile(r'(\w+)\s*=\s*\(\*\*\(code \*\*\)\(\*\(?(?:longlong \*\))?\s*(\w+)\)?\s*\+\s*0xa8\)\)')
DOUBLE_OF = re.compile(r'\*\(double \*\)\(\s*(\w+)\s*\+\s*8\)')
# 变参取第 i 个实参：`X = (**(code **)(*W + 0x180))(W, idx)`
FETCH_ARG = re.compile(r'(\w+)\s*=\s*(?:\([\w ]+\*\))?\s*\(?\*\*\(code \*\*\)\(\*\s*(\w+)\s*\+\s*0x180\)\)\(\s*\2\s*,\s*([^)]+)\)')
CAST_OF = re.compile(r'\(double \*\)\(\s*(\w+)\s*\+\s*8\)')
CTOR = re.compile(r'CXConstant::CXConstant\(\s*\w+\s*,\s*([\w.]+)\s*,')
ARITH = re.compile(r'^([df]Var\d+|local_[0-9a-f]+)\s*=\s*(.+)$')
# C 强转 / 去引用：`(double)`、`*(double *)(x + 8)` 这类不是算术，先剔掉再判运算符
CASTISH = r'(?:double|float|int|uint|char|bool|ulong|ulonglong|longlong|undefined\d*|code|CX\w+|String|NCollection_\w+)'
DEREF = re.compile(rf'\*\(\s*{CASTISH}\s*\*?\s*\)')
CAST = re.compile(rf'\(\s*{CASTISH}\s*\*?\s*\)')
BINARY = re.compile(r'[A-Za-z0-9_$)\]]\s*[+\-*/]\s*[A-Za-z0-9_$(]')
# 同一操作数自相减/自相除，通常说明两个不同取值被错绑成同一个参数（需人工复核）
SELF_CANCEL = re.compile(r'\((\$?\w+|p\[[^\]]+\])\)\s*[-/]\s*\(\1\)')
OFFSET = re.compile(r'0x[0-9a-fA-F]+')
# `(uVarA = SUB84(dVarX,0), uVarB = (int)((ulonglong)dVarX >> 0x20), …)`：把 double 拆成两个 u32 再拼回
SPLIT = re.compile(r'\(?\s*(\w+)\s*=\s*SUB84\((\w+),\s*0\)\s*,\s*(\w+)\s*=\s*\(int\)\(\(ulonglong\)\2\s*>>\s*0x20\)')
CONCAT = re.compile(r'CONCAT44\(\s*(\w+)\s*,\s*(\w+)\s*\)')
# 另一写法：先取低 32 位、再取高 32 位（同一对象 +8 处的 double）
LO_SPLIT = re.compile(r'^(\w+)\s*=\s*\(undefined4\)\s*\*\(undefined8 \*\)\(\s*(\w+)\s*\+\s*8\)$')
HI_SPLIT = re.compile(r'^(\w+)\s*=\s*\(undefined4\)\s*\(\(ulonglong\)\s*\*\(undefined8 \*\)\(\s*(\w+)\s*\+\s*8\)\s*>>\s*0x20\)$')


def statements(pseudo):
    """把伪代码拆成逻辑语句：按 `{`/`}` 断开、把跨行长表达式拼回。"""
    text = pseudo.replace('{', ' ; ').replace('}', ' ; ')
    out, buf = [], []
    for line in text.splitlines():
        code = line.split('//')[0].rstrip()
        if not code.strip():
            continue
        buf.append(code.strip())
        joined = ' '.join(buf)
        if joined.endswith(';'):
            for part in joined.split(';'):
                part = part.strip()
                if part:
                    out.append(part)
            buf = []
    return out


def concat_value(concat, lo, hi, numbers):
    """把 CONCAT44(hi,lo) 还原成被拆的那个 double；候选不唯一时标 sel(…)。"""
    literals = concat.get('__literals__') or {}
    value = literals.get((lo, hi)) or literals.get((hi, lo))
    if value is not None:
        return f'{value:g}'
    sources = concat.get((lo, hi)) or concat.get((hi, lo))
    if not sources:
        return f'p[CONCAT44({hi},{lo})]'
    resolved = sorted({numbers.get(s, s) for s in sources})
    if len(resolved) == 1:
        return resolved[0]
    return 'sel(' + '|'.join(resolved) + ')'


MAX_EXPR = 4000          # 单条算式长度上限，防代入爆炸
MAX_INLINE = 600         # 代入时忽略过长的中间值


NESTED_P = re.compile(r'p\[\(p\[([^\]]+)\]\)\]')


def tidy(expr):
    """清理代入产生的嵌套包装：`p[(p[x])]` → `p[x]`，`((x))` → `(x)`。"""
    prev = None
    while prev != expr:
        prev = expr
        expr = NESTED_P.sub(lambda m: f'p[{m.group(1)}]', expr)
    return expr


def subst_all(expr, values):
    """把已绑定的寄存器变量/参数名代入表达式（长的先代，避免 M/N 这类短名误伤）。"""
    for name, value in sorted(values.items(), key=lambda kv: -len(kv[0])):
        if name == value or len(value) > MAX_INLINE:
            continue
        try:
            expr = re.sub(rf'(?<![\w$]){re.escape(name)}(?![\w$])', f'({value})', expr)
        except re.error:
            continue          # 名字里含非法转义（极少见，来自字符串字面量），跳过该别名
        if len(expr) > MAX_EXPR:
            return expr[:MAX_EXPR] + '…'
    return expr


def param_bindings(stmts):
    """local → 参数名（两跳：String 构造 → look_string 结果）。"""
    by_local = {}
    for st in stmts:
        m = STR_CREATE.search(st)
        if m:
            by_local[m.group(1)] = m.group(2)
    by_var = {}
    for st in stmts:
        m = LOOK.search(st)
        if m and m.group(2) in by_local:
            by_var[m.group(1)] = by_local[m.group(2)]
    return by_var


def resolve_aliases(stmts, known):
    out = dict(known)
    for _ in range(3):
        for st in stmts:
            m = ALIAS.match(st)
            if not m:
                continue
            dst, src = m.group(1), m.group(2)
            if src in out and dst not in out:
                out[dst] = out[src]
    return out


PURE_REF = re.compile(r'^(?:[A-Za-z_$][\w$]*|\$\d+)$')
HELPER_CALL = re.compile(r'^(?:[A-Za-z_]\w*\s*)?\(?\s*[^()]*\)?\s*(FUN_[0-9a-f]+)\s*\(')


def load_helpers(path):
    """辅助函数表：addr → {kind, global_name, expr}（expr 为 ARITH 类辅助函数自身的算式）。"""
    if not Path(path).exists():
        return {}
    try:
        data = json.loads(Path(path).read_text())
    except json.JSONDecodeError:
        return {}
    table = {row['addr'].lower(): dict(row) for row in data.get('rows', [])}
    tables_path = RAW / 'helper-tables.json'
    if tables_path.exists():
        try:
            for row in json.loads(tables_path.read_text()):
                addr = row['addr'].lower()
                if addr in table:
                    table[addr]['table'] = {
                        'conditions': row.get('conditions') or [],
                        'constants': row.get('constants') or [],
                    }
        except json.JSONDecodeError as exc:
            print(f'warn: helper-tables.json unreadable ({exc})', file=sys.stderr)
    for addr, row in table.items():
        if row.get('kind') != 'ARITH':
            continue
        helper_path = HELPERS_DIR / f'{addr}.rea.json'
        if not helper_path.exists():
            continue
        try:
            pseudo = json.loads(helper_path.read_text()).get('normalized_result') or ''
        except json.JSONDecodeError:
            continue
        info = analyse(pseudo, {})
        if info.get('fused'):
            row['expr'] = info['fused']
    return table


def strip_leading_call(text):
    """去掉语句开头的 `FUN_xxx(...)`（含括号平衡）并返回剩余部分。"""
    m = re.match(r'^(?:\([^()]*\)\s*)?(FUN_[0-9a-f]+)\s*\(', text)
    if not m:
        return text, None
    start = text.index('(', m.start())
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[i + 1:].strip(), (m.group(1), text[start + 1:i])
    return text, None


HEX16 = re.compile(r'0x([0-9a-f]{16})')


def decode_hex_doubles(text):
    """把 `0x4008000000000000` 这类十六进制打包的 double 字面量解成可读数。"""
    def repl(m):
        raw = m.group(1)
        try:
            packed = bytes.fromhex(raw)[::-1]
            value = struct.unpack('<d', packed)[0]
        except (ValueError, TypeError, struct.error):
            return m.group(0)
        if math.isnan(value) or math.isinf(value) or not (1e-9 < abs(value) < 1e12):
            return m.group(0)
        return f'{value:g}'
    try:
        return HEX16.sub(repl, text)
    except (TypeError, re.error):
        return text


def split_args(text):
    """按顶层逗号拆分实参。"""
    args, depth, cur = [], 0, ''
    for ch in text:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            args.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


def inline_helper(info, args_text, numbers):
    """把辅助函数算式里的 param_N 换成实参；参数个数不符则放弃。"""
    body = info.get('expr')
    if not body:
        return None
    args = split_args(args_text)
    if not args:
        return None
    def repl(m):
        try:
            idx = int(m.group(1))
        except (TypeError, ValueError):
            return m.group(0)
        if 1 <= idx <= len(args):
            return f'({args[idx - 1]})'
        return f'param_{idx}'
    out = re.sub(r'param_(\d+)', repl, body)
    return out if 'param_' not in out else None


def split_pairs(pseudo):
    """u32 拆分/拼接回 double 的候选来源：{(lo,hi): [源变量…]}，附带所在条件语句。"""
    pairs = {}
    notes = {}
    for st in statements(pseudo):
        if 'SUB84' in st and '>>' in st:
            for m in SPLIT.finditer(st):
                notes[(m.group(1), m.group(3))] = st[:220]
    for m in SPLIT.finditer(pseudo):
        pairs.setdefault((m.group(1), m.group(3)), []).append(m.group(2))
    # 直接以字面量写死的 double：连续两条 `uVarA = 0x<lo>; uVarB = 0x<hi>;`
    lit = {}
    stmts = statements(pseudo)
    for first, second in zip(stmts, stmts[1:], strict=False):
        m1 = re.match(r'^(\w+)\s*=\s*(0x[0-9a-f]{1,8})$', first)
        m2 = re.match(r'^(\w+)\s*=\s*(0x[0-9a-f]{1,8})$', second)
        if not (m1 and m2) or m1.group(1) == m2.group(1):
            continue
        lo, hi = int(m1.group(2), 16), int(m2.group(2), 16)
        if hi < 0x3f000000:
            continue
        value = struct.unpack('<d', struct.pack('<II', lo & 0xffffffff, hi & 0xffffffff))[0]
        if 1e-9 < abs(value) < 1e9:
            lit[(m1.group(1), m2.group(1))] = value
    pending = {}
    for st in statements(pseudo):
        lo = LO_SPLIT.match(st)
        if lo:
            pending[lo.group(2)] = lo.group(1)
            continue
        hi = HI_SPLIT.match(st)
        if hi and hi.group(2) in pending:
            pairs.setdefault((pending[hi.group(2)], hi.group(1)), []).append(hi.group(2))
    pairs['__notes__'] = notes
    pairs['__literals__'] = lit
    return pairs


def numeric_block(pseudo):
    """返回“数值分支”子串：含 `+ 0xa8` 取数 且 含 `CXConstant::CXConstant` 的最深分支块。

    eval 的结构是「符号回退分支（新建同类节点并绑定实参）+ else 数值分支」，
    回退分支里的 `FUN_18025xxxx(local, &local)` 是在**构造新节点**，不是取参数，
    因此只能分析数值分支，否则会把构造调用误当取值来源。
    """
    depth, spans, start = 0, [], None
    for i, ch in enumerate(pseudo):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                spans.append(pseudo[start:i + 1])
                start = None
    best, best_score = None, -1
    for span in spans:
        fetches = span.count('+ 0xa8')
        if fetches and 'CXConstant::CXConstant' in span:
            score = fetches
            if score > best_score:
                best, best_score = span, score
    return best or pseudo


def analyse(pseudo, helpers=None, name_upper=''):
    """按语句顺序增量维护绑定：同一寄存器变量会被重用于不同参数，不能用最终态回填。"""
    helpers = helpers or {}
    scope = numeric_block(pseudo)
    stmts = statements(scope)
    concat = split_pairs(scope)
    strings, objects, numbers = {}, {}, {}
    external_calls = []
    tables_used = []
    interp_used = []
    steps, env = [], {}
    for st in stmts:
        m = STR_CREATE.search(st)
        if m:
            strings[m.group(1)] = m.group(2)
            continue
        m = LOOK.search(st)
        if m and m.group(2) in strings:
            objects[m.group(1)] = strings[m.group(2)]
            continue
        m = FETCH.search(st)
        if m:
            owner = objects.get(m.group(2)) or numbers.get(m.group(2))
            if owner:
                numbers[m.group(1)] = owner
            continue
        m = FETCH_ARG.search(st)
        if m:
            owner = objects.get(m.group(2))
            idx = m.group(3).strip()
            if idx.startswith('(int)'):
                idx = idx[5:].strip()
            numbers[m.group(1)] = f'{owner}[{idx}]' if owner else f'p[{m.group(1)}]'
            continue
        m = ALIAS.match(st)
        if m:
            dst, src = m.group(1), m.group(2)
            if src in objects:
                objects[dst] = objects[src]
            elif src in numbers:
                numbers[dst] = numbers[src]
            continue
        m = ARITH.match(st)
        if not m:
            continue
        target, rhs = m.group(1), m.group(2)
        expr = DOUBLE_OF.sub(lambda g: numbers.get(g.group(1), f'p[{g.group(1)}]'), rhs)
        expr = CONCAT.sub(lambda g: concat_value(concat, g.group(1), g.group(2), numbers), expr)
        expr = CAST_OF.sub(lambda g: f'num({numbers.get(g.group(1), g.group(1))})', expr)
        if '(code **)' in expr or 'look_string' in expr or 'MMgt::' in expr:
            continue
        # 纯取值行（`dVar1 = *(double *)(lVar + 8)` 或 `dVar1 = (double)FUN_x(...)`）
        # 不当作算术步，只登记别名，供后续表达式代入。
        plain = CAST.sub('', expr).strip()
        rest, call = strip_leading_call(plain)
        if call and rest == '':
            addr = call[0].lower()
            info = helpers.get(addr)
            if info and info.get('kind') == 'GLOBAL_GETTER' and info.get('global_name'):
                numbers[target] = info['global_name']
                continue
            if info and info.get('kind') == 'RNG':
                numbers[target] = 'RNG()'
                continue
            if info and info.get('kind') == 'ARITH' and info.get('expr'):
                inlined = inline_helper(info, call[1], numbers)
                numbers[target] = inlined or f'f[{addr}]({call[1]})'
                continue
            if info and info.get('kind') == 'NODE_CTOR':
                # 符号回退分支：这里是在“造节点”，不是取值，整条语句跳过
                continue
            if info and info.get('kind') == 'TABLE_BUILDER':
                numbers[target] = f'BUILDER({call[0]})'
                tables_used.append({'target': target, 'callee': call[0], 'kind': 'TABLE_BUILDER',
                                    'conditions': [], 'constants': []})
                continue
            if info and info.get('kind') == 'VARARG_GET':
                arg_text = decode_hex_doubles(subst_all(call[1], {**numbers, **env}))
                numbers[target] = f'ARG({arg_text})'
                interp_used.append({'target': target, 'callee': call[0], 'kind': 'VARARG_GET'})
                continue
            if info and info.get('kind') == 'INTERPOLATE':
                arg_text = decode_hex_doubles(subst_all(call[1], {**numbers, **env}))
                numbers[target] = f'INTERP({arg_text})'
                interp_used.append({'target': target, 'callee': call[0]})
                continue
            if info and info.get('kind') == 'STRING_TABLE':
                arg_text = decode_hex_doubles(subst_all(call[1], {**numbers, **env}))
                numbers[target] = f'STRLIT({arg_text})'
                interp_used.append({'target': target, 'callee': call[0], 'kind': 'STRING_TABLE'})
                continue
            if info and info.get('table') and (info['table']['conditions'] or info['table']['constants']):
                arg_text = decode_hex_doubles(subst_all(call[1], {**numbers, **env}))
                if re.search(rf'(?<![\w$]){re.escape(target)}(?![\w$])', arg_text):
                    arg_text = f'arg_of({target})'
                numbers[target] = f'table[{addr}]({arg_text})'
                tables_used.append({'target': target, 'callee': call[0], 'arg': arg_text, **info['table']})
                continue
            # 未反编译 / OTHER（错误文案、代理取值等）：不当作已知数值，记为外部调用
            numbers[target] = f'p[{target}]'
            external_calls.append({'target': target, 'callee': call[0]})
            continue
        if plain.startswith(('*(double *)', '*(float *)')):
            continue
        # 纯取值（参数名、`$N[i]` 变参元、`p[…]`）不产生算术步，只登记别名
        if not re.search(r'[-+*/]', plain) and '(' not in plain and len(plain) < 80:
            if plain in env:
                env[target] = env[plain]
            else:
                numbers[target] = plain
            continue
        probe = DEREF.sub('', subst_all(plain, {**numbers, **env}))
        has_operand = any(f' {n} ' in f' {probe} ' for n in numbers.values()) or bool(re.search(r'\d+\.\d', probe)) or '$' in probe
        if not ((BINARY.search(probe) and has_operand and not OFFSET.search(probe)) or 'pow(' in probe):
            continue
        expr = subst_all(expr, {**numbers, **env})
        acc = re.match(rf'^\(?{re.escape(target)}\)?\s*([+\-])\s*(.+)$', expr)
        if acc and acc.group(1) == '+':
            expr = f'SUM({acc.group(2)})'
        expr = tidy(expr)
        env[target] = expr
        steps.append({'target': target, 'expr': expr[:MAX_EXPR]})

    ctor_args = CTOR.findall(pseudo)
    params = sorted(set(objects.values()) | set(strings.values()))
    numeric = sorted(set(numbers.values()))
    fused = steps[-1]['expr'] if steps else None
    if ctor_args and ctor_args[-1] in env:
        fused = env[ctor_args[-1]]
    suspect = bool(SELF_CANCEL.search(fused or ''))
    select_note = None
    if 'sel(' in (fused or ''):
        for key, note in (concat.get('__notes__') or {}).items():
            if isinstance(key, tuple):
                select_note = note
                break
    if not fused and interp_used:
        fused = ' + '.join(f"{('STRLIT' if t.get('kind') == 'STRING_TABLE' else 'INTERP')}({t['callee'].lower()})"
                            for t in interp_used[:3])
    if not fused and tables_used:
        fused = ' + '.join(f"table[{t['callee'].lower()}]({t.get('arg', t['target'])})" for t in tables_used[:3])
    if not fused and external_calls:
        fused = 'CALL(' + ', '.join(f"{c['callee']}" for c in external_calls[:3]) + ')'
    status = 'NO_ARITH'
    if steps or external_calls or tables_used or interp_used:
        status = 'PARTIAL'
        residual = re.search(r'\b[dfu]Var\d+\b', fused or '')
        is_marker = (fused or '').startswith('CALL(')
        clean_expr = (steps and not external_calls and not tables_used and not interp_used
                      and numeric and ctor_args and 'p[' not in (fused or '') and not residual)
        if clean_expr:
            status = 'SELECTED' if 'sel(' in (fused or '') else 'EXPR'
        elif not steps and external_calls and is_marker:
            status = 'FE_OP' if name_upper.startswith('FE') else 'EXTERNAL_CALL'
        elif not steps and tables_used and not external_calls:
            status = 'TABLE_BUILDER' if all(t.get('kind') == 'TABLE_BUILDER' for t in tables_used) else 'TABLE_LOOKUP'
        elif not steps and interp_used and not external_calls:
            kinds = {t.get('kind') for t in interp_used}
            if kinds == {'STRING_TABLE'}:
                status = 'STRING_TABLE'
            elif kinds == {'VARARG_GET'}:
                status = 'VARARG_GET'
            else:
                status = 'INTERPOLATION'
    return {
        'status': status,
        'params': params,
        'numeric_params': numeric,
        'steps': steps,
        'fused': fused,
        'ctor_args': ctor_args[:4],
        'suspect': suspect,
        'select_note': select_note,
        'external_calls': external_calls[:6],
        'interp_used': interp_used[:3],
        'tables_used': [{'callee': t['callee'], 'target': t['target'], 'kind': t.get('kind'),
                         'conditions': (t.get('conditions') or [])[:6],
                         'constants': (t.get('constants') or [])[:6]}
                        for t in tables_used[:3]],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=str(RAW / 'nodes-expr.json'))
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'nodes-expr.md'))
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--helpers', default=str(RAW / 'helpers.json'))
    args = ap.parse_args()

    files = sorted(NODES.glob('*.rea.json'))
    if args.limit:
        files = files[:args.limit]
    helpers = load_helpers(args.helpers)
    rows, errors = [], []
    for path in files:
        name = path.stem.replace('.rea', '')
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({'name': name, 'error': str(exc)})
            continue
        pseudo = data.get('normalized_result') or ''
        if not pseudo:
            errors.append({'name': name, 'error': 'no normalized_result'})
            continue
        rows.append({'name': name, 'evidence_id': data.get('evidence_id'),
                     **analyse(pseudo, helpers, name.upper())})

    counts = {}
    for row in rows:
        counts[row['status']] = counts.get(row['status'], 0) + 1
    Path(args.json).write_text(json.dumps(
        {'generated_from': str(NODES), 'counts': counts, 'rows': rows},
        ensure_ascii=False, indent=1) + '\n')

    md = ['# 节点算式抽取（L5 / A 路线，机械替换，未做语义推断）', '',
          f'- 输入：`migration_workspace/raw/nodes/*.rea.json`（{len(files)} 份）',
          '- 状态分布：' + '、'.join(f'`{k}`={v}' for k, v in sorted(counts.items())),
          f'- 失败：{len(errors)}',
          '',
          '规则（`CalGlassDisp` 已人工核对，见 `calculation-core.md` §9）：',
          '',
          '1. `String::String(<local>,"名")` → `local` 绑定该参数名；',
          '2. 随后 `look_string(…, <local>, …)` 的结果变量绑定同名参数（含 `local_x = pVar5;` 别名）；',
          '3. `X = **(code **)(*W + 0xa8))(…)` 是该参数的数值对象，`*(double *)(X + 8)` 为数值；',
          '4. `dVar/fVar = …` 逻辑语句按出现顺序代入（多行表达式先拼接）。',
          '',
          '`p[变量]` = 该取值变量未能绑定到参数名，**保持未知、不猜**。',
          '',
          '| 节点 | 状态 | 解析到的参数名 | 代入后的表达式 |',
          '| --- | --- | --- | --- |']
    for row in sorted(rows, key=lambda r: (r['status'] != 'EXPR', r['name'])):
        params = ', '.join(f'`{p}`' for p in row['params']) or '—'
        expr = (row['fused'] or '—').replace('|', r'\|')
        if len(expr) > 240:
            expr = expr[:237] + '…'
        md.append(f"| `{row['name']}` | {row['status']} | {params} | `{expr}` |")
    if errors:
        md += ['', '## 失败清单', '']
        md += [f"- `{e['name']}`：{e['error']}" for e in errors]
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(json.dumps(counts, ensure_ascii=False))
    print(f'rows={len(rows)} errors={len(errors)} -> {args.md}')


if __name__ == '__main__':
    sys.exit(main())
