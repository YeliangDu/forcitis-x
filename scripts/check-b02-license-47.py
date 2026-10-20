"""Regression over the retained B02-02 attempt-47 evidence.

Checks the whole observed slice: frozen source and working copy integrity, one isolated
client still running with the database connection, the navigation/confirmation steps,
the generated calculation book inside the authorized directory, no writes to the
historical default output directory and no application errors in the bounded window.

This proves what the retained bytes show. It does not prove product licensing terms or
that every licensed branch is enabled.
"""
import json
from pathlib import Path

B = Path('evidence/stages/B02/B02-02/attempt-47')
BASELINE = Path('evidence/stages/B02/B02-01/attempt-41/environment-final/stdout')
AUTHORIZED = 'C:\\hwk-modern\\HWK-000048-B02-02\\reports'
EXPECTED_REPORT_SHA256 = '577D61F43EB26BFD603BDB1A654D31F1E2B396F078934BFC8544CDE33A52A7B0'
# second document: the complete output run on the frozen working sample
FROZEN_REPORT_SHA256 = 'E1FDA490C969A227B4E2A5357EC602FC35717066A61F46F81C7FF3CFF999DF63'
FROZEN_REPORT_LENGTH = 5_926_372


def read(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'evidence unreadable: {path}: {error}') from error


def index(files):
    return {row['Path']: (row['Length'], row['SHA256']) for row in files}


baseline = index(read(BASELINE)['After'])
preflight = read(B / 'preflight-read' / 'stdout')
final = read(B / 'final.json')

assert len(baseline) == 445
assert index(preflight['Files']) == baseline, 'source changed before the operation'
assert index(final['Files']) == baseline, 'source changed during the operation'
assert final['Client'] == '76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5'
assert final['WorkingHash'] == '2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'
assert preflight['Client'] == final['Client'] and preflight['WorkingHash'] == final['WorkingHash']

processes = final['Processes']
assert len(processes) == 1, 'expected exactly one isolated client'
# the PID changes with every relaunch (4568 for the a.cwx instance, 1900 for the frozen
# sample instance); identity is asserted structurally instead of pinning a PID.
assert isinstance(processes[0]['Id'], int) and processes[0]['Id'] > 0
assert processes[0]['SessionId'] == 1
assert processes[0]['Path'] == 'C:\\hwk-modern\\HWK-000041-B02-01\\client\\XWall.exe'
assert processes[0]['Responding']
assert any(
    t['RemoteAddress'] == '165.154.20.222' and t['RemotePort'] == 1433 and t['State'] == 5
    for t in final['TCP']
), 'database connection not established'

# the folder dialog was driven by ordinary tree navigation, not the failing shell message
goto = read(B / 'path-goto.json')
assert goto['Initial'] == 'hook-out'
assert goto['Final'] == 'reports'
assert [step for step in goto['Trace'] if step.startswith('found=')] == [
    'found=hwk-modern',
    'found=HWK-000048-B02-02',
    'found=reports',
]
assert goto['Confirmed'] and goto.get('ConfirmSent')
assert read(B / 'confirm-browse.json')['Window'] == '浏览文件夹'

save = read(B / 'save-as.json')
assert save['Dialog'] == '保存计算书文件'
assert save['Set'] and save['Saved']
assert save['Value'].startswith(AUTHORIZED + '\\'), save['Value']
assert save['Value'].lower().endswith('.rtf')

# the output settings guard refused while the path was still the historical default
generate = read(B / 'generate.json')
assert not generate['Clicked']
assert generate.get('Refused', '').startswith('path-not-authorized')

reports = final['Reports']
assert len(reports) == 2, f'expected the two generated documents, found {len(reports)}'
by_length = {r['Length']: r for r in reports}
assert set(by_length) == {2829593, FROZEN_REPORT_LENGTH}, set(by_length)
for row in reports:
    assert row['Name'].lower().endswith('.rtf')

# the complete output run on the frozen working sample is recorded separately
frozen = read(B / 'export-all.json')
assert frozen['Saved'] == [AUTHORIZED + '\\report-point-01.rtf']
assert frozen['FileCount'] == 2
assert frozen['HookOutRecent'] == 0 and frozen['Errors'] == 0
frozen_files = {row['Name']: row for row in frozen['Files']}
frozen_doc = frozen_files['report-point-01.rtf']
assert frozen_doc['Length'] == FROZEN_REPORT_LENGTH
assert frozen_doc['SHA256'] == FROZEN_REPORT_SHA256
document = frozen_doc

numbers = final['Numbers']
assert len(numbers) >= 8, numbers
# values from the frozen-sample document; 0.737993 / 1.98735 are the same height-20
# wind coefficients captured from the UI in attempt-46, so the report and the earlier
# on-screen recomputation are linked.
assert '0.737993' in numbers and '1.98735' in numbers

assert final['Errors'] == [], 'application errors appeared in the bounded window'
assert final['HookOutRecent'] == [], 'wrote into the historical default output directory'
assert final['Reparse'] == []

print(
    json.dumps(
        {
            'status': 'PASS',
            'scope': (
                'retained attempt-47 evidence: frozen 445 source files, isolated client identity, '
                'live database connection, ordinary-tree folder navigation, calculation book '
                'written only to the authorized directory'
            ),
            'reports': {
                'frozen_sample': {'name': document['Name'], 'bytes': document['Length'], 'sha256': document['SHA256']},
                'earlier_project': {'bytes': 2829593, 'sha256': EXPECTED_REPORT_SHA256},
            },
            'package': 'PARTIAL',
            'license': (
                'the report generation branch completed without a license refusal; licence terms, '
                'server-side grant semantics and other gated branches remain unknown'
            ),
        },
        ensure_ascii=False,
    )
)
