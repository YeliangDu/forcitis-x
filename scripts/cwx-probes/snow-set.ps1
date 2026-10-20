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

Add-Type @'
using System;using System.Runtime.InteropServices;public class CwxWin6 {
[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
[void][CwxWin6]::ShowWindow([CwxWin6]::GetConsoleWindow(),0)
[void][CwxWin6]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 700
[void][CwxWin6]::SetCursorPos(890,270)
[CwxWin6]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxWin6]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 150
[CwxWin6]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxWin6]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 900
$f=[Windows.Automation.AutomationElement]::FocusedElement
$before=@{Name=$f.Current.Name;Class=$f.Current.ClassName;Id=$f.Current.AutomationId}
if($f.Current.Class -ne 'Edit' -or $f.Current.Name -ne '0.4'){throw ('Expected focused Edit 0.4, got ' + $f.Current.ClassName + ' ' + $f.Current.Name)}
[Windows.Forms.SendKeys]::SendWait('{HOME}+{END}0.5')
Start-Sleep -Milliseconds 400
$typed=( [Windows.Automation.AutomationElement]::FocusedElement ).Current.Name
[Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Seconds 3
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\snow-set.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 BeforeFocus=$before
 TypedText=$typed
 AfterFocus=@{Name=([Windows.Automation.AutomationElement]::FocusedElement).Current.Name;Class=([Windows.Automation.AutomationElement]::FocusedElement).Current.ClassName}
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
}|ConvertTo-Json -Depth 5|Set-Content "$b\snow-set.json" -Encoding UTF8
