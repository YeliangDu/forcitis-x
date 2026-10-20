#!/usr/bin/env python3
"""PoC orchestrator: run the PoC steps in order, enforce gates, never claim a pass without evidence.

Design rules (mirror docs/poc-mvp-plan.md):
  * a step passes only when its command exits 0 **and** every declared artifact exists non-empty;
  * a PoC passes only when all its steps passed **and** its gate command exits 0;
  * a step whose `requires` are unmet is recorded BLOCKED (never silently skipped);
  * state is written to planning/poc-state.json; the command log to evidence/poc/orchestrator/.

Usage:
  python3 scripts/poc/orchestrate.py status
  python3 scripts/poc/orchestrate.py next
  python3 scripts/poc/orchestrate.py run P1            # run every runnable step of P1
  python3 scripts/poc/orchestrate.py run P1 --step s2   # run one step
  python3 scripts/poc/orchestrate.py gate P1            # re-check the PoC gate only
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / 'planning/poc-plan.json'
STATE = ROOT / 'planning/poc-state.json'
LOG_DIR = ROOT / 'evidence/poc/orchestrator'


def load(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def save_state(state):
    state['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def artifacts_ok(root, paths):
    missing = []
    for rel in paths:
        p = root / rel
        if not p.is_file() or p.stat().st_size == 0:
            missing.append(rel)
    return missing


def resolve_cwd(rel):
    """Refuse cwds that escape the repository."""
    target = (ROOT / rel).resolve()
    if target != ROOT and ROOT not in target.parents:
        raise SystemExit(f'cwd escapes repository: {rel}')
    return target


def run_step(poc, step, state):
    cwd = resolve_cwd(step.get('cwd', '.'))
    cmd = step['run']
    entry = state['pocs'][poc]['steps'].setdefault(step['id'], {})
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    started = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    log = LOG_DIR / f"{poc}-{step['id']}.log"
    log.write_text(f"$ ({cwd}) {' '.join(cmd)}\nexit={proc.returncode}\n--- stdout ---\n{proc.stdout}\n"
                   f"--- stderr ---\n{proc.stderr}\n", encoding='utf-8')
    missing = artifacts_ok(ROOT, step.get('artifacts', []))
    ok = proc.returncode == 0 and not missing
    entry.update({
        'status': 'PASS' if ok else ('BLOCKED' if proc.returncode == 2 else 'FAIL'),
        'exit': proc.returncode,
        'started': started,
        'finished': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'artifacts_missing': missing,
        'log': str(log.relative_to(ROOT)),
        'summary': (proc.stdout.strip().splitlines() or [''])[-1][:300],
    })
    return entry


def main(argv):
    plan = load(PLAN, None)
    if plan is None:
        raise SystemExit(f'missing {PLAN}')
    state = load(STATE, {'pocs': {}})
    for poc in plan['pocs']:
        state['pocs'].setdefault(poc['id'], {'status': 'NOT_RUN', 'steps': {}})

    cmd = argv[1] if len(argv) > 1 else 'status'

    if cmd == 'status':
        for poc in plan['pocs']:
            st = state['pocs'][poc['id']]
            steps = ', '.join(f"{k}={v.get('status')}" for k, v in st['steps'].items()) or '-'
            print(f"{poc['id']:<3} {st['status']:<8} {poc['title']}\n    steps: {steps}")
            if st.get('blocked_by'):
                for item in st['blocked_by']:
                    print(f"    blocked: {item}")
        return 0

    if cmd == 'next':
        for poc in plan['pocs']:
            for step in poc['steps']:
                st = state['pocs'][poc['id']]['steps'].get(step['id'], {})
                if st.get('status') != 'PASS':
                    print(f"{poc['id']}/{step['id']}: {step['title']}\n  run: {' '.join(step['run'])}")
                    if step.get('next_action'):
                        print(f"  needs: {step['next_action']}")
                    return 0
        print('all steps passed; check gates with: python3 scripts/poc/orchestrate.py gate <POC>')
        return 0

    if cmd == 'run':
        poc_id = argv[2]
        only = argv[4] if len(argv) > 4 and argv[3] == '--step' else None
        poc = next((p for p in plan['pocs'] if p['id'] == poc_id), None)
        if poc is None:
            raise SystemExit(f'unknown PoC {poc_id}')
        state['pocs'][poc_id]['status'] = 'RUNNING'
        failed = []
        for step in poc['steps']:
            if only and step['id'] != only:
                continue
            unmet = [r for r in step.get('requires', [])
                     if state['pocs'][poc_id]['steps'].get(r, {}).get('status') != 'PASS']
            if unmet:
                state['pocs'][poc_id]['steps'][step['id']] = {
                    'status': 'BLOCKED', 'requires_unmet': unmet}
                failed.append((step['id'], 'BLOCKED', f'requires {unmet}'))
                print(f"{poc_id}/{step['id']} BLOCKED (needs {unmet})")
                continue
            entry = run_step(poc_id, step, state)
            print(f"{poc_id}/{step['id']} {entry['status']} exit={entry['exit']} {entry['summary']}")
            if entry['status'] != 'PASS':
                failed.append((step['id'], entry['status'], entry['summary']))
                break
        passed = all(state['pocs'][poc_id]['steps'].get(s['id'], {}).get('status') == 'PASS'
                     for s in poc['steps'])
        state['pocs'][poc_id]['status'] = ('GATE_PENDING' if passed and not failed else
                                           (failed[0][1] if failed else 'RUNNING'))
        save_state(state)
        return 0 if not failed else 1

    if cmd == 'gate':
        poc_id = argv[2]
        poc = next((p for p in plan['pocs'] if p['id'] == poc_id), None)
        if poc is None:
            raise SystemExit(f'unknown PoC {poc_id}')
        gate = poc.get('gate')
        if gate is None:
            raise SystemExit(f'{poc_id} has no gate defined')
        proc = subprocess.run(gate['run'], cwd=resolve_cwd(gate.get('cwd', '.')),
                              capture_output=True, text=True, check=False)
        print(proc.stdout.strip() or proc.stderr.strip())
        verdict = 'PASS' if proc.returncode == 0 else ('BLOCKED' if proc.returncode == 2 else 'FAIL')
        state['pocs'][poc_id]['status'] = verdict
        state['pocs'][poc_id]['gate'] = {'run': gate['run'], 'exit': proc.returncode,
                                         'verdict': verdict}
        save_state(state)
        return 0 if verdict == 'PASS' else 1

    raise SystemExit(f'unknown command {cmd}')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
