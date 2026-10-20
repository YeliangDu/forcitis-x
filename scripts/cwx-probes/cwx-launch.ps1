$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$client='C:\hwk-modern\HWK-000041-B02-01\client'
$sample=Join-Path $b 'a.cwx'
if(@(Get-Process XWall -ErrorAction SilentlyContinue).Count){throw 'Existing XWall; refuse concurrent launch'}
if((Get-FileHash "$client\XWall.exe").Hash -ne '76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5'){throw 'exe mismatch'}
if((Get-FileHash $sample).Hash -ne '7F79C6F34A732C724C3035B52446256AFC9B1EE32940298B05D1D57641F508BF'){throw 'sample a.cwx mismatch'}
$p=Start-Process -FilePath "$client\XWall.exe" -ArgumentList ('"'+$sample+'"') -WorkingDirectory $client -PassThru
Start-Sleep -Seconds 15
$p.Refresh()
Add-Type @'
using System;using System.Runtime.InteropServices;public class CwxWin {
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
}
'@
[void][CwxWin]::ShowWindow([CwxWin]::GetConsoleWindow(),0)
$windows=@();$nodes=@()
$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p.Id)
foreach($w in $root.FindAll([Windows.Automation.TreeScope]::Children,$c)){
 $windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName;Pid=$w.Current.ProcessId}
 try{$els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition);for($i=0;$i -lt [Math]::Min($els.Count,900);$i++){$e=$els.Item($i).Current;$nodes+=[ordered]@{Window=$w.Current.Name;Name=$e.Name;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Class=$e.ClassName;Enabled=$e.IsEnabled;Offscreen=$e.IsOffscreen;Handle=$e.NativeWindowHandle}}}catch{}
}
if($p.MainWindowHandle -ne 0){[void][CwxWin]::SetForegroundWindow($p.MainWindowHandle)}
Start-Sleep -Seconds 2
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\cwx-launch.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 SampleHash=(Get-FileHash $sample).Hash
 SampleSize=(Get-Item $sample).Length
 Windows=$windows
 Nodes=$nodes
 TCP=@(Get-NetTCPConnection -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State)
}|ConvertTo-Json -Depth 8|Set-Content "$b\cwx-launch.json" -Encoding UTF8
