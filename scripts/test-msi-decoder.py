#!/usr/bin/env python3
"""Static acquisition regression, not product or original-runtime acceptance."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('decoder', Path(__file__).with_name('decode-msi-tables.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class DecoderTests(unittest.TestCase):
    def test_real_package_relations(self):
        cp, columns, tables = m.decode(m.BASE)
        self.assertEqual(cp, 936)
        props = {r['Property']: r['Value'] for r in tables['Property']}
        self.assertEqual(props['ProductVersion'], '05.45.1211')
        files = tables['File']
        self.assertEqual(len(files), 458)
        self.assertEqual(sorted(r['Sequence'] for r in files), list(range(1, 459)))
        components = {r['Component']: r for r in tables['Component']}
        dirs = {r['Directory']: r for r in tables['Directory']}
        for c in components.values():
            self.assertIn(c['Directory_'], dirs)
        for d in dirs.values():
            if d['Directory_Parent']:
                self.assertIn(d['Directory_Parent'], dirs)
        for row in files:
            self.assertIn(row['Component_'], components)
            payload = m.ROOT/'evidence/baseline/extracted/cab'/row['File']
            self.assertEqual(payload.stat().st_size, row['FileSize'])
        self.assertEqual({p.name for p in payload.parent.iterdir() if p.is_file()}, {r['File'] for r in files})
        for table in {r['Table'] for r in columns}:
            schema = sorted((r for r in columns if r['Table'] == table), key=lambda r:r['Number'])
            self.assertEqual([r['Number'] for r in schema], list(range(1,len(schema)+1)))
            if table not in tables:
                continue  # Schema-only table: no stream, no rows decoded.
            keys = [r['Name'] for r in schema if r['Type'] & 0x2000]
            records = [tuple(row[k] for k in keys) for row in tables[table]]
            self.assertEqual(len(records), len(set(records)), table)

    def test_corruption_rejected_and_clean_control(self):
        with tempfile.TemporaryDirectory() as d:
            work = Path(d)/'msi'
            shutil.copytree(m.BASE, work)
            for filename in ['!_StringData', '!File']:
                p = work/filename
                original = p.read_bytes()
                p.write_bytes(original[:-1])
                with self.assertRaises(ValueError):
                    m.decode(work)
                p.write_bytes(original)
                self.assertEqual(len(m.decode(work)[2]['File']), 458)

if __name__ == '__main__':
    unittest.main(verbosity=2)
