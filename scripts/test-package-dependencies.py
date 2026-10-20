#!/usr/bin/env python3
"""Real-payload acquisition checks; no runtime or business acceptance."""
import hashlib
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/baseline/b01/dependencies'


class AcquisitionTests(unittest.TestCase):
    def test_complete_inventory_and_independent_pe_headers(self):
        report = json.loads((OUT / 'inventory.json').read_text())
        expected = {str(p.relative_to(ROOT)) for directory in ('cab', 'msi')
                    for p in (ROOT / 'evidence/baseline/extracted' / directory).iterdir()
                    if p.is_file() and (directory == 'cab' or p.name.startswith('Binary.'))
                    and p.read_bytes().startswith(b'MZ')}
        self.assertEqual(expected, {r['source'] for r in report['pe']})
        for row in report['pe']:
            data = (ROOT / row['source']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), row['sha256'])
            self.assertEqual(row['exit_code'], 0)
            pe = struct.unpack_from('<I', data, 0x3c)[0]
            self.assertEqual(data[pe:pe+4], b'PE\0\0')
            machine = struct.unpack_from('<H', data, pe+4)[0]
            self.assertEqual(row['format'], [{0x8664: 'coff-x86-64', 0x14c: 'coff-i386'}[machine]])
            optional = pe + 24
            magic = struct.unpack_from('<H', data, optional)[0]
            directory = optional + {0x20b: 112, 0x10b: 96}[magic]
            self.assertEqual(row['clr_directory'], list(struct.unpack_from('<II', data, directory + 14*8)))

    def test_configs_are_byte_exact(self):
        report = json.loads((OUT / 'inventory.json').read_text())
        self.assertTrue(report['configs'])
        for row in report['configs']:
            self.assertEqual((ROOT / row['source']).read_bytes(), (ROOT / row['raw']).read_bytes())


if __name__ == '__main__':
    unittest.main()
