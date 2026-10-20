"""Evidence regression for the real sample's reversible load calculation slice.

This checks retained live observations, not solver equivalence or all licenses.
"""
import json
from pathlib import Path

B = Path('evidence/stages/B02/B02-02/attempt-46')
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def index(files):
    return {v['Path']: (v['Length'], v['SHA256']) for v in files}

baseline = read('evidence/stages/B02/B02-01/attempt-41/environment-final/stdout')['After']
before, after = (read(B / (n + '/stdout')) for n in ['preflight', 'postflight'])
assert len(baseline) == 445 and not before['Processes']
assert index(before['Files']) == index(after['Files']) == index(baseline)
for observation in [before, after]:
    assert observation['Client'] == '76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5'
    assert observation['WorkingHash'] == '2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'
assert len(after['Processes']) == 1 and after['Processes'][0]['Id'] == 113264
assert after['Processes'][0]['Responding'] is True
assert not after['Reports'] and not after['Errors']
assert any(t['RemoteAddress'] == '165.154.20.222' and t['RemotePort'] == 1433 and t['State'] == 5 for t in after['TCP'])

last = ''
results = {}
for name, height, coefficient, gust in [
    ('height21-text', 2021, '2.91', '1.5'),
    ('height21-corrected', 21, '0.754007', '1.976809'),
    ('height20-restored', 20, '0.737993', '1.98735'),
]:
    obs = read(B / (name + '.json'))
    assert last < obs['At'] < after['At']; last = obs['At']
    assert obs['Session'] == 4 and obs['Process'][0]['Id'] == 113264
    assert obs['Process'][0]['Path'] == r'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe'
    text = '\n'.join(t['Text'] for t in obs['Texts'])
    assert f'计算高度{height}m' in text and coefficient in text and gust in text
    assert '风荷载标准值计算' in text and '荷载组合计算' in text
    assert (B / (name + '.png')).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    results[height] = text
assert '-0.768453 kN/m2' in results[21] and '-0.756143 kN/m2' in results[20]
assert results[21] != results[20]
for height in [20, 21]:
    assert '面板荷载组合设计值为1.672032kN/m2' in results[height]
cleanup = read(B / 'cleanup/stdout')
assert not cleanup['Remaining'] and cleanup['Process'][0]['Id'] == 113264
print(json.dumps({'status': 'PASS', 'scope': 'retained real UI load recomputation and restoration, source integrity, TCP, bounded error query and own task cleanup', 'package': 'PARTIAL', 'license': 'load operation usable; license enforcement and other branches unknown'}))
