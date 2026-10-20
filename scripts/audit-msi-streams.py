#!/usr/bin/env python3
"""Independent, fixed-schema MSI stream audit; no original decoder imports.

Sources and scope are recorded in evidence/baseline/b01/msi-independent/findings.md.
This reads extracted streams, not OLE, and never executes MSI actions.
"""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'evidence/baseline/extracted/msi'
OUT = ROOT / 'evidence/baseline/b01/msi-independent'
# Explicit public table layouts, independent of the prior _Columns decoder.
SCHEMAS = {
    'Property': [('Property', 's'), ('Value', 's')],
    'File': [('File', 's'), ('Component_', 's'), ('FileName', 's'),
             ('FileSize', 'i4'), ('Version', 's'), ('Language', 's'),
             ('Attributes', 'i2'), ('Sequence', 'i2')],
    'CustomAction': [('Action', 's'), ('Type', 'i2'), ('Source', 's'), ('Target', 's')],
    'InstallExecuteSequence': [('Action', 's'), ('Condition', 's'), ('Sequence', 'i2')],
    'InstallUISequence': [('Action', 's'), ('Condition', 's'), ('Sequence', 'i2')],
}


def strings(pool, data):
    if len(pool) < 4 or len(pool) % 4 or pool[:4] != b'\xa8\x03\0\0':
        raise ValueError('Audit limited to codepage 936 and 16-bit string references')
    entries = {0: None}
    cursor = 0
    slot = 1
    while slot * 4 < len(pool):
        start = slot * 4
        size, refs = struct.unpack_from('<HH', pool, start)
        slot += 1
        extended = size == 0 and refs != 0
        if extended:
            if slot * 4 + 4 > len(pool):
                raise ValueError('Truncated extended length')
            size = int.from_bytes(pool[slot * 4:slot * 4 + 4], 'little')
            slot += 1
        end = cursor + size
        if end > len(data):
            raise ValueError('Truncated string data')
        raw = data[cursor:end]
        entries[len(entries)] = {
            'pool_offset': start, 'data_offset': cursor, 'length': size,
            'reference_count': refs, 'extended': extended,
            'text': raw.decode('cp936') if size else None,
            'sha256': hashlib.sha256(raw).hexdigest(),
        }
        cursor = end
    if cursor != len(data):
        raise ValueError('Unconsumed string data')
    return entries


def table(raw, schema, pool):
    widths = [4 if kind == 'i4' else 2 for _, kind in schema]
    if len(raw) % sum(widths):
        raise ValueError('Invalid table byte length')
    count = len(raw) // sum(widths)
    records = [{'values': {}, 'cells': {}} for _ in range(count)]
    column_base = 0
    for (name, kind), width in zip(schema, widths):
        column = raw[column_base:column_base + width * count]
        for row, (number,) in enumerate(struct.iter_unpack('<I' if width == 4 else '<H', column)):
            offset = column_base + row * width
            cell = {'offset': offset, 'hex': raw[offset:offset + width].hex()}
            if kind == 's':
                if number not in pool:
                    raise ValueError('String reference out of range')
                cell['string_id'] = number
                value = pool[number]['text'] if pool[number] else None
            else:
                value = number - 2 ** (width * 8 - 1) if number else None
            records[row]['values'][name] = value
            records[row]['cells'][name] = cell
        column_base += len(column)
    return records


def audit(base=BASE, comparison=None):
    inputs = {}
    def read(name):
        data = (base / name).read_bytes()
        inputs[name] = {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        return data
    pool = strings(read('!_StringPool'), read('!_StringData'))
    tables = {name: table(read('!' + name), schema, pool) for name, schema in SCHEMAS.items()}
    agreement = None
    if comparison is not None:
        agreement = {name: [r['values'] for r in rows] == comparison[name] for name, rows in tables.items()}
        if not all(agreement.values()):
            raise ValueError('Independent tables disagree with prior capture')
    return {'status': 'PARTIAL', 'evidence_type': 'STATIC_PACKAGE',
            'scope': 'Five fixed-schema extracted streams; no OLE reader or installer execution',
            'inputs': inputs, 'strings': pool, 'tables': tables, 'agreement': agreement}


if __name__ == '__main__':
    previous = json.loads((ROOT / 'evidence/baseline/b01/msi-decoded/tables.json').read_text())['tables']
    result = audit(comparison=previous)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'counts': {k: len(v) for k, v in result['tables'].items()},
                      'agreement': result['agreement']}, indent=2))
