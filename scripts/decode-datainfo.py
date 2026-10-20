#!/usr/bin/env python3
"""Decode an observed static config layout; does not open a database."""
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/baseline/b01/datainfo'


def decode(data):
    offset = 0

    def integer():
        nonlocal offset
        if offset + 4 > len(data):
            raise ValueError('truncated uint32')
        value = struct.unpack_from('<I', data, offset)[0]
        offset += 4
        return value

    count = integer()
    if count > (len(data) - 4) // 8:
        raise ValueError('record count exceeds available length headers')
    records = []
    for index in range(count):
        fields = {}
        for name in ('label', 'connection_template'):
            length_offset = offset
            units = integer()
            start = offset
            end = start + units * 2
            if end > len(data):
                raise ValueError('truncated UTF-16 field')
            text = data[start:end].decode('utf-16le', errors='strict')
            fields[name] = {'length_offset': length_offset, 'code_units': units,
                            'data_offset': start, 'byte_length': units * 2, 'text': text}
            offset = end
        records.append({'index': index, **fields})
    if offset != len(data):
        raise ValueError('unconsumed trailing bytes')
    return {'count': count, 'consumed_bytes': offset, 'records': records}


def collect():
    OUT.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((ROOT / 'evidence/baseline/b01/dependencies/inventory.json').read_text())
    sources = []
    for config in inventory['configs']:
        if not config['target_label'].lower().endswith('/hwksoftconfig.ini'):
            continue
        raw = (ROOT / config['source']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != config['sha256'] or raw != (ROOT / config['raw']).read_bytes():
            raise ValueError('source identity mismatch')
        match = re.search(rb'^DataInfo=([0-9A-Fa-f]+)\r?$', raw, re.M)
        if not match:
            raise ValueError('missing DataInfo hex')
        blob = bytes.fromhex(match[1].decode('ascii'))
        size = int(re.search(rb'^Size=(\d+)\r?$', raw, re.M)[1])
        if size != len(blob):
            raise ValueError('Size differs from decoded bytes')
        binary = OUT / (Path(config['source']).name + '.bin')
        binary.write_bytes(blob)
        selectors = dict((a.decode('ascii'), b.decode('ascii')) for a, b in
                         re.findall(rb'^(_X(?:64|86))=([^\r\n]*)', raw, re.M))
        sources.append({**config, 'hex_file_offset': match.start(1), 'hex_length': len(match[1]),
                        'declared_size': size, 'selectors': selectors,
                        'binary': str(binary.relative_to(ROOT)),
                        'blob_sha256': hashlib.sha256(blob).hexdigest(), **decode(blob)})
    result = {'evidence_type': 'STATIC_PACKAGE', 'status': 'PARTIAL',
              'layout': 'Observed uint32le record count, then pairs of uint32le UTF-16 code-unit lengths and UTF-16LE payloads; offsets relative to decoded blob.',
              'limitations': ['No execution or database connection; selector use and runtime provider availability unverified.',
                              'Layout inferred from complete consumption and roundtrip, not original parser control flow.'],
              'sources': sources}
    (OUT / 'decoded.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'sources': len(sources), 'counts': [s['count'] for s in sources],
                      'sizes': [s['consumed_bytes'] for s in sources], 'status': 'PARTIAL'}))


if __name__ == '__main__':
    collect()
