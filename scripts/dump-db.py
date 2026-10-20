#!/usr/bin/env python3
"""把只读副本库的表结构 + 样本行导出成本地 JSON（L7 数据层第 1 步）。

远端只 SELECT：不建表、不改库、不 attach 新库。产物写本轮目录，再 scp 回本地。

用法：
  python3 scripts/dump-db.py HWKCOPY_XWall
  python3 scripts/dump-db.py HWKCOPY_XWallTem
  python3 scripts/dump-db.py HWKCOPY_UserGlazing
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hwk_ecs import run_ps  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REMOTE_DIR = r'C:\hwk-modern\dbprobe-20261019b'
LOCAL_DIR = ROOT / 'migration_workspace/raw/db'
SSH = ['ssh', '-i', str(Path.home() / '.ssh/hwk-win-test'), '-o', 'IdentitiesOnly=yes',
       '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile=' + str(ROOT / 'evidence/runtime/ecs-20261018/known_hosts'),
       'Administrator@8.149.129.78']

SCRIPT = r'''
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Data
$db = '__DB__'
$out = '__OUT__'
$cn = New-Object System.Data.SqlClient.SqlConnection
$cn.ConnectionString = "Data Source=(localdb)\v11.0;Integrated Security=True;Initial Catalog=$db;Connect Timeout=60"
$cn.Open()
$cmd = $cn.CreateCommand()
$tables = @()
$cmd.CommandText = "SELECT name FROM sys.tables ORDER BY name"
$r = $cmd.ExecuteReader(); while($r.Read()){ $tables += $r.GetString(0) }; $r.Close()
$result = @()
foreach ($t in $tables) {
  $entry = [ordered]@{ name = $t; columns = @(); rows = 0; sample = @() }
  $safe = $t.Replace("'", "''")
  $cmd.CommandText = "SELECT COUNT(*) FROM [$safe]"
  $entry.rows = [int64]$cmd.ExecuteScalar()
  $cmd.CommandText = "SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='$safe' ORDER BY ORDINAL_POSITION"
  $r = $cmd.ExecuteReader()
  while($r.Read()){
    $entry.columns += [ordered]@{ name=$r.GetString(0); type=$r.GetString(1); len=$(if($r.IsDBNull(2)){ $null } else { $r.GetInt32(2) }); nullable=$r.GetString(3) }
  }
  $r.Close()
  if ($entry.rows -gt 0) {
    $cmd.CommandText = "SELECT TOP 3 * FROM [$safe]"
    $r = $cmd.ExecuteReader()
    while($r.Read()){
      $row = [ordered]@{}
      for($i=0; $i -lt $r.FieldCount; $i++){
        $v = $(if($r.IsDBNull($i)){ $null } else { $r.GetValue($i) })
        if ($v -is [datetime]) { $v = $v.ToString('yyyy-MM-dd HH:mm:ss') }
        if ($v -is [byte[]]) { $v = '<binary ' + $v.Length + 'B>' }
        $row[$r.GetName($i)] = $v
      }
      $entry.sample += $row
    }
    $r.Close()
  }
  $result += $entry
}
$cn.Close()
$json = ConvertTo-Json -InputObject $result -Depth 6 -Compress
[IO.File]::WriteAllText($out, $json, [Text.UTF8Encoding]::new($false))
Write-Output ("db={0} tables={1} bytes={2}" -f $db, $result.Count, $json.Length)
'''


ALLOWED = ('HWKCOPY_XWall', 'HWKCOPY_XWallTem', 'HWKCOPY_UserGlazing')


def dump(db):
    if db not in ALLOWED:
        raise SystemExit(f'refused: {db!r} not in {ALLOWED}')
    out_remote = f'{REMOTE_DIR}\\{db}-schema.json'
    script = SCRIPT.replace('__DB__', db).replace('__OUT__', out_remote)
    probe = ROOT / 'migration_workspace/raw/db-probe' / db
    print(run_ps(script, probe, timeout=900).strip())
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    local = LOCAL_DIR / f'{db}.json'
    run = subprocess.run(SSH + [f'type "{out_remote}"'], capture_output=True, timeout=300)
    if run.returncode:
        raise SystemExit(f'scp failed: {run.stderr[:200]!r}')
    text = run.stdout.decode('utf-8-sig', errors='replace')
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f'bad JSON ({exc}) len={len(text)}') from exc
    local.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    total_rows = sum(t['rows'] for t in data)
    print(f'{db}: {len(data)} tables, {total_rows} rows -> {local}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    dump(sys.argv[1])
