$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$b='C:\hwk-modern\run-20261018'
Add-Type @'
using System;using System.Runtime.InteropServices;public class HwkClose {
[DllImport("user32.dll")]public static extern bool PostMessage(IntPtr h,uint msg,IntPtr w,IntPtr l);
}
'@
$old=@(Get-Process XWall -ErrorAction SilentlyContinue|Where-Object {$_.Path -like "$b\*"})
foreach($p in $old){[void][HwkClose]::PostMessage($p.MainWindowHandle,0x10,[IntPtr]::Zero,[IntPtr]::Zero)}
Start-Sleep -Seconds 3
if(@(Get-Process XWall -ErrorAction SilentlyContinue|Where-Object {$_.Path -like "$b\*"}).Count -gt 0){& "$b\ui-probe.ps1";throw 'Normal close incomplete; no forced termination'}
$env:APPDATA=Join-Path $b 'appdata';$env:LOCALAPPDATA=Join-Path $b 'localappdata'
$p=Start-Process "$b\client\XWall.exe" -ArgumentList ('"'+$b+'\sample-working.cwx"') -WorkingDirectory "$b\client" -PassThru
Start-Sleep -Seconds 15
& "$b\ui-probe.ps1"
