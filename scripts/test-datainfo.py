#!/usr/bin/env python3
"""Static evidence regression and malformed-input checks, not business tests."""
import importlib.util
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('decoder', ROOT / 'scripts/decode-datainfo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DataInfoTests(unittest.TestCase):
    def test_real_package_roundtrip(self):
        result = json.loads((module.OUT / 'decoded.json').read_text())
        self.assertEqual(len(result['sources']), 3)
        self.assertEqual(len({s['sha256'] for s in result['sources']}), 1)
        for source in result['sources']:
            blob = (ROOT / source['binary']).read_bytes()
            self.assertEqual(source['count'], 17)
            self.assertEqual(len(blob), 9466)
            rebuilt = bytearray(struct.pack('<I', source['count']))
            for row in source['records']:
                for key in ('label', 'connection_template'):
                    field = row[key]
                    self.assertEqual(field['length_offset'], len(rebuilt))
                    encoded = field['text'].encode('utf-16le')
                    rebuilt.extend(struct.pack('<I', len(encoded) // 2))
                    self.assertEqual(field['data_offset'], len(rebuilt))
                    self.assertEqual(field['byte_length'], len(encoded))
                    rebuilt.extend(encoded)
            self.assertEqual(bytes(rebuilt), blob)
            raw = (ROOT / source['source']).read_bytes()
            start = source['hex_file_offset']
            self.assertEqual(bytes.fromhex(raw[start:start + source['hex_length']].decode()), blob)
            self.assertEqual(module.decode(blob)['records'], source['records'])

    def test_rejects_corruption(self):
        for blob in (b'', b'\x01', struct.pack('<I', 0) + b'X',
                     struct.pack('<II', 1, 0xffffffff),
                     struct.pack('<III', 1, 1, 0)[:9],
                     struct.pack('<II', 1, 1) + b'\x00\xd8' + struct.pack('<I', 0)):
            with self.subTest(blob=blob), self.assertRaises((ValueError, UnicodeDecodeError)):
                module.decode(blob)


if __name__ == '__main__':
    unittest.main()
