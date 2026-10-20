#!/usr/bin/env python3
"""P1 s3 helper: read-only export of the three profile tables from the HWKCOPY copy DB.

Writes evidence/poc/P1/input/{profiles,composites,gallery}.json. Uses SqlClient against the
LocalDB copy ((localdb)\\v11.0) because sqlcmd is not installed on the test host; the queries are
strict SELECTs and touch only the HWKCOPY_* database.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IN_DIR = ROOT / 'evidence/poc/P1/input'
HOST = 'Administrator@8.149.129.78'
KEY = str(Path.home() / '.ssh/hwk-win-test')
# sub-profile ids are derived from 复合型材参数表 at run time (MAINID/SUBID1..3)

PS = r'''
$ErrorActionPreference='Stop'
$cn = New-Object System.Data.SqlClient.SqlConnection
$cn.ConnectionString = "Data Source=(localdb)\v11.0;Integrated Security=True;Initial Catalog=HWKCOPY_XWall;Connect Timeout=60"
$cn.Open()
function Q($sql){
  $cmd=$cn.CreateCommand(); $cmd.CommandText=$sql; $cmd.CommandTimeout=120
  $r=$cmd.ExecuteReader(); $rows=@()
  while($r.Read()){ $o=[ordered]@{}; for($i=0;$i -lt $r.FieldCount;$i++){ $v=$r.GetValue($i); if($v -is [byte[]]){$v=[Convert]::ToBase64String($v)}; $o[$r.GetName($i)]=$v }; $rows+=$o }
  $r.Close(); return ,$rows
}
$out=[ordered]@{}
$composites = Q "SELECT IID,MAINID,SUBID1,SUBID2,SUBID3,LENGTH,IZ,IY,WZ1,WZ2,AREA,CX,CY,PERIM FROM [dbo].[复合型材参数表]"
$ids = @(); foreach($c in $composites){ foreach($k in 'MAINID','SUBID1','SUBID2','SUBID3'){ if($c[$k] -ne $null -and $c[$k] -ne 0){ $ids += [int]$c[$k] } } }
$ids = $ids | Sort-Object -Unique
$idList = ($ids -join ',')
$out.composites = $composites
$out.profile_ids_requested = $ids
# 复合型材的 MAINID/SUBID* 指向 图库数据表.IID（块）；型材行通过 图形ID 与之相连
$out.profiles = if($ids.Count -gt 0){ Q "SELECT IID,[图形ID] AS graphic_id,IZ,IY,WZ1,WZ2,WY1,WY2,SZ,SY,AREA,T,CX,CY,PERIM,JA FROM [dbo].[型材参数表] WHERE [图形ID] IN ($idList)" } else { @() }
$out.gallery = if($ids.Count -gt 0){ Q "SELECT IID,名称 AS name,BREP FROM [dbo].[图库数据表] WHERE IID IN ($idList)" } else { @() }
$out.stats = Q "SELECT (SELECT COUNT(*) FROM [dbo].[型材参数表]) AS profiles_total, (SELECT COUNT(*) FROM [dbo].[图库数据表]) AS gallery_total, (SELECT MIN(IID) FROM [dbo].[型材参数表]) AS profiles_min, (SELECT MAX(IID) FROM [dbo].[型材参数表]) AS profiles_max"
$cn.Close()
$out | ConvertTo-Json -Depth 6 -Compress
'''


PROBE = r'''
$ErrorActionPreference='Stop'
$cn = New-Object System.Data.SqlClient.SqlConnection
$cn.ConnectionString = "Data Source=(localdb)\v11.0;Integrated Security=True;Initial Catalog=HWKCOPY_XWall;Connect Timeout=60"
$cn.Open(); $cmd=$cn.CreateCommand(); $cmd.CommandText='@SQL@'; $cmd.CommandTimeout=120
$r=$cmd.ExecuteReader(); $rows=@()
while($r.Read()){ $o=[ordered]@{}; for($i=0;$i -lt $r.FieldCount;$i++){ $v=$r.GetValue($i); if($v -is [byte[]]){$v="<bytes " + $v.Length + ">"}; $o[$r.GetName($i)]=$v }; $rows+=$o }
$r.Close(); $cn.Close(); ,$rows | ConvertTo-Json -Depth 5 -Compress
'''


def probe(sql):
    """Run one read-only SELECT against the HWKCOPY copy and return rows."""
    script = PROBE.replace('@SQL@', sql.replace("'", "''"))
    local = Path(tempfile.mkdtemp(prefix='hwk-probe-')) / 'probe.ps1'
    local.write_text('\ufeff' + script, encoding='utf-8')
    remote = 'C:/Windows/Temp/hwk-poc-probe.ps1'
    subprocess.run(['scp', '-o', 'BatchMode=yes', '-i', KEY, str(local), f'{HOST}:{remote}'],
                   check=True, capture_output=True, text=True)
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-i', KEY, HOST,
                           f'powershell -NoProfile -ExecutionPolicy Bypass -File {remote}'],
                          capture_output=True, text=True, check=False,
                          encoding='utf-8', errors='replace')
    if proc.returncode != 0:
        return {'error': (proc.stdout + proc.stderr)[:600]}
    try:
        return json.loads(proc.stdout.strip().lstrip('\ufeff'))
    except json.JSONDecodeError as error:
        return {'error': f'{error}: {proc.stdout[:300]!r}'}


def main():
    if '--sql' in sys.argv:
        rows = probe(sys.argv[sys.argv.index('--sql') + 1])
        print(json.dumps(rows, ensure_ascii=False, indent=1)[:4000])
        return 0 if isinstance(rows, list) else 2
    script = PS
    remote = 'C:/Windows/Temp/hwk-poc-p1-export.ps1'
    local = Path(tempfile.mkdtemp(prefix='hwk-poc-')) / 'export.ps1'
    local.write_text('\ufeff' + script, encoding='utf-8')
    subprocess.run(['scp', '-o', 'BatchMode=yes', '-i', KEY, str(local), f'{HOST}:{remote}'],
                   check=True, capture_output=True, text=True)
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-i', KEY, HOST,
                           f'powershell -NoProfile -ExecutionPolicy Bypass -File {remote}'],
                          capture_output=True, text=True, check=False,
                          encoding='utf-8', errors='replace')
    if proc.returncode != 0:
        print('BLOCKED: remote export failed')
        print((proc.stdout + proc.stderr)[:800])
        return 2
    payload = proc.stdout.strip().lstrip('\ufeff')
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        print(f'BLOCKED: cannot parse remote JSON ({error}); head={payload[:300]!r}')
        return 2
    IN_DIR.mkdir(parents=True, exist_ok=True)
    (IN_DIR / '_raw-export.json').write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n',
                                             encoding='utf-8')
    for key in ('profiles', 'composites', 'gallery'):
        rows = data.get(key) or []
        (IN_DIR / f'{key}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n',
                                            encoding='utf-8')
        print(f'{key}: {len(rows)} rows')
    return 0


if __name__ == '__main__':
    sys.exit(main())
