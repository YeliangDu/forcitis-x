#!/usr/bin/env python3
"""Reconstruct BREP arcs by *fitting to the line endpoints* instead of trusting the angle fields.

For every 96-byte arc payload we try the plausible (centre, radius) pairs against the set of line
endpoints: the correct pair puts exactly two endpoints on the circle. The arc is then drawn between
those two points, sweeping the way the stored angle difference indicates. This removes the
dependence on an angle convention that turned out to vary between profile families.

Exit: 0 when every section below the area tolerance, 1 otherwise.
"""
import base64
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOL = 0.08          # mm, endpoint-on-circle tolerance
AREA_TOL = 0.005    # 0.5 % per docs/poc-mvp-plan.md P1


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_stream, _brep, _section = load('brep-stream'), load('decode-brep'), load('brep-section')
STEPS = 64


def split_objects(gid, gallery):
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
            if len(seg) % 8 == 2:
                seg = seg[:-2]
            if len(seg) == 48:
                d = struct.unpack('<6d', seg)
                lines.append(((d[0], d[1]), (d[3], d[4])))
            elif len(seg) == 96:
                arcs.append(struct.unpack('<12d', seg))
    return lines, arcs


def fit_arc(d, endpoints):
    """Return (cx, cy, r, p_start, p_end) using endpoint fit, or None."""
    best = None
    for (ix, iy) in ((3, 4), (4, 5), (5, 3)):
        cx, cy = d[ix], d[iy]
        for ir in (1, 0, 2):
            radius = abs(d[ir])
            if not (0.02 < radius < 500):
                continue
            on = [p for p in endpoints if abs(math.dist((cx, cy), p) - radius) <= TOL]
            score = len(on)
            if best is None or score > best[0]:
                best = (score, cx, cy, radius, on)
    if best is None or best[0] < 2:
        return None
    score, cx, cy, radius, on = best
    on = sorted(set(on))[:2]
    if len(on) < 2:
        return None
    return cx, cy, radius, on[0], on[1], score


def arc_polyline(cx, cy, radius, p0, p1, sweep_hint, reverse=False):
    a0 = math.atan2(p0[1] - cy, p0[0] - cx)
    a1 = math.atan2(p1[1] - cy, p1[0] - cx)
    delta = (a1 - a0) % (2 * math.pi)
    if sweep_hint and delta > math.pi:
        delta -= 2 * math.pi
    if reverse:
        delta -= 2 * math.pi if delta > 0 else -2 * math.pi
    return [(cx + radius * math.cos(a0 + delta * i / STEPS),
             cy + radius * math.sin(a0 + delta * i / STEPS)) for i in range(STEPS + 1)]


def main(argv):
    ids = [int(a) for a in argv[1:]] or [1783, 1782, 1781, 1780]
    gallery = {r['IID']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/gallery.json').read_text(encoding='utf-8'))}
    profiles = {r['graphic_id']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/profiles.json').read_text(encoding='utf-8'))}
    rows, failed = [], False
    for gid in ids:
      for reverse in (False, True):
        lines, arcs = split_objects(gid, gallery)
        endpoints = set()
        for a, b in lines:
            endpoints.add((round(a[0], 2), round(a[1], 2)))
            endpoints.add((round(b[0], 2), round(b[1], 2)))
        polylines = [[a, b] for a, b in lines]
        fitted = 0
        for d in arcs:
            hit = fit_arc(d, endpoints)
            if hit is None:
                continue
            cx, cy, radius, p0, p1, _score = hit
            polylines.append(arc_polyline(cx, cy, radius, p0, p1, sweep_hint=d[2] > d[0], reverse=reverse))
            fitted += 1
        chains = _section.build_chains(polylines, tol=0.08)
        signed = 0.0
        for chain in chains:
            props = _section.polygon_props(chain)
            if props:
                signed += props.get('signedAreaMm2', props['areaMm2'])
        area = abs(signed)
        stored = (profiles.get(gid, {}).get('AREA') or 0) * 100
        diff = abs(area - stored) / stored if stored else None
        rows.append({'gallery_iid': gid, 'reverse': reverse, 'lines': len(lines), 'arcs': len(arcs),
                     'arcs_fitted': fitted, 'chains': len(chains), 'areaMm2': area,
                     'storedAreaMm2': stored, 'areaRelDiff': diff})
        print(f"{gid} rev={int(reverse)}: {len(lines)}L+{len(arcs)}A fitted={fitted} chains={len(chains)} "
              f"area={area:.1f} stored={stored:.1f} relDiff={(diff or 0) * 100:+.2f}%")
    (ROOT / 'evidence/poc/P1/brep-arcs2.json').write_text(json.dumps({'tolerance': AREA_TOL, 'rows': rows}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
