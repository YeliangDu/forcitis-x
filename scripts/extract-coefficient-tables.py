"""Decode the static coefficient tables behind the two lookup nodes `GetSDr` / `GetSMr`.

Background
----------
`FUN_1802a0fa0` (`GetSDr`, 挠度系数 μ) and `FUN_1802a2940` (`GetSMr`, 弯矩系数 m) are the same
shape: read the (up to four) positional arguments, normalise them into an edge ratio, then feed
`FUN_180299d50(ratio, xAxis, yAxis)` — the shared piecewise-linear interpolator. Which axis pair is
used depends on the third argument `$2` (material / member code) and, on some paths, the fourth
argument `$3` (support / edge code). A few branches return a constant instead of a table.

Both node bodies pass the axis addresses as immediates, so the whole decision tree can be
transcribed from the shipped pseudo-code and the blobs decoded straight out of `.data`:

    [double count][count x double]      per axis (count stored as IEEE double, e.g. 14.0)

`FUN_180299d50` clamps below the first and above the last node, otherwise interpolates linearly
between neighbours, so this tool reproduces the node exactly.

Everything below is transcribed from the decompiled bodies (see `migration_workspace/
coefficient-tables.md` for the quote-by-quote mapping); the tool re-derives the numbers from the PE
and checks them against the coefficients the original itself printed.

Usage: python3 scripts/extract-coefficient-tables.py [--json <out>]
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

PE = Path('evidence/baseline/extracted/cab/_1D7374B2004D4FE39A79BCDFC9340FB8')  # HWKWallUtil.dll
OUT = Path('migration_workspace/raw/coefficient-tables.json')
IMAGE_BASE = 0x180000000

# --- axis pairs, named after their role ------------------------------------------------
# VA pairs are verbatim from the decompiled branch bodies (see BRANCHES below).
PAIRS = {
    'mu.glass.2arg':       (0x180544ba0, 0x180544c20),  # GetSDr($0,$1): 0,0.2,0.25,0.33,0.5..1
    'mu.glass.code11':     (0x180543e80, 0x180543f40),  # GetSDr($0,$1,11): 0.5..1 (铝板同表)
    'mu.glass.code13':     (0x180545060, 0x1805450c0),
    'mu.glass.code14':     (0x180545120, 0x1805451b0),
    'mu.glass.code15':     (0x180545240, 0x1805452d0),
    'mu.glass.code21':     (0x180543e80, None),         # y picked by $1<$0, see SIDE_PAIRS
    'mu.glass.code22':     (0x180543e80, None),
    'mu.point.4edge':      (0x180544f60, 0x180544fe0),  # $2=2, (int)$3==4
    'mu.point.other':      (0x180544e80, 0x180544ef0),  # $2=2, otherwise; ratio=(b/a)*0.5
    'm.glass.2arg':        (0x180544a20, 0x180544aa0),  # GetSMr($0,$1) / $2 in {0,9,20,[30,40),42}
    'm.point.six':         (0x180544ca0, 0x180544d20),  # $2=2 && (int)$3==6
    'm.point.other':       (0x180544da0, 0x180544e10),  # $2=2 otherwise; ratio=$0/($1*0.5)
    'm.code4':             (0x180543e80, 0x180545360),
    'm.code11.support20':  (0x180543e80, 0x180544300),
    'm.code11.support25':  (0x180543e80, 0x1805442a0),
    'm.code11.support30':  (0x180543e80, 0x180544360),
    'm.code11.other':      (0x180543e80, 0x1805443c0),
    'm.code3.support20':   (0x180543df0, 0x180545450),
    'm.code3.support25':   (0x180543df0, 0x1805454e0),
    'm.code3.support30':   (0x180543df0, 0x180545570),
    'm.code3.other':       (0x180543df0, 0x1805453c0),
}

# branches whose y axis is chosen by comparing the two raw edge lengths ($1 < $0)
SIDE_PAIRS = {
    ('mu.glass.code21', '$1 < $0'): 0x180544000,
    ('mu.glass.code21', 'else'):    0x1805440c0,
    ('mu.glass.code22', '$1 < $0'): 0x180544180,
    ('mu.glass.code22', 'else'):    0x180544240,
    ('m.code21', '$1 < $0'):        0x180543fa0,
    ('m.code21', 'else'):           0x180544060,
    ('m.code22', '$1 < $0'):        0x180544120,
    ('m.code22', 'else'):           0x1805441e0,
}
PAIRS['m.code21'] = (0x180543e80, None)
PAIRS['m.code22'] = (0x180543e80, None)

# --- branch model ----------------------------------------------------------------------
# `code` is the constant the node stores next to the result (visible in the pseudo-code as
# `local_128 = ...` / `local_138 = ...`), kept because it is the only branch id the binary shows.
# `cond` is the transcribed C condition; `match` lists the $2 / $3 values it accepts.
BRANCHES = {
    'GetSDr': [
        {'code': None, 'cond': 'argc < 2',
         'action': 'error/degenerate: FUN_1802986b0 on a 0x7fffff dummy constant', 'table': None},
        {'code': '0x2', 'cond': 'argc == 2 (any $2)',
         'action': 'table', 'table': 'mu.glass.2arg', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x4', 'cond': '$2 == 1',
         'action': 'const 0.013', 'table': None},
        {'code': '0x8', 'cond': '$2 in {0} or ~{20} or ~{9} or [30,40) or ~{42}',
         'action': 'table', 'table': 'mu.glass.2arg', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x10', 'cond': '$2 == 2',
         'action': 'table by $3', 'ratio': 'min/max if (int)$3==4 else ($1/$0)*0.5',
         'table_by_support': {'4': 'mu.point.4edge', 'else': 'mu.point.other'}},
        {'code': '0x20', 'cond': '$2 == 11',
         'action': 'table', 'table': 'mu.glass.code11', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x40', 'cond': '$2 == 21',
         'action': 'table', 'table': 'mu.glass.code21', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x80', 'cond': '$2 == 22',
         'action': 'table', 'table': 'mu.glass.code22', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x100', 'cond': '$2 == 13',
         'action': 'table', 'table': 'mu.glass.code13', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x200', 'cond': '$2 == 14',
         'action': 'table', 'table': 'mu.glass.code14', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x400', 'cond': '$2 == 15',
         'action': 'table', 'table': 'mu.glass.code15', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x800', 'cond': 'no other branch matched',
         'action': 'const 0.0', 'table': None},
    ],
    'GetSMr': [
        {'code': None, 'cond': 'argc < 2',
         'action': 'error/degenerate: FUN_180298f50 on a 0x7fffff dummy constant', 'table': None},
        {'code': '0x2', 'cond': 'argc == 2 (any $2)',
         'action': 'table', 'table': 'm.glass.2arg', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x4', 'cond': '$2 in {1} or {5} or {8}',
         'action': 'const 0.125', 'table': None},
        {'code': '0x8', 'cond': '$2 in {0} or ~{20} or ~{9} or [30,40) or ~{42}',
         'action': 'table', 'table': 'm.glass.2arg', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x10', 'cond': '$2 == 2',
         'action': 'table by $3', 'ratio': 'min/max if (int)$3==6 else $0/($1*0.5)',
         'table_by_support': {'6': 'm.point.six', 'else': 'm.point.other'}},
        {'code': '0x20', 'cond': '$2 == 3 (fall-through tail branch)',
         'action': 'table by $3', 'ratio': 'min($0,$1)/max($0,$1)',
         'table_by_support': {'20': 'm.code3.support20', '25': 'm.code3.support25',
                              '30': 'm.code3.support30', 'else': 'm.code3.other'}},
        {'code': '0x40', 'cond': '$2 == 4',
         'action': 'table', 'table': 'm.code4', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x80', 'cond': '$2 == 11',
         'action': 'table by $3', 'ratio': 'min($0,$1)/max($0,$1)',
         'table_by_support': {'20': 'm.code11.support20', '25': 'm.code11.support25',
                              '30': 'm.code11.support30', 'else': 'm.code11.other'}},
        {'code': '0x100', 'cond': '$2 == 21',
         'action': 'table', 'table': 'm.code21', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x200', 'cond': '$2 == 22',
         'action': 'table', 'table': 'm.code22', 'ratio': 'min($0,$1)/max($0,$1)'},
        {'code': '0x400', 'cond': 'no other branch matched',
         'action': 'const 0.0', 'table': None},
    ],
}

# --- anchors: coefficients the original printed in the frozen sample's calculation book ------
# evidence/stages/B02/B02-02/attempt-47/acceptance/frozen-report-head.txt
ANCHORS = [
    # (label, node, table, ratio, expected, tolerance, original text)
    ('μ 玻璃 2 参 (a/b=1)', 'GetSDr', 'mu.glass.2arg', 1.0, 0.00406, 5e-9,
     'μ: 挠度系数,按边长比a/b查 表6.1.3得: 0.00406'),
    ('μ 玻璃 $2=11 (a/b=1)', 'GetSDr', 'mu.glass.code11', 1.0, 0.00406, 5e-9,
     '同一样例的 11 点表在 a/b=1 处必须与 2 参表一致'),
    ('m 玻璃 2 参 (a/b=1)', 'GetSMr', 'm.glass.2arg', 1.0, 0.0442, 5e-9,
     'm: 玻璃板面跨中弯曲系数,按边长比a/b查表 6.1.2-1得: 0.0442'),
    ('m 玻璃 $2=0 (a/b=1)', 'GetSMr', 'm.glass.2arg', 1.0, 0.0442, 5e-9,
     '模板 GetSMr(al,bl,PRJGLASS,LINKNUM) 在 PRJGLASS=0 时走 $2 in {0,...} 分支'),
]

# data sanity: first/last x of the μ and m glass tables (from the printed report ranges)
SHAPE_CHECKS = [
    ('mu.glass.code11', 0.5, 1.0, 'μ 表从 a/b=0.5 起（0.01013）到 1.0 止 0.00406'),
    ('mu.glass.2arg', 0.0, 1.0, '2 参表把 a/b<0.5 的点接在 0 起步'),
    ('m.glass.2arg', 0.0, 1.0, 'm 表 0..1'),
    ('m.code3.other', 0.0, 1.0, '石材族 16 点表 0..1'),
]


def sections(data):
    pe_off = struct.unpack_from('<I', data, 0x3C)[0]
    coff = pe_off + 4
    n = struct.unpack_from('<H', data, coff + 2)[0]
    opt_size = struct.unpack_from('<H', data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from('<H', data, opt)[0]
    base = (struct.unpack_from('<Q', data, opt + 24)[0] if magic == 0x20B
            else struct.unpack_from('<I', data, opt + 28)[0])
    out = []
    sec = opt + opt_size
    for i in range(n):
        off = sec + i * 40
        name = data[off:off + 8].rstrip(b'\0').decode('ascii', 'replace')
        vsize, vaddr, rawsize, rawptr = struct.unpack_from('<IIII', data, off + 8)
        out.append((name, vaddr, vsize, rawptr, rawsize))
    return base, out


def read_axis(data, secs, base, va):
    rva = va - base
    for name, vaddr, vsize, rawptr, rawsize in secs:
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            delta = rva - vaddr
            if delta >= rawsize:
                raise SystemExit(f'VA {va:#x} in {name} is zero-fill, no file bytes')
            offset = rawptr + delta
            count = struct.unpack_from('<d', data, offset)[0]
            if not (0 < count <= 64) or int(count) != count:
                raise SystemExit(f'VA {va:#x}: implausible element count {count}')
            count = int(count)
            try:
                values = struct.unpack_from('<' + 'd' * count, data, offset + 8)
            except struct.error as error:
                raise SystemExit(f'VA {va:#x}: table runs past EOF ({error})') from error
            blob = data[offset + 8:offset + 8 + 8 * count]
            return {'va': va, 'section': name, 'offset': offset, 'count': count,
                    'values': list(values),
                    'sha256': hashlib.sha256(blob).hexdigest()}
    raise SystemExit(f'VA {va:#x} not inside any section')


def interpolate(xs, ys, x):
    """Same rule as FUN_180299d50: clamp outside, linear between neighbours."""
    if x <= xs[0]:
        return ys[0], 'clamp-low'
    if x >= xs[-1]:
        return ys[-1], 'clamp-high'
    for i in range(1, len(xs)):
        if x <= xs[i]:
            span = xs[i] - xs[i - 1]
            t = 0.0 if span == 0 else (x - xs[i - 1]) / span
            return ys[i - 1] + t * (ys[i] - ys[i - 1]), f'between {xs[i - 1]:g} and {xs[i]:g}'
    return ys[-1], 'clamp-high'


def main():
    data = PE.read_bytes()
    base, secs = sections(data)
    if base != IMAGE_BASE:
        raise SystemExit(f'unexpected image base {base:#x}')

    vAs = {}
    for x_va, y_va in PAIRS.values():
        for va in (x_va, y_va):
            if va is not None:
                vAs[va] = None
    for va in SIDE_PAIRS.values():
        vAs[va] = None
    tables = {va: read_axis(data, secs, base, va) for va in sorted(vAs)}

    ok = True
    problems = []

    # every table must be a strictly increasing x axis where it is used as one
    for label, (x_va, y_va) in PAIRS.items():
        x = tables[x_va]
        vals = x['values']
        if any(b <= a for a, b in zip(vals, vals[1:], strict=False)):
            ok = False
            problems.append(f'{label}: x axis not strictly increasing at {x_va:#x}')
        if y_va is not None and tables[y_va]['count'] != x['count']:
            ok = False
            problems.append(f'{label}: count mismatch {x["count"]} vs {tables[y_va]["count"]}')

    # the two side-selected y axes of $2=22 are byte-identical: the branch exists but is a no-op
    same_22 = tables[0x180544180]['sha256'] == tables[0x180544240]['sha256']

    report = {'pe': str(PE), 'pe_sha256': hashlib.sha256(data).hexdigest(),
              'image_base': base, 'tables': {f'{va:#x}': t for va, t in tables.items()},
              'pairs': {k: {'x': f'{v[0]:#x}', 'y': f'{v[1]:#x}' if v[1] is not None else None}
                        for k, v in PAIRS.items()},
              'side_pairs': {f'{k[0]}|{k[1]}': f'{v:#x}' for k, v in SIDE_PAIRS.items()},
              'shape_checks': [], 'branches': BRANCHES, 'anchors': [],
              'observations': [], 'problems': problems, 'passed': None}

    for label, expected_first, expected_last, why in SHAPE_CHECKS:
        xs = tables[PAIRS[label][0]]['values']
        good = abs(xs[0] - expected_first) <= 1e-9 and abs(xs[-1] - expected_last) <= 1e-9
        ok = ok and good
        report['shape_checks'].append({'label': label, 'x_first': xs[0], 'x_last': xs[-1],
                                       'expected_first': expected_first,
                                       'expected_last': expected_last, 'why': why,
                                       'match': good})
        print(f"{'OK ' if good else 'FAIL'} shape {label:20s} x: {xs[0]:g} .. {xs[-1]:g}")

    for label, node, pair, ratio, expected, tol, why in ANCHORS:
        xs = tables[PAIRS[pair][0]]['values']
        ys = tables[PAIRS[pair][1]]['values']
        value, how = interpolate(xs, ys, ratio)
        good = abs(value - expected) <= tol
        ok = ok and good
        report['anchors'].append({'label': label, 'node': node, 'pair': pair,
                                  'ratio': ratio, 'expected': expected,
                                  'computed': value, 'rule': how,
                                  'tolerance': tol, 'match': good, 'source_text': why})
        print(f"{'OK ' if good else 'FAIL'} anchor {label:22s} {pair:20s} ratio={ratio:<5g} "
              f"computed={value:.9f} expected={expected:<8g} ({how})")

    report['observations'] = [
        '$2 = 13/14/15 与 21/22、以及 $2 in {0,9,20,[30,40),42} 是两套并存的分支：前者索引'
        '定长轴表，后者复用 2 参表；$2 是材料/构件代码（11 = 铝板 ALUS/ALUC，0/1/2 = 玻璃 '
        'PRJGLASS，3 = 石材 STONECAL 的 3 参路径），$3 是支承/边数代码（GetSDr: 4=四边；'
        'GetSMr: 6=六点，20/25/30=石材/铝板细分的支承条件，语义未定）。',
        f'$2 = 22 的两张 y 轴（0x180544180 / 0x180544240）字节完全相同：sha256 一致 = {same_22}，'
        '即该 tie-break 分支存在但对结果无影响。',
        'GetSDr 的 $2=2 非四边分支用 (b/a)*0.5，GetSMr 的 $2=2 非六点分支用 $0/($1*0.5)：'
        '两个节点的写法不同，不可互换。',
        'μ 表（0.01013..0.00406）与 m 表（0.125..0.0442）在 a/b=1 处分别给出原版打印的 '
        '0.00406 / 0.0442；原版计算书把 μ 标成"表6.1.3"、把 η 标成"表6.1.2-2"，与 JGJ102-2003 '
        '编号互为对调，属原版文案问题，复刻时应照抄。',
    ]
    if not same_22:
        ok = False
        problems.append('0x180544180 / 0x180544240 不再相同，观察记录需更新')

    report['passed'] = ok
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    print(f'\ntables decoded: {len(tables)}   branches: '
          f'{sum(len(v) for v in BRANCHES.values())}   json: {OUT}')
    if problems:
        for p in problems:
            print('PROBLEM', p)
    print('RESULT', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
