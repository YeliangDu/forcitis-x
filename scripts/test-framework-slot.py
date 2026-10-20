#!/usr/bin/env python3
"""Real input regression of writable dispatch slot, relocation and bounded branch bytes."""
import importlib.util, struct, unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('slot',Path(__file__).with_name('audit-framework-slot.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,_=m.audit();cls.b=m.SOURCE.read_bytes()
 def test_slot_and_loader_relocation(self):
  a=self.a;self.assertEqual(a['slot']['file_offset'],0x42c84);self.assertEqual(a['slot']['initial_value'],0x1003b09d)
  self.assertEqual(self.b[0x42c84:0x42c88],bytes.fromhex('9db00310'))
  self.assertEqual(a['slot']['section']['name'],'.data');self.assertTrue(a['slot']['section']['characteristics']&0x80000000)
  self.assertEqual(len(a['slot_relocation']),1);r=a['slot_relocation'][0];self.assertEqual(r['type'],3)
  self.assertEqual(struct.unpack_from('<H',self.b,r['entry_offset'])[0],0x3884)
 def test_dispatch_branch_and_reference_scope(self):
  a=self.a;refs=a['slot_literal_references'];calls=[r for r in refs if r['hex']=='ff1584380410'];writes=[r for r in refs if r['hex']=='a384380410']
  self.assertEqual(len(calls),15);self.assertEqual([r['address'] for r in writes],[0x1003b0b3]);self.assertEqual(len(refs),16)
  self.assertEqual(a['slot']['initial_target_hex'],'558bece8ac00000084c0b86bbe03107505a160600410a3843804105dffe0')
  self.assertEqual(a['alternate_iat_declaration']['name'],'GetEnvironmentVariableW')
  self.assertEqual(a['alternate_iat_declaration']['dll'],'KERNEL32.dll')
if __name__=='__main__':unittest.main(verbosity=2)
