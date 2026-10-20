#!/usr/bin/env python3
"""Offline objdump/config evidence. Never loads or executes package code."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/baseline/b01/dependencies'


def collect():
    OUT.mkdir(parents=True, exist_ok=True)
    mapping = json.loads((ROOT / 'evidence/baseline/b01/msi-decoded/file-map.json').read_text())
    tables = json.loads((ROOT / 'evidence/baseline/b01/msi-decoded/tables.json').read_text())['tables']
    records = []
    configs = []
    candidates = [(ROOT / 'evidence/baseline/extracted/cab' / r['File'], r['symbolic_target']) for r in mapping]
    candidates += [(p, p.name) for p in sorted((ROOT / 'evidence/baseline/extracted/msi').glob('Binary.*'))]
    for path, target in candidates:
        data = path.read_bytes()
        identity = {'source': str(path.relative_to(ROOT)), 'target_label': target,
                    'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
        if target.lower().endswith(('.config', '.ini')):
            copy = OUT / (path.name + '.config.raw')
            copy.write_bytes(data)
            configs.append({**identity, 'raw': str(copy.relative_to(ROOT))})
        if not data.startswith(b'MZ'):
            continue
        run = subprocess.run(['objdump', '-p', str(path)], capture_output=True, text=True)
        raw = OUT / (path.name + '.objdump.txt')
        raw.write_text(run.stdout + run.stderr)
        clr = re.search(r'Entry e\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+) CLR Runtime Header', run.stdout)
        records.append({**identity, 'exit_code': run.returncode,
                        'format': re.findall(r'file format (\S+)', run.stdout),
                        'imports': re.findall(r'DLL Name: (.+)', run.stdout),
                        'clr_directory': [int(x, 16) for x in clr.groups()] if clr else None,
                        'raw': str(raw.relative_to(ROOT))})
    actions = {r['Action']: r for r in tables['CustomAction']}
    sequences = {name: sorted([{**r, 'custom_action': actions[r['Action']]} for r in tables[name]
                              if r['Action'] in actions], key=lambda r: r['Sequence'])
                 for name in ('InstallExecuteSequence', 'InstallUISequence')}
    result = {'evidence_type': 'STATIC_PACKAGE', 'status': 'PARTIAL',
              'limitations': ['objdump headers/imports do not establish executed calls or runtime prerequisites',
                              'MSI table interpretation still awaits independent reader verification',
                              'CLR directory presence does not identify required framework version'],
              'pe': records, 'configs': configs, 'custom_action_sequences': sequences,
              'framework_properties': [r for r in tables['Property'] if any(s in r['Property'].upper() for s in ('FRAMEWORK', 'NET', 'FX'))],
              'launch_conditions': tables['_VsdLaunchCondition']}
    (OUT / 'inventory.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pe_count': len(records), 'objdump_failures': sum(r['exit_code'] != 0 for r in records),
                      'config_count': len(configs), 'status': 'PARTIAL'}))


if __name__ == '__main__':
    collect()
