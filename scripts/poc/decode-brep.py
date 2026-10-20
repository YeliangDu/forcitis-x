#!/usr/bin/env python3
"""P1 s4: split a 图库数据表.BREP blob into records (same tag+UTF-16-name framing as .cwx).

Evidence so far (evidence/poc/P1/input/gallery.json): every BREP starts with
`13 80` = tag 0x8013 = 0x8000|19, then the 19 UTF-16 chars of a `HWKCADGraph*` class name.
Record length is not stored, so records are located by scanning for the next plausible tag whose
name decodes to a known class (the same rule cwx-frame.py uses for .cwx).

Writes evidence/poc/P1/brep-records.json. Exit: 0 parsed, 2 no fixtures, 1 unparsable.
"""
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IN_DIR = ROOT / 'evidence/poc/P1/input'
OUT = ROOT / 'evidence/poc/P1/brep-records.json'
NAME_RE = re.compile(r'^HWK[A-Za-z0-9_]{3,60}$')


def names_at(blob, pos):
    """Return (name, payload_start) if a record header starts at pos."""
    if pos + 2 > len(blob):
        return None
    tag = int.from_bytes(blob[pos:pos + 2], 'little')
    if not tag & 0x8000:
        return None
    length = tag & 0x7FFF
    end = pos + 2 + 2 * length
    if length < 4 or end > len(blob):
        return None
    try:
        name = blob[pos + 2:end].decode('utf-16-le')
    except UnicodeDecodeError:
        return None
    if not NAME_RE.match(name):
        return None
    return name, end


def find_records(blob):
    records, pos = [], 0
    first = names_at(blob, 0)
    if first is None:
        return records
    records.append({'pos': 0, 'name': first[0], 'payload': first[1]})
    pos = first[1]
    while pos < len(blob) - 2:
        hit = None
        for probe in range(pos, len(blob) - 2):
            found = names_at(blob, probe)
            if found:
                hit = (probe, found[0], found[1])
                break
        if hit is None:
            break
        records.append({'pos': hit[0], 'name': hit[1], 'payload': hit[2]})
        pos = hit[2]
    for i, rec in enumerate(records):
        rec['payload_len'] = (records[i + 1]['pos'] if i + 1 < len(records) else len(blob)) - rec['payload']
    return records


def main():
    gallery = IN_DIR / 'gallery.json'
    if not gallery.is_file():
        print('BLOCKED: evidence/poc/P1/input/gallery.json missing')
        return 2
    rows = json.loads(gallery.read_text(encoding='utf-8'))
    out = []
    for row in rows:
        raw = row.get('BREP')
        if not raw:
            continue
        blob = base64.b64decode(raw) if isinstance(raw, str) else bytes(raw)
        records = find_records(blob)
        out.append({'gallery_iid': row['IID'], 'name': row.get('name'), 'bytes': len(blob),
                    'records': len(records),
                    'types': sorted({r['name'] for r in records}),
                    'detail': records[:40]})
        print(f"{row['IID']:>5} {row.get('name',''):<14} bytes={len(blob):>6} records={len(records):>4} "
              f"types={len({r['name'] for r in records})}")
    if not out:
        print('BLOCKED: no BREP payloads')
        return 2
    OUT.write_text(json.dumps({'rows': out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    first = out[0]
    print('first row types:', ', '.join(first['types'][:8]))
    print('first row first records:', [(r['name'], r['payload_len']) for r in first['detail'][:6]])
    return 0


if __name__ == '__main__':
    sys.exit(main())
