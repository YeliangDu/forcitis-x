#!/usr/bin/env python3
"""从 REA/Ghidra 反编译文本里抽取 CXMap 条目 → 构造实现函数 的绑定表。

反编译文本的稳定形态（每登记一个条目）：
    XYUtil::String::String(local_XXXX,"Name");
    XYUtil::CXMap::setName(pCVar4,local_XXXX,true,pCVar2);
    ... pCVar4 来自紧邻其上的 pCVar4 = (CXMap *)FUN_<addr>(pvVar5,...);

因此「名字」绑定的是它上方最近一次 `(CXMap *)FUN_<addr>(` 构造调用。首次 setName 使用
`pCVar4 = this`，此时构造实现函数记为空（表示沿用外层对象）。

产出：markdown 表 + JSON。绑定为**静态推断**：反编译文本顺序即构造顺序，
但重排/内联优化可能使个别条目错配，故逐条保留名字串与构造地址，供人工复核。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STR_DEF = re.compile(r'XYUtil::String::String\((\w+),\s*"([^"]+)"\)')
CTOR = re.compile(r'(?:pCVar4|this)\s*=\s*\(CXMap \*\)FUN_([0-9a-f]+)\(')
SELF = re.compile(r'pCVar4\s*=\s*this;')
SETNAME = re.compile(r'XYUtil::CXMap::setName\((\w+),\s*(\w+),')


def read_json(path):
    """读取 JSON；失败时报出具体文件而不是抛裸异常。"""
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        raise SystemExit(f'无法读取 JSON：{path}（{exc}）') from exc


def extract(pseudo):
    """按出现顺序返回 [{name, ctor, self}];ctor 为 None 表示 pCVar4 = this。"""
    pending_local = None
    pending_name = None
    current_ctor = None
    current_is_self = False
    rows = []
    for raw in pseudo.splitlines():
        line = raw.strip()
        m = STR_DEF.search(line)
        if m:
            pending_local, pending_name = m.group(1), m.group(2)
            continue
        m = CTOR.search(line)
        if m:
            current_ctor = f'FUN_{int(m.group(1), 16):x}'
            current_is_self = False
            continue
        if SELF.search(line):
            current_ctor = None
            current_is_self = True
            continue
        m = SETNAME.search(line)
        if m and pending_name and m.group(2) == pending_local:
            rows.append({'name': pending_name,
                         'ctor': current_ctor,
                         'is_self': current_is_self,
                         'set_local': m.group(2)})
            pending_local = pending_name = None
            current_ctor = None
            current_is_self = False
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rea_json', nargs='+', help='REA decompile --format json 的输出文件')
    ap.add_argument('--entries', help='cxmap-entries.json，用于补充注册点与所属函数')
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    site_by_name = {}
    if a.entries:
        e = read_json(a.entries)
        for x in e.get('entries', []):
            if x.get('name'):
                site_by_name[x['name']] = x

    all_rows = []
    sources = []
    for f in a.rea_json:
        data = read_json(f)
        pseudo = data.get('normalized_result') or ''
        rows = extract(pseudo)
        declared = pseudo.count('setName(')
        sources.append({'file': f, 'evidence_id': data.get('evidence_id'),
                        'declared_setName': declared, 'bound': len(rows),
                        'provider': (data.get('provider') or {}).get('name'),
                        'provider_version': (data.get('provider') or {}).get('version')})
        for r in rows:
            r['source_evidence_id'] = data.get('evidence_id')
            s = site_by_name.get(r['name'])
            r['site'] = f"{s['site']:#x}" if s else None
            r['owner'] = s.get('owner_export') if s else None
            r['owner_va'] = s.get('owner_va') if s else None
            all_rows.append(r)

    ctors = {}
    for r in all_rows:
        if r['ctor']:
            ctors.setdefault(r['ctor'], []).append(r['name'])
    shared = {k: v for k, v in ctors.items() if len(v) > 1}

    md = ['# CXMap 条目 → 构造实现函数 绑定表', '',
          '绑定为静态推断：名字绑定其上方最近一次 `(CXMap *)FUN_<addr>(` 构造调用；'
          '`pCVar4 = this` 记为空，表示沿用外层对象。重排或内联可能造成个别错配，逐条留地址供复核。',
          '', '## 来源', '', '| 文件 | provider | setName 数 | 成功绑定 |', '| --- | --- | --- | --- |']
    for s in sources:
        md.append(f"| `{s['file']}` | {s['provider']} {s['provider_version']} | "
                  f"{s['declared_setName']} | {s['bound']} |")
    md += ['', f'合计绑定 {len(all_rows)} 条；不同构造实现函数 {len(ctors)} 个；'
           f'被多个名字复用的实现函数 {len(shared)} 个。', '',
           '## 条目表', '',
           '| 序号 | 名字 | 构造实现函数 | 复用数 | 注册点 | 所属函数 | evidence_id |',
           '| --- | --- | --- | --- | --- | --- | --- |']
    for i, r in enumerate(all_rows, 1):
        ctor = r['ctor'] or ('沿用 this' if r['is_self'] else 'UNKNOWN')
        reuse = len(ctors.get(r['ctor'], [])) if r['ctor'] else 1
        owner = r['owner'] or (f"FUN_{r['owner_va']:x}" if r['owner_va'] else 'UNKNOWN')
        if owner not in ('UNKNOWN',) and owner.startswith('?'):
            owner = owner.split('@')[0].lstrip('?0123456789_$')
        md.append(f"| {i} | `{r['name']}` | `{ctor}` | {reuse} | `{r['site'] or 'UNKNOWN'}` | "
                  f"`{owner}` | `{(r['source_evidence_id'] or '')[:18]}…` |")
    if shared:
        md += ['', '## 多个名字复用同一构造实现（需人工判定语义）', '']
        for k, v in sorted(shared.items(), key=lambda kv: -len(kv[1])):
            md.append(f"- `{k}`：{len(v)} 个名字 — " + ', '.join(f'`{n}`' for n in v[:8])
                      + ('…' if len(v) > 8 else ''))
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({'sources': sources, 'bindings': all_rows},
                                       ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  bound={len(all_rows)}  ctors={len(ctors)}  shared={len(shared)}')


if __name__ == '__main__':
    sys.exit(main())
