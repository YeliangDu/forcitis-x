#!/usr/bin/env python3
"""Acquisition checks only, not HWK business acceptance."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit-msi-streams.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AuditTests(unittest.TestCase):
    def test_real_source_and_comparison_tamper(self):
        old = json.loads((m.ROOT / 'evidence/baseline/b01/msi-decoded/tables.json').read_text())['tables']
        result = m.audit(comparison=old)
        props = {r['values']['Property']: r['values']['Value'] for r in result['tables']['Property']}
        self.assertEqual(props['ProductVersion'], '05.45.1211')
        self.assertEqual(sum(bool(s and s['extended']) for s in result['strings'].values()), 1)
        for row in result['tables']['File']:
            payload = m.ROOT / 'evidence/baseline/extracted/cab' / row['values']['File']
            self.assertEqual(payload.stat().st_size, row['values']['FileSize'])
        altered = copy.deepcopy(old)
        altered['Property'][0]['Value'] = 'tampered'
        with self.assertRaisesRegex(ValueError, 'disagree'):
            m.audit(comparison=altered)

    def test_bad_streams_fail_closed(self):
        pool = (m.BASE / '!_StringPool').read_bytes()
        data = (m.BASE / '!_StringData').read_bytes()
        for bad_pool, bad_data in [(pool[:-1], data), (pool, data[:-1]),
                                   (pool, data + b'x'), (pool[:2] + b'\0\x80' + pool[4:], data)]:
            with self.subTest(lengths=(len(bad_pool), len(bad_data))):
                with self.assertRaises(ValueError):
                    m.strings(bad_pool, bad_data)
        strings = m.strings(pool, data)
        raw = (m.BASE / '!Property').read_bytes()
        for bad in [raw[:-1], b'\xff\xff' + raw[2:]]:
            with self.assertRaises(ValueError):
                m.table(bad, m.SCHEMAS['Property'], strings)


if __name__ == '__main__':
    unittest.main(verbosity=2)
