#!/usr/bin/env python3
"""Block census for a DWG/DXF: how many blocks, and which ones look like profile sections.

Two-pass group-code scan (works on converter output that ezdxf refuses):
  pass 1: OBJECTS/BLOCK_RECORD -> {handle: name}
  pass 2: BLOCKS -> per block (owner handle 330 -> name) entity stream; ENTITIES -> INSERT placement
Then每块计算闭合环与特性，并按"有闭合环且净面积>=阈值"标记为疑似型材断面。

Usage: python3 scripts/poc/dwg-blocks.py <file> [--json out]
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
SECTION_AREA_MIN = 50.0     # mm², below this a ring is decoration, not a profile


def to_dxf_path(path):
    path = Path(path)
    if path.suffix.lower() != '.dwg':
        return path, None
    import shutil
    tool = shutil.which('dwg2dxf')
    if tool is None:
        raise SystemExit('DWG needs LibreDWG (dwg2dxf) or an ODA converter')
    out = Path(tempfile.mkdtemp(prefix='dwg2dxf-')) / (path.stem + '.dxf')
    proc = subprocess.run([tool, '--as', 'r2000', '-o', str(out), str(path)],
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0 or not out.is_file():
        raise SystemExit(f'dwg2dxf failed: {(proc.stderr or proc.stdout)[:200]}')
    return out, tool


def pairs_of(path):
    lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    return [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]


def block_record_names(pairs):
    """BLOCK_RECORD lives in the TABLES section: `0 BLOCK_RECORD / 5 handle / ... / 2 name`."""
    names, in_record, handle = {}, False, None
    for code, value in pairs:
        if code == '0':
            in_record = value == 'BLOCK_RECORD'
            handle = None
            continue
        if not in_record:
            continue
        if code == '5':
            handle = value
        elif code == '2' and handle:
            names[handle] = value
            in_record = False
    return names


def scan_blocks(pairs, names):
    blocks = defaultdict(list)
    inserts = Counter()
    section, name, current, fields, verts = None, None, None, {}, []

    def emit():
        nonlocal current, fields, verts
        if not current or name is None:
            current, fields, verts = None, {}, []
            return
        target = blocks[name]
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
            emit()
            if value == 'SECTION':
                section = 'SECTION'
            elif value == 'ENDSEC':
                section = None
            elif value in ('BLOCK', 'ENDBLK'):
                name = None
            elif value == 'INSERT':
                inserts['__pending__'] += 1
            current = value
            continue
        if current == 'SECTION' and code == '2':
            section = value
            current = None
            continue
        if section == 'BLOCKS' and current == 'BLOCK':
            if code == '330':
                name = names.get(value)
            continue
        if section == 'ENTITIES' and current == 'INSERT':
            continue
        if section == 'BLOCKS' and name is None:
            continue
        if current == 'LWPOLYLINE' and code in ('10', '20', '42'):
            if code == '10':
                verts.append([float(value), 0.0, 0.0])
            elif code == '20' and verts:
                verts[-1][1] = float(value)
            elif code == '42' and verts:
                verts[-1][2] = float(value)
        elif code in ('10', '20', '11', '21', '40', '50', '51'):
            fields[code] = value
    emit()
    return blocks, inserts


def main(argv):
    path = next((a for a in argv[1:] if not a.startswith('--')), None)
    if not path:
        print('usage: dwg-blocks.py <file> [--json out]')
        return 64
    dxf_path, converter = to_dxf_path(path)
    pairs = pairs_of(dxf_path)
    names = block_record_names(pairs)
    blocks, _ = scan_blocks(pairs, names)
    rows = []
    for name, segs in blocks.items():
        if not segs:
            continue
        loops = _dxf.build_loops([_dxf.polyline_of(seg) for seg in segs])
        try:
            props = _dxf.properties(loops)
        except ValueError:
            rows.append({'block': name, 'segments': len(segs), 'status': 'no closed ring'})
            continue
        rows.append({'block': name, 'segments': len(segs), 'rings': props['rings'],
                     'areaMm2': props['areaMm2'], 'ixMm4': props['ixMm4'], 'iyMm4': props['iyMm4'],
                     'bboxMm': props['bboxMm'], 'status': 'ok'})
    sections = [r for r in rows if r['status'] == 'ok' and r['areaMm2'] >= SECTION_AREA_MIN]
    sections.sort(key=lambda r: -r['areaMm2'])
    print(f'blocks with geometry: {len(rows)}   closed-ring blocks: {sum(1 for r in rows if r["status"] == "ok")}   '
          f'profile-like (>= {SECTION_AREA_MIN:g} mm²): {len(sections)}')
    for row in sections[:25]:
        w = row['bboxMm'][2] - row['bboxMm'][0]
        h = row['bboxMm'][3] - row['bboxMm'][1]
        print(f"  {row['block'][:26]:<26} A={row['areaMm2']:9.2f}  rings={row['rings']:<2} "
              f"bbox={w:7.1f}x{h:6.1f}  Ix={row['ixMm4']:11.4g}")
    if '--json' in argv:
        out = Path(argv[argv.index('--json') + 1])
        out.write_text(json.dumps({'file': path, 'converter': converter or 'none',
                                   'blocks': len(rows), 'sections': sections}, ensure_ascii=False, indent=1) + '\n',
                       encoding='utf-8')
        print(f'wrote {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
