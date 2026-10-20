$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$x=[int]$args[0]; $y=[int]$args[1]; $tag=[string]$args[2]
$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}

Add-Type @'
using System;using System.Runtime.InteropServices;public class CwxClick {
[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
[void][CwxClick]::ShowWindow([CwxClick]::GetConsoleWindow(),0)
[void][CwxClick]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 700
[void][CwxClick]::SetCursorPos($x,$y)
[CwxClick]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxClick]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 120
[CwxClick]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxClick]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Seconds 2

$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p.Id)
$windows=@();$nodes=@()
foreach($w in $root.FindAll([Windows.Automation.TreeScope]::Children,$c)){
 $windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName}
 $els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
 for($i=0;$i -lt [Math]::Min($els.Count,1200);$i++){
  $e=$els.Item($i).Current
  $nodes+=[ordered]@{Name=$e.Name;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Class=$e.ClassName;Enabled=$e.IsEnabled;Handle=$e.NativeWindowHandle;Rect=@($e.BoundingRectangle.X,$e.BoundingRectangle.Y,$e.BoundingRectangle.Width,$e.BoundingRectangle.Height)}
 }
}
$focused=[Windows.Automation.AutomationElement]::FocusedElement.Current
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\$tag.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Click=@($x,$y)
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Focused=@{Name=$focused.Name;Class=$focused.ClassName;Id=$focused.AutomationId;Type=$focused.ControlType.ProgrammaticName}
 Windows=$windows
 Nodes=$nodes
}|ConvertTo-Json -Depth 8|Set-Content "$b\$tag.json" -Encoding UTF8
