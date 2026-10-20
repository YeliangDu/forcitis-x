#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('readiness',Path(__file__).with_name('summarize-runtime-readiness.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_edges_and_architecture_are_not_collapsed(self):
  a=m.collect(); deps=json.loads((m.ROOT/m.BASE/'dependencies/inventory.json').read_text())['pe']
  self.assertEqual(len(a['import_edges']),sum(len(r['imports']) for r in deps))
  for edge in a['import_edges']:
   expected={r['source'] for r in deps if r['target_label'].rsplit('/',1)[-1].lower()==edge['import_name'].lower()}
   self.assertEqual({r['source'] for r in edge['package_candidates']},expected)
   self.assertEqual(edge['runtime_binding'],'NOT_RUN')
  self.assertTrue(any(not r['package_candidates'] for r in a['import_edges']))
  for edge in a['import_edges']:
   for candidate in edge['package_candidates']:
    self.assertEqual(candidate['same_format'],candidate['format']==edge['importer_format'])
 def test_version_and_unattributed_plugins_remain_distinct(self):
  a=m.collect();self.assertEqual(a['versions']['package_product_version'],'05.45.1211');self.assertEqual(a['versions']['xwall_file_version'],'5.4.25.1209');self.assertIsNone(a['versions']['installed_version'])
  self.assertEqual(len(a['managed_declarations']),13);self.assertEqual(sum(not r['framework_declarations'] for r in a['managed_declarations']),2)
if __name__=='__main__':unittest.main(verbosity=2)
