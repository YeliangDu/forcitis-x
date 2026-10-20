#!/usr/bin/env python3
"""Assemble BREP sections into rings (outer + holes) and compute section properties.

Fixes the previous assembly bug: every curve is used exactly once (edge-used set), only closed loops
are kept, and holes are identified by containment depth instead of by signed-area sign alone.

Usage: python3 scripts/poc/brep-ring.py [gid ...]   (default 1783 1782 1781 1780)
"""
import base64
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOL = 0.08
AREA_TOL = 0.005


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_stream, _brep = load('brep-stream'), load('decode-brep')
STEPS = 64


def split_objects(gid, gallery):
    blob = base64.b64decode(gallery[gid]['BREP'])
    lines, arcs = [], []
    for rec in _brep.find_records(blob):
        if not rec['name'].endswith(('HWKCADGraphArc', 'HWKCADGraphLine')):
            continue
        body = blob[rec['payload']:rec['payload'] + rec['payload_len']]
        marks = _stream.headers(body)
        for k, (pos, _o) in enumerate(marks):
            start = pos + 16
            stop = marks[k + 1][0] if k + 1 < len(marks) else len(body)
            seg = body[start:stop]
            if len(seg) % 8 == 2:
                seg = seg[:-2]
            if len(seg) == 48:
                d = struct.unpack('<6d', seg)
                lines.append(((d[0], d[1]), (d[3], d[4])))
            elif len(seg) == 96:
                arcs.append(struct.unpack('<12d', seg))
    return lines, arcs


Q = 0.05  # mm snap grid for node matching


def key(point):
    return (round(point[0] / Q), round(point[1] / Q))


def fit_arc(d, endpoints):
    best = None
    for (ix, iy) in ((3, 4), (4, 5), (5, 3)):
        cx, cy = d[ix], d[iy]
        for ir in (1, 0, 2):
            radius = abs(d[ir])
            if not (0.02 < radius < 500):
                continue
            on = [p for p in endpoints if abs(math.dist((cx, cy), p) - radius) <= TOL]
            if best is None or len(on) > best[0]:
                best = (len(on), cx, cy, radius, sorted(set(on)))
    if best is None or best[0] < 2:
        return None
    _, cx, cy, radius, on = best
    return cx, cy, radius, on[0], on[1]


def arc_points(cx, cy, radius, p0, p1, sweep_hint):
    a0 = math.atan2(p0[1] - cy, p0[0] - cx)
    a1 = math.atan2(p1[1] - cy, p1[0] - cx)
    delta = (a1 - a0) % (2 * math.pi)
    if sweep_hint and delta > math.pi:
        delta -= 2 * math.pi
    return [(cx + radius * math.cos(a0 + delta * i / STEPS),
             cy + radius * math.sin(a0 + delta * i / STEPS)) for i in range(STEPS + 1)]


def cell(point):
    return (int(math.floor(point[0] / Q)), int(math.floor(point[1] / Q)))


def neighbours(point):
    cx, cy = cell(point)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            yield (cx + dx, cy + dy)


def build_loops(polylines):
    """Walk curves into closed loops; each curve used at most once (grid-hash nodes, no rounding loss)."""
    nodes = {}
    for index, poly in enumerate(polylines):
        for end, point in ((0, poly[0]), (-1, poly[-1])):
            nodes.setdefault(cell(point), []).append((index, end, point))
    used = set()
    loops = []
    for index, poly in enumerate(polylines):
        if index in used:
            continue
        chain = list(poly)
        used.add(index)
        start_point, cur_point = poly[0], poly[-1]
        while math.dist(cur_point, start_point) > TOL:
            step, best_d = None, TOL
            for cellkey in neighbours(cur_point):
                for other, end, point in nodes.get(cellkey, []):
                    if other in used or other == index:
                        continue
                    d = math.dist(point, cur_point)
                    if d <= best_d:
                        step, best_d = (other, end), d
            if step is None:
                break
            other, end = step
            used.add(other)
            nxt = polylines[other]
            chain += list(nxt) if end == 0 else list(reversed(nxt))
            cur_point = chain[-1]
        if math.dist(cur_point, start_point) <= TOL and len(chain) >= 4:
            loops.append(chain)
    return loops


