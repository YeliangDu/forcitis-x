#!/usr/bin/env python3
"""Parse the Line/Arc geometry of a BREP using the decompile-confirmed field order.

HWKCADGraphModelDocObject::Serialize : int(21) , int64(+0x8) , int32(+0xc) , CbString(+0x10)
HWKCADGraphBase::Serialize          : int32(+0x48) , double(+0x50)
HWKCADGraphArc::Serialize           : int32(+0x70) , 3×double(+0x90/0x98/0xa0) ,
                                      gp_Pnt(+0xa8)=3 doubles , gp_Vec(+0xc0)=3 doubles , gp_Vec(+0xd8)=3 doubles
(HWKCADGraphLine is the same shape as Arc; the three doubles are the arc/line parameters.)
Everything after these fields is relation bookkeeping: int count + count × int id.
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
    raise SystemExit('cannot load scripts/poc/decode-brep.py')
_brep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_brep)

OUT = ROOT / 'evidence/poc/P1/brep-curves.json'


def read_string(buf, cursor):
    count = struct.unpack_from('<I', buf, cursor)[0]
    if count > 4096 or cursor + 4 + 2 * count > len(buf):
        return None, cursor
    text = buf[cursor + 4:cursor + 4 + 2 * count].decode('utf-16-le', 'replace')
    return text, cursor + 4 + 2 * count


def parse_entity(buf):
    """entity fields in write order; returns dict or None if the header does not fit."""
    cursor = 0
    version = struct.unpack_from('<i', buf, cursor)[0]
    cursor += 4
    ident = struct.unpack_from('<q', buf, cursor)[0]
    cursor += 8
    kind = struct.unpack_from('<i', buf, cursor)[0]
    cursor += 4
    name, cursor = read_string(buf, cursor)
    if name is None:
        return None
    base_int = struct.unpack_from('<i', buf, cursor)[0]
    cursor += 4
    base_double = struct.unpack_from('<d', buf, cursor)[0]
    cursor += 8
    own_int = struct.unpack_from('<i', buf, cursor)[0]
    cursor += 4
    params = struct.unpack_from('<3d', buf, cursor)
    cursor += 24
    pnt = struct.unpack_from('<3d', buf, cursor)
    cursor += 24
    vec1 = struct.unpack_from('<3d', buf, cursor)
    cursor += 24
    vec2 = struct.unpack_from('<3d', buf, cursor)
    cursor += 24
    return {'version': version, 'id': ident, 'kind': kind, 'name': name,
            'base_int': base_int, 'base_double': base_double, 'own_int': own_int,
            'params': [round(v, 4) for v in params], 'pnt': [round(v, 4) for v in pnt],
            'vec1': [round(v, 4) for v in vec1], 'vec2': [round(v, 4) for v in vec2],
            'fields_bytes': cursor, 'total_bytes': len(buf)}


def main():
    gallery = json.loads((ROOT / 'evidence/poc/P1/input/gallery.json').read_text(encoding='utf-8'))
    out = []
    for row in gallery:
        blob = base64.b64decode(row['BREP'])
        record = [r for r in _brep.find_records(blob) if r['name'].endswith(('HWKCADGraphArc', 'HWKCADGraphLine'))]
        entry = {'gallery_iid': row['IID'], 'name': row.get('name'), 'curves': []}
        for rec in record:
            body = blob[rec['payload']:rec['payload'] + rec['payload_len']]
            parsed = parse_entity(body)
            if parsed:
                parsed['type'] = rec['name'].rsplit('@', 1)[0].split(':')[-1]
                entry['curves'].append(parsed)
        out.append(entry)
        first = entry['curves'][0] if entry['curves'] else None
        print(f"{row['IID']:>5} {row.get('name',''):<12} curves={len(entry['curves'])} "
              f"fields={first['fields_bytes'] if first else '-'}B/{first['total_bytes'] if first else '-'}B "
              f"params={first['params'] if first else '-'} pnt={first['pnt'] if first else '-'}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'rows': out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('→', OUT.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
