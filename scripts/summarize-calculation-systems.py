#!/usr/bin/env python3
"""清点产品级"计算体系"：解析安装包里的 HWKSchemaList.xml 与 HWKSchema_*.xml。

数据来源（安装包实测，不运行程序）：
  Support/HWKSchemaList.xml   —— 体系清单（StructDesc 大类 + CheckDesc 体系名 + ClassName）
  Support/HWKSchema_*.xml     —— 每个体系的构件类清单（HWKInfoBase ClassName）

输出 markdown 清点 + JSON。所有数字是静态声明，不代表运行验证或计算书覆盖。
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = re.compile(
    r'<(HWK\w+Schema)\s+StructDesc="([^"]*)"\s+CheckDesc="([^"]*)"\s+ClassName="([^"]*)"')
CLASSNAME = re.compile(r'ClassName="(HWK\w+)"')


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        raise SystemExit(f'无法读取 JSON：{path}（{exc}）') from exc


def read_text(path):
    try:
        return Path(path).read_bytes().decode('utf-8-sig', 'replace')
    except OSError as exc:
        raise SystemExit(f'无法读取文件：{path}（{exc}）') from exc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--install', required=True, help='install-package.json')
    ap.add_argument('--cab', required=True, help='CAB 解包目录')
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    entries = read_json(a.install)['entries']
    by_name = {r['name']: r for r in entries}
    cab = Path(a.cab)

    def body(name):
        return read_text(cab / by_name[name]['member'])

    listing = body('HWKSchemaList.xml')
    stripped = re.sub(r'<!--.*?-->', '', listing, flags=re.S)
    rows = ENTRY.findall(stripped)
    commented = re.findall(r'<!--\s*<HWK\w+Schema[^>]*CheckDesc="([^"]*)"', listing)

    groups = collections.Counter(r[1] for r in rows)
    schema_files = sorted(r['name'][:-4] for r in entries
                          if r['ext'] == '.xml' and r['name'].startswith('HWKSchema_'))
    declared = {r[3] for r in rows}

    per_schema = {}
    class_hits = collections.Counter()
    for name in schema_files:
        text = body(name + '.xml')
        names = CLASSNAME.findall(text)
        per_schema[name] = names
        class_hits.update(names)

    md = ['# 计算体系清点（安装包静态实测）', '',
          f'- 清单文件：`HWKSchemaList.xml`（{by_name["HWKSchemaList.xml"]["bytes"]} 字节）',
          f'- **有效体系条目：{len(rows)} 个**，分 {len(groups)} 个大类',
          f'- 体系 Schema 文件：{len(schema_files)} 个',
          f'- 被注释禁用：{len(commented)} 个' + (f'（{", ".join(commented)}）' if commented else ''),
          '', '## 1. 按大类统计', '', '| 大类（StructDesc） | 体系数 |', '| --- | --- |']
    for k, v in groups.most_common():
        md.append(f'| {k} | {v} |')

    md += ['', '## 2. 体系清单', '', '| # | 大类 | 体系（CheckDesc） | Schema 类 |', '| --- | --- | --- | --- |']
    for i, (_tag, st, ck, cn) in enumerate(rows, 1):
        md.append(f'| {i} | {st} | {ck} | `{cn}` |')

    md += ['', '## 3. 清单与文件的一致性', '']
    missing_file = sorted(declared - set(schema_files))
    extra_file = sorted(set(schema_files) - declared)
    md.append(f'- 清单引用但目录中无同名文件：{len(missing_file)} 个 — '
              + (', '.join(f'`{x}`' for x in missing_file) or '无'))
    md.append(f'- 目录中存在但清单未引用：{len(extra_file)} 个 — '
              + (', '.join(f'`{x}`' for x in extra_file) or '无'))
    md.append('- 说明：文件名大小写差异（如 `CeilingFrame2d` vs `CeilingFrame2D`）在 Windows 上等价，此处按字节比较。')

    md += ['', '## 4. 构件类引用', '',
           f'- schema 文件中出现的不同 `ClassName`：{len(class_hits)} 个',
           f'- 引用总次数：{sum(class_hits.values())}',
           f'- 单个体系类数：中位 {sorted(per_schema.values(), key=len)[len(per_schema) // 2] and len(sorted(per_schema.values(), key=len)[len(per_schema) // 2])}，'
           f'最多 {max((len(v) for v in per_schema.values()), default=0)}'
           f'（{max(per_schema, key=lambda k: len(per_schema[k])) if per_schema else "—"}）', '',
           '| 构件类 | 出现体系数 |', '| --- | --- |']
    for k, v in class_hits.most_common(20):
        md.append(f'| `{k}` | {v} |')

    md += ['', '## 5. 口径与未验项', '',
           '- 本表是**安装包声明的体系清单**，不等于"实际能算通"：每个体系的计算正确性、'
           '计算书输出、异常分支均未验证。',
           '- `Support/*.xdf`（106 个数据定义文件）实测为**加密/压缩二进制**'
           '（头部 `\\x00 36 00 00 <count> … 38 00 00 00`，可打印率约 36%），'
           '内容未解密，因此材料/型材/规范数据层仍是 NOT_RUN。',
           '- 体系与 `HWKCalc_*` 实现类的映射（哪个体系用哪些计算类）未建立。',
           '- 与 SQL 库 `XWall.mdf` / `XWallTem.mdf` 的表结构关系未验证。']
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({
        'systems': [{'tag': t, 'group': g, 'name': n, 'schema': c} for t, g, n, c in rows],
        'groups': dict(groups), 'commented_out': commented,
        'schema_files': schema_files, 'per_schema_classes': per_schema,
        'class_hits': dict(class_hits),
    }, ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  systems={len(rows)}  groups={len(groups)}  schemas={len(schema_files)}')


if __name__ == '__main__':
    sys.exit(main())
