#!/usr/bin/env python3
"""Source contract checks; no simulated Windows error or runtime equivalence."""
import importlib.util, struct, unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('state',Path(__file__).with_name('audit-framework-error-state.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
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
 def test_state_offsets_and_branch_guards(self):
  by={x['address']:x['hex'] for x in self.a['instructions']}
  expected={0x1003b1da:'c70690ba0010',0x1003b1e6:'894604',0x1003b1eb:'c6460801',0x1003b235:'80790800',0x1003b239:'c70190ba0010',0x1003b241:'83790400',0x1003b247:'ff7104'}
  for k,v in expected.items():self.assertEqual(by[k],v)
  self.assertEqual([(r['address'],r['target']) for r in self.a['relative_edges']],[(0x1003b23f,0x1003b250),(0x1003b245,0x1003b250)])
 def test_import_declarations(self):
  self.assertEqual([(x['address'],x['declaration']['dll'],x['declaration']['name']) for x in self.a['import_links']],[(0x1003b1e0,'KERNEL32.dll','GetLastError'),(0x1003b24a,'KERNEL32.dll','SetLastError')])
 def test_direct_call_references(self):
  rows=self.a['incoming_direct_calls'];self.assertEqual(len(rows),13)
  self.assertEqual({t:sum(r['target']==t for r in rows) for t in (0x1003b1d7,0x1003b235)},{0x1003b1d7:6,0x1003b235:7})
  for r in rows:
   raw=bytes.fromhex(r['hex']);self.assertEqual(raw[0],0xe8);self.assertEqual(r['address']+5+struct.unpack_from('<i',raw,1)[0],r['target'])
  self.assertTrue({0x1003b29f,0x1003b2e1,0x1003b65f,0x1003b6a4}.issubset({r['address'] for r in rows}))
if __name__=='__main__':unittest.main(verbosity=2)
