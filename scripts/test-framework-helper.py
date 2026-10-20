#!/usr/bin/env python3
import importlib.util, unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('helper',Path(__file__).with_name('audit-framework-helper.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,_=m.audit()
 def test_source_windows_are_complete(self):
  for w in self.a['ranges']:
   rows=[x for x in self.a['instructions'] if w['start']<=x['address']<w['end_exclusive']]
   self.assertEqual(''.join(x['hex'] for x in rows),w['hex'])
   cursor=w['start']
   for x in rows:self.assertEqual(x['address'],cursor);cursor+=len(bytes.fromhex(x['hex']))
   self.assertEqual(cursor,w['end_exclusive'])
 def test_probe_and_import_declarations(self):
  a=self.a;self.assertEqual(a['probe_literal']['ascii'],'VSD_FORCE_ANSI');self.assertEqual(len(a['import_links']),6)
  self.assertEqual([x['declaration']['name'] for x in a['import_links']],['GetVersion','GetEnvironmentVariableA','SetLastError','SetLastError','GetEnvironmentVariableA','GetEnvironmentVariableA'])
  self.assertEqual([x['address'] for x in a['register_call_sites']],[0x1003bf42,0x1003bf76])
  for x in a['cache_bytes']:
   self.assertIsNone(x['file_offset']);r=x['address']-0x10000000-x['section']['rva'];self.assertGreaterEqual(r,x['section']['raw_size']);self.assertLess(r,x['section']['virtual_size'])
if __name__=='__main__':unittest.main(verbosity=2)
