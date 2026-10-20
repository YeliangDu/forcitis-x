#!/usr/bin/env python3
"""Constraint search for the BREP entity layout (P1 s4, route A) — tail-first.

1. Relation arrays are `u32 count + count × u32 id`. Scan from the end for the longest suffix that
   parses as a whole number of such arrays; that fixes where the entity fields stop.
2. The region before it is tried against the decompile-confirmed kind order
   (i64, i32, str, i32, f64, i32, f64×3, pnt, vec, vec) at a few start offsets, with up to 3
   leading container ints allowed.
Print every candidate that consumes the header region exactly.

Usage: python3 scripts/poc/solve-brep-layout.py [gallery_iid]
"""
import base64
import importlib.util
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location('decode_brep', ROOT / 'scripts/poc/decode-brep.py')
if _spec is None or _spec.loader is None:
    raise SystemExit('cannot load decode-brep.py')
_brep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_brep)

KINDS = ['i64', 'i32', 'str', 'i32', 'f64', 'i32', 'f64', 'f64', 'f64', 'pnt', 'vec', 'vec']
WIDTH = {'i32': 4, 'i64': 8, 'f64': 8, 'pnt': 24, 'vec': 24, 'str': 4}


def relation_arrays(body, start):
    """Return number of arrays if body[start:] is exactly a sequence of relation arrays."""
    cursor, arrays = start, 0
    while cursor < len(body):
        if cursor + 4 > len(body):
            return None
        count = struct.unpack_from('<I', body, cursor)[0]
        if count == 0 or count > 512 or cursor + 4 + 4 * count > len(body):
            return None
        ids = struct.unpack_from(f'<{count}I', body, cursor + 4)
        if any(i >= 4096 for i in ids):
            return None
        cursor += 4 + 4 * count
        arrays += 1
        if arrays > 24:
            return None
    return arrays


def parse_fields(body, start, kinds):
    cursor, values = start, []
    for kind in kinds:
        if kind == 'str':
            if cursor + 4 > len(body):
                return None
            count = struct.unpack_from('<I', body, cursor)[0]
            if count == 0:
                cursor += 4
                values.append('')
                continue
            if count > 256 or cursor + 4 + 2 * count > len(body):
                return None
            try:
                text = body[cursor + 4:cursor + 4 + 2 * count].decode('utf-16-le')
            except UnicodeDecodeError:
                return None
            if not all(32 <= ord(ch) < 127 for ch in text):
                return None
            values.append(text)
            cursor += 4 + 2 * count
            continue
        width = WIDTH[kind]
        if cursor + width > len(body):
            return None
        if kind == 'i32':
            values.append(struct.unpack_from('<i', body, cursor)[0])
        elif kind == 'i64':
            values.append(struct.unpack_from('<q', body, cursor)[0])
        elif kind == 'f64':
            value = struct.unpack_from('<d', body, cursor)[0]
            if value != value or abs(value) > 1e4:
                return None
            values.append(round(value, 4))
        else:
            triple = struct.unpack_from('<3d', body, cursor)
            if any(v != v or abs(v) > 1e4 for v in triple):
                return None
            values.append([round(v, 4) for v in triple])
        cursor += width
    return cursor, values


def main(argv):
    gid = int(argv[1]) if len(argv) > 1 else 1783
    gallery = {r['IID']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/gallery.json').read_text(encoding='utf-8'))}
    blob = base64.b64decode(gallery[gid]['BREP'])
    for rec in _brep.find_records(blob):
        if not rec['name'].endswith(('HWKCADGraphArc', 'HWKCADGraphLine')):
            continue
        body = blob[rec['payload']:rec['payload'] + rec['payload_len']]
        print(f"{rec['name']} body={len(body)}")
        splits = [(p, relation_arrays(body, p)) for p in range(len(body) - 8, 0, -4)]
        splits = [(p, n) for p, n in splits if n]
        print('  relation-suffix candidates:', [(p, n) for p, n in splits[:4]])
        for stop, arrays in splits[:4]:
            for start in (0, 4, 8, 12, 16, 20):
                for cut in range(4):
                    kinds = KINDS[cut:] if cut else KINDS
                    hit = parse_fields(body, start, kinds)
                    if hit and hit[0] == stop:
                        print(f'  MATCH start={start} kinds={len(kinds)} stop={stop} arrays={arrays}')
                        print('    values:', hit[1])
                        return 0
    print('  no candidate')
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
