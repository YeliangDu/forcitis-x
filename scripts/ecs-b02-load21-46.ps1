$ErrorActionPreference='Stop'
$b='C:\hwk-modern\HWK-000046-B02-02'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$p=Get-Process -Id 113264 -ErrorAction Stop
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Existing process identity changed'}
$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$c)
$windows=@();$nodes=@()
foreach($w in $wins){$windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName};$els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition);for($i=0;$i -lt [Math]::Min($els.Count,1200);$i++){$e=$els.Item($i).Current;$nodes+=[ordered]@{Name=$e.Name;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Enabled=$e.IsEnabled;Offscreen=$e.IsOffscreen;Handle=$e.NativeWindowHandle;Class=$e.ClassName;Rect=@($e.BoundingRectangle.X,$e.BoundingRectangle.Y,$e.BoundingRectangle.Width,$e.BoundingRectangle.Height)}}}
Add-Type @'
using System;using System.Runtime.InteropServices;public class Hwk42Window {
[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
[void][Hwk42Window]::ShowWindow([Hwk42Window]::GetConsoleWindow(),0)
[void][Hwk42Window]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Seconds 1
[void][Hwk42Window]::SetCursorPos(948,162)
[Hwk42Window]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[Hwk42Window]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 80
[Hwk42Window]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[Hwk42Window]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 80
$f=[Windows.Automation.AutomationElement]::FocusedElement;if($f.Current.ProcessId -ne $p.Id -or $f.Current.ClassName -ne 'Edit' -or $f.Current.Name -ne '2021'){throw 'Expected height edit2021'}
[Windows.Forms.SendKeys]::SendWait('{HOME}+{END}21{ENTER}')
Start-Sleep -Seconds 5
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$c)
$windows=@();$nodes=@()
foreach($w in $wins){$windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName};$els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition);for($i=0;$i -lt [Math]::Min($els.Count,1200);$i++){$e=$els.Item($i).Current;$nodes+=[ordered]@{Name=$e.Name;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Enabled=$e.IsEnabled;Offscreen=$e.IsOffscreen;Handle=$e.NativeWindowHandle;Class=$e.ClassName;Rect=@($e.BoundingRectangle.X,$e.BoundingRectangle.Y,$e.BoundingRectangle.Width,$e.BoundingRectangle.Height)}}}

$texts=@()
foreach($w in $wins){$es=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition);foreach($el in $es){$pat=$null;if($el.TryGetCurrentPattern([Windows.Automation.TextPattern]::Pattern,[ref]$pat)){$texts+=[ordered]@{Handle=$el.Current.NativeWindowHandle;Name=$el.Current.Name;Text=$pat.DocumentRange.GetText(200000)}}}}
$s=[Windows.Forms.SystemInformation]::VirtualScreen;$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\height21-corrected.png");$g.Dispose();$bmp.Dispose()
[ordered]@{At=(Get-Date).ToUniversalTime().ToString('o');Session=[Diagnostics.Process]::GetCurrentProcess().SessionId;Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle);Texts=$texts;Windows=$windows;Nodes=$nodes;TCP=@(Get-NetTCPConnection -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State);UDP=@(Get-NetUDPEndpoint -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort)}|ConvertTo-Json -Depth 8|Set-Content "$b\height21-corrected.json" -Encoding UTF8
