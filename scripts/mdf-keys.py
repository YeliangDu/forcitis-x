#!/usr/bin/env python3
"""从 SQL Server MDF 里抽取"命名键"并分组（只读静态扫描，不挂载数据库）。

观察到的键形态（XWallTem.mdf 实测）：
    <体系前缀>_<对象>_<用途>[_<后缀>]
例如 CEILINGFRAME2D_RESULT_MG / MG_WATERTIGHT_BASEINFO_GD / MSGPGLS_PS_DISP_MG0
其中 `MG_` 前缀与 `_MG0/_GD/_FJ/_JD/_SH` 后缀的含义**未验证**，本脚本不解释，只统计。

输出：markdown 统计 + JSON（键 → 出现次数 → 所属分组）。
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

KEY = re.compile(rb'(?:[A-Z0-9_]\x00){5,60}')
PREFIX = re.compile(r'^[A-Z][A-Z0-9]*')


def read_bytes(path):
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise SystemExit(f'无法读取文件：{path}（{exc}）') from exc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mdf', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    per_file = {}
    all_keys = collections.Counter()
    for f in a.mdf:
        b = read_bytes(f)
        keys = collections.Counter()
        for mt in KEY.finditer(b):
            s = mt.group(0).decode('utf-16le')
            s = s.rstrip('\x00')
            if re.fullmatch(r'[A-Z][A-Z0-9_]{4,59}', s) and '__' not in s:
                keys[s] += 1
        per_file[f] = {'bytes': len(b), 'keys': len(keys)}
        all_keys.update(keys)

    groups = collections.Counter()
    group_members = collections.defaultdict(list)
    for k in all_keys:
        g = PREFIX.match(k)
        gname = g.group(0) if g else '?'
        groups[gname] += 1
        group_members[gname].append(k)

    md = ['# MDF 命名键清点（静态扫描）', '',
          '| 文件 | 大小 | 不同键数 |', '| --- | --- | --- |']
    for f, v in per_file.items():
        md.append(f"| `{Path(f).name}` | {v['bytes'] / 1048576:.1f} MB | {v['keys']} |")
    md += ['', f'- 合并后不同键：{len(all_keys)}；按首段分组：{len(groups)} 组', '',
           '## 前缀分组（按不同键数）', '', '| 前缀 | 键数 | 示例 |', '| --- | --- | --- |']
    for g, n in groups.most_common(40):
        sample = sorted(group_members[g])[:3]
        md.append(f'| `{g}` | {n} | ' + ', '.join(f'`{s}`' for s in sample) + ' |')

    md += ['', '## 后缀分布（仅统计，不解释语义）', '']
    suffix = collections.Counter()
    for k in all_keys:
        parts = k.split('_')
        suffix[parts[-1] if len(parts) > 1 else '(无)'] += 1
    md.append('| 末段 | 键数 |')
    md.append('| --- | --- |')
    for s, n in suffix.most_common(25):
        md.append(f'| `{s}` | {n} |')

    md += ['', '## 口径与限制', '',
           '- 只做 UTF-16 大写标识符扫描，**不解析行/列**，因此没有类型、单位、数值。',
           '- 键的出现位置（哪张表、哪一列）未知；表结构仍需 `sysschobjs`/`syscolpars` 解析。',
           '- 前缀/后缀只按字符串分段统计，**不推断含义**（`MG`/`JD`/`GD`/`FJ`/`SH` 均未验证）。']
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({
        'files': per_file,
        'keys': dict(all_keys),
        'groups': dict(groups),
    }, ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  keys={len(all_keys)}  groups={len(groups)}')


if __name__ == '__main__':
    sys.exit(main())
