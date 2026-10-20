import json
from pathlib import Path
from hwk_ecs import run_ps,upload
b=Path('evidence/stages/B02/B02-02/attempt-45');r=r'C:\hwk-modern\HWK-000045-B02-02'
s=Path('evidence/stages/B02/B02-02/attempt-44/hashes.ps1').read_text().replace('HWK-000044','HWK-000045').replace('hashes.json','hashes-after.json')
s+=r'''
[ordered]@{At=(Get-Date).ToUniversalTime().ToString('o');Sample=(Get-FileHash 'C:\hwk-modern\HWK-000041-B02-01\projects\sample-working.cwx'|Select Path,Hash);Reports=@(Get-ChildItem 'C:\hwk-modern\HWK-000045-B02-02\reports' -File -Recurse|Select FullName,Length)}|ConvertTo-Json -Depth 5|Set-Content 'C:\hwk-modern\HWK-000045-B02-02\post-hashes.json' -Encoding UTF8
'''
p=b/'hashes-after.ps1';p.write_text(s);upload(p,r+'\\hashes-after.ps1')
print(run_ps(r"$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -WindowStyle Hidden -File C:\hwk-modern\HWK-000045-B02-02\hashes-after.ps1';$p=New-ScheduledTaskPrincipal -UserId 'Administrator' -LogonType Interactive -RunLevel Highest;Register-ScheduledTask -TaskName 'HWKModern-000045-Hashes' -Action $a -Principal $p|Out-Null;Start-ScheduledTask -TaskName 'HWKModern-000045-Hashes';for($i=0;$i -lt 20;$i++){Start-Sleep -Seconds 1;if(Test-Path 'C:\hwk-modern\HWK-000045-B02-02\post-hashes.json'){break}};[ordered]@{Source=[IO.File]::ReadAllText('C:\hwk-modern\HWK-000045-B02-02\hashes-after.json');Post=[IO.File]::ReadAllText('C:\hwk-modern\HWK-000045-B02-02\post-hashes.json');Info=(Get-ScheduledTaskInfo -TaskName 'HWKModern-000045-Hashes'|Select LastRunTime,LastTaskResult)}|ConvertTo-Json -Depth 5",b/'hashes-after',60)[:100])
x=json.loads((b/'hashes-after/stdout').read_text(encoding='utf-8-sig'));(b/'source-hashes-after.json').write_text(x['Source']);(b/'post-hashes.json').write_text(x['Post'])
print(run_ps("Unregister-ScheduledTask -TaskName 'HWKModern-000045-Probe' -Confirm:$false;Unregister-ScheduledTask -TaskName 'HWKModern-000045-Hashes' -Confirm:$false;[ordered]@{At=(Get-Date).ToUniversalTime().ToString('o');Remaining=@(Get-ScheduledTask|Where-Object {$_.TaskName -like 'HWKModern-000045-*'}|Select TaskName);Processes=@(Get-Process XWall -ErrorAction SilentlyContinue|Select Id,Path,SessionId)}|ConvertTo-Json -Depth 5",b/'cleanup'))
