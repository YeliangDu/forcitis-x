#!/usr/bin/env python3
"""全量导出一批"小表"到本地 JSON（L7 数据层第 2 批）。

远端只 `SELECT *`；结果写远端文件后拉回。表名白名单写死在脚本里（防注入）。
用法：python3 scripts/fetch-tables.py [--db HWKCOPY_XWallTem] TABLE...
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

# 只允许导出这些表（白名单，避免把业务库整表拉走）
ALLOWED = {
    '常用材料特性表', '抗滑移系数', '塑性发展系数表', '标准规范表', '规范表',
    '玻璃参数', '风压数据', '材料安全系数表', '钢材强度表', '铝材强度表',
    '玻璃强度表', '材料类别表', '墙体材料表', '连接构件承压强度表',
}

SCRIPT = r'''
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Data
$db='__DB__'
$tables=@(__TABLES__)
$out='__OUT__'
$cn = New-Object System.Data.SqlClient.SqlConnection
$cn.ConnectionString = "Data Source=(localdb)\v11.0;Integrated Security=True;Initial Catalog=$db;Connect Timeout=60"
$cn.Open()
$cmd=$cn.CreateCommand()
$all=[ordered]@{}
foreach($t in $tables){
  $safe=$t.Replace("'","''")
  $cmd.CommandText="SELECT * FROM [$safe]"
  $r=$cmd.ExecuteReader()
  $rows=@()
  while($r.Read()){
    $row=[ordered]@{}
    for($i=0;$i -lt $r.FieldCount;$i++){
      $name=$r.GetName($i)
      if($name -like '*SSMA_TimeStamp*'){ continue }
      $v=$(if($r.IsDBNull($i)){ $null } else { $r.GetValue($i) })
      if($v -is [datetime]){ $v=$v.ToString('yyyy-MM-dd HH:mm:ss') }
      if($v -is [byte[]]){ $v='<binary '+$v.Length+'B>' }
      $row[$name]=$v
    }
    $rows+=$row
  }
  $r.Close()
  $all[$t]=$rows
  Write-Output ("{0}`t{1}" -f $t,$rows.Count)
}
$cn.Close()
[IO.File]::WriteAllText($out, (ConvertTo-Json -InputObject $all -Depth 5 -Compress), [Text.UTF8Encoding]::new($false))
'''


ALLOWED_DBS = ('HWKCOPY_XWall', 'HWKCOPY_XWallTem', 'HWKCOPY_UserGlazing')


def fetch(db, tables):
    if db not in ALLOWED_DBS:
        raise SystemExit(f'refused db: {db!r}')
    bad = [t for t in tables if t not in ALLOWED]
    if bad:
        raise SystemExit(f'refused (not whitelisted): {bad}')
    listed = ','.join(f"'{t}'" for t in tables)
    out_remote = f'{REMOTE_DIR}\\tables-{db}.json'
    script = (SCRIPT.replace('__DB__', db)
                    .replace('__TABLES__', listed)
                    .replace('__OUT__', out_remote))
    print(run_ps(script, ROOT / 'migration_workspace/raw/db-probe' / f'tables-{db}', timeout=900))
    run = subprocess.run(SSH + [f'type "{out_remote}"'], capture_output=True, timeout=300)
    if run.returncode:
        raise SystemExit(f'pull failed: {run.stderr[:200]!r}')
    text = run.stdout.decode('utf-8-sig', errors='replace')
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f'bad JSON: {exc}') from exc
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    local = LOCAL_DIR / f'tables-{db}.json'
    local.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    total = sum(len(v) for v in data.values())
    print(f'{db}: {len(data)} 表 / {total} 行 -> {local}')


if __name__ == '__main__':
    args = sys.argv[1:]
    db = 'HWKCOPY_XWallTem'
    if args[:1] == ['--db']:
        db = args[1]
        args = args[2:]
    if not args:
        raise SystemExit(__doc__)
    fetch(db, args)
