$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';$b='C:\hwk-modern\run-20261018'
Add-Type -AssemblyName Accessibility
Add-Type -ReferencedAssemblies ([System.Reflection.Assembly]::LoadWithPartialName('Accessibility').Location) -TypeDefinition @'
using System;using System.Runtime.InteropServices;
public static class HwkAccessible {
 [DllImport("oleacc.dll")] public static extern int AccessibleObjectFromWindow(IntPtr h,uint id,ref Guid iid,[MarshalAs(UnmanagedType.Interface)] out Accessibility.IAccessible obj);
 [DllImport("oleacc.dll")] public static extern int AccessibleChildren(Accessibility.IAccessible obj,int start,int count,[Out,MarshalAs(UnmanagedType.LPArray,SizeParamIndex=2)] object[] children,out int obtained);
}
'@
$ui=Get-Content "$b\ui.json" -Raw -Encoding UTF8|ConvertFrom-Json
$items=@($ui.Windows|ForEach-Object {[PSCustomObject]@{Handle=$_.Handle;Name=$_.Name;Class=$_.Class}})+@($ui.Nodes|Where-Object {$_.Handle -gt 0})
$result=@()
foreach($item in $items){
 $iid=[Guid]'618736e0-3c3d-11cf-810c-00aa00389b71';[Accessibility.IAccessible]$acc=$null
 $hr=[HwkAccessible]::AccessibleObjectFromWindow([IntPtr]$item.Handle,([uint32]4294967292),[ref]$iid,[ref]$acc)
 if($hr -ne 0 -or $null -eq $acc){continue}
 $children=@();try{$count=$acc.accChildCount;for($i=1;$i -le [Math]::Min($count,150);$i++){try{$children+=[PSCustomObject]@{Index=$i;Name=$acc.get_accName($i);Role=$acc.get_accRole($i);State=$acc.get_accState($i);DefaultAction=$acc.get_accDefaultAction($i)}}catch{}}}catch{}
 $result+=[PSCustomObject]@{Handle=$item.Handle;Class=$item.Class;Name=$item.Name;ChildCount=$count;Children=$children}
}
$result|ConvertTo-Json -Depth 6|Set-Content "$b\accessibility.json" -Encoding UTF8
