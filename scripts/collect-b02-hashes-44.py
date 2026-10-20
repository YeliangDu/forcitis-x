from pathlib import Path
from hwk_ecs import run_ps,upload
b=Path('evidence/stages/B02/B02-02/attempt-44')
s=r'''$ErrorActionPreference='Stop'
$source='C:\Program Files\HWKSoft\XWallClient'
$links=@(Get-ChildItem $source -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint});if($links.Count){throw 'reparse'}
$files=@(Get-ChildItem $source -File -Recurse -Force|Sort-Object FullName|ForEach-Object{[ordered]@{Path=$_.FullName.Substring($source.Length);Length=$_.Length;SHA256=(Get-FileHash $_.FullName).Hash}})
[ordered]@{At=(Get-Date).ToUniversalTime().ToString('o');Files=$files}|ConvertTo-Json -Depth 5|Set-Content 'C:\hwk-modern\HWK-000044-B02-02\hashes.json' -Encoding UTF8
'''
(b/'hashes.ps1').write_text(s);upload(b/'hashes.ps1',r'C:\hwk-modern\HWK-000044-B02-02\hashes.ps1')
print(run_ps(r"$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -File C:\hwk-modern\HWK-000044-B02-02\hashes.ps1';$p=New-ScheduledTaskPrincipal -UserId 'Administrator' -LogonType Interactive -RunLevel Highest;Register-ScheduledTask -TaskName 'HWKModern-000044-Hashes' -Action $a -Principal $p|Out-Null;Start-ScheduledTask -TaskName 'HWKModern-000044-Hashes'",b/'hashes-schedule'))
