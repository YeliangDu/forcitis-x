#!/usr/bin/env python3
"""Real-input regression for bounded framework declarations and instruction anchors."""
import importlib.util,struct,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('framework',Path(__file__).with_name('audit-framework-static.py')); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,_=m.audit();cls.raw=m.SOURCE.read_bytes()
 def test_declarations_and_anchors(self):
  p={r['values']['Property']:r['values']['Value'] for r in self.a['properties']}
  self.assertEqual(p['VSDFrameworkVersion'],'ANY');self.assertEqual(p['VSDAllowLaterFrameworkVersions'],'False')
  for text,off,va,site in [('VSDFrameworkVersion',0x1248,0x10001e48,0x10011476),('VSDAllowLaterFrameworkVersions',0x1564,0x10002164,0x10011d63),('VSDFXAvailable',0x1638,0x10002238,0x10012246)]:
   r=next(r for r in self.a['literals'] if r['text']==text)
   self.assertEqual((r['file_offset'],r['address']),(off,va));self.assertEqual(self.raw[off:off+r['bytes']],(text+'\0').encode('utf-16le'))
   ins=next(i for i in r['instruction_literal_matches'] if i['address']==site)
   self.assertEqual(bytes.fromhex(ins['hex']),b'\x68'+struct.pack('<I',va))
 def test_import_identity_and_unresolved_ordinals(self):
  imports=self.a['imports'];self.assertEqual(len(imports),164)
  self.assertTrue(any(r['dll']=='KERNEL32.dll' and r['name']=='GetProcAddress' for r in imports))
  msi=[r for r in imports if r['dll']=='msi.dll'];self.assertEqual(len(msi),20)
  self.assertTrue(all(r['name'] is None and r['ordinal'] is not None for r in msi))
  for c in self.a['checkfx_address_window']['iat_call_matches']:
   ins=c['instruction'];p=ins['file_offset'];self.assertEqual(self.raw[p:p+6],b'\xff\x15'+struct.pack('<I',c['iat_address']))
  unresolved=[c for c in self.a['checkfx_address_window']['iat_call_matches'] if c['import_declaration'] is None]
  self.assertEqual([c['iat_address'] for c in unresolved],[0x10043884])
  self.assertEqual(len(self.a['checkfx_address_window']['iat_call_matches']),57)
if __name__=='__main__':unittest.main(verbosity=2)
