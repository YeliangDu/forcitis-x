#!/usr/bin/env python3
"""Classify candidate blocks into section families (aluminium profile / steel tube / sheet / hardware).

Features per block: net area, bbox, fill ratio, ring count, aspect ratio, estimated wall thickness
(t ≈ 2A / Σ perimeter, exact for a two-ring thin-walled tube).
"""
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = re.compile(r'(钉|螺栓|铆|销|螺母|垫圈|压块|ST\d|bolt|screw|rivet)', re.I)
FRAME = re.compile(r'(图框|汇总表|材料表|^A3|^A4|^YQ\d|^TK)', re.I)


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_blocks = load('dwg-blocks')
_dxf = load('dxf-section')


def perimeter(loops):
    total = 0.0
    for loop in loops:
        for i in range(len(loop)):
            a, b = loop[i], loop[(i + 1) % len(loop)]
            total += math.dist(a, b)
    return total


def features(name, segs, loops, props):
    w = props['bboxMm'][2] - props['bboxMm'][0]
    h = props['bboxMm'][3] - props['bboxMm'][1]
    area = props['areaMm2']
    per = perimeter(loops)
    fill = area / (w * h) if w and h else 0.0
    aspect = max(w, h) / max(1e-9, min(w, h))
    wall = 2 * area / per if per else 0.0
    return {'block': name, 'areaMm2': area, 'wMm': w, 'hMm': h, 'rings': props['rings'],
            'fill': fill, 'aspect': aspect, 'wallMm': wall, 'perimeterMm': per}


def looks_rectangular_tube(f):
    """A single hole whose wall is uniform and whose outer ring is axis-aligned."""
    return (f['rings'] == 2 and 0.18 <= f['fill'] <= 0.45 and 1.0 <= f['wallMm'] <= 6.0
            and f['aspect'] <= 4)


def classify(f):
    name = f['block']
    if FRAME.search(name) or max(f['wMm'], f['hMm']) > 200:
        return 'frame/table'
    if HARDWARE.search(name) or f['fill'] > 0.85:
        return 'hardware'
    if f['aspect'] > 8:
        return 'legend/leader'
    if looks_rectangular_tube(f):
        return 'steel-tube/square-tube'
    if f['rings'] >= 2 and 0.10 <= f['fill'] <= 0.65 and 0.8 <= f['wallMm'] <= 8:
        return 'aluminium-profile'
    if f['rings'] == 1 and f['fill'] < 0.25:
        return 'sheet/bracket'
    return 'unclear'


def main(argv):
    path = next((a for a in argv[1:] if not a.startswith('--')), None) or 'evidence/poc/P1/sections/real-profiles.dwg'
    dxf_path, _ = _blocks.to_dxf_path(path)
    pairs = _blocks.pairs_of(dxf_path)
    names = _blocks.block_record_names(pairs)
    blocks, _ = _blocks.scan_blocks(pairs, names)
    rows = []
    for name, segs in blocks.items():
        if not segs:
            continue
        loops = _dxf.build_loops([_dxf.polyline_of(seg) for seg in segs])
        try:
            props = _dxf.properties(loops)
        except ValueError:
            continue
        if props['areaMm2'] < 30:
            continue
        f = features(name, segs, loops, props)
        f['category'] = classify(f)
        rows.append(f)
    order = ['aluminium-profile', 'steel-tube/square-tube', 'sheet/bracket', 'hardware',
             'legend/leader', 'frame/table', 'unclear']
    rows.sort(key=lambda r: (order.index(r['category']), -r['areaMm2']))
    for r in rows:
        print(f"{r['category']:<16} {r['block'][:22]:<22} A={r['areaMm2']:8.2f} rings={r['rings']:<2} "
              f"fill={r['fill']:.2f} t≈{r['wallMm']:.2f} {r['wMm']:.0f}x{r['hMm']:.0f}")
    summary = {c: sum(1 for r in rows if r['category'] == c) for c in order}
    print('summary:', summary)
    out = ROOT / 'evidence/poc/P1/blocks-classified.json'
    out.write_text(json.dumps({'file': path, 'summary': summary, 'rows': rows}, ensure_ascii=False, indent=1) + '\n',
                   encoding='utf-8')
    print('wrote', out.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
