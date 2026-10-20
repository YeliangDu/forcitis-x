#!/usr/bin/env python3
"""P1 s3: ingest the original system's profile tables (read-only export) as fixtures.

Status codes: 0 = inputs present and validated, 1 = inputs invalid, 2 = inputs absent (BLOCKED).

The export is read-only; nothing here writes to the original database. Expected fixture files in
evidence/poc/P1/input/ (JSON, one object per row):

  profiles.json   -> 型材参数表     : IID, 图形ID, IZ, IY, WZ1, WZ2, WY1, WY2, SZ, SY, AREA, T, CX, CY, PERIM, JA
  composites.json -> 复合型材参数表 : IID, MAINID, SUBID1..SUBID3, LENGTH, IZ, IY, WZ1, WZ2, AREA, CX, CY
  gallery.json    -> 图库数据表     : IID, 名称, BREP(hex/base64), SLD(optional)

Producing them (read-only, on the copy DB):
  SELECT ... FROM [dbo].[型材参数表] FOR JSON PATH
  SELECT ... FROM [dbo].[复合型材参数表] FOR JSON PATH
  SELECT IID, 名称, BREP FROM [dbo].[图库数据表] WHERE IID IN (SELECT DISTINCT 图形ID FROM [dbo].[型材参数表])
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IN_DIR = ROOT / 'evidence/poc/P1/input'
OUT = ROOT / 'evidence/poc/P1/old-system-inputs.json'

REQUIRED = {
    'profiles.json': ['IID', 'graphic_id', 'IZ', 'IY', 'WZ1', 'WZ2', 'AREA', 'T'],
    'composites.json': ['IID', 'MAINID', 'SUBID1', 'IZ', 'IY', 'WZ1', 'WZ2', 'AREA'],
    'gallery.json': ['IID', 'BREP'],
}

SQL = """-- read-only export (run against the HWKCOPY_* copy, never the live DB)
SELECT IID,[图形ID],IZ,IY,WZ1,WZ2,WY1,WY2,SZ,SY,AREA,T,CX,CY,PERIM,JA
  FROM [dbo].[型材参数表] FOR JSON PATH;
SELECT IID,MAINID,SUBID1,SUBID2,SUBID3,LENGTH,IZ,IY,WZ1,WZ2,AREA,CX,CY
  FROM [dbo].[复合型材参数表] FOR JSON PATH;
SELECT IID,名称,BREP FROM [dbo].[图库数据表]
 WHERE IID IN (SELECT DISTINCT [图形ID] FROM [dbo].[型材参数表]) FOR JSON PATH;
"""


def main():
    problems, counts = [], {}
    for name, keys in REQUIRED.items():
        path = IN_DIR / name
        if not path.is_file():
            problems.append(f'missing {path.relative_to(ROOT)}')
            counts[name] = 0
            continue
        try:
            rows = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as error:
            problems.append(f'{name}: invalid JSON ({error})')
            counts[name] = 0
            continue
        if not isinstance(rows, list) or not rows:
            problems.append(f'{name}: expected a non-empty array')
            counts[name] = 0
            continue
        missing_keys = [k for k in keys if k not in rows[0]]
        if missing_keys:
            problems.append(f'{name}: missing columns {missing_keys}')
        counts[name] = len(rows)
    if problems:
        print('BLOCKED: original-system fixtures incomplete')
        for item in problems:
            print(f'  - {item}')
        print('\nRun this read-only export and save the three arrays as evidence/poc/P1/input/*.json:')
        print(SQL)
        return 2 if any(p.startswith('missing') for p in problems) else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'source': 'HWKCOPY (read-only)', 'counts': counts,
                               'files': {k: f'evidence/poc/P1/input/{k}' for k in REQUIRED}},
                              ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'OK fixtures: {counts}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
