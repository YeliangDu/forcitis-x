#!/usr/bin/env python3
"""P1 s5 + gate: compare engine output with the original system's stored profile properties.

Two checks, in increasing strength:
  A. composition identity  : composite.AREA == sum(sub.AREA)                    (needs 型材 + 复合 rows)
  B. geometry reproduction : engine(contours) ~= stored AREA/IZ/IY/WZ1/WZ2      (also needs BREP outlines)

Exit codes: 0 all available checks pass, 1 mismatch, 2 inputs missing (BLOCKED).
The 0.5% tolerance comes from docs/poc-mvp-plan.md P1.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IN_DIR = ROOT / 'evidence/poc/P1/input'
OUT = ROOT / 'evidence/poc/P1/compare.json'
TOL = 0.005


def load(name):
    path = IN_DIR / name
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def rel(a, b):
    return abs(a - b) / abs(b) if b else abs(a)


def main(argv):
    gate = '--gate' in argv
    profiles, composites = load('profiles.json'), load('composites.json')
    if profiles is None or composites is None:
        print('BLOCKED: need evidence/poc/P1/input/{profiles,composites}.json '
              '(run scripts/poc/ingest-profiles.py for the exact export)')
        return 2
    # composite MAINID/SUBID* reference 图库数据表.IID; profile rows carry it as 图形ID
    by_graphic = {row['graphic_id']: row for row in profiles}
    checks, failures = [], []
    for comp in composites:
        main = by_graphic.get(comp.get('MAINID'))
        subs = [by_graphic.get(comp[k]) for k in ('SUBID1', 'SUBID2', 'SUBID3') if comp.get(k)]
        subs = [s for s in subs if s]
        if not main or not subs:
            continue
        # A: the composite row carries the MAIN profile's areaMm2 (measured 3/3, exact)
        diff = rel(main['AREA'], comp['AREA'])
        checks.append({'check': 'A-areaMm2-equals-main', 'composite': comp['IID'],
                       'stored': comp['AREA'], 'main_area': main['AREA'],
                       'rel_diff': diff, 'pass': diff <= TOL})
        if diff > TOL:
            failures.append(f"A composite {comp['IID']}: {comp['AREA']} vs MAIN {main['AREA']}")
        # B: the SUBID rows partition the MAIN profile (their areas sum to it)
        sub_sum = sum(s['AREA'] for s in subs)
        diff_b = rel(sub_sum, main['AREA'])
        checks.append({'check': 'B-sub-areas-partition-main', 'composite': comp['IID'],
                       'main_area': main['AREA'], 'sum_of_sub_profiles': sub_sum,
                       'rel_diff': diff_b, 'pass': diff_b <= TOL})
        if diff_b > TOL:
            failures.append(f"B composite {comp['IID']}: subs {sub_sum} vs MAIN {main['AREA']}")
        # C: second moments of the composite must be recomputed from the outlines (needs BREP)
        checks.append({'check': 'C-second-moments', 'composite': comp['IID'],
                       'stored_IZ': comp['IZ'], 'main_IZ': main['IZ'],
                       'status': 'BLOCKED', 'pass': None,
                       'why': 'composite IZ differs from MAIN and from sum(sub): needs sub outlines (BREP)'})
    contours = load('contours.json')
    geometry = 'PENDING'
    if contours:
        request = {'sections': contours}
        req_path = ROOT / 'evidence/poc/P1/input/_props-request.json'
        res_path = ROOT / 'evidence/poc/P1/input/_props-result.json'
        req_path.write_text(json.dumps(request), encoding='utf-8')
        proc = subprocess.run(['node', 'scripts/section-props.mts', str(req_path), str(res_path)],
                              cwd=ROOT / 'replica', capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            failures.append(f'section-props failed: {proc.stderr[:200]}')
            geometry = 'FAIL'
        else:
            result = json.loads(res_path.read_text(encoding='utf-8'))
            geometry = 'PASS'
            for section in result['sections']:
                stored = by_graphic.get(section['profile_id'])
                if not stored:
                    continue
                for key, field in (('areaMm2', 'AREA'), ('ixMm4', 'IZ'), ('iyMm4', 'IY'),
                                   ('wxTopMm3', 'WZ1'), ('wxBottomMm3', 'WZ2')):
                    if field not in stored:
                        continue
                    diff = rel(section['properties'][key], stored[field])
                    ok = diff <= TOL
                    checks.append({'check': f'geometry-{field}', 'profile': section['profile_id'],
                                   'computed': section['properties'][key], 'stored': stored[field],
                                   'rel_diff': diff, 'pass': ok})
                    if not ok:
                        failures.append(f"profile {section['profile_id']} {field}: "
                                        f"computed {section['properties'][key]} vs stored {stored[field]}")
    a_b_pass = bool([c for c in checks if c['pass'] is not None]) and not failures
    ok = a_b_pass
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'tolerance': TOL, 'checks': checks, 'failures': failures,
                               'criteria': {'A': 'areaMm2 == MAIN areaMm2', 'B': 'sum(SUB areas) == MAIN areaMm2',
                                            'C': 'second moments from outlines (BLOCKED on BREP)'},
                               'geometry_status': geometry, 'passed': ok},
                              ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'checks': len(checks), 'failures': len(failures),
                      'geometry': geometry, 'passed': ok}, ensure_ascii=False))
    if gate:
        # the hard criterion needs C; A/B alone cannot close P1
        return 0 if ok and geometry == 'PASS' else 2
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
