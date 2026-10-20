#!/usr/bin/env python3
"""Regression for bounded routing evidence, not a Windows conversion test."""
import importlib.util, unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('dispatch',Path(__file__).with_name('audit-framework-dispatch.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,_=m.audit()
 def test_source_coverage(self):
  for w in self.a['ranges']:
   rows=[x for x in self.a['instructions'] if w['start']<=x['address']<w['end_exclusive']];cursor=w['start']
   for x in rows:self.assertEqual(x['address'],cursor);cursor+=len(bytes.fromhex(x['hex']))
   self.assertEqual(cursor,w['end_exclusive']);self.assertEqual(''.join(x['hex'] for x in rows),w['hex'])
 def test_routing_and_argument_bytes(self):
  by={x['address']:x['hex'] for x in self.a['instructions']}
  for start,branch,target in [(0x1003b2a4,0x1003b2ab,0x1003b2c5),(0x1003b664,0x1003b66b,0x1003b685)]:
   self.assertEqual(by[start],'817d08e9fd0000');self.assertEqual(by[branch],'7518')
   self.assertIn({'address':branch,'target':target,'kind':'short_branch','target_in_windows':True},self.a['relative_edges'])
  self.assertEqual({x['address']:x['target'] for x in self.a['relative_edges'] if x['kind']=='call'},{0x1003b29f:0x1003b1d7,0x1003b2bb:0x1003b320,0x1003b2e1:0x1003b235,0x1003b65f:0x1003b1d7,0x1003b67b:0x1003b6ae,0x1003b6a4:0x1003b235})
 def test_import_declarations(self):
  self.assertEqual([(x['address'],x['iat_address'],x['declaration']['dll'],x['declaration']['name']) for x in self.a['import_links']],[(0x1003b2d6,0x10046108,'KERNEL32.dll','MultiByteToWideChar'),(0x1003b699,0x10046104,'KERNEL32.dll','WideCharToMultiByte')])
if __name__=='__main__':unittest.main(verbosity=2)
