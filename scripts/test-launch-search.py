#!/usr/bin/env python3
"""Static acquisition regression; not original HWK business acceptance."""
import importlib.util
from pathlib import Path
import unittest
import json
import hashlib
spec=importlib.util.spec_from_file_location('launch',Path(__file__).with_name('audit-launch-search.py'))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LaunchTests(unittest.TestCase):
    def test_rea_resource_capture_ranges(self):
        e=json.loads((m.OUT/'rea-resources.json').read_text())
        raw=(m.ROOT/'evidence/baseline/extracted/msi/Binary.MSVBDPCADLL').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),e['subject']['digest']['sha256'])
        resources=e['normalized_result']['resources']
        self.assertEqual(len(resources),2)
        for r in resources:
            p=r['payload']; loc=p['location']
            self.assertEqual(hashlib.sha256(raw[loc['offset']:loc['offset']+loc['bytes']]).hexdigest(),p['sha256'])

    def test_real_source_links(self):
        a=m.audit()
        self.assertTrue(all(a['agreement'].values()))
        self.assertEqual(len(a['searches']),4)
        self.assertEqual(a['tables']['_VsdLaunchCondition'][0]['values']['Condition'],'VSDFXAvailable')
        self.assertEqual({r['signature']['values']['FileName'].split('|')[-1] for r in a['searches']},
                         {'HWUtil.ini','XWall.mdf','XWall_log.ldf','hwksoftconfig.ini'})
        self.assertEqual([r['row']['values']['Type'] for r in a['actions']], [3073,51,307,307,1,1,19,19,51])
        self.assertTrue(all(r['directory_locator']['values']['Depth']==0 for r in a['searches']))

    def test_signature_truncation_and_reference_fail(self):
        reader=m.load('audit-msi-streams')
        base=reader.BASE
        pool=reader.strings((base/'!_StringPool').read_bytes(),(base/'!_StringData').read_bytes())
        raw=(base/'!Signature').read_bytes()
        for bad in [raw[:-1],b'\xff\xff'+raw[2:]]:
            with self.assertRaises(ValueError): reader.table(bad,m.SCHEMAS['Signature'],pool)

if __name__=='__main__': unittest.main(verbosity=2)
