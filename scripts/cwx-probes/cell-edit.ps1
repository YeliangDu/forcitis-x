$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$x=[int]$args[0]; $y=[int]$args[1]; $expect=[string]$args[2]; $new=[string]$args[3]

$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}

Add-Type @'
using System;using System.Runtime.InteropServices;public class CwxWin13 {
[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
function Focus-Info {
  $f=[Windows.Automation.AutomationElement]::FocusedElement.Current
  return @{Name=$f.Name;Class=$f.ClassName;Id=$f.AutomationId;Type=$f.ControlType.ProgrammaticName}
}
[void][CwxWin13]::ShowWindow([CwxWin13]::GetConsoleWindow(),0)
[void][CwxWin13]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 800
[void][CwxWin13]::SetCursorPos($x,$y)
[CwxWin13]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxWin13]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 120
[CwxWin13]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxWin13]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 900
$log=@()
$log+=@{step='after-click';focus=(Focus-Info)}
if((Focus-Info).Class -ne 'Edit'){
  [Windows.Forms.SendKeys]::SendWait('{F2}')
  Start-Sleep -Milliseconds 800
  $log+=@{step='after-F2';focus=(Focus-Info)}
}
$f=Focus-Info
if($f.Class -ne 'Edit' -or $f.Name -notmatch $expect){
  [ordered]@{At=(Get-Date).ToUniversalTime().ToString('o');Session=[Diagnostics.Process]::GetCurrentProcess().SessionId;Attempts=$log;Outcome='NO_EDIT_MODE';Expected=$expect}|ConvertTo-Json -Depth 5|Set-Content "$b\cell-edit.json" -Encoding UTF8
  exit 0
}
$old=$f.Name
[Windows.Forms.SendKeys]::SendWait('{HOME}+{END}')
Start-Sleep -Milliseconds 200
[Windows.Forms.SendKeys]::SendWait($new)
Start-Sleep -Milliseconds 400
$typed=(Focus-Info).Name
[Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Seconds 3
$log+=@{step='after-enter';focus=(Focus-Info);typed=$typed}
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\cell-edit.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Click=@($x,$y)
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 OldText=$old
 TypedText=$typed
 Attempts=$log
 Outcome='EDITED'
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
}|ConvertTo-Json -Depth 6|Set-Content "$b\cell-edit.json" -Encoding UTF8
