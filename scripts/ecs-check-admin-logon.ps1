$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
Add-Type @'
using System;using System.Runtime.InteropServices;
public class HwkLogon {
[DllImport("advapi32.dll",SetLastError=true,CharSet=CharSet.Unicode)]
public static extern bool LogonUser(string u,string d,string p,int t,int pr,out IntPtr tok);
[DllImport("kernel32.dll")]public static extern bool CloseHandle(IntPtr h);
}
'@
$pwPath='C:\hwk-modern\.pw-rotated'
$result=[ordered]@{At=[DateTime]::UtcNow.ToString('o');PwFileExists=(Test-Path $pwPath)}
if($result.PwFileExists){
  $pw=([IO.File]::ReadAllText($pwPath)).Trim()
  $result.PwLength=$pw.Length
  $tok=[IntPtr]::Zero
  $result.LogonAdministrator=[HwkLogon]::LogonUser('Administrator','HWK-WIN-TEST',$pw,2,0,[ref]$tok)
  if($tok -ne [IntPtr]::Zero){[void][HwkLogon]::CloseHandle($tok)}
  $result.LastError=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
}
$k=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
$result.AutoAdminLogon=$k.AutoAdminLogon
$result.DefaultUserName=$k.DefaultUserName
$result.DefaultDomainName=$k.DefaultDomainName
$result.PasswordStoredInRegistry=[bool]$k.DefaultPassword
$result | ConvertTo-Json -Depth 4
