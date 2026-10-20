import sys,json,base64
from pathlib import Path
sys.path.insert(0,'scripts');from hwk_ecs import run_ps_stdin as run_ps
b=Path('evidence/stages/B02/B02-02/attempt-43');label=sys.argv[1]
s=r"$b='C:\hwk-modern\HWK-000043-B02-02';[ordered]@{Task=(Get-ScheduledTaskInfo -TaskName 'HWKModern-000043-Probe'|Select LastTaskResult,LastRunTime);Image=[Convert]::ToBase64String([IO.File]::ReadAllBytes(\"$b\desktop.png\"));UI=[IO.File]::ReadAllText(\"$b\ui.json\")}|ConvertTo-Json -Depth 5".replace('\\"','"')
x=json.loads(run_ps(s,b/(label+'-capture-retry'),45));(b/(label+'.png')).write_bytes(base64.b64decode(x['Image']));(b/(label+'.json')).write_text(x['UI']);print(x['Task'])
