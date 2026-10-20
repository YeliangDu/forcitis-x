#!/usr/bin/env python3
"""Second-method cross-check for a section: scanline raster vs Green's theorem.

Independent integration of the same ring set: rasterise with the even-odd rule and integrate
area / first / second moments numerically. If both methods agree, the *math* is right; the remaining
risk is whether the ring set itself is the intended geometry.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_blocks = load('dwg-blocks')
_dxf = load('dxf-section')


def scanline(loops, step=0.02, dxf_path=None):
    return _scanline(loops, step)


def _scanline(loops, step=0.02):
    xs = np.concatenate([np.array([p[0] for p in loop]) for loop in loops])
    ys = np.concatenate([np.array([p[1] for p in loop]) for loop in loops])
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    gx = np.arange(x0, x1, step) + step / 2
    gy = np.arange(y0, y1, step) + step / 2
    area = sx = sy = ix = iy = 0.0
    for y in gy:
        crossings = []
        for loop in loops:
            pts = np.array(loop)
            xa, ya = pts[:, 0], pts[:, 1]
            xb, yb = np.roll(xa, -1), np.roll(ya, -1)
            mask = (ya > y) != (yb > y)
            if mask.any():
                crossings.extend((xa[mask] + (y - ya[mask]) * (xb[mask] - xa[mask])
                                  / (yb[mask] - ya[mask])).tolist())
        inside = np.zeros(gx.shape, dtype=bool)
        crossings.sort()
        for k in range(0, len(crossings) - 1, 2):
            inside |= (gx > crossings[k]) & (gx < crossings[k + 1])
        n = inside.sum()
        if not n:
            continue
        cell = step * step
        area += n * cell
        sx += gx[inside].sum() * cell
        sy += y * n * cell
        ix += (y * y) * n * cell
        iy += (gx[inside] ** 2).sum() * cell
    cx, cy = sx / area, sy / area
    return {'areaMm2': area, 'cxMm': cx, 'cyMm': cy,
            'ixMm4': ix - area * cy * cy, 'iyMm4': iy - area * cx * cx}


def main(argv):
    block = argv[1] if len(argv) > 1 else 'PBW7525103'
    dxf_path = Path(argv[2]) if len(argv) > 2 else ROOT / 'evidence/poc/P1/sections/real-profiles.dwg'
    dxf_path, _conv = _blocks.to_dxf_path(dxf_path)
    pairs = _blocks.pairs_of(dxf_path)
    names = _blocks.block_record_names(pairs)
    blocks, _ = _blocks.scan_blocks(pairs, names)
    segs = blocks.get(block)
    if not segs:
        print(f'block {block} not found')
        return 1
    loops = _dxf.build_loops([_dxf.polyline_of(s) for s in segs])
    green = _dxf.properties(loops)
    raster = scanline(loops)
    rows = []
    ok = True
    for key, label in (('areaMm2', 'A'), ('ixMm4', 'Ix'), ('iyMm4', 'Iy'), ('cxMm', 'Cx'), ('cyMm', 'Cy')):
        a, b = float(green[key]), float(raster[key])
        ref = max(abs(a), 1e-9)
        rel = abs(a - b) / ref
        good = rel <= 2e-2
        ok = ok and good
        rows.append({'quantity': label, 'green': a, 'scanline': b, 'relDiff': rel, 'match': good})
    print(json.dumps({'block': block, 'rings': green['rings'], 'checks': rows, 'both_agree': ok},
                     ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
