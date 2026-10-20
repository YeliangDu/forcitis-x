"""B02-02 attempt-47: create this card's directory and capture a read-only preflight.

Creates only C:\\hwk-modern\\HWK-000048-B02-02 (+reports). Never launches, focuses or
closes a client; never writes outside that directory.
"""
from pathlib import Path

from hwk_ecs import run_ps

CARD = 'HWK-000048-B02-02'
base = Path('evidence/stages/B02/B02-02/attempt-47')
base.mkdir(parents=True, exist_ok=True)

prepare = r'''$ErrorActionPreference='Stop'
$card='C:\hwk-modern\HWK-000048-B02-02'
if(Test-Path -LiteralPath $card){throw 'Card directory already exists'}
foreach($p in @('C:\','C:\hwk-modern')){$i=Get-Item -LiteralPath $p -Force;if($i.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse ancestor: $p"}}
$null=New-Item -ItemType Directory -Path $card
$null=New-Item -ItemType Directory -Path "$card\reports"
[ordered]@{At=[DateTime]::UtcNow.ToString('o');Card=$card;Identity=(whoami);Sessions=@(quser 2>&1|ForEach-Object{"$_"});Processes=@(Get-Process XWall -ErrorAction SilentlyContinue|Select-Object Id,Path,SessionId,Responding,MainWindowHandle,MainWindowTitle,StartTime);Tasks=@(Get-ScheduledTask|Where-Object {$_.TaskName -like 'HWKModern*'}|Select-Object TaskName,State)}|ConvertTo-Json -Depth 6|Set-Content "$card\prepare.json" -Encoding UTF8
'''
print(run_ps(prepare, base / 'prepare'))

preflight = r'''$ErrorActionPreference='Stop'
$card='C:\hwk-modern\HWK-000048-B02-02'
$source='C:\Program Files\HWKSoft\XWallClient'
$client='C:\hwk-modern\HWK-000041-B02-01\client'
$sample='C:\hwk-modern\HWK-000041-B02-01\projects\sample-working.cwx'
if(@(Get-ChildItem -LiteralPath $source -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Source reparse points'}
if(@(Get-ChildItem -LiteralPath $client -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Client reparse points'}
$files=@(Get-ChildItem -LiteralPath $source -File -Recurse -Force|Sort-Object FullName|ForEach-Object{[ordered]@{Path=$_.FullName.Substring($source.Length);Length=$_.Length;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
$px=@(Get-Process XWall -ErrorAction SilentlyContinue)
$tcp=@(foreach($p in $px){Get-NetTCPConnection -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State})
[ordered]@{
 At=[DateTime]::UtcNow.ToString('o')
 Files=$files
 Client=(Get-FileHash -LiteralPath "$client\XWall.exe" -Algorithm SHA256).Hash
 WorkingHash=(Get-FileHash -LiteralPath $sample -Algorithm SHA256).Hash
 Processes=@($px|Select-Object Id,Path,SessionId,Responding,MainWindowHandle,MainWindowTitle,StartTime)
 TCP=$tcp
 Reports=@(Get-ChildItem -LiteralPath "$card\reports" -File -Recurse -ErrorAction SilentlyContinue|Select-Object FullName,Length)
 Tasks=@(Get-ScheduledTask|Where-Object {$_.TaskName -like 'HWKModern*'}|Select-Object TaskName,State)
}|ConvertTo-Json -Depth 6|Set-Content "$card\preflight.json" -Encoding UTF8
'''
print(run_ps(preflight, base / 'preflight', timeout=600))

read_back = r'''$ErrorActionPreference='Stop'
$card='C:\hwk-modern\HWK-000048-B02-02'
$p=Get-Content "$card\preflight.json" -Raw -Encoding UTF8|ConvertFrom-Json
[ordered]@{At=[DateTime]::UtcNow.ToString('o');Files=$p.Files;Client=$p.Client;WorkingHash=$p.WorkingHash;Processes=$p.Processes;TCP=$p.TCP;Reports=$p.Reports;Tasks=$p.Tasks}|ConvertTo-Json -Depth 6
'''
print(run_ps(read_back, base / 'preflight-read', timeout=300))
