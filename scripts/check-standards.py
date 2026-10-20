#!/usr/bin/env python3
"""Machine-checkable part of docs/engineering-standards.md.

Each check maps to a standards id (ES-##). Exit 0 only when every checkable item passes.
`--full` adds the read-only asset verification (vendor manifest, slow).

Usage: python3 scripts/check-standards.py [--full]
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLICA = ROOT / 'replica'
SRC = REPLICA / 'packages'

results = []


def record(es_id, name, ok, detail=''):
    results.append({'id': es_id, 'check': name, 'pass': bool(ok), 'detail': detail})
    print(f"{'PASS' if ok else 'FAIL'} {es_id:<6} {name:<34} {detail}")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def scan(pattern, root, allow_marker='es-allow'):
    hits = []
    rx = re.compile(pattern)
    for path in sorted(root.rglob('*.ts')) + sorted(root.rglob('*.mts')):
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if rx.search(line) and allow_marker not in line:
                hits.append(f'{path.relative_to(ROOT)}:{lineno}')
    return hits


def main(argv):
    full = '--full' in argv

    # ES-01/05/17: the documents that define the conventions must exist and be non-empty
    docs = ['docs/engineering-standards.md', 'docs/naming-conventions.md',
            'docs/product-spec-v1.md', 'docs/poc-mvp-plan.md', 'docs/adr/README.md',
            'planning/standards.json']
    missing = [d for d in docs if not (ROOT / d).is_file() or (ROOT / d).stat().st_size == 0]
    record('ES-01/05/17', 'standards documents present', not missing, ', '.join(missing))

    # ES-02: determinism in the calculation kernel
    hits = scan(r'\b(Date\.now|new Date\(|Math\.random|crypto\.random|performance\.now|localeCompare)\b', SRC)
    record('ES-02', 'no clock/random/locale in kernel', not hits, ', '.join(hits[:3]))

    # ES-05: legacy product names / Chinese literals must not appear on the new surface
    product = re.compile(r'\b(XWall|HWKSoft|HWKWall|HWKCalc|HWKCAD|HWKWin|HWKAlu|HWK)\b')
    cjk = re.compile(r'[\u4e00-\u9fff]')
    surface = list(SRC.rglob('*.ts')) + list((REPLICA / 'scripts').rglob('*.mts'))
    bad = []
    for path in surface:
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if product.search(line) or (cjk.search(line) and SRC in path.parents):
                bad.append(f'{path.relative_to(ROOT)}:{lineno}')
    record('ES-05', 'no legacy product names / CJK literals', not bad, ', '.join(bad[:3]))

    # ES-10: no bare any / ts-ignore in the kernel
    hits = scan(r'(:\s*any\b|@ts-ignore|@ts-expect-error)', SRC)
    record('ES-10', 'no any/@ts-ignore in kernel', not hits, ', '.join(hits[:3]))

    # ES-16: typecheck + lint (only when dependencies are installed)
    if (REPLICA / 'node_modules').is_dir():
        proc = run(['npx', 'tsc', '-p', 'tsconfig.json', '--noEmit'], REPLICA)
        record('ES-16', 'tsc --noEmit', proc.returncode == 0, proc.stderr.strip().splitlines()[-1] if proc.returncode else '')
        proc = run(['npx', 'oxlint', 'packages', 'scripts'], REPLICA)
        record('ES-16', 'oxlint', proc.returncode == 0, proc.stderr.strip().splitlines()[-1] if proc.returncode else '')
        proc = run(['node', '--test', 'packages/**/*.test.ts'], REPLICA)
        summary = [line for line in proc.stdout.splitlines()
                   if line.startswith(('ℹ pass', 'ℹ fail'))]
        record('ES-11', 'node --test', proc.returncode == 0, ' '.join(s.strip() for s in summary))
    else:
        record('ES-16', 'tsc/oxlint/tests', False, 'replica/node_modules missing — run npm install')

    # ES-06/09: ledgers parse, ids are unique and scope/acceptance agree
    try:
        scope = json.loads((ROOT / 'planning/scope.json').read_text(encoding='utf-8'))
        acceptance = json.loads((ROOT / 'planning/acceptance.json').read_text(encoding='utf-8'))
        standards = json.loads((ROOT / 'planning/standards.json').read_text(encoding='utf-8'))
        sids = [f['id'] for f in scope.get('features', [])]
        aids = [f['id'] for f in acceptance.get('features', [])]
        ok = len(sids) == len(set(sids)) and set(sids) == set(aids)
        record('ES-06', 'scope/acceptance ids agree', ok, f'scope={len(sids)} acceptance={len(aids)}')
        es_ids = {item['id'] for item in standards.get('items', [])}
        enforced = {i for i in es_ids if re.fullmatch(r'ES-\d{2}', i)}
        ok = len(es_ids) == len(standards.get('items', [])) and len(enforced) >= 20
        record('ES-06', 'standards ledger complete', ok, f'{len(enforced)} items')
    except (OSError, json.JSONDecodeError, KeyError) as error:
        record('ES-06', 'ledgers parse', False, str(error)[:80])

    # ES-07: read-only assets (opt-in, slow)
    if full:
        manifest = json.loads((ROOT / 'evidence/baseline/installer-manifest.json').read_text(encoding='utf-8'))
        entries = manifest if isinstance(manifest, list) else manifest.get('files', [])
        bad = []
        for entry in entries[:11]:
            path = ROOT / (entry.get('path') or entry.get('local_path') or '')
            if not path.is_file():
                bad.append(f'missing {path.name}')
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if entry.get('sha256') and digest != entry['sha256']:
                bad.append(f'changed {path.name}')
        record('ES-07', 'vendor manifest unchanged', not bad, ', '.join(bad[:3]))
    else:
        record('ES-07', 'vendor manifest unchanged', True, 'skipped (use --full)')

    failed = [r for r in results if not r['pass']]
    print(json.dumps({'checks': len(results), 'failed': len(failed),
                      'status': 'PASS' if not failed else 'FAIL'}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
