#!/usr/bin/env python3
"""通用 `.cwx` 记录读取器：类型名 → 16 字节头 → double 序列。

实测格式（2026-10-18，`各种栏杆样例.cwx` / `HWKCADGraphArc`）：
    <类型名 UTF-16>          (len(name)*2 字节)
    <u32 a><u32 b>           (8 字节)
    <8 字节零>
    <double 序列>            (每个 8 字节，直到下一个类型名或标记)

本脚本不做语义解释：只把记录切出来并解码 double，供人工/公式核对。
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

TYPE = re.compile(rb'(?:H\x00W\x00K\x00)(?:[\x20-\x7e]\x00){3,60}')


def read_bytes(path):
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise SystemExit(f'无法读取文件：{path}（{exc}）') from exc


def parse(b):
    """返回 [{name, pos, a, b, doubles}]。"""
    marks = []
    for m in TYPE.finditer(b):
        try:
            s = m.group(0).decode('utf-16le')
        except UnicodeDecodeError:
            continue
        if re.fullmatch(r'HWK[A-Za-z0-9_]{2,40}', s):
            marks.append((m.start(), s))
    recs = []
    for i, (pos, name) in enumerate(marks):
        body = pos + len(name) * 2
        if body + 16 > len(b):
            continue
        a, bb = struct.unpack_from('<II', b, body)
        q = body + 16
        end = marks[i + 1][0] if i + 1 < len(marks) else len(b)
        n = (end - q) // 8
        if n <= 0 or n > 512:
            continue
        vals = []
        for k in range(n):
            v = struct.unpack_from('<d', b, q + 8 * k)[0]
            vals.append(v)
        recs.append({'name': name, 'pos': pos, 'a': a, 'b': bb, 'doubles': vals})
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cwx')
    ap.add_argument('--type', help='只看某个类型；省略则汇总')
    ap.add_argument('--limit', type=int, default=8)
    ap.add_argument('--json')
    ap.add_argument('--out')
    a = ap.parse_args()

    b = read_bytes(a.cwx)
    recs = parse(b)
    if a.type:
        recs = [r for r in recs if r['name'] == a.type]
    if not recs:
        raise SystemExit('未找到匹配记录')

    if not a.type:
        import collections
        cnt = collections.Counter(r['name'] for r in parse(b))
        md = [f'# `.cwx` 记录汇总 — `{a.cwx}`', '',
              f'- 文件字节：{len(b)}；识别记录：{sum(cnt.values())}；类型：{len(cnt)}', '',
              '| 类型 | 实例 | 中位 double 数 |', '| --- | --- | --- |']
        import statistics
        for name, c in cnt.most_common(30):
            ns = [len(r['doubles']) for r in parse(b) if r['name'] == name]
            md.append(f'| `{name}` | {c} | {statistics.median(ns):.0f} |')
    else:
        md = [f'# `.cwx` 记录 — `{a.type}`', '',
              f'- 文件：`{a.cwx}`；实例：{len(recs)}', '']
        for r in recs[:a.limit]:
            md += [f"## 偏移 {r['pos']}（头 {r['a']}/{r['b']}，{len(r['doubles'])} 个 double）", '',
                   '| # | 值 |', '| --- | --- |']
            for i, v in enumerate(r['doubles'][:14]):
                md.append(f'| {i} | {v!r} |')
            md.append('')
    text = '\n'.join(md) + '\n'
    if a.out:
        Path(a.out).write_text(text)
        print(f'{a.out}  records={len(recs)}')
    else:
        sys.stdout.write(text)
    if a.json:
        Path(a.json).write_text(json.dumps(recs, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    sys.exit(main())
