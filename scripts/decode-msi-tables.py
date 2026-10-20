#!/usr/bin/env python3
"""Read already extracted MSI streams; never executes installer code.
Format references: GNOME/msitools libmsi/{table,string}.c (see evidence report).
Limited to 16-bit string references; supports extended string pool entries.
"""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'evidence/baseline/extracted/msi'
OUT = ROOT / 'evidence/baseline/b01/msi-decoded'


def decode(base):
    pool = (base / '!_StringPool').read_bytes()
    data = (base / '!_StringData').read_bytes()
    codepage, flags = struct.unpack('<HH', pool[:4])
    if flags or len(pool) % 4:
        raise ValueError('Unsupported string pool header')
    strings = [None]
    offset = 0
    pos = 4
    while pos < len(pool):
        length, refs = struct.unpack_from('<HH', pool, pos)
        pos += 4
        if length == 0 and refs:
            low, high = struct.unpack_from('<HH', pool, pos)
            length = low + (high << 16)
            pos += 4
        if offset + length > len(data):
            raise ValueError('Truncated string data')
        strings.append(data[offset:offset+length].decode(f'cp{codepage}') if length else None)
        offset += length
    if offset != len(data):
        raise ValueError('Unconsumed string data')

    def table(name, cols):
        raw = (base / ('!' + name)).read_bytes()
        widths = [2 if t & 0x800 or (t & 0xff) <= 2 else 4 for _, t in cols]
        row_size = sum(widths)
        if len(raw) % row_size:
            raise ValueError(f'Invalid table size: {name}')
        count = len(raw) // row_size
        rows = [{} for _ in range(count)]
        offset = 0
        for (col, typ), width in zip(cols, widths):
            for i, row in enumerate(rows):
                start = offset * count + i * width
                value = int.from_bytes(raw[start:start+width], 'little')
                row[col] = strings[value] if typ & 0x800 else (value - (1 << (8*width-1)) if value else None)
            offset += width
        return rows

    columns = table('_Columns', [('Table', 0x840), ('Number', 2), ('Name', 0x840), ('Type', 2)])
    tables = {}
    for name in sorted({r['Table'] for r in columns}):
        schema = sorted((r for r in columns if r['Table'] == name), key=lambda r: r['Number'])
        if (base / ('!' + name)).exists():
            tables[name] = table(name, [(r['Name'], r['Type']) for r in schema])
    return codepage, columns, tables


def collect():
    codepage, columns, tables = decode(BASE)
    OUT.mkdir(parents=True, exist_ok=True)
    def save(name, obj):
        (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    save('tables.json', {'evidence_type': 'STATIC_PACKAGE', 'codepage': codepage, 'columns': columns, 'tables': tables})
    dirs = {r['Directory']: r for r in tables['Directory']}
    components = {r['Component']: r for r in tables['Component']}
    def directory(key, seen=()):
        if key in seen:
            raise ValueError('Directory cycle')
        row = dirs[key]
        target = row['DefaultDir'].split(':')[0].split('|')[-1]
        parent = directory(row['Directory_Parent'], seen+(key,)) if row['Directory_Parent'] else []
        # Standard directory roots stay symbolic: runtime property resolution is unknown.
        return parent + ([f'[{key}]'] if not row['Directory_Parent'] else ([] if target == '.' else [target]))
    files = []
    for row in tables['File']:
        component = components[row['Component_']]
        payload = ROOT / 'evidence/baseline/extracted/cab' / row['File']
        path = '/'.join(directory(component['Directory_']) + [row['FileName'].split('|')[-1]])
        files.append({**row, 'symbolic_target': path, 'cab_exists': payload.is_file(),
                      'size_matches': payload.is_file() and payload.stat().st_size == row['FileSize'],
                      'sha256': hashlib.sha256(payload.read_bytes()).hexdigest() if payload.is_file() else None})
    save('file-map.json', files)
    summary = {'evidence_type': 'STATIC_PACKAGE', 'status': 'PARTIAL',
               'properties': {r['Property']: r['Value'] for r in tables['Property']},
               'table_counts': {k: len(v) for k, v in tables.items()},
               'schema_without_stream': sorted({r['Table'] for r in columns} - set(tables)),
               'files': len(files), 'cab_matches': sum(r['cab_exists'] for r in files),
               'size_matches': sum(r['size_matches'] for r in files),
               'unmapped_cab': sorted(p.name for p in (ROOT/'evidence/baseline/extracted/cab').iterdir() if p.is_file() and p.name not in {r['File'] for r in files}),
               'dependency_tables': {k: tables.get(k) for k in ['Media', '_VsdLaunchCondition', 'AppSearch', 'Signature', 'DrLocator', 'CustomAction', 'ModuleSignature']},
               'limitations': ['Custom limited parser; independent MSI reader comparison pending.', 'Symbolic target paths do not resolve Windows folder properties.', 'No installer execution, runtime dependency or launch condition acceptance verified.']}
    save('summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    collect()
