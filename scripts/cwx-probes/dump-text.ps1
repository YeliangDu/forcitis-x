$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b='C:\hwk-modern\run-20261019-cwx'
$tag=[string]$args[0]
$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}
$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p.Id)
$texts=@();$windows=@();$named=@()
foreach($w in $root.FindAll([Windows.Automation.TreeScope]::Children,$c)){
 $windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName}
 $els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
 for($i=0;$i -lt [Math]::Min($els.Count,1500);$i++){
  $e=$els.Item($i)
  $cur=$e.Current
  if($cur.Name){ $named += $cur.Name }
  $pat=$null
  if($e.TryGetCurrentPattern([Windows.Automation.TextPattern]::Pattern,[ref]$pat)){
    $t=$pat.DocumentRange.GetText(200000)
    if($t -and $t.Trim()){ $texts += [ordered]@{handle=$cur.NativeWindowHandle;class=$cur.ClassName;len=$t.Length;text=$t} }
  }
 }
}
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\$tag.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Windows=$windows
 Texts=$texts
 Named=$named
}|ConvertTo-Json -Depth 6|Set-Content "$b\$tag.json" -Encoding UTF8
