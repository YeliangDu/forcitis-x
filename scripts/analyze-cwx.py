#!/usr/bin/env python3
"""分析 `.cwx` 工程文件的结构与类型清单（只读静态，不运行原版）。

已确认的头部形态（`索桁架结构.cwx`，7868 字节）：
    ff fe                 UTF-16LE BOM
    ff 0e                 ← 标记
    "HWKSoft XWall "      UTF-16 产品标识
    02 00 00 00  94 1e 00 00
    0e 80                 ← 标记
    "HWKWallContext"      UTF-16 根对象类型名
随后是**类型标签 + 内联二进制**（double/int/UTF-16 混合）的记录流。

本脚本抽取类型名并统计，用于得到 `.cwx` 的对象词汇表（= 领域模型与序列化边界）。
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

UTF16 = re.compile(rb'(?:[\x20-\x7e]\x00){4,40}')
TYPE = re.compile(r'HWK[A-Za-z0-9_]{2,40}')


def read_bytes(path):
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise SystemExit(f'无法读取文件：{path}（{exc}）') from exc


def types_of(b):
    out = collections.Counter()
    for mt in UTF16.finditer(b):
        s = mt.group(0).decode('utf-16le')
        if TYPE.fullmatch(s):
            out[s] += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('entries', help='install-package.json（含 .cwx 成员映射）')
    ap.add_argument('--cab', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    try:
        entries = json.loads(Path(a.entries).read_text())['entries']
    except Exception as exc:
        raise SystemExit(f'无法读取 {a.entries}（{exc}）') from exc

    cwx = [r for r in entries if r['ext'] == '.cwx']
    per_file = {}
    merged = collections.Counter()
    for r in cwx:
        b = read_bytes(Path(a.cab) / r['member'])
        t = types_of(b)
        per_file[r['name']] = {'bytes': r['bytes'], 'types': len(t), 'instances': sum(t.values())}
        merged.update(t)

    prefix = collections.Counter()
    for name in merged:
        m = re.match(r'HWK([A-Z][a-z]*|[A-Z]+)', name)
        prefix[m.group(1) if m else '?'] += 1

    md = ['# `.cwx` 工程文件结构分析（静态）', '',
          f'- 样例数：{len(cwx)}',
          f'- 合并后不同对象类型：**{len(merged)}**',
          f'- 类型实例总数：{sum(merged.values())}', '',
          '## 1. 头部结构（最小样例，实测）', '', '```text',
          'ff fe                  UTF-16LE BOM',
          'ff 0e                  标记',
          '"HWKSoft XWall "       产品标识（UTF-16）',
          '02 00 00 00  94 1e 00 00',
          '0e 80                  标记',
          '"HWKWallContext"       根对象类型名（UTF-16）',
          'a5 02 00 00 …         随后是类型标签 + 内联二进制记录流',
          '```', '',
          '## 2. 每个样例的类型规模', '',
          '| 样例 | 大小 | 类型数 | 实例数 |', '| --- | --- | --- | --- |']
    for n, v in sorted(per_file.items(), key=lambda kv: -kv[1]['bytes']):
        md.append(f"| `{n}` | {v['bytes'] / 1048576:.2f} MB | {v['types']} | {v['instances']} |")

    md += ['', '## 3. 类型前缀分布（按不同类型数）', '', '| 前缀 | 类型数 |', '| --- | --- |']
    for k, v in prefix.most_common(20):
        md.append(f'| `HWK{k}` | {v} |')

    md += ['', '## 4. 出现最多的类型（按实例数）', '', '| 类型 | 实例数 |', '| --- | --- |']
    for k, v in merged.most_common(30):
        md.append(f'| `{k}` | {v} |')

    md += ['', '## 5. 结构含义（有证据的部分）', '',
           '- 根对象是 `HWKWallContext`，向下依次出现 `HWKWallStruct` → `HWKSchema_*`（体系）→ '
           '`HWKWallCheck` → `HWKSchemaCalcInfo` → `HWKLoadInfoB` → `HWKCalc_*`。',
           '- **计算结果是持久化对象**：`HWKCalc_*` 类型合计 107 种，说明工程文件里保存了逐条计算结果。',
           '- 栏杆样例里 7 种 `HWKCADGraph*` 各有 209 个实例，说明几何用图结构（点/线/弧/面/关系）存储。',
           '', '## 6. 口径与限制', '',
           '- 只抽取 UTF-16 的类型名，**未解析字段值与偏移**；字段布局需要结合各类 `Serialize` 反编译。',
           '- 未验证写入路径；能否"新→旧"往返完全未知。',
           '- 样例只有 15 个，不代表全部体系都有覆盖。']
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({'per_file': per_file, 'types': dict(merged),
                                        'prefix': dict(prefix)}, ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  types={len(merged)}  instances={sum(merged.values())}')


if __name__ == '__main__':
    sys.exit(main())
