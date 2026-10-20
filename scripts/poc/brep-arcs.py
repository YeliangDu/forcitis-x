#!/usr/bin/env python3
"""Resolve each BREP arc's parameter mapping by endpoint continuity, then rebuild the section.

Arc payload = 96 B = 12 doubles. The field order is not uniform across arcs, so for every arc we try
candidate mappings (which double is the radius, which two are the start/end angle, which two are the
centre, plus sign/order variants) and keep the one whose two endpoints land on existing line
endpoints. Arcs that match nothing are reported instead of being silently drawn.

Then: tessellate, chain, compute area / centroid / second moments, compare with 型材参数表.

Usage: python3 scripts/poc/brep-arcs.py [gid ...]
"""
import base64
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_stream = load('brep-stream')
_brep = load('decode-brep')
_section = load('brep-section')

STEPS = 48
TOL = 0.06


def raw_pieces(gid, gallery):
    blob = base64.b64decode(gallery[gid]['BREP'])
    lines, arcs = [], []
    for rec in _brep.find_records(blob):
        if not rec['name'].endswith(('HWKCADGraphArc', 'HWKCADGraphLine')):
            continue
        body = blob[rec['payload']:rec['payload'] + rec['payload_len']]
        marks = _stream.headers(body)
        for k, (pos, _obj) in enumerate(marks):
            start = pos + 16
            stop = marks[k + 1][0] if k + 1 < len(marks) else len(body)
            seg = body[start:stop]
            if len(seg) % 8 == 2:      # trailing 2-byte relation marker when present
                seg = seg[:-2]
            if len(seg) == 48:
                d = struct.unpack('<6d', seg)
                lines.append(((d[0], d[1]), (d[3], d[4])))
            elif len(seg) == 96:
                arcs.append(struct.unpack('<12d', seg))
    return lines, arcs


def endpoints(lines):
    pts = set()
    for a, b in lines:
        pts.add((round(a[0], 2), round(a[1], 2)))
        pts.add((round(b[0], 2), round(b[1], 2)))
    return pts


def candidates(d):
    """Yield (label, cx, cy, r, a0, a1) from the 12 doubles."""
    names = ['d0', 'd1', 'd2']
    for (i_r, i_a, i_b) in ((1, 0, 2), (2, 0, 1), (0, 1, 2), (1, 2, 0), (2, 1, 0)):
        for (i_x, i_y) in ((3, 4), (4, 5), (5, 3)):
            for sign in (1, -1):
                for swap in (False, True):
                    cx, cy, radius = d[i_x], d[i_y], d[i_r]
                    a0, a1 = (d[i_b], d[i_a]) if swap else (d[i_a], d[i_b])
                    if radius <= 0 or not (0.01 < radius < 500):
                        continue
                    if not (abs(a0) < 20 and abs(a1) < 20):
                        continue
                    yield (f'{names[i_r]}r sign{sign} swap{swap} c{i_x},{i_y}',
                           cx, cy, sign * radius, a0, a1)


def resolve(arc, pts):
    best = None
    for label, cx, cy, radius, a0, a1 in candidates(arc):
        e1 = (round(cx + abs(radius) * math.cos(a0), 2), round(cy + abs(radius) * math.sin(a0), 2))
        e2 = (round(cx + abs(radius) * math.cos(a1), 2), round(cy + abs(radius) * math.sin(a1), 2))
        hit = (e1 in pts) + (e2 in pts)
        if best is None or hit > best[0]:
            best = (hit, label, cx, cy, abs(radius), a0, a1)
        if hit == 2:
            break
    return best


def arc_points(cx, cy, radius, a0, a1):
    return [(cx + radius * math.cos(a0 + (a1 - a0) * i / STEPS),
             cy + radius * math.sin(a0 + (a1 - a0) * i / STEPS)) for i in range(STEPS + 1)]


def main(argv):
    ids = [int(a) for a in argv[1:]] or [1783, 1782, 1781, 1780]
    gallery = {r['IID']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/gallery.json').read_text(encoding='utf-8'))}
    profiles = {r['graphic_id']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/profiles.json').read_text(encoding='utf-8'))}
    report = []
    for gid in ids:
        lines, arcs = raw_pieces(gid, gallery)
        pts = endpoints(lines)
        polylines = [[a, b] for a, b in lines]
        labels = {}
        unresolved = 0
        for arc in arcs:
            best = resolve(arc, pts)
            if best is None or best[0] == 0:
                unresolved += 1
                continue
            _, label, cx, cy, radius, a0, a1 = best
            labels[label] = labels.get(label, 0) + 1
            polylines.append(arc_points(cx, cy, radius, a0, a1))
        chains = _section.build_chains(polylines, tol=0.06)
        area = 0.0
        for chain in chains:
            props = _section.polygon_props(chain)
            if not props:
                continue
            area += props['areaMm2']
        stored = profiles.get(gid, {})
        row = {'gallery_iid': gid, 'name': gallery[gid].get('name'), 'lines': len(lines), 'arcs': len(arcs),
               'unresolved_arcs': unresolved, 'chains': len(chains), 'areaMm2': area,
               'storedAreaMm2': (stored.get('AREA') or 0) * 100, 'mappings': labels}
        row['areaRelDiff'] = (abs(area - row['storedAreaMm2']) / row['storedAreaMm2']) if row['storedAreaMm2'] else None
        report.append(row)
        print(f"{gid}: {row['lines']}L+{row['arcs']}A unresolved={unresolved} chains={len(chains)} "
              f"area={area:.1f} stored={row['storedAreaMm2']:.1f} relDiff={(row['areaRelDiff'] or 0) * 100:.2f}%")
        print('   mappings:', labels)
    (ROOT / 'evidence/poc/P1/brep-arcs.json').write_text(json.dumps({'rows': report}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
