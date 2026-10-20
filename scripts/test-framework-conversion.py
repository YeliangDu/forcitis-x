#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('conversion',Path(__file__).with_name('audit-framework-conversion.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,_=m.audit()
 def test_contiguous_source_coverage(self):
  for w in self.a['ranges']:
   rows=[x for x in self.a['instructions'] if w['start']<=x['address']<w['end_exclusive']];cursor=w['start']
   for x in rows:self.assertEqual(x['address'],cursor);cursor+=len(bytes.fromhex(x['hex']))
   self.assertEqual(cursor,w['end_exclusive']);self.assertEqual(''.join(x['hex'] for x in rows),w['hex'])
 def test_local_branches_land_on_instructions(self):
  starts={x['address'] for x in self.a['instructions']}
  for e in self.a['relative_edges']:
   if e['target_in_windows']:self.assertIn(e['target'],starts)
  self.assertEqual({x['target'] for x in self.a['relative_edges'] if x['kind']=='call'},{0x1003b932,0x1003b96a,0x1003b1d7,0x1003ba5b,0x1003b655,0x1003b235,0x1003b295,0x1003b8b5})
 def test_error_import_and_buffer_write_bytes(self):
  self.assertEqual([x['address'] for x in self.a['import_links']],[0x1003b9b4,0x1003ba3c,0x1003bac1])
  for x in self.a['import_links']:self.assertEqual(x['declaration']['name'],'GetLastError')
  by={x['address']:x['hex'] for x in self.a['instructions']}
  self.assertEqual(by[0x1003bad0],'6a7a');self.assertEqual(by[0x1003badb],'66890457');self.assertEqual(by[0x1003bae9],'8901')
if __name__=='__main__':unittest.main(verbosity=2)
