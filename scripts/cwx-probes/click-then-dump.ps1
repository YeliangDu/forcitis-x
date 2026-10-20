$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$tag=[string]$args[0]
$x=[int]$args[1]; $y=[int]$args[2]

$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}

Add-Type @'
using System;using System.Runtime.InteropServices;public class CwxWin14 {
[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
[void][CwxWin14]::ShowWindow([CwxWin14]::GetConsoleWindow(),0)
[void][CwxWin14]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 600
[void][CwxWin14]::SetCursorPos($x,$y)
[CwxWin14]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxWin14]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Seconds 2
$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p.Id)
$nodes=@()
foreach($w in $root.FindAll([Windows.Automation.TreeScope]::Children,$c)){
 $els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
 for($i=0;$i -lt [Math]::Min($els.Count,1200);$i++){
  $e=$els.Item($i).Current
  if($e.Name){
   $nodes+=[ordered]@{Name=$e.Name;Class=$e.ClassName;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Rect=@($e.BoundingRectangle.X,$e.BoundingRectangle.Y,$e.BoundingRectangle.Width,$e.BoundingRectangle.Height)}
  }
 }
}
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\$tag.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Focused=@{Name=([Windows.Automation.AutomationElement]::FocusedElement).Current.Name;Class=([Windows.Automation.AutomationElement]::FocusedElement).Current.ClassName}
 NameNodes=@($nodes | Where-Object { $_.Name -like '*各种样式*' })
 AllNamed=$nodes
}|ConvertTo-Json -Depth 6|Set-Content "$b\$tag.json" -Encoding UTF8
