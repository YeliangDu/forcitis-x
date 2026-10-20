$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}

Add-Type @'
using System;using System.Runtime.InteropServices;using System.Text;using System.Collections.Generic;
public class CwxIn3 {
 [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern IntPtr GetWindow(IntPtr h, uint cmd);
 [DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
 [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
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
 public static string ComboText(IntPtr h) {
  int len = (int)SendMessageW(h, 0x147, IntPtr.Zero, IntPtr.Zero);
  StringBuilder sb = new StringBuilder(len + 2);
  SendMessageW(h, 0x148, (IntPtr)(len + 1), Marshal.StringToHGlobalUni(sb.ToString()));
  return sb.ToString();
 }
}
'@
[void][CwxIn3]::ShowWindow([CwxIn3]::GetConsoleWindow(),0)
$tops=[CwxIn3]::Top([uint32]$p.Id)
$dialogs=@()
foreach($row in $tops){
 $parts=$row.Split('|')
 if($parts[1] -eq '#32770'){
  $handle=[IntPtr][int64]$parts[0]
  $dialogs+=@{ window=$row; controls=@([CwxIn3]::Kids($handle)) }
 }
}
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\saveas-inspect.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 TopWindows=$tops
 Dialogs=$dialogs
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
}|ConvertTo-Json -Depth 7|Set-Content "$b\saveas-inspect.json" -Encoding UTF8
