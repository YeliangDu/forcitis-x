#!/usr/bin/env python3
"""风荷载链 WLS → WLD 的本地实现（L8 最小切片的计算侧）。

公式**逐字来自** `计算模板`（见 `migration_workspace/formula-chains.md`）：

    μz = μh × (z/10)^α2                （另有"取小值"分支，需原版判定）
    μf = 0.5 × 35^(1.8×(α-0.16)) × (z/10)^(-α)
    βgz = Kk(region) × (1 + 2μf)
    Wk  = [γ0×] βgz × μz × μsl × ω0    （Wk < ωklim 时取 ωklim）
    W   = γwf × Wk

系数来源标注：
- `ω0`（基本风压）：`HWKCOPY_XWallTem.风压数据`（实测，北京=0.45）
- `μh/α2/α/Kk`：**尚未与原版绑定**；本脚本把它们当显式输入，并给出一组来自
  `helper-tables.md`（`fun_180255170`）的候选值供人工核对，**不假定其语义**。
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# Kk(REGION)：GetKk（eval 0x18025c4f0）与 GetBgzcal（0x180258000）两处独立解码一致
KK = {'A': 0.92, 'B': 0.89, 'C': 0.85, 'D': 0.80}
# α（地面粗糙度指数）：GetBgzcal 的 uVar15/16 解码 A=0.12 B=0.16 C=0.22 D=0.30
ALPHA = {'A': 0.12, 'B': 0.16, 'C': 0.22, 'D': 0.30}
# I10（10m 高名义湍流度）：`LOAD_WINDSTANDCALC` 原文写明 A/B/C/D = 0.12/0.14/0.23/0.39；
# 与 `fun_180255170` 里 uVar12/13 解码出的 0.12/0.14/0.23/0.39 完全一致 → 该变量就是 I10。
I10 = {'A': 0.12, 'B': 0.14, 'C': 0.23, 'D': 0.39}


def wls(z, mu_h, alpha2, alpha, kk, mu_sl, omega0, gamma0=1.0, omega_lim=0.0):
    """按原文算式计算 Wk；返回各中间量与结果。"""
    mu_z = mu_h * (z / 10.0) ** alpha2
    mu_f = 0.5 * 35.0 ** (1.8 * (alpha - 0.16)) * (z / 10.0) ** (-alpha)
    beta_gz = kk * (1.0 + 2.0 * mu_f)
    wk = beta_gz * mu_z * mu_sl * omega0
    if gamma0 != 1.0:
        wk = gamma0 * wk
    clamped = False
    if omega_lim and wk < omega_lim:
        wk = omega_lim
        clamped = True
    return {'mu_z': mu_z, 'mu_f': mu_f, 'beta_gz': beta_gz, 'wk': wk,
            'clamped_to': omega_lim if clamped else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--z', type=float, default=80.0)
    ap.add_argument('--omega0', type=float, default=0.45, help='基本风压 kN/m^2（北京 实测 0.45）')
    ap.add_argument('--mu-sl', type=float, default=1.0, help='局部体型系数（用户/规范输入）')
    ap.add_argument('--gamma-wf', type=float, default=1.4, help='风荷载分项系数（需与原版默认值核对）')
    ap.add_argument('--gamma0', type=float, default=1.0)
    ap.add_argument('--omega-lim', type=float, default=0.0)
    ap.add_argument('--region', default='B', help='地区类别 A/B/C/D（决定 Kk(REGION)）')
    ap.add_argument('--form', choices=('old', 'new'), default='new',
                    help="old: βgz=Kk×(1+2μf)（GB50009-2001）；new: βgz=1+2·g·I10·(z/10)^(-α)（2012 形式）")
    ap.add_argument('--g', type=float, default=2.5, help='峰值因子 GLOB_g（候选值，待原版确认）')
    ap.add_argument('--beta-lower', action='store_true',
                    help='施加《工程结构通用规范》下限 1+0.7/μz^0.5')
    ap.add_argument('--json')
    args = ap.parse_args()

    # 候选系数：来自 helper-tables.md（fun_180255170）里的常量，语义待与原版核对。
    # 这里只做“把候选代进原文算式”的展示，不声明它们就是 μh/α2/α。
    region = args.region.upper()
    kk = KK.get(region, KK['D'])
    alpha = ALPHA.get(region, ALPHA['D'])
    # 主候选：α 与 Kk 均来自反编译实证；μz 的形式 μh=1.0、α2=2α 属**推得**（GB50009 形式），待原版确认
    candidates = [
        {'label': f'推得：μh=1.0 α2=2α={2*alpha:g} (Kk={kk})', 'mu_h': 1.0,
         'alpha2': 2 * alpha, 'alpha': alpha, 'kk': kk},
        {'label': f'变体：μh=1.0 α2=α={alpha:g}', 'mu_h': 1.0, 'alpha2': alpha, 'alpha': alpha, 'kk': kk},
    ]
    rows = []
    for cand in candidates:
        res = wls(args.z, cand['mu_h'], cand['alpha2'], cand['alpha'], cand['kk'],
                  args.mu_sl, args.omega0, args.gamma0, args.omega_lim)
        wk = res['wk']
        rows.append({'candidate': cand['label'], **cand, **res, 'w': args.gamma_wf * wk})

    print(f'输入：z={args.z} m, ω0={args.omega0} kN/m², μsl={args.mu_sl}, '
          f'γwf={args.gamma_wf}, γ0={args.gamma0}, ωklim={args.omega_lim}, form={args.form}')
    print(f"{'候选':28s} {'μz':>8s} {'μf':>8s} {'βgz':>8s} {'Wk':>8s} {'W':>8s}")
    for r in rows:
        print(f"{r['candidate']:28s} {r['mu_z']:8.3f} {r['mu_f']:8.3f} "
              f"{r['beta_gz']:8.3f} {r['wk']:8.3f} {r['w']:8.3f}")
    if args.json:
        Path(args.json).write_text(json.dumps({'inputs': vars(args), 'rows': rows},
                                              ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    sys.exit(main())
