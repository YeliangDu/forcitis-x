#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('audit',Path(__file__).with_name('audit-install-consumer-return.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ConsumerReturn(unittest.TestCase):
 def test_prefixed_transfers_have_no_false_fallthrough(self):
  d=m.collect();g=d['ranges'][-1]
  self.assertEqual([e['to'] for e in g['edges'] if e['from']==0x1001a911],[0x1001a8e0])
  self.assertFalse(any(e['from']==0x1001a8f3 for e in g['edges']))
  self.assertTrue(any(b['address']==0x1001a8f3 and b['kind']=='prefixed_ret' for b in g['boundaries']))
 def test_callback_and_ordinal_are_source_facts_only(self):
  d=m.collect();ins={i['address']:i for g in d['ranges'] for i in g['instructions']}
  self.assertEqual(ins[0x10037b5b]['hex'],'ff55dc')
  self.assertEqual(ins[0x10037be4]['hex'],'c20c00')
  self.assertEqual(d['condition_import']['dll'],'msi.dll')
  self.assertEqual(d['condition_import']['ordinal'],47)
  self.assertIsNone(d['condition_import']['name'])
  self.assertEqual(d['status'],'BLOCKED')
 def test_corrupted_prefixed_source_is_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)
   for f in m.base.INPUTS:
    p=root/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((m.base.ROOT/f).read_bytes())
   p=root/m.base.INPUTS[1];s=p.read_text();self.assertIn('1001a911: f2 e9 c9 ff ff ff',s)
   p.write_text(s.replace('1001a911: f2 e9 c9 ff ff ff','1001a911: f2 e9 c8 ff ff ff',1))
   with patch.object(m.base,'ROOT',root):
    with self.assertRaisesRegex(ValueError,'source mismatch'):m.collect()
if __name__=='__main__':unittest.main()
