#!/usr/bin/env python3
"""把 `HWKCOPY_XWallTem.计算模板` 全量公式取回本地（L7 第 2 步输入）。

远端只 SELECT；`CONTEXT` 以 base64 传回，避免编码损失。产物：`raw/db/formulas-raw.json`。
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hwk_ecs import run_ps  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REMOTE_DIR = r'C:\hwk-modern\dbprobe-20261019b'
LOCAL = ROOT / 'migration_workspace/raw/db/formulas-raw.json'
SSH = ['ssh', '-i', str(Path.home() / '.ssh/hwk-win-test'), '-o', 'IdentitiesOnly=yes',
       '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile=' + str(ROOT / 'evidence/runtime/ecs-20261018/known_hosts'),
       'Administrator@8.149.129.78']

SCRIPT = r'''
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Data
$out = '__OUT__'
$cn = New-Object System.Data.SqlClient.SqlConnection
$cn.ConnectionString = "Data Source=(localdb)\v11.0;Integrated Security=True;Initial Catalog=HWKCOPY_XWallTem;Connect Timeout=60"
$cn.Open()
$cmd = $cn.CreateCommand()
$cmd.CommandText = "SELECT IID, TITLE, SYMBOL, CONTEXT FROM 计算模板 ORDER BY IID"
$r = $cmd.ExecuteReader()
$rows = @()
while($r.Read()){
  $ctx = $null
  if(-not $r.IsDBNull(3)){ $ctx = [Convert]::ToBase64String([byte[]]$r.GetValue(3)) }
  $rows += [ordered]@{
    iid = $r.GetInt32(0)
    title = $(if($r.IsDBNull(1)){ $null } else { $r.GetString(1) })
    symbol = $(if($r.IsDBNull(2)){ $null } else { $r.GetString(2) })
    context_b64 = $ctx
  }
}
$r.Close(); $cn.Close()
$json = ConvertTo-Json -InputObject $rows -Depth 4 -Compress
[IO.File]::WriteAllText($out, $json, [Text.UTF8Encoding]::new($false))
Write-Output ("rows={0} bytes={1}" -f $rows.Count, $json.Length)
'''


def main():
    out_remote = f'{REMOTE_DIR}\\formulas-raw.json'
    print(run_ps(SCRIPT.replace('__OUT__', out_remote), ROOT / 'migration_workspace/raw/db-probe/formulas', timeout=900).strip())
    run = subprocess.run(SSH + [f'type "{out_remote}"'], capture_output=True, timeout=300)
    if run.returncode:
        raise SystemExit(f'pull failed: {run.stderr[:200]!r}')
    text = run.stdout.decode('utf-8-sig', errors='replace')
    try:
        rows = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f'bad JSON: {exc}') from exc
    for row in rows:
        if row.get('context_b64'):
            raw = base64.b64decode(row['context_b64'])
            row['context_text'] = raw.decode('gbk', errors='replace')
            row.pop('context_b64', None)
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n')
    print(f'{len(rows)} formulas -> {LOCAL}')


if __name__ == '__main__':
    main()
