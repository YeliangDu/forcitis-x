# HWK-000037: only this new directory may be written. Never launches a client.
$source='C:\Program Files\HWKSoft\XWallClient'
$root='C:\hwk-modern\HWK-000037-B02-01'
function Manifest($base) { @(Get-ChildItem -LiteralPath $base -File -Recurse | Sort-Object FullName | ForEach-Object { [ordered]@{Path=$_.FullName.Substring($base.Length);Length=$_.Length;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash} }) }
$before=Manifest $source
if(@(Get-ChildItem -LiteralPath $source -Recurse -Force | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Source has reparse points'}
if((Get-FileHash -LiteralPath "$source\XWall.exe").Hash -ne '76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5'){throw 'XWall frozen hash mismatch'}
$existing=Test-Path -LiteralPath $root
if($existing){throw 'Refuse to overwrite existing card directory'}
$null=New-Item -ItemType Directory -Path $root
foreach($dir in @('client','projects','outputs')){$null=New-Item -ItemType Directory -Path "$root\$dir"}
Get-ChildItem -LiteralPath $source | Copy-Item -Destination "$root\client" -Recurse
$sample=Get-ChildItem -LiteralPath "$source\示例" -Filter '*.cwx' | Where-Object {(Get-FileHash -LiteralPath $_.FullName).Hash -eq '2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'}
if(@($sample).Count -ne 1){throw 'Real sample hash binding failed'}
Copy-Item -LiteralPath $sample.FullName -Destination "$root\projects\sample-working.cwx"
$after=Manifest $source
$client=Manifest "$root\client"
$metadata=[ordered]@{}
foreach($key in @('instance-id','region-id','zone-id')) {try{$metadata[$key]=Invoke-RestMethod -Uri "http://100.100.100.200/latest/meta-data/$key" -TimeoutSec 3}catch{$metadata[$key]=@{Status='UNKNOWN';Error=$_.Exception.Message}}}
$runtime=@(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue | Where-Object {$_.DisplayName -match 'Visual C\+\+|SQL Server|\.NET'} | Select-Object DisplayName,DisplayVersion)
$result=[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o');Identity=(whoami);OS=(Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture);Culture=(Get-Culture).Name;SystemLocale=(Get-WinSystemLocale).Name;Timezone=(Get-TimeZone).Id
 Sessions=@(quser 2>&1 | ForEach-Object {"$_"});Processes=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -in @('XWall.exe','sqlservr.exe','explorer.exe')} | Select-Object Name,ProcessId,SessionId,ExecutablePath)
 Fonts=@(Get-ChildItem 'C:\Windows\Fonts' -File | Select-Object Name,Length);Runtimes=$runtime;DotNet=(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full' | Select-Object Version,Release)
 DatabaseServices=@(Get-Service | Where-Object {$_.Name -match 'SQL'} | Select-Object Name,Status);LocalDBInfo=@(if(Test-Path 'C:\Program Files\Microsoft SQL Server\110\Tools\Binn\SqlLocalDB.exe'){& 'C:\Program Files\Microsoft SQL Server\110\Tools\Binn\SqlLocalDB.exe' info})
 Metadata=$metadata;Cost=@{Status='UNKNOWN';Reason='No billing API queried; IMDS provides identity only; no resource created'}
 Root=$root;Before=$before;After=$after;Client=$client;SampleSource=$sample.FullName;SampleSourceHash=(Get-FileHash -LiteralPath $sample.FullName).Hash;SampleWorkingHash=(Get-FileHash "$root\projects\sample-working.cwx").Hash
 OutputFiles=@(Get-ChildItem "$root\outputs" -Force);ReparsePoints=@(Get-ChildItem -LiteralPath $root -Recurse -Force | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint} | Select-Object FullName)
 ExistingTasks=@(Get-ScheduledTask | Where-Object {$_.TaskName -like 'HWKModern*'} | Select-Object TaskName,State)
 Cleanup=@{Preserve='ECS, original installation, prior run-20261018 and all unrelated processes/tasks';AllowedDirectory=$root;AllowedTasks=@();Action='No cleanup executed; only this card directory may later be removed after evidence retention and confirming no process uses it'}
}
$result | ConvertTo-Json -Depth 10
