#!/usr/bin/env python3
"""玻璃板块自重 WWEIGHT 的本地实现（L8 预演用的短链）。

公式**逐字来自** `计算模板.WWEIGHT`（见 `migration_workspace/formula-chains.md`）：

    GSAK = ρ × (Σt)/1000           # kN/m²；ρ 为体积密度 kN/m³，t 为各层厚度 mm
    G    = γGfm × GSAK × AREA      # kN

分支（原文 `IsEqual(GLS_STRUCT, n)` 决定参与求和的层数）：

| GLS_STRUCT | 参与厚度 |
| --- | --- |
| 0 | t（单片） |
| 1 / 2 | t1 + t2 |
| 3 | t1 + t2 + t3 |
| 4 | t1 + t2 + t3 + t4 |

数据来源：
- `ρ`：`HWKCOPY_XWall.材料特性表.DENSITY`（实测 玻璃=25.6，铝合金=28.3，钢材=78.5 kN/m³）
- 厚度/面积：构件输入（工程文件）
- `γGfm`：自重分项系数（**候选**，需与原版默认值核对；本脚本默认 1.2 并在输出里标注）
"""
import argparse
import sys

# 实测自 DB（kN/m³）；`GetM(GLOB_BOARDMATERIAL)` 取的就是这张表
DENSITY = {'玻璃': 25.6, '铝合金': 28.3, '钢材': 78.5}
LAYERS = {0: ('t',), 1: ('t1', 't2'), 2: ('t1', 't2'), 3: ('t1', 't2', 't3'),
          4: ('t1', 't2', 't3', 't4')}


def gsak(structure, thicknesses, density):
    """按原文分支求和后乘密度除 1000。厚度单位 mm，返回 kN/m²。"""
    keys = LAYERS.get(structure)
    if not keys:
        raise ValueError(f'unsupported GLS_STRUCT={structure}')
    total_mm = sum(thicknesses.get(k, 0.0) for k in keys)
    return density * total_mm / 1000.0, total_mm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--structure', type=int, default=2, help='GLS_STRUCT：0 单片 1/2 两片 3 三片 4 四片')
    ap.add_argument('--t1', type=float, default=6.0)
    ap.add_argument('--t2', type=float, default=6.0)
    ap.add_argument('--t3', type=float, default=0.0)
    ap.add_argument('--t4', type=float, default=0.0)
    ap.add_argument('--area', type=float, default=1.5 * 1.5, help='板块面积 m²')
    ap.add_argument('--material', default='玻璃', choices=sorted(DENSITY))
    ap.add_argument('--gamma-gfm', type=float, default=1.2, help='自重分项系数（候选值）')
    args = ap.parse_args()

    density = DENSITY[args.material]
    thicknesses = {'t': args.t1, 't1': args.t1, 't2': args.t2, 't3': args.t3, 't4': args.t4}
    value, total_mm = gsak(args.structure, thicknesses, density)
    g = args.gamma_gfm * value * args.area
    print(f'材料={args.material} ρ={density} kN/m³  GLS_STRUCT={args.structure}  Σt={total_mm:g} mm')
    print(f'GSAK = {density:g} × {total_mm:g}/1000 = {value:.4f} kN/m²')
    print(f'G    = {args.gamma_gfm:g} × {value:.4f} × {args.area:g} = {g:.4f} kN'
          f'   （γGfm={args.gamma_gfm:g} 为候选值）')


if __name__ == '__main__':
    sys.exit(main())
