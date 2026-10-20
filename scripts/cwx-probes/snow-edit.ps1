$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}
if($p.MainWindowTitle -notlike '*b.cwx*'){throw ('Expected document b.cwx, got ' + $p.MainWindowTitle)}
$f=[Windows.Automation.AutomationElement]::FocusedElement
if($f.Current.Class -ne 'Edit' -or $f.Current.Name -ne '0.4'){throw ('Expected focused Edit 0.4, got ' + $f.Current.Class + ' ' + $f.Current.Name)}
[Windows.Forms.SendKeys]::SendWait('{HOME}+{END}0.5{ENTER}')
Start-Sleep -Seconds 3
$f2=[Windows.Automation.AutomationElement]::FocusedElement
Add-Type @'
using System;using System.Runtime.InteropServices;public class CwxWin5 {
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
[void][CwxWin5]::ShowWindow([CwxWin5]::GetConsoleWindow(),0)
if($p.MainWindowHandle -ne 0){[void][CwxWin5]::SetForegroundWindow($p.MainWindowHandle)}
Start-Sleep -Milliseconds 500
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\snow-edit.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Before=@{Class='Edit';Name='0.4'}
 After=@{Name=$f2.Current.Name;Class=$f2.Current.ClassName;Id=$f2.Current.AutomationId}
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
}|ConvertTo-Json -Depth 5|Set-Content "$b\snow-edit.json" -Encoding UTF8
