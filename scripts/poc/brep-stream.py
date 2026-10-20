#!/usr/bin/env python3
"""Split a BREP entity body into sub-objects and profile their payload sizes (P1 s4).

Model (measured): each sub-object starts with `u32 version(6) + u32 objectId + u64 0` (16 B).
Between two headers sits the previous object's payload; the last 2 bytes before the next header
carry a small marker (observed `04 00`).

Usage: python3 scripts/poc/brep-stream.py [gallery_iid]
"""
import base64
import importlib.util
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location('decode_brep', ROOT / 'scripts/poc/decode-brep.py')
if _spec is None or _spec.loader is None:
    raise SystemExit('cannot load decode-brep.py')
_brep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_brep)

VERSION = 6


def headers(body):
    """Positions where `u32 6 | u32 id | u64 0` starts."""
    out = []
    for pos in range(len(body) - 16):
        if body[pos:pos + 4] != struct.pack('<I', VERSION):
            continue
        obj_id = struct.unpack_from('<I', body, pos + 4)[0]
        if not 1 <= obj_id <= 99999:
            continue
        if body[pos + 8:pos + 16] != b'\x00' * 8:
            continue
        out.append((pos, obj_id))
    return out


def main(argv):
    gid = int(argv[1]) if len(argv) > 1 else 1783
    gallery = {r['IID']: r for r in json.loads((ROOT / 'evidence/poc/P1/input/gallery.json').read_text(encoding='utf-8'))}
    blob = base64.b64decode(gallery[gid]['BREP'])
    for rec in _brep.find_records(blob):
        if not rec['name'].endswith(('HWKCADGraphArc', 'HWKCADGraphLine')):
            continue
        body = blob[rec['payload']:rec['payload'] + rec['payload_len']]
        marks = headers(body)
        ids = [i for _, i in marks]
        print(f"{rec['name']} body={len(body)} sub-objects={len(marks)} ids={ids[:12]}{'…' if len(ids) > 12 else ''}")
        lengths = []
        for k, (pos, obj_id) in enumerate(marks):
            start = pos + 16
            stop = marks[k + 1][0] if k + 1 < len(marks) else len(body)
            lengths.append((obj_id, stop - start))
        hist = Counter(length for _, length in lengths)
        print('  payload length histogram:', dict(sorted(hist.items())[:12]))
        for obj_id, length in lengths[:6]:
            start = next(p for p, i in marks if i == obj_id) + 16
            seg = body[start:start + min(length, 48)]
            print(f'   id={obj_id:<4} len={length:<5} head={seg.hex()[:64]}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
