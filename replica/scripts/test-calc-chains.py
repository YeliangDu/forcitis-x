#!/usr/bin/env python3
"""两条已实现计算链的回归断言（防"改一处悄悄弄坏已验证的算式"）。

跑法：`python3 replica/scripts/test-calc-chains.py`
覆盖：
1. `calc-glass-weight`：GSAK = ρ×Σt/1000（DB 实测 ρ=25.6）三条结构分支；
2. `calc-wind`：B 区 z=80/ω0=0.45 时的 Wk（α2=2α 候选）与 βgz；
3. `nodes-expr`：`CalGlassDisp` 的算式与人工核对结论**逐字一致**（曾因括号整理被改坏过一次）。
退出码 0 = 全通过。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPLICA = ROOT / 'replica' / 'scripts'
failures = []


def check(name, ok, detail=''):
    print(f'{"PASS" if ok else "FAIL"}  {name}' + (f'  {detail}' if detail and not ok else ''))
    if not ok:
        failures.append(name)


def run(args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, check=False).stdout


def parse_table(out):
    """从 calc-wind 输出的"推得"行里取末尾 5 个数值：μz、μf、βgz、Wk、W。

    该行形如：`推得：μh=1.0 α2=2α=0.32 (Kk=0.89)   1.945  0.358  1.528  1.338  1.873`
    标签里也含数字，所以必须从**行尾**倒着取。
    """
    import re as _re
    for line in out.splitlines():
        if line.startswith('推得'):
            numbers = _re.findall(r'-?\d+\.\d+', line.split(')', 1)[-1])
            if len(numbers) >= 5:
                mu_z, mu_f, beta_gz, wk, w = numbers[-5:]
                return {'mu_z': mu_z, 'mu_f': mu_f, 'beta_gz': beta_gz, 'wk': wk, 'w': w}
    return {}


def main():
    # 1) 玻璃自重
    for structure, th, expect in ((0, 6, 0.1536), (2, 12, 0.3072), (3, 18, 0.4608)):
        out = run([str(REPLICA / 'calc-glass-weight.py'), '--structure', str(structure),
                   '--t1', str(th if structure == 0 else 6), '--t2', '6', '--t3', '6'])
        ok = f'GSAK = 25.6 × {th}/1000 = {expect:.4f}' in out
        check(f'glass-weight struct={structure} Σt={th}mm → {expect}', ok, out[:200])

    # 2) 风荷载（B 区 80m）
    out = run([str(REPLICA / 'calc-wind.py'), '--region', 'B', '--z', '80'])
    row = parse_table(out)
    try:
        wk = float(row.get('wk', 'nan'))
        beta = float(row.get('beta_gz', 'nan'))
    except ValueError:
        wk = beta = float('nan')
    check('wind B/80m Wk≈1.338', abs(wk - 1.338) < 5e-3, f'got {wk}')
    check('wind B/80m βgz≈1.528', abs(beta - 1.528) < 5e-3, f'got {beta}')

    # 3) 已核对算式不被改坏
    expr_path = ROOT / 'migration_workspace' / 'raw' / 'nodes-expr.json'
    if expr_path.exists():
        try:
            rows = {r['name']: r for r in json.loads(expr_path.read_text())['rows']}
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            check('nodes-expr.json 可解析', False, str(exc))
            rows = {}
        expected = '((qwk * ms * (pow(aw,4.0))) / dw) * theta * 1000000000.0'
        got = (rows.get('CalGlassDisp') or {}).get('fused')
        check('CalGlassDisp 算式逐字一致', got == expected, str(got))
        status = (rows.get('CalGlassDisp') or {}).get('status')
        check('CalGlassDisp 状态=EXPR', status == 'EXPR', str(status))
    else:
        check('nodes-expr.json 存在', False, str(expr_path))

    print()
    if failures:
        print(f'{len(failures)} 项失败: {failures}')
        return 1
    print('全部通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
