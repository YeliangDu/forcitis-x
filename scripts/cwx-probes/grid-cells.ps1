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
$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p.Id)
$edits=@();$texts=@()
foreach($w in $root.FindAll([Windows.Automation.TreeScope]::Children,$c)){
 $els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
 for($i=0;$i -lt [Math]::Min($els.Count,1200);$i++){
  $e=$els.Item($i).Current
  $row=@{Name=$e.Name;Class=$e.ClassName;Id=$e.AutomationId;Rect=@($e.BoundingRectangle.X,$e.BoundingRectangle.Y,$e.BoundingRectangle.Width,$e.BoundingRectangle.Height)}
  if($e.ClassName -eq 'Edit'){ $edits+=$row }
  elseif($e.Name -match '^[0-9.]+$'){ $texts+=$row }
 }
}
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\grid-cells.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Edits=$edits
 NumericTexts=$texts
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
}|ConvertTo-Json -Depth 6|Set-Content "$b\grid-cells.json" -Encoding UTF8
