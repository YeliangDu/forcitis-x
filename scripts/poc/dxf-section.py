#!/usr/bin/env python3
"""DXF -> section properties (the *product* path for the section library).

Pipeline: DXF entities -> segments/arcs -> snapped loops -> hole classification -> properties.
Replaces the BREP decoding route: the library imports drawings, not the old binary format.

Supported: LINE, ARC, LWPOLYLINE (with bulges), POLYLINE, CIRCLE; model space plus block INSERTs.
Units are taken from $INSUNITS when present; geometry is otherwise assumed millimetres.

Usage:
  python3 scripts/poc/dxf-section.py <file.dxf> [--json out] [--selftest]
"""
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import ezdxf  # pyright: ignore[reportPrivateImportUsage]
from ezdxf.lldxf.const import DXFStructureError  # pyright: ignore[reportPrivateImportUsage]

ROOT = Path(__file__).resolve().parents[2]
SNAP = 0.02
ARC_STEPS = 64

UNITS = {1: 25.4, 2: 304.8, 4: 1.0, 5: 10.0, 6: 1000.0}  # inches/feet/mm/cm/m -> mm factor


def segments_from_entity(e, scale):
    """Yield ('line', p0, p1) / ('arc', c, r, a0, a1) in millimetres."""
    kind = e.dxftype()
    if kind == 'LINE':
        a, b = e.dxf.start, e.dxf.end
        yield ('line', (a.x * scale, a.y * scale), (b.x * scale, b.y * scale))
    elif kind == 'CIRCLE':
        c = e.dxf.center
        yield ('arc', (c.x * scale, c.y * scale), e.dxf.radius * scale, 0.0, 2 * math.pi)
    elif kind == 'ARC':
        c = e.dxf.center
        yield ('arc', (c.x * scale, c.y * scale), e.dxf.radius * scale,
               math.radians(e.dxf.start_angle), math.radians(e.dxf.end_angle))
    elif kind == 'LWPOLYLINE':
        pts = list(e.get_points('xyb'))
        for i in range(len(pts)):
            x1, y1, bulge = pts[i]
            x2, y2, _ = pts[(i + 1) % len(pts)]
            if abs(bulge) < 1e-12:
                yield ('line', (x1 * scale, y1 * scale), (x2 * scale, y2 * scale))
            else:
                yield bulge_to_arc(x1, y1, x2, y2, bulge, scale)
    elif kind == 'POLYLINE':
        verts = [(v.dxf.location.x, v.dxf.location.y, getattr(v.dxf, 'bulge', 0.0)) for v in e.vertices]
        for i in range(len(verts)):
            x1, y1, bulge = verts[i]
            x2, y2, _ = verts[(i + 1) % len(verts)]
            if abs(bulge) < 1e-12:
                yield ('line', (x1 * scale, y1 * scale), (x2 * scale, y2 * scale))
            else:
                yield bulge_to_arc(x1, y1, x2, y2, bulge, scale)


def bulge_to_arc(x1, y1, x2, y2, bulge, scale):
    theta = 4 * math.atan(bulge)
    chord = math.dist((x1, y1), (x2, y2))
    if chord == 0:
        return ('line', (x1 * scale, y1 * scale), (x2 * scale, y2 * scale))
    radius = chord / (2 * math.sin(abs(theta) / 2))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    h = math.sqrt(max(0.0, radius ** 2 - (chord / 2) ** 2))
    nx, ny = -(y2 - y1) / chord, (x2 - x1) / chord
    sign = 1 if bulge > 0 else -1
    cx, cy = mx + sign * nx * h, my + sign * ny * h
    a0 = math.atan2(y1 - cy, x1 - cx)
    a1 = a0 + theta
    return ('arc', (cx * scale, cy * scale), radius * scale, a0, a1)


def entity_stream(doc, scale):
    out = []

    def walk(layout, depth=0):
        for e in layout:
            if e.dxftype() == 'INSERT' and depth < 4:
                try:
                    walk(e.virtual_entities(), depth + 1)
                except (AttributeError, ValueError) as error:
                    sys.stderr.write(f'insert skipped: {error}\n')
            else:
                out.extend(segments_from_entity(e, scale))

    walk(doc.modelspace())
    return out


