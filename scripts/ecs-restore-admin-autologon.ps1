$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
# Restore the documented Administrator autologon (evidence/runtime/ecs-20261018/autologon-setup).
# The password is read from the rotated file and never printed or written to any log.
$pwPath='C:\hwk-modern\.pw-rotated'
if(-not (Test-Path $pwPath)){throw 'rotated password file missing'}
$pw=([IO.File]::ReadAllText($pwPath)).Trim()
if($pw.Length -lt 8){throw 'refusing: rotated password looks invalid'}
$w='HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
$before=Get-ItemProperty $w
Set-ItemProperty -Path $w -Name 'AutoAdminLogon' -Value '1' -Type String
Set-ItemProperty -Path $w -Name 'DefaultUserName' -Value 'Administrator' -Type String
Set-ItemProperty -Path $w -Name 'DefaultDomainName' -Value 'HWK-WIN-TEST' -Type String
Set-ItemProperty -Path $w -Name 'DefaultPassword' -Value $pw -Type String
$after=Get-ItemProperty $w
[ordered]@{
 At=[DateTime]::UtcNow.ToString('o')
 Before=@{AutoAdminLogon=$before.AutoAdminLogon;DefaultUserName=$before.DefaultUserName;DefaultDomainName=$before.DefaultDomainName;HadDefaultPassword=[bool]$before.DefaultPassword}
 After=@{AutoAdminLogon=$after.AutoAdminLogon;DefaultUserName=$after.DefaultUserName;DefaultDomainName=$after.DefaultDomainName;HasDefaultPassword=[bool]$after.DefaultPassword}
 SecretPrinted='never'
} | ConvertTo-Json -Depth 4
