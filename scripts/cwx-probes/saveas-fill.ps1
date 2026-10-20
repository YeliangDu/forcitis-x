$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$target=Join-Path $b 'b.cwx'
$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}
if(Test-Path $target){throw 'Target b.cwx already exists; refusing to overwrite implicitly'}

Add-Type @'
using System;using System.Runtime.InteropServices;using System.Text;using System.Collections.Generic;
public class CwxIn4 {
 [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern IntPtr GetWindow(IntPtr h, uint cmd);
 [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessageW(IntPtr h, uint msg, IntPtr w, string l);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessageW(IntPtr h, uint msg, IntPtr w, StringBuilder l);
 public delegate bool EnumProc(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumProc cb, IntPtr l);
 [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
 public static List<string> Top(uint want) {
  List<string> rows = new List<string>();
  EnumWindows((h, l) => {
   uint pid; GetWindowThreadProcessId(h, out pid);
   if (pid != want || !IsWindowVisible(h)) return true;
   StringBuilder t = new StringBuilder(512); GetWindowTextW(h, t, 512);
   StringBuilder c = new StringBuilder(256); GetClassNameW(h, c, 256);
   RECT r; GetWindowRect(h, out r);
   rows.Add(string.Format("{0}|{1}|{2}|{3},{4},{5},{6}|owner={7}", h.ToInt64(), c.ToString(), t.ToString(), r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top, GetWindow(h, 4).ToInt64()));
   return true;
  }, IntPtr.Zero);
  return rows;
 }
 public static List<string> Kids(IntPtr parent) {
  List<string> rows = new List<string>();
  EnumChildWindows(parent, (h, l) => {
   StringBuilder t = new StringBuilder(512); GetWindowTextW(h, t, 512);
   StringBuilder c = new StringBuilder(256); GetClassNameW(h, c, 256);
   RECT r; GetWindowRect(h, out r);
   rows.Add(string.Format("{0}|{1}|{2}|id={3}|{4},{5},{6},{7}", h.ToInt64(), c.ToString(), t.ToString(), GetDlgCtrlID(h), r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top));
   return true;
  }, IntPtr.Zero);
  return rows;
 }
 public static string GetText(IntPtr h) {
  StringBuilder sb = new StringBuilder(1024);
  int n = (int)SendMessageW(h, 0x000D, (IntPtr)1024, sb); // WM_GETTEXT
  return sb.ToString(0, Math.Max(n, 0));
 }
}
'@
[void][CwxIn4]::ShowWindow([CwxIn4]::GetConsoleWindow(),0)
$tops=[CwxIn4]::Top([uint32]$p.Id)
$dialog=$null
foreach($row in $tops){ $parts=$row.Split('|'); if($parts[1] -eq '#32770' -and $parts[2] -eq '另存为'){ $dialog=[IntPtr][int64]$parts[0] } }
if($dialog -eq $null){ throw 'Save As dialog not found' }
$kids=[CwxIn4]::Kids($dialog)
$editRow=$kids | Where-Object { $_ -match '\|Edit\|.*\|id=1001\|' } | Select-Object -First 1
$saveRow=$kids | Where-Object { $_ -match '\|Button\|保存' } | Select-Object -First 1
if(-not $editRow){ throw 'Filename edit id=1001 not found' }
if(-not $saveRow){ throw 'Save button not found' }
$edit=[IntPtr][int64]$editRow.Split('|')[0]
$save=[IntPtr][int64]$saveRow.Split('|')[0]
$before=[CwxIn4]::GetText($edit)
[void][CwxIn4]::SendMessageW($edit,0x000C,[IntPtr]::Zero,$target) # WM_SETTEXT
Start-Sleep -Milliseconds 400
$after=[CwxIn4]::GetText($edit)
if($after -ne $target){ throw ('Filename edit rejected text: ' + $after) }
[void][CwxIn4]::SendMessageW($save,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero) # BM_CLICK
Start-Sleep -Seconds 5
$tops2=[CwxIn4]::Top([uint32]$p.Id)
$confirm=@()
foreach($row in $tops2){ $parts=$row.Split('|'); if($parts[1] -eq '#32770'){ $confirm+=@{ window=$row; controls=@([CwxIn4]::Kids([IntPtr][int64]$parts[0])) } } }
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\saveas-fill.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Target=$target
 EditBefore=$before
 EditAfter=$after
 TopWindowsAfter=$tops2
 DialogsAfter=$confirm
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
 AHash=(Get-FileHash (Join-Path $b 'a.cwx')).Hash
 BHash=$(if(Test-Path $target){(Get-FileHash $target).Hash}else{$null})
}|ConvertTo-Json -Depth 7|Set-Content "$b\saveas-fill.json" -Encoding UTF8