def polyline_of(seg):
    if seg[0] == 'line':
        return [seg[1], seg[2]]
    _, (cx, cy), r, a0, a1 = seg
    span = (a1 - a0) % (2 * math.pi)
    if span < 1e-9:
        span = 2 * math.pi
    return [(cx + r * math.cos(a0 + span * i / ARC_STEPS),
             cy + r * math.sin(a0 + span * i / ARC_STEPS)) for i in range(ARC_STEPS + 1)]


def cell(point):
    return (int(math.floor(point[0] / SNAP)), int(math.floor(point[1] / SNAP)))


def build_loops(polylines):
    nodes = {}
    for index, poly in enumerate(polylines):
        for end, point in ((0, poly[0]), (-1, poly[-1])):
            nodes.setdefault(cell(point), []).append((index, end, point))
    used, loops = set(), []
    for index, poly in enumerate(polylines):
        if index in used:
            continue
        used.add(index)
        chain = list(poly)
        start, cur = poly[0], poly[-1]
        while math.dist(cur, start) > SNAP:
            cx, cy = cell(cur)
            step, best = None, SNAP
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for other, end, point in nodes.get((cx + dx, cy + dy), []):
                        if other in used:
                            continue
                        d = math.dist(point, cur)
                        if d <= best:
                            step, best = (other, end), d
            if step is None:
                break
            other, end = step
            used.add(other)
            nxt = polylines[other]
            chain += list(nxt) if end == 0 else list(reversed(nxt))
            cur = chain[-1]
        if math.dist(cur, start) <= SNAP and len(chain) >= 4:
            loops.append(chain)
    return loops


def signed_area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


def inside(point, ring):
    x, y = point
    hit = False
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        if (y1 > y) != (y2 > y) and x1 + (y - y1) * (x2 - x1) / (y2 - y1) > x:
            hit = not hit
    return hit


def properties(loops):
    rings = [{'pts': loop, 'area': abs(signed_area(loop))} for loop in loops]
    for ring in rings:
        n = len(ring['pts'])
        cx = sum(p[0] for p in ring['pts']) / n
        cy = sum(p[1] for p in ring['pts']) / n
        probe = (cx, cy) if inside((cx, cy), ring['pts']) else ring['pts'][0]
        ring['depth'] = sum(1 for other in rings
                            if other is not ring and other['area'] > ring['area']
                            and inside(probe, other['pts']))
    # normalise orientation: outer rings CCW, holes CW; otherwise signed moments cancel each other
    for ring in rings:
        wanted_positive = ring['depth'] % 2 == 0
        if (signed_area(ring['pts']) > 0) != wanted_positive:
            ring['pts'] = list(reversed(ring['pts']))
    area = ix = iy = ixy = sx = sy = 0.0
    for ring in rings:
        pts = ring['pts']
        a2 = sxr = syr = ixr = iyr = ixyr = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            cross = x1 * y2 - x2 * y1
            a2 += cross
            sxr += (x1 + x2) * cross
            syr += (y1 + y2) * cross
            ixr += (y1 * y1 + y1 * y2 + y2 * y2) * cross
            iyr += (x1 * x1 + x1 * x2 + x2 * x2) * cross
            ixyr += (x1 * y2 + 2 * x1 * y1 + 2 * x2 * y2 + x2 * y1) * cross
        # orientation already encodes outer(+)/hole(−), so accumulate the raw signed terms
        area += a2 / 2
        sx += sxr / 6
        sy += syr / 6
        ix += ixr / 12
        iy += iyr / 12
        ixy += ixyr / 24
    if not area:
        raise ValueError('no closed ring found — check that the drawing contains a closed outline '
                         '(segments within the snap tolerance)')
    cx, cy = sx / area, sy / area
    return {'areaMm2': float(area), 'cxMm': float(cx), 'cyMm': float(cy),
            'ixMm4': float(ix - area * cy * cy), 'iyMm4': float(iy - area * cx * cx),
            'ixyMm4': float(ixy - area * cx * cy), 'rings': len(rings),
            'depths': [int(r['depth']) for r in rings],
            'bboxMm': [float(min(p[0] for loop in loops for p in loop)),
                       float(min(p[1] for loop in loops for p in loop)),
                       float(max(p[0] for loop in loops for p in loop)),
                       float(max(p[1] for loop in loops for p in loop))]}


