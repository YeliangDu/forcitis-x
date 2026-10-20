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
if($p.MainWindowTitle -notlike '*a.cwx*'){throw ('Unexpected title: ' + $p.MainWindowTitle)}
Add-Type @'
using System;using System.Runtime.InteropServices;public class CwxFg {
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
[void][CwxFg]::ShowWindow([CwxFg]::GetConsoleWindow(),0)
[void][CwxFg]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Seconds 1
[Windows.Forms.SendKeys]::SendWait('^+s')
Start-Sleep -Seconds 3

$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p.Id)
$windows=@();$nodes=@()
foreach($w in $root.FindAll([Windows.Automation.TreeScope]::Children,$c)){
 $windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName;Enabled=$w.Current.IsEnabled}
 $els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
 for($i=0;$i -lt [Math]::Min($els.Count,600);$i++){
  $e=$els.Item($i).Current
  $nodes+=[ordered]@{Window=$w.Current.Name;Name=$e.Name;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Class=$e.ClassName;Enabled=$e.IsEnabled;Offscreen=$e.IsOffscreen;Handle=$e.NativeWindowHandle;Rect=@($e.BoundingRectangle.X,$e.BoundingRectangle.Y,$e.BoundingRectangle.Width,$e.BoundingRectangle.Height)}
 }
}
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\saveas-open.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Windows=$windows
 Nodes=$nodes
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
}|ConvertTo-Json -Depth 8|Set-Content "$b\saveas-open.json" -Encoding UTF8
