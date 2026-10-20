#!/usr/bin/env python3
"""解析 `.cwx` 里的参数绑定记录（HWKInfoRelation / HWKInfoRelationOfSelf）。

实测格式（2026-10-19，`a.cwx` / `b.cwx` 双样本验证）：
  记录 = u16 tag(0x8000|len) + UTF-16 名 + u32 A + [可选 u32 0] + u32 个数 + 重复单元
  HWKInfoRelationOfSelf 单元 = u32 长度 + UTF-16 名 + u32 长度 + UTF-16 值（成对）
  HWKInfoRelation     单元 = u32 长度 + UTF-16 名（纯名字）
长度前缀是 **u32**；`b.cwx` 在 A 后多一个 u32 0，故对两种偏移各试一次。

用法：python3 scripts/parse-info-relation.py FILE [FILE...]
"""
import struct
import sys
from pathlib import Path


def parse_record(data, rec, paired):
    tag = struct.pack('<H', 0x8000 | len(rec)) + rec.encode('utf-16-le')
    i = data.find(tag)
    if i < 0:
        return None
    base = i + len(tag)
    for skip in (4, 8):
        try:
            count = struct.unpack_from('<I', data, base + skip)[0]
            if not 0 < count < 5000:
                continue
            p = base + skip + 4
            items = []
            for _ in range(count):
                ln = struct.unpack_from('<I', data, p)[0]
                if ln > 200 or p + 4 + 2 * ln > len(data):
                    raise ValueError('bad length')
                name = data[p + 4:p + 4 + 2 * ln].decode('utf-16-le')
                p += 4 + 2 * ln
                if paired:
                    ln2 = struct.unpack_from('<I', data, p)[0]
                    if ln2 > 200 or p + 4 + 2 * ln2 > len(data):
                        raise ValueError('bad length')
                    value = data[p + 4:p + 4 + 2 * ln2].decode('utf-16-le')
                    p += 4 + 2 * ln2
                    items.append((name, value))
                else:
                    items.append((name, None))
            return items
        except (ValueError, UnicodeDecodeError, struct.error):
            continue
    return None


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        data = Path(arg).read_bytes()
        print(f'== {arg}')
        pairs = parse_record(data, 'HWKInfoRelationOfSelf', paired=True)
        if pairs:
            print(f'  绑定对 {len(pairs)} 条：')
            for name, value in pairs:
                print(f'    {name} → {value}')
        names = parse_record(data, 'HWKInfoRelation', paired=False)
        if names:
            print(f'  名字列表 {len(names)} 条：' + ', '.join(n for n, _ in names[:8]))


if __name__ == '__main__':
    sys.exit(main())