def signed_area(points):
    total = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        total += x1 * y2 - x2 * y1
    return total / 2


def inside(point, ring):
    x, y = point
    hit = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xin > x:
                hit = not hit
    return hit


def representative_point(ring):
    """A point strictly inside the ring (vertex-based tests fail on boundary)."""
    n = len(ring)
    sx = sum(p[0] for p in ring) / n
    sy = sum(p[1] for p in ring) / n
    if inside((sx, sy), ring):
        return (sx, sy)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        for t in (1e-3, 1e-2, 0.1):
            probe = (mid[0] + (sx - mid[0]) * t, mid[1] + (sy - mid[1]) * t)
            if inside(probe, ring):
                return probe
    return (sx, sy)


def moments(points):
    """Second moments about the origin via Green's theorem."""
    ix = iy = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        ix += (y1 * y1 + y1 * y2 + y2 * y2) * cross
        iy += (x1 * x1 + x1 * x2 + x2 * x2) * cross
    return ix / 12, iy / 12


def main(argv):
    ids = [int(a) for a in argv[1:]] or [1783, 1782, 1781, 1780]
    gallery = {r['IID']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/gallery.json').read_text(encoding='utf-8'))}
    profiles = {r['graphic_id']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/profiles.json').read_text(encoding='utf-8'))}
    rows, failed = [], False
    for gid in ids:
        lines, arcs = split_objects(gid, gallery)
        endpoints = {p for seg in lines for p in seg}
        polylines = [list(seg) for seg in lines]
        pending = list(arcs)
        for _pass in range(3):                      # arcs may join other arcs, not only lines
            still = []
            for d in pending:
                hit = fit_arc(d, endpoints)
                if hit:
                    cx, cy, radius, p0, p1 = hit
                    pts = arc_points(cx, cy, radius, p0, p1, sweep_hint=d[2] > d[0])
                    polylines.append(pts)
                    endpoints.update({pts[0], pts[-1]})
                else:
                    still.append(d)
            pending = still
            if not pending:
                break
        loops = build_loops(polylines)
        rings = [{'points': loop, 'area': abs(signed_area(loop))} for loop in loops]
        for ring in rings:
            probe = representative_point(ring['points'])
            ring['depth'] = sum(1 for other in rings
                                if other is not ring and inside(probe, other['points']))
        area = sum(ring['area'] * (1 if ring['depth'] % 2 == 0 else -1) for ring in rings)
        ix = iy = 0.0
        for ring in rings:
            rix, riy = moments(ring['points'])
            sign = 1 if ring['depth'] % 2 == 0 else -1
            ix += sign * rix
            iy += sign * riy
        stored = profiles.get(gid, {})
        stored_area = (stored.get('AREA') or 0) * 100
        diff = abs(area - stored_area) / stored_area if stored_area else None
        rows.append({'gallery_iid': gid, 'name': gallery[gid].get('name'), 'loops': len(rings),
                     'depths': [r['depth'] for r in rings], 'areaMm2': area,
                     'storedAreaMm2': stored_area, 'areaRelDiff': diff})
        ok = diff is not None and diff <= AREA_TOL
        failed = failed or not ok
        print(f"{gid}: {len(lines)}L+{len(arcs)}A loops={len(rings)} depths={rows[-1]['depths'][:6]} "
              f"area={area:.1f} stored={stored_area:.1f} relDiff={(diff or 0) * 100:+.2f}% {'OK' if ok else 'FAIL'}")
    (ROOT / 'evidence/poc/P1/brep-rings.json').write_text(json.dumps({'rows': rows}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
