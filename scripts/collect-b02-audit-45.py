import json
from pathlib import Path
from hwk_ecs import run_ps
b=Path('evidence/stages/B02/B02-02/attempt-45')
s=r'''$b='C:\hwk-modern\HWK-000045-B02-02';[ordered]@{At=(Get-Date).ToUniversalTime().ToString('o');Source=[IO.File]::ReadAllText("$b\hashes.json");Texts=[IO.File]::ReadAllText("$b\texts.json");Processes=@(Get-Process XWall|Select Id,Path,SessionId,Responding);Reports=@(Get-ChildItem "$b\reports" -File -Recurse -ErrorAction SilentlyContinue|ForEach-Object{[ordered]@{Path=$_.FullName;Length=$_.Length;SHA256=(Get-FileHash $_.FullName).Hash}});Sample=(Get-FileHash 'C:\hwk-modern\HWK-000041-B02-01\projects\sample-working.cwx'|Select Path,Hash);Errors=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001,1026;StartTime=[datetime]'2026-10-18T18:03:21Z'} -MaxEvents 15 -ErrorAction SilentlyContinue|Select TimeCreated,Id,ProviderName,Message)}|ConvertTo-Json -Depth 7'''
x=json.loads(run_ps(s,b/'audit',60));(b/'audit.json').write_text(json.dumps(x,ensure_ascii=False,indent=2));(b/'source-hashes.json').write_text(x['Source']);(b/'texts.json').write_text(x['Texts']);print({k:v for k,v in x.items() if k not in ['Source','Texts']})
