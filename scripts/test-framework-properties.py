#!/usr/bin/env python3
"""Source contract checks; no simulated Windows error or runtime equivalence."""
import importlib.util, struct, unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('state',Path(__file__).with_name('audit-framework-properties.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,_=m.audit()
 def test_source_coverage(self):
  source=m.SOURCE.read_bytes()
  for w in self.a['ranges']:
   rows=[x for x in self.a['instructions'] if w['start']<=x['address']<w['end_exclusive']];cursor=w['start']
   for r in rows:
    raw=bytes.fromhex(r['hex']);self.assertEqual(r['address'],cursor);self.assertEqual(source[r['file_offset']:r['file_offset']+len(raw)],raw);cursor+=len(raw)
   self.assertEqual(cursor,w['end_exclusive']);self.assertEqual(''.join(r['hex'] for r in rows),w['hex'])
 def test_property_call_and_guard_anchors(self):
  by={x['address']:x['hex'] for x in self.a['instructions']}
  expected={0x10011476:'68481e0010',0x10011d63:'6864210010',0x10011d73:'83bd88faffff00',0x10011dd0:'c785a0faffff01000000',0x10012234:'80bd97faffff00',0x10012246:'6838220010',0x100123a8:'33c0',0x10012452:'0fb7f6',0x1001246f:'8bc6',0x10012476:'c20400'}
  for k,v in expected.items():self.assertEqual(by[k],v)
  edges={(r['address'],r['target']) for r in self.a['relative_edges']}
  self.assertTrue({(0x10011487,0x100385b9),(0x10011d6e,0x100385b9),(0x10012251,0x10038bcc),(0x1001223b,0x1001232d),(0x100123aa,0x10012471)}<=edges)
 def test_ordinal_thunks_and_literal_values(self):
  links={r['address']:r['declaration'] for r in self.a['import_links']}
  self.assertEqual((links[0x1003c78b]['dll'],links[0x1003c78b]['ordinal']),('msi.dll',145))
  self.assertEqual((links[0x1003c791]['dll'],links[0x1003c791]['ordinal']),('msi.dll',74))
  self.assertIsNone(links[0x1003c791]['name'])
  values={r['address']:r['text'] for r in self.a['literals']}
  self.assertEqual(values[0x100021a4],'false');self.assertEqual(values[0x10001eac],'ANY');self.assertEqual(values[0x10001e0c],'TRUE')
if __name__=='__main__':unittest.main(verbosity=2)
