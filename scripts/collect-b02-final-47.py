"""B02-02 attempt-47 postflight: verify integrity, the generated calculation book and errors.

Read-only over the ECS: reads hashes, the produced report and bounded event channels,
then writes final.json inside this card's directory.
"""
import json
from pathlib import Path

from hwk_ecs import run_ps


def load_json_text(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise SystemExit(f'remote capture is not JSON: {error}') from error


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'evidence unreadable: {path}: {error}') from error

CARD = 'HWK-000048-B02-02'
base = Path('evidence/stages/B02/B02-02/attempt-47')
base.mkdir(parents=True, exist_ok=True)

capture = r'''$ErrorActionPreference='Stop'
$card='C:\hwk-modern\HWK-000048-B02-02'
$source='C:\Program Files\HWKSoft\XWallClient'
$client='C:\hwk-modern\HWK-000041-B02-01\client'
$sample='C:\hwk-modern\HWK-000041-B02-01\projects\sample-working.cwx'
$files=@(Get-ChildItem -LiteralPath $source -File -Recurse -Force|Sort-Object FullName|ForEach-Object{[ordered]@{Path=$_.FullName.Substring($source.Length);Length=$_.Length;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
$px=@(Get-Process XWall -ErrorAction SilentlyContinue)
$tcp=@(foreach($p in $px){Get-NetTCPConnection -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State})
$rep=@(Get-ChildItem -LiteralPath "$card\reports" -File -Force)
$rtf=@($rep|Sort-Object Length -Descending|Select-Object -First 1)
$excerpt='';$numbers=@();$docHash=''
if($rtf.Count -eq 1){
 $text=[IO.File]::ReadAllText($rtf[0].FullName)
 $excerpt=$text.Substring(0,[Math]::Min(2500,$text.Length))
 $numbers=@([regex]::Matches($text,'\d+\.\d{4,6}')|ForEach-Object{$_.Value}|Select-Object -Unique -First 40)
 $docHash=(Get-FileHash -LiteralPath $rtf[0].FullName -Algorithm SHA256).Hash
}
$errors=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001,1026;StartTime=[datetime]'2026-10-19T19:45:00Z'} -ErrorAction SilentlyContinue|Where-Object {$_.Message -match 'XWall'}|ForEach-Object{[ordered]@{Time=$_.TimeCreated.ToUniversalTime().ToString('o');Id=$_.Id;Excerpt=$_.Message.Substring(0,[Math]::Min(300,$_.Message.Length))}})
[ordered]@{
 At=[DateTime]::UtcNow.ToString('o')
 Files=$files
 Client=(Get-FileHash -LiteralPath "$client\XWall.exe" -Algorithm SHA256).Hash
 WorkingHash=(Get-FileHash -LiteralPath $sample -Algorithm SHA256).Hash
 Processes=@($px|Select-Object Id,Path,SessionId,Responding,MainWindowTitle)
 TCP=$tcp
 Reports=@($rep|ForEach-Object{[ordered]@{Name=$_.Name;Length=$_.Length;LastWriteTimeUtc=$_.LastWriteTime.ToUniversalTime().ToString('o');SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
 ReportHash=$docHash
 Excerpt=$excerpt
 Numbers=$numbers
 Errors=$errors
 HookOutRecent=@(Get-ChildItem -LiteralPath 'C:\hwk\hook-out' -Recurse -File -ErrorAction SilentlyContinue|Where-Object {$_.LastWriteTimeUtc -gt [datetime]'2026-10-19T19:45:00Z'}|Select-Object FullName,Length)
 Reparse=@(Get-ChildItem -LiteralPath $card -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object FullName)
 Skills=@()
}|ConvertTo-Json -Depth 6|Set-Content "$card\final.json" -Encoding UTF8
'''

read_back = r'''$p=Get-Content 'C:\hwk-modern\HWK-000048-B02-02\final.json' -Raw -Encoding UTF8|ConvertFrom-Json
[ordered]@{At=$p.At;Files=$p.Files;Client=$p.Client;WorkingHash=$p.WorkingHash;Processes=$p.Processes;TCP=$p.TCP;Reports=$p.Reports;ReportHash=$p.ReportHash;Numbers=$p.Numbers;Errors=$p.Errors;HookOutRecent=$p.HookOutRecent;Reparse=$p.Reparse}|ConvertTo-Json -Depth 6
'''

print(run_ps(capture, base / 'final', timeout=600))
out = run_ps(read_back, base / 'final-read', timeout=300)
data = load_json_text(out)
(base / 'final.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')

pre = load_json(base / 'preflight-read' / 'stdout')
baseline = load_json('evidence/stages/B02/B02-01/attempt-41/environment-final/stdout')['After']
index = lambda rows: {row['Path']: (row['Length'], row['SHA256']) for row in rows}  # noqa: E731

comparison = {
    'at': data['At'],
    'baseline_files': len(baseline),
    'source_matches_baseline': index(baseline) == index(data['Files']),
    'source_stable_since_preflight': index(pre['Files']) == index(data['Files']),
    'client_hash_matches': data['Client'] == '76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5',
    'working_sample_matches': data['WorkingHash'] == '2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3',
    'client_processes': data['Processes'],
    'tcp': data['TCP'],
    'reports': data['Reports'],
    'report_sha256': data['ReportHash'],
    'excerpt_head': (base / 'final.json').exists() and data['Numbers'][:8],
    'error_count': len(data['Errors']),
    'errors': data['Errors'],
    'writes_to_default_dir': data['HookOutRecent'],
    'reparse_points': data['Reparse'],
}
(base / 'final-comparison.json').write_text(
    json.dumps(comparison, ensure_ascii=False, indent=1), encoding='utf-8'
)
print(json.dumps(comparison, ensure_ascii=False, indent=1)[:2600])
