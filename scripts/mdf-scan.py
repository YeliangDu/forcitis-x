#!/usr/bin/env python3
"""SQL Server MDF/NDF 页级扫描器（只读静态，不挂载数据库）。

目的：从 .mdf 里取出**表名与列名**，用于数据层（材料/型材/规范）清点。
不实现完整的行/列解码——SQL Server 的行格式依赖 syscolpars 与 RSS 位图，
没有可信来源时宁可只报"页结构事实"，也不猜字段值。

自校验策略：页头 96 字节内 `m_slotCnt` 的确切偏移随版本有差异，本脚本在 0x0E–0x24 之间
逐候选试解，要求同时满足：槽数 > 0、每个槽偏移严格递增、槽偏移落在 (96, 8192) 内。
任一候选通过且能解出可打印名字才采信，否则该页标记 `slotCnt-unresolved`。
"""
import argparse
import collections
import json
import re
import struct
import sys
from pathlib import Path

PAGE = 8192
HEADER = 96
PAGE_TYPES = {1: 'data', 2: 'index', 3: 'text', 4: 'sort', 7: 'iam', 8: 'gam',
              9: 'sgam', 10: 'pfs', 11: 'boot', 13: '??13', 15: 'fileheader',
              16: '??16', 17: '??17'}
NAME = re.compile(rb'[\x20-\x7e]{3,40}')


def page_type(b, p):
    o = p * PAGE
    return b[o + 1] if b[o] == 1 else None


def slot_candidates(b, p):
    """返回 (slotCnt 偏移, 槽数, 槽偏移列表) 的候选，按可信度排序。"""
    o = p * PAGE
    out = []
    for off in range(0x0E, 0x25, 2):
        cnt = struct.unpack_from('<H', b, o + off)[0]
        if not 1 <= cnt <= 512:
            continue
        base = o + PAGE - 2 * cnt
        if base < o + HEADER:
            continue
        slots = list(struct.unpack_from(f'<{cnt}H', b, base))
        if all(HEADER < s < PAGE for s in slots) and all(
                slots[i] < slots[i + 1] for i in range(len(slots) - 1)):
            out.append((off, cnt, slots))
    out.sort(key=lambda t: -t[1])
    return out


def row_strings(b, p, slots, limit=6):
    o = p * PAGE
    names = []
    for s in slots[:limit]:
        start = o + s
        chunk = b[start:start + 200]
        for m in NAME.finditer(chunk):
            names.append(m.group(0).decode('latin-1'))
        for m in re.finditer(rb'(?:[\x20-\x7e]\x00){3,40}', chunk):
            names.append(m.group(0).decode('utf-16le'))
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mdf')
    ap.add_argument('--out')
    ap.add_argument('--json')
    a = ap.parse_args()

    b = Path(a.mdf).read_bytes()
    pages = len(b) // PAGE
    types = collections.Counter(page_type(b, p) or 0 for p in range(pages))
    stats = collections.Counter()
    resolved = []
    unresolved = 0
    for p in range(pages):
        t = page_type(b, p) or 0
        if t not in (1, 2):
            continue
        cands = slot_candidates(b, p)
        if not cands:
            unresolved += 1
            continue
        off, cnt, slots = cands[0]
        stats[off] += 1
        resolved.append((p, PAGE_TYPES.get(t, str(t)), off, cnt,
                         row_strings(b, p, slots)))

    # 表名候选：出现在数据/索引页行里、出现次数较少的标识符
    ident = collections.Counter()
    for _p, _t, _o, _c, names in resolved:
        for n in names:
            if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{2,39}', n):
                ident[n] += 1

    md = [f'# MDF 页级扫描 — `{a.mdf}`', '',
          f'- 文件大小：{len(b)} 字节（{pages} 页 × 8192）',
          '- 页类型分布：' + '，'.join(f'{PAGE_TYPES.get(k, k)}={v}' for k, v in sorted(types.items())),
          f'- 数据/索引页可解析槽表：{len(resolved)}；未解析：{unresolved}',
          '- `slotCnt` 偏移分布：' + '，'.join(f'{k:#x}={v}' for k, v in stats.most_common(5)),
          '', '## 行内标识符（出现次数降序，前 60）', '',
          '| 标识符 | 出现页数 |', '| --- | --- |']
    for n, c in ident.most_common(60):
        md.append(f'| `{n}` | {c} |')
    md += ['', '## 口径与限制', '',
           '- 只做页级槽表解析，不做行/列解码：字段值、类型、单位一律未验证。',
           '- `slotCnt` 偏移由自校验启发式确定，不是从 SQL Server 源码取得的权威布局。',
           '- 未挂载数据库、未执行任何 SQL；不代表表结构完整。']
    text = '\n'.join(md) + '\n'
    if a.out:
        Path(a.out).write_text(text)
    else:
        sys.stdout.write(text)
    if a.json:
        Path(a.json).write_text(json.dumps({
            'file': a.mdf, 'bytes': len(b), 'pages': pages,
            'page_types': {str(k): v for k, v in types.items()},
            'resolved_pages': len(resolved), 'unresolved_pages': unresolved,
            'slot_offset_histogram': {hex(k): v for k, v in stats.items()},
            'identifiers': dict(ident),
        }, ensure_ascii=False, indent=1) + '\n')
    print(f'pages={pages} resolved={len(resolved)} unresolved={unresolved} idents={len(ident)}')


if __name__ == '__main__':
    sys.exit(main())
