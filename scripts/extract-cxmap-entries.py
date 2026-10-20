#!/usr/bin/env python3
"""导出某个 native 模块里 CXMap 命名条目的登记清单（只读静态分析，不运行目标）。

判定依据：调用导入函数
  `HWKSciCal.dll!?setName@CXMap@XYUtil@@QEAAXAEBVString@2@_NPEAV?$CXDict@VCXMap@XYUtil@@@2@@Z`
即 `XYUtil::CXMap::setName(const String&, bool, CXDict<CXMap>*)` 的每一条调用点，
用调用点之前最近的 `lea ...,%rdx  # 0x...` 取名字串、最近的 `movb $imm,%r8b` 取 bool 实参。

产出：markdown 清单 + 同名 JSON。所有数字均为静态引用计数，不等于业务语义条目数。
"""
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSN = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*([^\s#]+)\s*(.*)$')
REF = re.compile(r'#\s*0x([0-9a-f]+)')
NAME_RDX = re.compile(r'leaq?\s+.*%rdx')
BOOL_R8 = re.compile(r'movb\s+\$0x([0-9a-f]+),\s*%r8b')
SETNAME = 'setName@CXMap@XYUtil'


def load_pe():
    spec = importlib.util.spec_from_file_location(
        'dossier', ROOT / 'scripts' / 'extract-function-dossier.py')
    if spec is None or spec.loader is None:
        raise SystemExit('无法加载 scripts/extract-function-dossier.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def disassembly(pe):
    cache_dir = ROOT / 'migration_workspace' / '.cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f'objdump-{pe.sha256[:16]}.txt'
    if not cache.exists():
        run = subprocess.run(['objdump', '-d', str(pe.path)],
                             capture_output=True, text=True, check=False)
        if run.returncode:
            raise SystemExit(run.stderr)
        cache.write_text(run.stdout)
    return cache.read_text().splitlines()


def setName_slot(pe):
    for addr, it in pe.iat.items():
        name = it.get('name') or ''
        if SETNAME in name:
            return addr, it
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dll')
    ap.add_argument('--out', required=True, help='markdown 输出路径')
    ap.add_argument('--json', required=True, help='JSON 输出路径')
    a = ap.parse_args()

    mod = load_pe()
    pe = mod.PE(a.dll)
    slot, imp = setName_slot(pe)
    if slot is None or imp is None:
        raise SystemExit('未找到 CXMap::setName 导入槽')
    export_by_va = {pe.base + r: n for n, r in pe.exports}
    ranges = sorted(mod.pdata_ranges(pe))

    entries = []
    cand_name = None
    cand_bool = None
    for line in disassembly(pe):
        m = INSN.match(line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        op, args = m.group(3), m.group(4)
        if op.startswith('lea') and NAME_RDX.search(f'{op} {args}'):
            rm = REF.search(args)
            if rm:
                target = int(rm.group(1), 16)
                text = pe.zstr(target - pe.base, 96)
                cand_name = {'addr': target, 'text': text} if text else None
            continue
        bm = BOOL_R8.search(f'{op} {args}')
        if bm:
            cand_bool = int(bm.group(1), 16)
            continue
        if op.startswith('call') and slot in {
                int(x, 16) for x in REF.findall(args)}:
            site_rva = addr - pe.base
            owner_va = None
            owner_name = None
            for begin, end, _chained in ranges:
                if begin <= site_rva < end:
                    owner_va = pe.base + begin
                    owner_name = export_by_va.get(owner_va)
                    break
            entries.append({
                'site': addr,
                'name': cand_name['text'] if cand_name else None,
                'name_va': cand_name['addr'] if cand_name else None,
                'bool_arg': cand_bool,
                'owner_export': owner_name,
                'owner_va': owner_va,
            })
            cand_name = None
            cand_bool = None

    named = [e for e in entries if e['name']]
    distinct = {}
    for e in named:
        distinct.setdefault(e['name'], []).append(e)
    fmt_by_name = {}
    for name in distinct:
        fmt_by_name[name] = pe.b.find(f'{name}(%1'.encode('ascii')) >= 0

    md = [f'# CXMap 命名条目清单 — {Path(a.dll).name}',
          '',
          f'- 模块 SHA-256：`{pe.sha256}`',
          f'- 注册 API：`{imp["dll"]}!{imp["name"]}`（导入槽 `{slot:#x}`）',
          f'- 调用点总数：{len(entries)}；解析出名字的：{len(named)}；不同名字：{len(distinct)}',
          f'- 带求值跟踪文本 `名字(%1…` 的：{sum(1 for v in fmt_by_name.values() if v)}',
          '',
          '说明：以上均为静态引用计数，不等于业务语义条目数；名单不构成功能库存闭合证明。',
          '',
          '## 条目表',
          '',
          '| 序号 | 名字 | 名字 VA | bool 实参 | 注册点 | 所属函数（.pdata 边界） | 跟踪文本 |',
          '| --- | --- | --- | --- | --- | --- | --- |']
    for i, (name, sites) in enumerate(sorted(distinct.items()), 1):
        e = sites[0]
        if e['owner_export']:
            owner = e['owner_export'].split('@')[0].lstrip('?0123456789_$')
        elif e['owner_va']:
            owner = f"FUN_{e['owner_va']:x}（未导出）"
        else:
            owner = 'UNKNOWN'
        md.append(f"| {i} | `{name}` | `{e['name_va']:#x}` | "
                  f"{'true' if e['bool_arg'] == 1 else e['bool_arg']} | `{e['site']:#x}` | "
                  f"`{owner}` | {'是' if fmt_by_name[name] else '否'} |")
    dup = {k: len(v) for k, v in distinct.items() if len(v) > 1}
    md += ['', '## 重复登记（同名多调用点）', '']
    md += [f'- `{k}`：{v} 次' for k, v in sorted(dup.items())] or ['无']
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({
        'module_sha256': pe.sha256,
        'setName_import': imp,
        'call_sites': len(entries),
        'named_call_sites': len(named),
        'distinct_names': len(distinct),
        'entries': entries,
    }, ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  distinct={len(distinct)}  sites={len(entries)}')


if __name__ == '__main__':
    sys.exit(main())
