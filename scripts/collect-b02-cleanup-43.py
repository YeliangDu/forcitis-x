import sys
from pathlib import Path
sys.path.insert(0,'scripts');from hwk_ecs import run_ps_stdin
s=r'''$t=Get-ScheduledTask -TaskName 'HWKModern-000043-Probe';if($t.State -ne 'Ready'){throw 'Task not complete'};if($t.Actions.Execute -ne 'powershell.exe' -or $t.Actions.Arguments -notlike '*C:\hwk-modern\HWK-000043-B02-02\action.ps1*'){throw 'Action identity mismatch'};Unregister-ScheduledTask -TaskName 'HWKModern-000043-Probe' -Confirm:$false;[ordered]@{Remaining=@(Get-ScheduledTask -TaskName 'HWKModern-000043-Probe' -ErrorAction SilentlyContinue).Count;Process=(Get-Process -Id 60096|Select Id,Path,SessionId)}|ConvertTo-Json'''
print(run_ps_stdin(s,Path('evidence/stages/B02/B02-02/attempt-43/cleanup'),35))
