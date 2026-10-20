#!/usr/bin/env python3
"""Acquisition tests: real source consistency and damaged resource rejection."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('resources',Path(__file__).with_name('decode-installer-resources.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def test_source(self):
        a=m.audit(); strings,version=a['resources']
        self.assertEqual([r['text'] for r in strings['strings'] if r['text']],['.NET Core Desktop Runtime','.NET Core Runtime','.NET Desktop Runtime','.NET Runtime'])
        self.assertEqual(version['file_version'],'16.0.32016.11111')
        self.assertEqual(version['product_version'],version['file_version'])
        fields=version['tree']['children'][0]['children'][0]['children']
        self.assertEqual(next(x['text'] for x in fields if x['key']=='OriginalFilename'),'DPCA.DLL')
        entries=a['exports']['entries']; self.assertEqual(len(entries),18)
        self.assertEqual({x['name']:x['rva'] for x in entries if x['name'] in ('CheckFX','VsdLaunchConditions')},{'CheckFX':0x11359,'VsdLaunchConditions':0x16c3e})
    def test_corruption(self):
        import json
        e=json.loads((m.OUT/'rea-resources.json').read_text()); raw=Path(e['subject']['local_path']).read_bytes()
        for r in e['normalized_result']['resources']:
            loc=r['payload']['location']; b=raw[loc['offset']:loc['offset']+loc['bytes']]
            decoder=m.block if r['type']['id']==16 else lambda x:m.strings(x,96)
            with self.assertRaises(ValueError): decoder(b[:-1])
            with self.assertRaises(ValueError): decoder(b'\xff\xff'+b[2:])
if __name__=='__main__': unittest.main(verbosity=2)
