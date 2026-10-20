$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$b='C:\hwk-modern\run-20261018'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;using System.Runtime.InteropServices;public class HwkForeground {
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("user32.dll")]public static extern IntPtr GetForegroundWindow();
[DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,out uint pid);
}
'@
$p=@(Get-Process XWall | Where-Object {$_.Path -like "$b\*"})
if($p.Count -ne 1){throw 'Expected exactly one isolated XWall'}
$ok=[HwkForeground]::SetForegroundWindow($p[0].MainWindowHandle);Start-Sleep -Milliseconds 500
[uint32]$owner=0;[void][HwkForeground]::GetWindowThreadProcessId([HwkForeground]::GetForegroundWindow(),[ref]$owner)
[PSCustomObject]@{SetForeground=$ok;ForegroundPid=$owner;ExpectedPid=$p[0].Id}|ConvertTo-Json|Set-Content "$b\open-action.json" -Encoding UTF8
if($owner -ne $p[0].Id){throw 'Foreground not owned by isolated XWall; no keys sent'}
[Windows.Forms.SendKeys]::SendWait('^o');Start-Sleep -Seconds 2
& "$b\ui-probe.ps1"
