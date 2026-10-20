param([string]$Base='C:\hwk-modern\run-20261018',[switch]$Start)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$errors=@()
if($Start){
 $exe=Join-Path $Base 'client\XWall.exe'
 if(!(Test-Path $exe)){throw 'Isolated client missing'}
 if(@(Get-Process XWall -ErrorAction SilentlyContinue).Count -gt 0){throw 'Existing XWall process: do not start competing app'}
 $env:APPDATA=Join-Path $Base 'appdata';$env:LOCALAPPDATA=Join-Path $Base 'localappdata'
 New-Item $env:APPDATA,$env:LOCALAPPDATA -ItemType Directory -Force|Out-Null
 $p=Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru
 Start-Sleep -Seconds 15
}
$processes=@(Get-Process | Where-Object {$_.ProcessName -eq 'XWall' -and $_.Path -like "$Base\*"})
$windows=@();$nodes=@();$root=[Windows.Automation.AutomationElement]::RootElement
foreach($proc in $processes){
 $condition=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
 $wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$condition)
 foreach($w in $wins){
  $windows+=[PSCustomObject]@{Name=$w.Current.Name;Class=$w.Current.ClassName;Pid=$proc.Id;Handle=$w.Current.NativeWindowHandle}
  try{$els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition);for($i=0;$i -lt [Math]::Min($els.Count,700);$i++){$e=$els.Item($i);$c=$e.Current;$nodes+=[PSCustomObject]@{Name=$c.Name;AutomationId=$c.AutomationId;Type=$c.ControlType.ProgrammaticName;Class=$c.ClassName;Enabled=$c.IsEnabled;Offscreen=$c.IsOffscreen;Handle=$c.NativeWindowHandle}}}catch{$errors+=$_.Exception.Message}
 }
}
try{$screen=[Windows.Forms.SystemInformation]::VirtualScreen;$bitmap=New-Object Drawing.Bitmap($screen.Width,$screen.Height);$graphics=[Drawing.Graphics]::FromImage($bitmap);$graphics.CopyFromScreen($screen.X,$screen.Y,0,0,$bitmap.Size);$bitmap.Save((Join-Path $Base 'desktop.png'));$graphics.Dispose();$bitmap.Dispose()}catch{$errors+=$_.Exception.Message}
[PSCustomObject]@{At=(Get-Date).ToUniversalTime().ToString('o');Session=[Diagnostics.Process]::GetCurrentProcess().SessionId;Processes=@($processes|Select-Object Id,Path,SessionId,MainWindowTitle);Windows=$windows;Nodes=$nodes;Errors=$errors}|ConvertTo-Json -Depth 6|Set-Content (Join-Path $Base 'ui.json') -Encoding UTF8
