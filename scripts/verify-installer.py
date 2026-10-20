#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'evidence/baseline/installer-manifest.json').read_text())
base=root/m['destination']
expected={x['path'] for x in m['files']}
actual={str(x.relative_to(base)) for x in base.rglob('*') if x.is_file()}
errors=[]
if actual != expected: errors.append('File inventory differs')
for x in m['files']:
 p=base/x['path']
 if not p.is_file(): errors.append('Missing: '+x['path']); continue
 if p.stat().st_size!=x['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']: errors.append('Mismatch: '+x['path'])
print('FAIL: '+repr(errors) if errors else 'PASS: installer file inventory, sizes and SHA-256 match manifest')
sys.exit(bool(errors))
