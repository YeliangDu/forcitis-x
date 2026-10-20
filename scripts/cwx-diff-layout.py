#!/usr/bin/env python3
"""用差分法从 `.cwx` 里恢复某个类型的字段布局（不依赖反编译 CbArchive）。

原理（实测依据）：同类型对象在文件中出现多次，且类型名在每个实例中的**相对位置固定**
（例如 `HWKCADGraphLine` 恒在 `HWKCADGraphArc` 前 170 字节）。因此：
  · 把所有实例按类型名对齐，逐字节比较 → 恒定偏移 = 结构字段；变化偏移 = 数据字段
  · 8 字节对齐且值域像浮点 → 数值字段；后随 UTF-16 → 字符串字段

用法：python3 scripts/cwx-diff-layout.py <cwx> --type HWKCADGraphArc [--window 400]
输出：字段边界表（恒定/变化、疑似 double、疑似字符串），markdown。
"""
import argparse
import struct
import sys
from pathlib import Path


def read_bytes(path):
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise SystemExit(f'无法读取文件：{path}（{exc}）') from exc


def occurrences(b, name, back, fwd):
    pat = name.encode('utf-16le')
    out = []
    i = 0
    while True:
        j = b.find(pat, i)
        if j < 0:
            break
        start = j - back
        if start >= 0 and j + fwd <= len(b):
            out.append(b[start:j + fwd])
        i = j + 1
    return out


def looks_double(chunk):
    if len(chunk) != 8:
        return None
    v = struct.unpack('<d', chunk)[0]
    if v != v or abs(v) > 1e18:
        return None
    if v == 0.0:
        return 0.0
    if 1e-12 < abs(v) < 1e18:
        return v
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cwx')
    ap.add_argument('--type', required=True)
    ap.add_argument('--window', type=int, default=400)
    ap.add_argument('--out')
    a = ap.parse_args()

    b = read_bytes(a.cwx)
    back = a.window // 2
    fwd = a.window - back
    wins = occurrences(b, a.type, back, fwd)
    if len(wins) < 3:
        raise SystemExit(f'{a.type} 只出现 {len(wins)} 次，样本不足')

    size = min(len(w) for w in wins)
    wins = [w[:size] for w in wins]
    varying = [i for i in range(size) if len({w[i] for w in wins}) > 1]
    const = [i for i in range(size) if len({w[i] for w in wins}) == 1]

    # 把连续变化/恒定区段合并
    def runs(idxs):
        out = []
        for i in idxs:
            if out and i == out[-1][1] + 1:
                out[-1][1] = i
            else:
                out.append([i, i])
        return out

    md = [f'# 差分布局恢复 — `{a.type}`', '',
          f'- 文件：`{a.cwx}`（{len(b)} 字节）',
          f'- 实例数：{len(wins)}；窗口：类型名前后共 {a.window} 字节',
          f'- 恒定字节：{len(const)}；变化字节：{len(varying)}', '',
          '## 变化区段（数据字段候选）', '',
          '| 起止偏移（相对窗口） | 长度 | 首实例 hex | 疑似 |', '| --- | --- | --- | --- |']
    for s, e in runs(varying):
        seg = wins[0][s:e + 1]
        guess = '字符串(UTF-16)' if len(seg) > 1 and any(
            seg[i + 1] == 0 for i in range(0, len(seg) - 1, 2)) else ''
        if len(seg) >= 8 and len(seg) % 8 == 0:
            d = looks_double(seg[:8])
            if d is not None:
                guess = f'double≈{d}'
        md.append(f'| {s}–{e} | {e - s + 1} | `{seg[:16].hex()}` | {guess} |')

    md += ['', '## 恒定区段（结构字段候选，前 12 段）', '',
           '| 起止偏移 | 长度 | 值 hex |', '| --- | --- | --- |']
    for s, e in runs(const)[:12]:
        md.append(f'| {s}–{e} | {e - s + 1} | `{wins[0][s:e + 1][:16].hex()}` |')

    md += ['', '## 口径与限制', '',
           '- 窗口以类型名居中；"偏移"是相对窗口的，不是文件绝对偏移。',
           '- 恒定 ≠ 一定是结构字段（也可能所有实例恰好同值）。',
           '- 未做跨文件比对；不同类型混在同一窗口时会互相干扰。',
           '- **未验证任何字段的业务含义**。']
    text = '\n'.join(md) + '\n'
    if a.out:
        Path(a.out).write_text(text)
        print(f'{a.out}  instances={len(wins)} varying_bytes={len(varying)}')
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    sys.exit(main())
