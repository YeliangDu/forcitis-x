import sys,json,base64
from pathlib import Path
from hwk_ecs import run_ps,upload
b=Path('evidence/stages/B02/B02-02/attempt-46');b.mkdir(parents=True,exist_ok=True)
r=r'C:\hwk-modern\HWK-000046-B02-02'
mode=sys.argv[1]
if mode=='prepare':
 print(run_ps("$b='"+r+"';if(Test-Path $b){throw 'exists'};New-Item $b -ItemType Directory|Out-Null;Get-Process XWall -ErrorAction SilentlyContinue|Select Id,Path,SessionId,Responding|ConvertTo-Json",b/'prepare'))
elif mode=='run':
 name=sys.argv[2];src=b/(name+'.ps1');src.write_text(src.read_text().replace('desktop.png',name+'.png').replace('ui.json',name+'.json'));upload(src,r+'\\probe.ps1')
 print(run_ps("$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -WindowStyle Hidden -File "+r+"\\probe.ps1';$p=New-ScheduledTaskPrincipal -UserId 'Administrator' -LogonType Interactive -RunLevel Highest;Register-ScheduledTask -Force -TaskName 'HWKModern-000046-Probe' -Action $a -Principal $p|Out-Null;Start-ScheduledTask -TaskName 'HWKModern-000046-Probe'",b/(name+'-schedule')))
elif mode=='read':
 name=sys.argv[2];x=json.loads(run_ps("$b='"+r+"';for($i=0;$i -lt 30 -and !(Test-Path (\"$b\\"+name+".json\"));$i++){Start-Sleep -Seconds 1};[ordered]@{Task=(Get-ScheduledTaskInfo -TaskName 'HWKModern-000046-Probe'|Select LastTaskResult,LastRunTime);Image=[Convert]::ToBase64String([IO.File]::ReadAllBytes(\"$b\\"+name+".png\"));UI=[IO.File]::ReadAllText(\"$b\\"+name+".json\")}|ConvertTo-Json -Depth 5",b/(name+'-capture-'+str(len(list(b.glob(name+'-capture*')))))))
 (b/(name+'.png')).write_bytes(base64.b64decode(x['Image']));(b/(name+'.json')).write_text(x['UI']);print(x['Task'])
