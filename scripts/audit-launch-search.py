#!/usr/bin/env python3
"""Restricted static MSI launch/search declarations; does not evaluate conditions."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/baseline/b01/launch-search'

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

SCHEMAS = {
    '_VsdLaunchCondition': [('Condition','s'),('Description','s'),('Url','s')],
    'AppSearch': [('Property','s'),('Signature_','s')],
    'DrLocator': [('Signature_','s'),('Parent','s'),('Path','s'),('Depth','i2')],
    'Signature': [('Signature','s'),('FileName','s'),('MinVersion','s'),('MaxVersion','s'),
                  ('MinSize','i4'),('MaxSize','i4'),('MinDate','i4'),('MaxDate','i4'),('Languages','s')],
    'Directory': [('Directory','s'),('Directory_Parent','s'),('DefaultDir','s')],
}

def audit():
    ole = load('audit-ole-bindings')
    m = load('audit-msi-streams')
    source = ole.SOURCE.read_bytes()
    c = ole.Compound(source)
    streams = {e['name']: c.stream(e)[0] for e in c.entries if e['type'] == 2}
    pool = m.strings(streams['!_StringPool'], streams['!_StringData'])
    schemas = dict(SCHEMAS, **m.SCHEMAS)
    tables = {n: m.table(streams['!'+n], s, pool) for n,s in schemas.items()}
    old = json.loads((ROOT/'evidence/baseline/b01/msi-decoded/tables.json').read_text())
    agreement = {n: [r['values'] for r in rows] == old['tables'][n] for n,rows in tables.items()}
    if not all(agreement.values()): raise ValueError('Prior table disagreement')
    def index(name, key):
        rows = tables[name]
        result = {r['values'][key]: r for r in rows}
        if len(result) != len(rows): raise ValueError('Duplicate key')
        return result
    sig = index('Signature','Signature')
    loc = index('DrLocator','Signature_')
    searches = []
    for row in tables['AppSearch']:
        key = row['values']['Signature_']
        if key not in sig or key not in loc: raise ValueError('Unbound search')
        searches.append(dict(app_search=row, signature=sig[key], directory_locator=loc[key]))
    props = index('Property','Property')
    dirs = index('Directory','Directory')
    actions = []
    for row in tables['CustomAction']:
        v = row['values']; source_kind_bits = v['Type'] & 0x30
        item = dict(row=row, base_type=v['Type'] & 0x3f, source_kind_bits=source_kind_bits,
                    sequences={n:[r for r in tables[n] if r['values']['Action']==v['Action']]
                               for n in ['InstallExecuteSequence','InstallUISequence']})
        # Record literal identifier matches only; do not infer runtime values or Type semantics.
        item['source_literal_matches'] = dict(property=props.get(v['Source']),directory=dirs.get(v['Source']))
        actions.append(item)
    relevant = {k:r for k,r in props.items() if k.startswith('VSD') or k in ['TARGETDIR','FolderForm_AllUsers']}
    used = ['!'+n for n in tables] + ['!_StringPool','!_StringData']
    return dict(status='PARTIAL', evidence_type='STATIC_PACKAGE_SOURCE_BYTES',
        source=str(ole.SOURCE.relative_to(ROOT)), source_sha256=ole.digest(source),
        inputs={n:dict(size=len(streams[n]),sha256=ole.digest(streams[n])) for n in used},
        tables=tables, agreement=agreement, searches=searches, actions=actions,
        related_property_declarations=relevant,
        limits=['Reuses restricted CFB and string/cell readers; independent review pending',
                'No condition evaluation, action execution, framework requirement or runtime path proved',
                'Type masks are arithmetic observations, not validated action semantics',
                'No Windows or solver execution; no target architecture choice'])

if __name__ == '__main__':
    result = audit()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], counts={n:len(r) for n,r in result['tables'].items()},
                          searches=len(result['searches']),agreement=result['agreement']),indent=2))
