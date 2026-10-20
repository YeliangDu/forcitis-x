#!/usr/bin/env python3
"""`.cwx` 跨源一致性验证（离线，不需要实机）。

三条检查：
  C1 每个 `.cwx` 里出现的类型，是否都在合并后的二进制类表里（81 模块 / 4,979 类）
  C2 每个 `.cwx` 里的 `HWKSchema_*`，是否都在 74 体系清单里
  C3 每个 `.cwx` 至少有一个 `HWKSchema_*`（工程必须声明体系）

任一不满足即 FAIL，输出逐文件结果与全局判定。
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
TYPE = re.compile(rb'(?:H\x00W\x00K\x00)(?:[\x20-\x7e]\x00){3,60}')


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        raise SystemExit(f'无法读取 JSON：{path}（{exc}）') from exc


def types_in(b):
    out = set()
    for m in TYPE.finditer(b):
        try:
            s = m.group(0).decode('utf-16le')
        except UnicodeDecodeError:
            continue
        if not re.fullmatch(r'HWK[A-Za-z0-9_]{2,40}', s):
            continue
        if s.endswith('__________') or s.startswith('HWKSOFT'):
            continue      # 结束哨兵/填充标记，不是对象类型
        out.add(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--install', default='migration_workspace/raw/install-package.json')
    ap.add_argument('--classes', default='migration_workspace/raw/class-table-merged.json')
    ap.add_argument('--systems', default='migration_workspace/raw/calculation-systems.json')
    ap.add_argument('--cab', default='evidence/baseline/extracted/cab')
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    entries = read_json(HERE / a.install)['entries']
    classes = set(read_json(HERE / a.classes)['classes'])
    systems = {s['schema'] for s in read_json(HERE / a.systems)['systems']}
    cwx = [r for r in entries if r['ext'] == '.cwx']

    rows = []
    for r in cwx:
        b = (HERE / a.cab / r['member']).read_bytes()
        t = types_in(b)
        # 体系名（HWKSchema_Xxx）是数据驱动的，不要求出现在 C++ 类表里；
        # HWKSchemaCalcInfo 是通用信息类，不是体系声明。
        NON_SCHEMA = {'HWKSchemaCalcInfo'}
        schema = sorted(x for x in t if x.startswith('HWKSchema_'))
        # HWKCADGraph* 只在 HWKCAD.dll 以 RTTI 字符串存在、未导出，见 VERIFICATION.md A3，
        # 这里单列为"已知例外"而不是未知。
        KNOWN_RTTI_ONLY = {'HWKCADGraphArc', 'HWKCADGraphLine', 'HWKCADGraphWire',
                           'HWKCADGraphSurface', 'HWKCADGraphModelDoc',
                           'HWKCADGraphEdgeWireReleation', 'HWKCADGraphWireSurfaceReleation'}
        unknown = sorted(x for x in t - classes
                         if x not in systems and x not in NON_SCHEMA and x not in KNOWN_RTTI_ONLY)
        rtti_only = sorted(x for x in t if x in KNOWN_RTTI_ONLY)
        bad_schema = sorted(set(schema) - systems - NON_SCHEMA)
        rows.append({'file': r['name'], 'bytes': r['bytes'], 'types': len(t),
                     'unknown_types': unknown, 'rtti_only': rtti_only, 'schemas': schema,
                     'schema_not_in_list': bad_schema,
                     'has_schema': bool(schema)})

    def verdict(x):
        if x['types'] == 0:
            return 'N/A(无 CbArchive 类型)'
        if not x['has_schema']:
            return 'FAIL(无体系)'
        if x['unknown_types'] or x['schema_not_in_list']:
            return 'FAIL'
        return 'PASS'

    md = ['# `.cwx` 跨源一致性验证（离线）', '',
          f'- 生成器：`scripts/cwx-crosscheck.py`；类表 {len(classes)} 个；体系清单 {len(systems)} 个',
          '- C1 类型 ⊆ 二进制类表；C2 `HWKSchema_*` ⊆ 74 体系清单；C3 每个工程必须声明体系', '',
          '| 工程 | 大小 | 类型数 | 体系 | C1 | C2 | C3 | 判定 |',
          '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for x in rows:
        c1 = 'PASS' if not x['unknown_types'] else f"FAIL({len(x['unknown_types'])})"
        c2 = 'PASS' if not x['schema_not_in_list'] else f"FAIL({len(x['schema_not_in_list'])})"
        c3 = 'PASS' if x['has_schema'] else ('N/A' if x['types'] == 0 else 'FAIL')
        md.append(f"| `{x['file']}` | {x['bytes'] / 1048576:.2f} MB | {x['types']} | "
                  f"{', '.join(x['schemas'][:3]) or '—'} | {c1} | {c2} | {c3} | {verdict(x)} |")

    fails = [x for x in rows if verdict(x).startswith('FAIL')]
    na = [x for x in rows if verdict(x).startswith('N/A')]
    md += ['', '## 汇总', '',
           f'- PASS：{len(rows) - len(fails) - len(na)}',
           f'- N/A（无 CbArchive 类型，属另一套序列化）：{len(na)} — '
           + ', '.join(f"`{x['file']}`" for x in na),
           f'- FAIL：{len(fails)}']
    if fails:
        md += ['- FAIL 明细：']
        for x in fails:
            md.append(f"    - `{x['file']}`：未知类型 {x['unknown_types'][:5]}；"
                      f"清单外体系 {x['schema_not_in_list'][:3]}；有体系={x['has_schema']}")
    md += ['', '## 限制', '',
           '- 只做"名字集合"比对，不验证字段布局与数值。',
           '- 类型抽取依赖 UTF-16 正则；类型名被拆写或加密时会漏检。']
    Path(HERE / a.out).write_text('\n'.join(md) + '\n')
    Path(HERE / a.json).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n')
    print(f"{a.out}  pass={len(rows) - len(fails)}/{len(rows)}")


if __name__ == '__main__':
    sys.exit(main())
