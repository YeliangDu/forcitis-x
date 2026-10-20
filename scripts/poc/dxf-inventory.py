#!/usr/bin/env python3
"""DWG/DXF entity inventory + per-block section properties.

Answers two questions for any drawing:
  1. which entity types does it contain, and can we handle them?  (--inventory)
  2. which block is which section, and what are its properties?     (--by-block)

Implemented as a group-code scanner so it also works for DXF files that third-party converters emit
with broken handles/sub-entities (ezdxf then refuses to open them).

Usage:
  python3 scripts/poc/dxf-inventory.py <file.dwg|dxf> --inventory
  python3 scripts/poc/dxf-inventory.py <file.dwg|dxf> --by-block [--json out]
"""
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_dxf = load('dxf-section')
SUPPORTED = {'LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE', 'POLYLINE', 'INSERT'}
GEOMETRY_ONLY = {'TEXT', 'MTEXT', 'DIMENSION', 'ATTDEF', 'ATTRIB', 'HATCH', 'POINT', 'VIEWPORT',
                 'LEADER', 'MLEADER', 'TOLERANCE', 'WIPEOUT', 'IMAGE', 'OLE2FRAME'}


def to_dxf_path(path):
    path = Path(path)
    if path.suffix.lower() != '.dwg':
        return path, None
    import shutil
    tool = shutil.which('dwg2dxf')
    if tool is None:
        raise SystemExit('DWG needs LibreDWG (dwg2dxf) or an ODA converter on the server')
    out = Path(tempfile.mkdtemp(prefix='dwg2dxf-')) / (path.stem + '.dxf')
    proc = subprocess.run([tool, '--as', 'r2000', '-o', str(out), str(path)],
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0 or not out.is_file():
        raise SystemExit(f'dwg2dxf failed: {(proc.stderr or proc.stdout)[:300]}')
    return out, tool


def scan(path):
    """Return {'header':..., 'entities': Counter, 'blocks': {name: [segments]}, 'model': [segments],
    'inserts': [(block, x, y, sx, sy, rot)]}."""
    lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    insunits = 4
    section = None
    block_name = None
    blocks = defaultdict(list)
    model = []
    inserts = []
    counts = Counter()
    current = None
    fields = {}
    verts = []
    block_insert = {'x': 0.0, 'y': 0.0, 'sx': 1.0, 'sy': 1.0, 'rot': 0.0}

    def flush(target):
        nonlocal current, fields, verts
        if not current:
            return
        counts[current] += 1
        if current == 'LWPOLYLINE':
            for i in range(len(verts)):
                x1, y1, b = verts[i]
                x2, y2, _ = verts[(i + 1) % len(verts)]
                target.append(('line', (x1, y1), (x2, y2)) if abs(b) < 1e-12
                              else _dxf.bulge_to_arc(x1, y1, x2, y2, b, 1.0))
        elif current == 'LINE' and {'10', '11'} <= fields.keys():
            target.append(('line', (float(fields['10']), float(fields['20'])),
                           (float(fields['11']), float(fields['21']))))
        elif current == 'ARC' and '10' in fields:
            target.append(('arc', (float(fields['10']), float(fields['20'])), float(fields['40']),
                           math.radians(float(fields.get('50', 0))),
                           math.radians(float(fields.get('51', 360)))))
        elif current == 'CIRCLE' and '10' in fields:
            target.append(('arc', (float(fields['10']), float(fields['20'])), float(fields['40']),
                           0.0, 2 * math.pi))
        current, fields, verts = None, {}, []

    for code, value in pairs:
        if code == '0':
            if section == 'BLOCKS':
                flush(blocks[block_name] if block_name else model)
            else:
                flush(model)
            if value == 'BLOCK':
                block_name = None
                block_insert = {'x': 0.0, 'y': 0.0, 'sx': 1.0, 'sy': 1.0, 'rot': 0.0}
            elif value == 'ENDBLK':
                block_name = None
            elif value == 'INSERT':
                inserts.append([None, 0.0, 0.0, 1.0, 1.0, 0.0])
            elif value == 'SECTION':
                section = 'SECTION'
            elif value == 'ENDSEC':
                section = None
            current = value
            continue
        if code == '0' or value == '':
            continue
        if current == 'SECTION' and code == '2':
            section = value
            current = None
            continue
        if section == 'HEADER' and code == '9' and value == '$INSUNITS':
            insunits = -1
            continue
        if insunits == -1 and code == '70':
            insunits = int(value)
            continue
        if section == 'BLOCKS' and current == 'BLOCK':
            if code == '2' and block_name is None:
                block_name = value
            elif code in ('10', '20'):
                block_insert['x' if code == '10' else 'y'] = float(value)
            continue
        if current == 'INSERT' and inserts:
            row = inserts[-1]
            if code == '2':
                row[0] = value
            elif code == '10':
                row[1] = float(value)
            elif code == '20':
                row[2] = float(value)
            elif code == '41':
                row[3] = float(value)
            elif code == '42':
                row[4] = float(value)
            elif code == '50':
                row[5] = math.radians(float(value))
            continue
        target = blocks[block_name] if (section == 'BLOCKS' and block_name) else model
        if current == 'LWPOLYLINE' and code in ('10', '20', '42'):
            if code == '10':
                verts.append([float(value), 0.0, 0.0])
            elif code == '20' and verts:
                verts[-1][1] = float(value)
            elif code == '42' and verts:
                verts[-1][2] = float(value)
        elif code in ('10', '20', '11', '21', '40', '50', '51'):
            fields[code] = value
        del target
    flush(model)
    scale = _dxf.UNITS.get(insunits, 1.0)
    return {'insunits': insunits, 'scale': scale, 'counts': counts,
            'blocks': {name: segs for name, segs in blocks.items() if segs and not name.startswith('*')},
            'model': model, 'inserts': [tuple(r) for r in inserts if r[0]]}


def main(argv):
    path = next((a for a in argv[1:] if not a.startswith('--')), None)
    if not path:
        print('usage: dxf-inventory.py <file> [--inventory|--by-block] [--json out]')
        return 64
    dxf_path, converter = to_dxf_path(path)
    data = scan(dxf_path)
    if '--inventory' in argv:
        counts = data['counts']
        known = {k: v for k, v in counts.items() if k in SUPPORTED}
        other = {k: v for k, v in counts.items() if k not in SUPPORTED and k not in GEOMETRY_ONLY}
        text = {k: v for k, v in counts.items() if k in GEOMETRY_ONLY}
        print(json.dumps({'file': path, 'converter': converter or 'none', 'insunits': data['insunits'],
                          'scaleToMm': data['scale'], 'entities': sum(counts.values()),
                          'supported': known, 'nonGeometric': text, 'unsupported': other,
                          'blocks': len(data['blocks']), 'inserts': len(data['inserts'])},
                         ensure_ascii=False, indent=1))
        return 0
    if '--by-block' in argv:
        rows = []
        for name, segs in data['blocks'].items():
            stream = [(seg[0], (seg[1][0] * data['scale'], seg[1][1] * data['scale']),
                       (seg[2][0] * data['scale'], seg[2][1] * data['scale'])) if seg[0] == 'line'
                      else (seg[0], (seg[1][0] * data['scale'], seg[1][1] * data['scale']),
                            seg[2] * data['scale'], seg[3], seg[4]) for seg in segs]
            loops = _dxf.build_loops([_dxf.polyline_of(seg) for seg in stream])
            try:
                props = _dxf.properties(loops)
            except ValueError:
                rows.append({'block': name, 'segments': len(segs), 'status': 'no closed ring'})
                continue
            rows.append({'block': name, 'segments': len(segs), 'rings': props['rings'],
                         'areaMm2': props['areaMm2'], 'ixMm4': props['ixMm4'], 'iyMm4': props['iyMm4'],
                         'cxMm': props['cxMm'], 'cyMm': props['cyMm'], 'status': 'ok'})
        rows.sort(key=lambda r: -(r.get('areaMm2') or 0))
        for row in rows[:20]:
            if row['status'] == 'ok':
                print(f"{row['block'][:28]:<28} seg={row['segments']:<5} rings={row['rings']:<3} "
                      f"A={row['areaMm2']:10.2f} Ix={row['ixMm4']:12.4g} Iy={row['iyMm4']:12.4g}")
            else:
                print(f"{row['block'][:28]:<28} seg={row['segments']:<5} {row['status']}")
        print(f'blocks with geometry: {len(rows)}')
        if '--json' in argv:
            out = Path(argv[argv.index('--json') + 1])
            out.write_text(json.dumps({'file': path, 'blocks': rows}, ensure_ascii=False, indent=1) + '\n',
                           encoding='utf-8')
            print(f'wrote {out}')
        return 0
    print('choose --inventory or --by-block')
    return 64


if __name__ == '__main__':
    sys.exit(main(sys.argv))
