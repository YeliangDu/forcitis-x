#!/usr/bin/env python3
"""Rebuild a section outline from BREP sub-objects and compare with the stored properties.

Sub-object payload (measured + endpoint-verified):
  line  : 48 B = 2 × (x, y, z)                     (two 3-D endpoints)
  curve : 96 B = (startRad, radius, endRad, cx, cy, cz, ...) — arc around (cx,cy) from startRad to endRad
  marker: 2 B   (relation stub, no geometry)

Arcs are tessellated, segments are chained by shared endpoints, and the closed polygon is fed to the
same formulas the TypeScript engine uses (Green's theorem). Compare with 型材参数表 AREA/IZ/IY.

Usage: python3 scripts/poc/brep-section.py [gallery_iid ...]
"""
import base64
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_brep = load_module('decode-brep')
_stream = load_module('brep-stream')
ARC_STEPS = 64


def pieces(body):
    """Yield ('line', p1, p2) / ('arc', cx, cy, r, a0, a1) from one BREP body."""
    marks = _stream.headers(body)
    out = []
    for k, (pos, _obj_id) in enumerate(marks):
        start = pos + 16
        stop = marks[k + 1][0] if k + 1 < len(marks) else len(body)
        seg = body[start:stop - 2] if stop - start >= 2 else b''
        if len(seg) == 48:
            d = struct.unpack('<6d', seg)
            out.append(('line', (d[0], d[1]), (d[3], d[4])))
        elif len(seg) == 96:
            d = struct.unpack('<12d', seg)
            out.append(('arc', (d[3], d[4]), d[1], d[0], d[2]))
    return out


def tessellate(item):
    if item[0] == 'line':
        return [item[1], item[2]]
    _, center, radius, a0, a1 = item
    cx, cy = center
    return [(cx + radius * math.cos(a0 + (a1 - a0) * i / ARC_STEPS),
             cy + radius * math.sin(a0 + (a1 - a0) * i / ARC_STEPS)) for i in range(ARC_STEPS + 1)]


def polygon_props(points):
    """Signed area, centroid, second moments about the origin (Green's theorem)."""
    a2 = ix = iy = sx = sy = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        a2 += cross
        sx += (x1 + x2) * cross
        sy += (y1 + y2) * cross
        ix += (y1 * y1 + y1 * y2 + y2 * y2) * cross
        iy += (x1 * x1 + x1 * x2 + x2 * x2) * cross
    area = a2 / 2
    if area == 0:
        return None
    return {'areaMm2': abs(area), 'cxMm': sx / (6 * area), 'cyMm': sy / (6 * area),
            'ixMm4': ix / 12, 'iyMm4': iy / 12}


def green_area(items):
    """Area from per-piece Green integral: 1/2 * sum of integral(x dy - y dx) over every piece."""
    total = 0.0
    for item in items:
        if item[0] == 'line':
            (x1, y1), (x2, y2) = item[1], item[2]
            total += x1 * y2 - x2 * y1
        else:
            _, (cx, cy), radius, a0, a1 = item
            total += (radius * cx * (math.sin(a1) - math.sin(a0))
                      + radius * cy * (math.cos(a0) - math.cos(a1))
                      + radius * radius * (a1 - a0))
    return abs(total) / 2


def build_chains(polylines, tol=1e-3):
    """Join tessellated polylines by shared endpoints (either direction) into closed chains."""
    remaining = [list(pl) for pl in polylines]
    chains = []
    while remaining:
        chain = remaining.pop(0)
        grown = True
        while grown:
            grown = False
            for index, other in enumerate(remaining):
                if abs(chain[-1][0] - other[0][0]) < tol and abs(chain[-1][1] - other[0][1]) < tol:
                    chain = chain + other[1:]
                elif abs(chain[-1][0] - other[-1][0]) < tol and abs(chain[-1][1] - other[-1][1]) < tol:
                    chain = chain + list(reversed(other))[1:]
                elif abs(chain[0][0] - other[-1][0]) < tol and abs(chain[0][1] - other[-1][1]) < tol:
                    chain = other + chain[1:]
                elif abs(chain[0][0] - other[0][0]) < tol and abs(chain[0][1] - other[0][1]) < tol:
                    chain = list(reversed(other)) + chain[1:]
                else:
                    continue
                remaining.pop(index)
                grown = True
                break
        chains.append(chain)
    return chains


def main(argv):
    ids = [int(a) for a in argv[1:]] or [1783, 1782, 1781, 1780]
    gallery = {r['IID']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/gallery.json').read_text(encoding='utf-8'))}
    profiles = {r['graphic_id']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/profiles.json').read_text(encoding='utf-8'))}
    out = []
    for gid in ids:
        blob = base64.b64decode(gallery[gid]['BREP'])
        items = []
        for rec in _brep.find_records(blob):
            if not rec['name'].endswith(('HWKCADGraphArc', 'HWKCADGraphLine')):
                continue
            body = blob[rec['payload']:rec['payload'] + rec['payload_len']]
            items.extend(pieces(body))
        chains = build_chains([tessellate(item) for item in items])
        props = None
        for chain in chains:
            part = polygon_props(chain)
            if part is None:
                continue
            if props is None:
                props = dict(part)
            else:
                for key in ('areaMm2', 'ixMm4', 'iyMm4'):
                    props[key] += part[key]
        points = [p for chain in chains for p in chain]
        stored = profiles.get(gid, {})
        area_direct = green_area(items)
        row = {'gallery_iid': gid, 'greenAreaMm2': area_direct, 'name': gallery[gid].get('name'), 'lines': sum(1 for i in items if i[0] == 'line'),
               'arcs': sum(1 for i in items if i[0] == 'arc'), 'points': len(points), 'computed': props,
               'stored': {k: stored.get(k) for k in ('AREA', 'IZ', 'IY', 'WZ1', 'WZ2')}}
        if stored.get('AREA'):
            row['areaRelDiff'] = abs(area_direct - stored['AREA'] * 100) / (stored['AREA'] * 100)
        out.append(row)
        print(f"{gid}: {row['lines']}L+{row['arcs']}A green={area_direct:.1f} "
              f"stored={stored.get('AREA', 0) * 100:.1f} relDiff={row.get('areaRelDiff', float('nan')) * 100:.2f}%")
    (ROOT / 'evidence/poc/P1/brep-section.json').write_text(json.dumps({'rows': out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
