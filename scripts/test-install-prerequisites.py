#!/usr/bin/env python3
"""Checks the contract-specific source anchors and rejects corrupt decoding."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('prereqs', Path(__file__).with_name('summarize-install-prerequisites.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class Prerequisites(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.data = m.collect()
 def test_msi_consumer_and_install_completion_declarations(self):
  x = self.data
  self.assertEqual(x['launch_condition_rows'][0]['values']['Condition'], 'VSDFXAvailable')
  for table in ('InstallUISequence', 'InstallExecuteSequence'):
   rows = {r['Action']:r for r in x['sequences'][table]}
   self.assertEqual(rows['DIRCA_CheckFX']['Sequence'], 1)
   self.assertEqual(rows['VSDCA_VsdLaunchConditions']['Sequence'], 399)
   self.assertEqual(rows['VSDCA_VsdLaunchConditions']['Condition'], 'NOT Installed')
  rows = {r['Action']:r for r in x['sequences']['InstallExecuteSequence']}
  self.assertEqual(rows['InstallFinalize']['Sequence'], 6600)
 def test_callback_identity_and_unresolved_returns_are_preserved(self):
  x = self.data; ins = {i['address']:i for g in x['ranges'] for i in g['instructions']}
  self.assertEqual(ins[0x10016d38]['hex'], '68bf240110')
  self.assertEqual(ins[0x10012476]['hex'], 'c20400')
  self.assertEqual(ins[0x10012234]['hex'], '80bd97faffff00')
  self.assertEqual({r['text'] for r in x['consumer_literals']}, {'_VsdLaunchCondition', 'SELECT * FROM `%s`'})
  self.assertEqual(len(x['flag_references']), 13)
  self.assertEqual(x['status'], 'PARTIAL')
  self.assertTrue(all(g['boundaries'] for g in x['ranges']))
 def test_corrupted_retained_instruction_is_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root = Path(tmp)
   for relative in m.INPUTS:
    dst = root / relative; dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes((m.ROOT/relative).read_bytes())
   p = root/m.INPUTS[1]
   text = p.read_text(); self.assertIn('10012476: c2 04 00', text)
   p.write_text(text.replace('10012476: c2 04 00', '10012476: c2 08 00', 1))
   with patch.object(m, 'ROOT', root):
    with self.assertRaisesRegex(ValueError, 'source mismatch'): m.collect()
if __name__ == '__main__': unittest.main()