def to_dxf(path):
    """Return a DXF path for the input; DWG is converted server-side (no user-side conversion)."""
    path = Path(path)
    if path.suffix.lower() != '.dwg':
        return path, None
    tool = shutil.which('dwg2dxf')
    if tool is None:
        raise SystemExit('DWG import requires LibreDWG (dwg2dxf) or an ODA converter on the server')
    out_dir = Path(tempfile.mkdtemp(prefix='dwg2dxf-'))
    out = out_dir / (path.stem + '.dxf')
    proc = subprocess.run([tool, '--as', 'r2000', '-o', str(out), str(path)],
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0 or not out.is_file():
        raise SystemExit(f'dwg2dxf failed: {(proc.stderr or proc.stdout)[:300]}')
    return out, tool


def raw_dxf_entities(path, scale):
    """Group-code scan of the ENTITIES section: tolerant of malformed DXF from converters."""
    lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    out, current, in_entities, verts = [], None, False, []
    fields = {}
    for code, value in pairs:
        if code == '0':
            if current == 'LWPOLYLINE' and in_entities:
                for i in range(len(verts)):
                    x1, y1, b = verts[i]
                    x2, y2, _ = verts[(i + 1) % len(verts)]
                    if abs(b) < 1e-12:
                        out.append(('line', (x1 * scale, y1 * scale), (x2 * scale, y2 * scale)))
                    else:
                        out.append(bulge_to_arc(x1, y1, x2, y2, b, scale))
            elif current and in_entities and fields:
                if current == 'LINE' and '10' in fields and '11' in fields:
                    out.append(('line', (float(fields['10']) * scale, float(fields['20']) * scale),
                                (float(fields['11']) * scale, float(fields['21']) * scale)))
                elif current == 'ARC' and '10' in fields:
                    out.append(('arc', (float(fields['10']) * scale, float(fields['20']) * scale),
                                float(fields['40']) * scale, math.radians(float(fields.get('50', 0))),
                                math.radians(float(fields.get('51', 360)))))
                elif current == 'CIRCLE' and '10' in fields:
                    out.append(('arc', (float(fields['10']) * scale, float(fields['20']) * scale),
                                float(fields['40']) * scale, 0.0, 2 * math.pi))
            current, fields, verts = value, {}, []
            in_entities = value == 'SECTION' and False or in_entities
            continue
        if current == 'SECTION' and code == '2' and value == 'ENTITIES':
            in_entities = True
            current = None
            continue
        if current == 'ENDSEC' and value == '':
            in_entities = False
        if not in_entities:
            continue
        if current == 'LWPOLYLINE' and code in ('10', '20', '42'):
            fields.setdefault(code, value)
            if code == '10':
                verts.append([float(value), 0.0, 0.0])
            elif code == '20' and verts:
                verts[-1][1] = float(value)
            elif code == '42' and verts:
                verts[-1][2] = float(value)
        elif code in ('10', '20', '11', '21', '40', '50', '51'):
            fields[code] = value
    return out


def sections_from_outer_rings(loops):
    """One section per outermost ring; a ring belongs to the smallest ring that contains it.

    Correct for profile drawings: separate profiles are separate outer rings, holes are contained.
    """
    rings = []
    for loop in loops:
        area = abs(signed_area(loop))
        if area < 1.0:
            continue
        rings.append({'pts': loop, 'area': area})
    for ring in rings:
        n = len(ring['pts'])
        cx = sum(p[0] for p in ring['pts']) / n
        cy = sum(p[1] for p in ring['pts']) / n
        probe = (cx, cy) if inside((cx, cy), ring['pts']) else ring['pts'][0]
        ring['probe'] = probe
    for ring in rings:
        ring['contained_by'] = [other for other in rings
                                if other is not ring and other['area'] > ring['area']
                                and inside(ring['probe'], other['pts'])]
    groups = {}
    for ring in rings:
        if ring['contained_by']:
            parent = min(ring['contained_by'], key=lambda r: r['area'])
            groups.setdefault(id(parent), [parent]).append(ring)
        else:
            groups.setdefault(id(ring), [ring])
    return [g[0]['pts'] and [r['pts'] for r in g] for g in groups.values()]


def cluster_rings(loops, gap=5.0):
    """Group rings into separate sections by bounding-box proximity (a drawing holds many profiles)."""
    def bbox(loop):
        xs = [p[0] for p in loop]
        ys = [p[1] for p in loop]
        return min(xs), min(ys), max(xs), max(ys)

    boxes = [bbox(loop) for loop in loops]
    parent = list(range(len(loops)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def near(a, b):
        return not (a[2] + gap < b[0] or b[2] + gap < a[0] or a[3] + gap < b[1] or b[3] + gap < a[1])

    for i in range(len(loops)):
        for j in range(i + 1, len(loops)):
            if near(boxes[i], boxes[j]):
                ra, rb = find(i), find(j)
                if ra != rb:
                    parent[rb] = ra
    groups = {}
    for i in range(len(loops)):
        groups.setdefault(find(i), []).append(loops[i])
    return list(groups.values())


def analyse_multi(path, gap=5.0):
    dxf_path, converter = to_dxf(path)
    unit_code, scale = 4, 1.0
    stream = None
    try:
        doc = ezdxf.readfile(str(dxf_path))  # pyright: ignore[reportPrivateImportUsage]
        unit_code = doc.header.get('$INSUNITS', 4)
        scale = UNITS.get(unit_code, 1.0)
        stream = entity_stream(doc, scale)
    except (ValueError, DXFStructureError) as error:
        sys.stderr.write(f'ezdxf rejected the DXF ({error}); using group-code scan\n')
    if stream is None:
        stream = raw_dxf_entities(dxf_path, scale)
    loops = build_loops([polyline_of(seg) for seg in stream])
    if not loops:
        return []
    # translate to the local origin: absolute drawing coordinates (hundreds of metres) destroy the
    # second-moment subtraction through catastrophic cancellation
    x0 = min(p[0] for loop in loops for p in loop)
    y0 = min(p[1] for loop in loops for p in loop)
    loops = [[(p[0] - x0, p[1] - y0) for p in loop] for loop in loops]
    sections = []
    for group in sections_from_outer_rings(loops):
        try:
            props = properties(group)
        except ValueError:
            continue
        props['entities'] = len(stream)
        props['units'] = f'INSUNITS={unit_code} scale={scale}'
        props['sourceFormat'] = Path(path).suffix.lower().lstrip('.')
        props['converter'] = converter or 'none (native DXF)'
        props['cxMm'] += x0
        props['cyMm'] += y0
        props['bboxMm'] = [props['bboxMm'][0] + x0, props['bboxMm'][1] + y0,
                           props['bboxMm'][2] + x0, props['bboxMm'][3] + y0]
        if props['areaMm2'] < 1.0:
            continue
        sections.append(props)
    sections.sort(key=lambda s: (-s['areaMm2']))
    return sections


def analyse(path):
    dxf_path, converter = to_dxf(path)
    unit_code, scale = 4, 1.0
    stream = None
    try:
        doc = ezdxf.readfile(str(dxf_path))  # pyright: ignore[reportPrivateImportUsage]
        unit_code = doc.header.get('$INSUNITS', 4)
        scale = UNITS.get(unit_code, 1.0)
        stream = entity_stream(doc, scale)
    except (ValueError, DXFStructureError) as error:            # converters can emit loose DXFs
        sys.stderr.write(f'ezdxf rejected the DXF ({error}); falling back to a group-code scan\n')
    if stream is None:
        stream = raw_dxf_entities(dxf_path, scale)
    loops = build_loops([polyline_of(seg) for seg in stream])
    props = properties(loops)
    props['entities'] = len(stream)
    props['units'] = f'INSUNITS={unit_code} scale={scale}'
    props['sourceFormat'] = Path(path).suffix.lower().lstrip('.')
    props['converter'] = converter or 'none (native DXF)'
    return props


def selftest_dwg():
    """End-to-end: build a DXF, convert it to DWG with dwgwrite, then import the DWG."""
    if shutil.which('dwgwrite') is None:
        print(json.dumps({'dwg_selftest': 'SKIP (dwgwrite not available)'}))
        return 0
    work = Path(tempfile.mkdtemp())
    dxf_path = work / 'input.dxf'
    dwg_path = work / 'input.dwg'
    doc = ezdxf.new('R2010')  # pyright: ignore[reportPrivateImportUsage]
    doc.header['$INSUNITS'] = 4
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (100, 0), (100, 60), (0, 60)], close=True)
    msp.add_lwpolyline([(40, 20), (60, 20), (60, 40), (40, 40)], close=True)
    doc.saveas(dxf_path)
    proc = subprocess.run(['dwgwrite', '-o', str(dwg_path), str(dxf_path)],
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(json.dumps({'dwg_selftest': 'SKIP (dwgwrite failed)', 'detail': proc.stderr[:200]}))
        return 0
    props = analyse(dwg_path)
    expected_area = 100 * 60 - 20 * 20
    ok = bool(abs(float(props['areaMm2']) - expected_area) / expected_area < 1e-6 and props['rings'] == 2)
    print(json.dumps({'dwg_selftest': ok, **{k: props[k] for k in ('areaMm2', 'ixMm4', 'rings', 'depths', 'sourceFormat', 'converter')}}, ensure_ascii=False))
    return 0 if ok else 1


def selftest():
    import tempfile
    name = Path(tempfile.mkdtemp()) / 'selftest.dxf'
    doc = ezdxf.new('R2010')  # pyright: ignore[reportPrivateImportUsage]
    doc.header['$INSUNITS'] = 4
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (100, 0), (100, 60), (0, 60)], close=True)
    msp.add_lwpolyline([(40, 20), (60, 20), (60, 40), (40, 40)], close=True)   # hole
    doc.saveas(name)
    props = analyse(name)
    expected_area = 100 * 60 - 20 * 20
    expected_ix = (100 * 60 ** 3 - 20 * 20 ** 3) / 12
    ok = bool(abs(float(props['areaMm2']) - expected_area) / expected_area < 1e-9
          and abs(float(props['ixMm4']) - expected_ix) / expected_ix < 1e-9
          and abs(float(props['cxMm']) - 50) < 1e-9 and abs(float(props['cyMm']) - 30) < 1e-9
          and props['rings'] == 2 and sorted(props['depths']) == [0, 1])
    print(json.dumps({'selftest': ok, **props}, ensure_ascii=False))
    return 0 if ok else 1


