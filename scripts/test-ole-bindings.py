#!/usr/bin/env python3
"""Acquisition regression, not product acceptance."""
import importlib.util, struct, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('ole',Path(__file__).with_name('audit-ole-bindings.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def test_real_package(self):
        r=m.audit()
        self.assertEqual(len(r['streams']),59)
        self.assertEqual(len(r['binary_rows']),6)
        self.assertEqual({b['action']['Target'] for b in r['bindings']},
                         {'HWKInstallDo','CheckFX','VsdLaunchConditions'})
        self.assertTrue(any(s['mini'] for s in r['streams']))
        self.assertTrue(any(not s['mini'] for s in r['streams']))
    def test_corruption_rejected(self):
        data=m.SOURCE.read_bytes()
        for changed in [b'bad'+data[3:],data[:-1],data[:30]+b'\x0c\0'+data[32:]]:
            with self.subTest(header=changed[:32].hex()):
                with self.assertRaises(ValueError): m.audit(changed)
        c=m.Compound(data)
        bad=bytearray(data)
        # Redirect directory first sector to an out-of-file SID.
        struct.pack_into('<I',bad,48,0x10000000)
        with self.assertRaises(ValueError): m.audit(bytes(bad))
        # Change a real payload byte: comparison must fail.
        entry=next(e for e in c.entries if e['name']=='Binary.MSVBDPCADLL')
        bad=bytearray(data); bad[(entry['start']+1)*512]^=1
        with self.assertRaisesRegex(ValueError,'differs'): m.audit(bytes(bad))
        with self.assertRaisesRegex(ValueError,'cycle'):
            m.Compound.chain(0,[0],lambda _: b'x')
if __name__=='__main__': unittest.main(verbosity=2)
