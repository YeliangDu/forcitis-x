import sys
from pathlib import Path
sys.path.insert(0,'scripts');from hwk_ecs import run_ps_stdin
b=Path('evidence/stages/B02/B02-02/attempt-43')
s=r'''[ordered]@{At=(Get-Date).ToUniversalTime().ToString('o');Task=(Get-ScheduledTask -TaskName 'HWKModern-000043-Probe'|Select State);Info=(Get-ScheduledTaskInfo -TaskName 'HWKModern-000043-Probe'|Select LastTaskResult);Hashes=@('C:\Program Files\HWKSoft\XWallClient\XWall.exe','C:\Program Files\HWKSoft\XWallClient\示例\门窗计算示例1.cwx','C:\hwk-modern\run-20261018\sample-working.cwx'|ForEach-Object{Get-FileHash $_|Select Path,Hash});UI=[IO.File]::ReadAllText('C:\hwk-modern\HWK-000043-B02-02\ui.json')}|ConvertTo-Json -Depth 6'''
print(run_ps_stdin(s,b/'final-read',40)[:180])
