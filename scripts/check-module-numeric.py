"""Recompute a module's intermediate values from the original's own printed report text.

The reference values come from the calculation book the original produced for the frozen
sample (evidence/stages/B02/B02-02/attempt-47/acceptance/frozen-report-head.txt). Each case
states its formula, the inputs, and the printed result; a mismatch is reported, never rounded
away silently.

The two coefficient lookups are no longer taken as inputs: μ/m come from the tables
`GetSDr`/`GetSMr` index (scripts/extract-coefficient-tables.py) and η from the tables `GetNg`
indexes (scripts/extract-lookup-table.py). Both extractors must have been run first; they are
the only path by which the tables reach this check.

Usage: python3 scripts/check-module-numeric.py [case ...]
"""
import json
import sys
from pathlib import Path

OUT = Path('evidence/stages/B02/B02-02/attempt-47/acceptance')
SOURCE = 'frozen-report-head.txt (门窗计算示例1.cwx, sha256 2FFA32CB…0FBE3)'
ETA_JSON = Path('migration_workspace/raw/lookup-tables.json')
COEF_JSON = Path('migration_workspace/raw/coefficient-tables.json')


def interpolate(xs, ys, x):
    """Same rule as FUN_180299d50: clamp outside the first/last node, linear between."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            span = xs[i] - xs[i - 1]
            t = 0.0 if span == 0 else (x - xs[i - 1]) / span
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1]


def _load(path, producer):
    if not path.exists():
        raise SystemExit(f'{path} missing — run {producer} first')
    return json.loads(path.read_text(encoding='utf-8'))


def eta(table, theta):
    """η 折减系数 from the tables `GetNg` (FUN_1802980c0) interpolates."""
    data = _load(ETA_JSON, 'python3 scripts/extract-lookup-table.py')
    entry = data['tables'][table]
    return interpolate(entry['x'], entry['y'], theta)


def coef(pair, ratio):
    """μ / m from the axis pair the decompiled branch selects in GetSDr / GetSMr."""
    data = _load(COEF_JSON, 'python3 scripts/extract-coefficient-tables.py')
    xs = data['tables'][data['pairs'][pair]['x']]['values']
    ys = data['tables'][data['pairs'][pair]['y']]['values']
    return interpolate(xs, ys, ratio)


CASES = {
    # 玻璃跨中挠度, JGJ102-2003 6.1.2-3 / 6.1.3-2
    'glass-disp': {
        'module': '玻璃跨中挠度',
        'inputs': {'t1_mm': 6.0, 't2_mm': 6.0, 'E_N_mm2': 72000.0, 'nu': 0.2,
                   'qk_kN_m2': 1.0, 'a_m': 1.0},
        'steps': [
            ('te_mm', lambda i: 0.95 * (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) ** (1 / 3), 7.18155, 5e-6),
            ('D_N_mm', lambda i: i['E_N_mm2'] * (0.95 * (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) ** (1 / 3)) ** 3
             / (12 * (1 - i['nu'] ** 2)), 2314912.5, 0.5),
            # μ = GetSDr(Hw, Bw) → 2-arg branch, ratio = min/max = 1.0
            ('mu_table_6_1_3', lambda i: coef('mu.glass.2arg', i['a_m'] / i['a_m']), 0.00406, 5e-9),
            ('theta', lambda i: i['qk_kN_m2'] * i['a_m'] ** 4
             / (i['E_N_mm2'] * (0.95 * (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) ** (1 / 3)) ** 4) * 1e9,
             5.221494, 5e-7),
            # η = GetNg(θ) → default table
            ('eta_table_6_1_2_2', lambda i: eta('eta.default', i['qk_kN_m2'] * i['a_m'] ** 4
                                                / (i['E_N_mm2'] * (0.95 * (i['t1_mm'] ** 3
                                                                           + i['t2_mm'] ** 3) ** (1 / 3)) ** 4)
                                                * 1e9), 0.998228, 5e-7),
            ('df_mm', lambda i: coef('mu.glass.2arg', 1.0) * i['qk_kN_m2'] * i['a_m'] ** 4
             / (i['E_N_mm2'] * (0.95 * (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) ** (1 / 3)) ** 3
                / (12 * (1 - i['nu'] ** 2)))
             * eta('eta.default', i['qk_kN_m2'] * i['a_m'] ** 4
                   / (i['E_N_mm2'] * (0.95 * (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) ** (1 / 3)) ** 4) * 1e9)
             * 1e9, 1.750738, 2e-6),
        ],
    },
    # 玻璃面板强度（跨中应力）, JGJ102-2003 6.1.2-1 / 荷载分配 / 6.1.2-2(η) 逐片折减
    'glass-stress': {
        'module': '玻璃面板强度（跨中应力）',
        'inputs': {'q_design_kN_m2': 1.672032, 'qk_kN_m2': 1.0, 't1_mm': 6.0, 't2_mm': 6.0,
                   'E_N_mm2': 72000.0, 'a_m': 1.0},
        'steps': [
            ('q1_kN_m2', lambda i: 1.1 * i['q_design_kN_m2'] * i['t1_mm'] ** 3
             / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3), 0.919618, 5e-7),
            ('q2_kN_m2', lambda i: i['q_design_kN_m2'] * i['t2_mm'] ** 3
             / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3), 0.836016, 5e-7),
            ('qk1_kN_m2', lambda i: 1.1 * i['qk_kN_m2'] * i['t1_mm'] ** 3
             / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3), 0.55, 5e-7),
            # m = GetSMr(al, bl, PRJGLASS=0, LINKNUM) → $2 in {0,...} branch, 表 6.1.2-1
            ('m_table_6_1_2_1', lambda i: coef('m.glass.2arg', 1.0), 0.0442, 5e-9),
            ('theta1', lambda i: 1.1 * i['qk_kN_m2'] * i['t1_mm'] ** 3
             / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) * i['a_m'] ** 4 * 1e9
             / (i['E_N_mm2'] * i['t1_mm'] ** 4), 5.894204, 5e-7),
            ('theta2', lambda i: i['qk_kN_m2'] * i['t2_mm'] ** 3
             / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) * i['a_m'] ** 4 * 1e9
             / (i['E_N_mm2'] * i['t2_mm'] ** 4), 5.358368, 5e-7),
            ('eta1_table_6_1_2_2', lambda i: eta('eta.default', 1.1 * i['qk_kN_m2'] * i['t1_mm'] ** 3
                                                 / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3)
                                                 * i['a_m'] ** 4 * 1e9
                                                 / (i['E_N_mm2'] * i['t1_mm'] ** 4)), 0.992846, 5e-7),
            ('eta2_table_6_1_2_2', lambda i: eta('eta.default', i['qk_kN_m2'] * i['t2_mm'] ** 3
                                                 / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3)
                                                 * i['a_m'] ** 4 * 1e9
                                                 / (i['E_N_mm2'] * i['t2_mm'] ** 4)), 0.997133, 5e-7),
            ('sigma1_N_mm2', lambda i: 6 * coef('m.glass.2arg', 1.0) * (
                1.1 * i['q_design_kN_m2'] * i['t1_mm'] ** 3
                / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3)) * i['a_m'] ** 2 * 1000
                / i['t1_mm'] ** 2
                * eta('eta.default', 1.1 * i['qk_kN_m2'] * i['t1_mm'] ** 3
                      / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) * i['a_m'] ** 4 * 1e9
                      / (i['E_N_mm2'] * i['t1_mm'] ** 4)), 6.726054, 5e-7),
            ('sigma2_N_mm2', lambda i: 6 * coef('m.glass.2arg', 1.0) * (
                i['q_design_kN_m2'] * i['t2_mm'] ** 3
                / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3)) * i['a_m'] ** 2 * 1000
                / i['t2_mm'] ** 2
                * eta('eta.default', i['qk_kN_m2'] * i['t2_mm'] ** 3
                      / (i['t1_mm'] ** 3 + i['t2_mm'] ** 3) * i['a_m'] ** 4 * 1e9
                      / (i['E_N_mm2'] * i['t2_mm'] ** 4)), 6.140995, 5e-7),
        ],
    },
}


def run(case_name):
    case = CASES[case_name]
    inputs = case['inputs']
    rows, ok = [], True
    for name, fn, printed, tol in case['steps']:
        computed = round(fn(inputs), 9)
        good = abs(computed - printed) <= tol
        ok = ok and good
        rows.append({'quantity': name, 'printed': printed, 'computed': computed,
                     'abs_diff': abs(computed - printed), 'tolerance': tol, 'match': good})
    return {'case': case_name, 'module': case['module'], 'source': SOURCE,
            'tables': {'eta': str(ETA_JSON), 'coefficient': str(COEF_JSON)},
            'inputs': inputs, 'steps': rows, 'all_matched': ok, 'open': case.get('open', [])}


def main(argv):
    names = argv[1:] or list(CASES)
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name in names:
        if name not in CASES:
            raise SystemExit(f'unknown case {name}; known: {", ".join(CASES)}')
        result = run(name)
        (OUT / f'{name}-numeric-check.json').write_text(
            json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
        results.append(result)
        for row in result['steps']:
            flag = 'OK ' if row['match'] else 'FAIL'
            print(f"{flag} {name:12s} {row['quantity']:18s} printed={row['printed']:<12} "
                  f"computed={row['computed']:<16} diff={row['abs_diff']:.2e}")
        for note in result['open']:
            print(f'OPEN {name}: {note}')
    print(json.dumps({'cases': len(results), 'all_matched': all(r['all_matched'] for r in results)}))
    return 0 if all(r['all_matched'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