def main(argv):
    if '--split' in argv:
        path = next(a for a in argv[1:] if not a.startswith('--'))
        sections = analyse_multi(path)
        for i, props in enumerate(sections[:15], 1):
            print(f"#{i:<2} A={props['areaMm2']:10.2f} mm²  Ix={props['ixMm4']:14.4g}  Iy={props['iyMm4']:14.4g}  "
                  f"rings={props['rings']} bbox={[round(v, 1) for v in props['bboxMm']]}")
        print(f'total sections: {len(sections)}')
        if '--json' in argv:
            import json as _json
            out = Path(argv[argv.index('--json') + 1])
            out.write_text(_json.dumps({'file': path, 'sections': sections}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
            print(f'wrote {out}')
        return 0
    if '--selftest' in argv:
        return selftest()
    if '--selftest-dwg' in argv:
        return selftest_dwg()
    path = next((a for a in argv[1:] if not a.startswith('--')), None)
    if not path:
        print('usage: dxf-section.py <file.dxf> [--json out] [--selftest]')
        return 64
    props = analyse(path)
    text = json.dumps({'file': path, **props}, ensure_ascii=False, indent=1)
    if '--json' in argv:
        out = Path(argv[argv.index('--json') + 1])
        out.write_text(text + '\n', encoding='utf-8')
        print(f'wrote {out}')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
