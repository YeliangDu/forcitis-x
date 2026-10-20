import sys,json,base64,time
from pathlib import Path
from hwk_ecs import run_ps,upload
b=Path('evidence/stages/B02/B02-02/attempt-45');b.mkdir(parents=True,exist_ok=True)
r=r'C:\hwk-modern\HWK-000045-B02-02'
mode=sys.argv[1]
if mode=='prepare':
 print(run_ps("$b='"+r+"';if(Test-Path $b){throw 'exists'};New-Item $b -ItemType Directory|Out-Null;Get-Process -Id 78216|Select Id,Path,SessionId,Responding|ConvertTo-Json",b/'prepare'))
else:
 name=sys.argv[2]
 if mode=='run':
  upload(b/(name+'.ps1'),r+'\\probe.ps1')
  print(run_ps("$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -WindowStyle Hidden -File "+r+"\\probe.ps1';$p=New-ScheduledTaskPrincipal -UserId 'Administrator' -LogonType Interactive -RunLevel Highest;Register-ScheduledTask -Force -TaskName 'HWKModern-000045-Probe' -Action $a -Principal $p|Out-Null;Start-ScheduledTask -TaskName 'HWKModern-000045-Probe'",b/(name+'-schedule')))
 time.sleep(8)
 x=json.loads(run_ps("$b='"+r+"';[ordered]@{Task=(Get-ScheduledTaskInfo -TaskName 'HWKModern-000045-Probe'|Select LastTaskResult,LastRunTime);Image=[Convert]::ToBase64String([IO.File]::ReadAllBytes(\"$b\\desktop.png\"));UI=[IO.File]::ReadAllText(\"$b\\ui.json\")}|ConvertTo-Json -Depth 5",b/(name+'-capture')))
 (b/(name+'.png')).write_bytes(base64.b64decode(x['Image']));(b/(name+'.json')).write_text(x['UI']);print(x['Task'])
