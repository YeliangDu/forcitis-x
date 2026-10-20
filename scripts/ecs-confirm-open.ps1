$ErrorActionPreference='Stop';$b='C:\hwk-modern\run-20261018'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$p=@(Get-Process XWall|Where-Object {$_.Path -like "$b\*"});if($p.Count -ne 1){throw 'Unique isolated process required'}
$root=[Windows.Automation.AutomationElement]::RootElement
$c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$p[0].Id)
$observed=Get-Content "$b\ui.json" -Raw -Encoding UTF8|ConvertFrom-Json
$meta=@($observed.Nodes|Where-Object {$_.Name -eq '打开' -and $_.Class -eq '#32770' -and $_.Type -eq 'ControlType.Window'})
if($meta.Count -ne 1){throw 'Unique observed file dialog required'}
$d=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]$meta[0].Handle)
if($d.Current.ProcessId -ne $p[0].Id -or $d.Current.ClassName -ne '#32770'){throw 'Dialog ownership changed'}
$edit=@($observed.Nodes|Where-Object {$_.AutomationId -eq '1148' -and $_.Type -eq 'ControlType.Edit'})
if($edit.Count -ne 1){throw 'Unique observed filename edit required'}
$e=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]$edit[0].Handle)
if($e.Current.AutomationId -ne '1148' -or $e.Current.ProcessId -ne $p[0].Id){throw 'Edit identity changed'}
Add-Type @'
using System;using System.Runtime.InteropServices;public class HwkDialogInput {
[DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern IntPtr SendMessage(IntPtr h,uint msg,IntPtr w,string text);
[DllImport("user32.dll",EntryPoint="SendMessageW")]public static extern IntPtr ClickMessage(IntPtr h,uint msg,IntPtr w,IntPtr l);
}
'@
if($e.Current.ClassName -ne 'Edit'){throw 'Expected observed native filename Edit'}
$result=[HwkDialogInput]::SendMessage([IntPtr]$edit[0].Handle,0xC,[IntPtr]::Zero,"$b\sample-working.cwx")
if($result -eq [IntPtr]::Zero){throw 'Native filename set failed'}
$buttonMeta=@($observed.Nodes|Where-Object {$_.AutomationId -eq '1' -and $_.Name -eq '打开(O)' -and $_.Type -eq 'ControlType.Button'})
if($buttonMeta.Count -ne 1){throw 'Unique observed open button required'}
$button=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]$buttonMeta[0].Handle)
if($button.Current.Name -ne '打开(O)' -or $button.Current.ProcessId -ne $p[0].Id){throw 'Button identity changed'}
[void][HwkDialogInput]::ClickMessage([IntPtr]$buttonMeta[0].Handle,0xF5,[IntPtr]::Zero,[IntPtr]::Zero)
[PSCustomObject]@{Action='OpenInvoked';Input="$b\sample-working.cwx";SHA256=(Get-FileHash "$b\sample-working.cwx").Hash;At=(Get-Date).ToUniversalTime().ToString('o')}|ConvertTo-Json|Set-Content "$b\confirmed-open.json" -Encoding UTF8
Start-Sleep -Seconds 12
& "$b\ui-probe.ps1"
