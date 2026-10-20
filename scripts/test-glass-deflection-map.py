"""Pins the glass-deflection orchestration map so the claim cannot drift silently.

Checks the produced artifacts against their sources. Fails loudly instead of reporting a
"clean" run when a source file or an invariant changed.
"""
import json
import re
import sys
from pathlib import Path

WS = Path('migration_workspace')
MAP = WS / 'raw/glass-deflection-map.json'
MD = WS / 'glass-deflection-map.md'


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'cannot read {path}: {error}') from error


def main():
    report = load(MAP)
    formulas = load(WS / 'formulas.json')
    entries = load(WS / 'raw/cxmap-entries.json')
    rows = entries['entries']
    # some call sites have no parsed name; they explain the 380/381 bookkeeping gap and must
    # never enter the name set.
    registry = {r['name'] for r in rows if isinstance(r.get('name'), str) and r['name']}
    unnamed = len(rows) - len(registry)
    # 379 classes / 380 distinct names in the older note / 381 in this entries file:
    # keep the real number instead of forcing a remembered one, and pin the range.
    assert 379 <= len(registry) <= 381, f'unexpected registered-name count {len(registry)}'
    summary = report['summary']

    # 1. the map covers a non-empty, reproducible selection of the real formula library
    assert len(report['formulas']) == 25, len(report['formulas'])
    symbols = {f['symbol'] for f in report['formulas']}
    library_symbols = {f['symbol'] for f in formulas}
    assert symbols <= library_symbols, sorted(symbols - library_symbols)[:5]
    for row in report['formulas']:
        assert row['calls'], row['symbol']

    # 2. per-formula call counts must add up to the summary
    per_formula = sum(info['count'] for row in report['formulas'] for info in row['calls'].values())
    assert per_formula == summary['calls'], f"per-formula {per_formula} != summary {summary['calls']}"
    assert summary['resolved'] > 0 and summary['resolved'] <= summary['calls']
    assert summary['arity_ok'] + summary['arity_variadic'] == summary['resolved'], 'arity buckets do not close'
    assert summary['arity_mismatch'] == 0, f"unexpected arity mismatches: {report['unresolved']}"

    # 3. unresolved names must really be absent from the 379-name registry
    for name in report['unresolved']:
        assert name not in registry, f'{name} is registered but was reported unresolved'
        assert '${' + name in ''.join(f['text'] for f in formulas), name

    # 4. the decisive finding: the glass computing nodes are never called by templates
    for node in ('CalGlassDisp', 'CalGlassPSDisp', 'CalGlassStress', 'CalGlassPSStress'):
        assert report['node_call_sites'][node] == 0, node
        assert node in registry, node
        assert not any('${' + node in f['text'] for f in formulas), node
    never = sum(1 for name in registry if not any('${' + name in f['text'] for f in formulas))
    assert report['nodes_never_called'] == never, f"recorded {report['nodes_never_called']} != recomputed {never}"

    # 5. the markdown states the same numbers as the json
    md = MD.read_text(encoding='utf-8')
    assert f'共 {len(report["formulas"])} 条模板' in md
    assert f'调用总数 {summary["calls"]}' in md
    assert f'**{never} 个' in md or f'{never} 个在全部' in md
    assert 'CalGlassDisp' in md and re.search(r'CalGlassDisp`=0', md)

    print(json.dumps({
        'status': 'PASS',
        'formulas': len(report['formulas']),
        'calls': summary['calls'],
        'registry_hits': summary['resolved'],
        'variadic': summary['arity_variadic'],
        'genuine_arity_mismatch': summary['arity_mismatch'],
        'non_node_template_functions': sorted(report['unresolved']),
        'nodes_never_called_by_templates': never,
        'registered_names_in_entries_file': len(registry),
        'entries_without_a_name': unnamed,
    }, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
