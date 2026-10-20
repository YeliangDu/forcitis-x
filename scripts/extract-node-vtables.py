#!/usr/bin/env python3
"""从绑定表批量提取每个 CXMap 节点的虚表与 eval 覆盖地址。

做法（纯静态，不需要逐个反编译）：
 1. 读 `cxmap-bindings.json` 得到 名字 → 构造实现函数；
 2. 用 .pdata 取每个构造函数的精确区间，在该区间的 objdump 指令里找出被写入对象首字段的
    vftable 地址（候选：`# 0x...` 目标落在数据节，且该处 8 字节槽指向 .text）；
 3. 以基类 `CXMap` 的 vftable（HWKSciCal.dll 导出 `??_7CXMap@XYUtil@@6B@`）为参照，
    逐槽比对，槽位 8 = `eval`（基类值等于 `CXMap::eval` 导出地址）；
 4. 输出 名字 → vftable → eval 覆盖地址。

局限：vftable 的识别依赖启发式；未通过校验的条目输出 `UNKNOWN` 而不是猜值。
"""
import argparse
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSN = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*([^\s#]+)\s*(.*)$')
REF = re.compile(r'#\s*0x([0-9a-f]+)')


def load_dossier():
    spec = importlib.util.spec_from_file_location(
        'dossier', ROOT / 'scripts' / 'extract-function-dossier.py')
    if spec is None or spec.loader is None:
        raise SystemExit('无法加载 scripts/extract-function-dossier.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        raise SystemExit(f'无法读取 JSON：{path}（{exc}）') from exc


def slots(pe, va, count):
    o = pe.maybe_off(va - pe.base)
    if o is None:
        return []
    return [struct.unpack_from('<Q', pe.b, o + 8 * i)[0] for i in range(count)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bindings', required=True)
    ap.add_argument('--entries', required=True)
    ap.add_argument('--dll', required=True)
    ap.add_argument('--sci', required=True, help='HWKSciCal.dll，用于取基类 vftable')
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    mod = load_dossier()
    pe = mod.PE(a.dll)
    sci = mod.PE(a.sci)
    base_va = next((sci.base + r for n, r in sci.exports if n.startswith('??_7CXMap@XYUtil@@6B@')), None)
    if base_va is None:
        raise SystemExit('未找到 CXMap 基类 vftable')
    base_eval = next((sci.base + r for n, r in sci.exports if n.startswith('?eval@CXMap@XYUtil@@UE')), None)
    base = slots(sci, base_va, 25)
    if base_eval is not None and base[8] != base_eval:
        raise SystemExit('基类 vftable 槽 8 与 CXMap::eval 不符，槽位假设失效')

    text_lo, text_hi = pe.base + 0x1000, pe.base + 0x1000 + 0x400000
    cache = ROOT / 'migration_workspace' / '.cache'
    dis = None
    for p in cache.glob('objdump-*.txt'):
        if p.name.endswith(pe.sha256[:16] + '.txt'):
            dis = p.read_text().splitlines()
    if dis is None:
        raise SystemExit('缺少该模块的 objdump 缓存，请先跑一次 extract-function-dossier.py')

    ctor_of = {}
    for b in read_json(a.bindings)['bindings']:
        if b.get('ctor'):
            ctor_of[b['name']] = int(b['ctor'].split('_')[1], 16)   # 已是绝对 VA

    ranges = sorted(mod.pdata_ranges(pe))
    ctor_ranges = []
    for ctor in set(ctor_of.values()):
        span = next(((b, e) for b, e, _c in ranges if b == ctor - pe.base), None)
        if span:
            ctor_ranges.append((pe.base + span[0], pe.base + span[1], ctor))
    ctor_ranges.sort()
    cand = {}
    for line in dis:
        m = INSN.match(line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        owner = next((c for b, e, c in ctor_ranges if b <= addr < e), None)
        if owner is None:
            continue
        rest = m.group(4)
        if 'lea' not in m.group(3):
            continue
        rm = REF.search(rest)
        if not rm:
            continue
        target = int(rm.group(1), 16)
        s = slots(pe, target, 9)
        if len(s) < 9:
            continue
        if not all(text_lo <= x < text_hi for x in s[:9]):
            continue
        cand.setdefault(owner, target)

    rows = []
    for name, ctor in sorted(ctor_of.items()):
        vt = cand.get(ctor)
        row = {'name': name, 'ctor': f'FUN_{ctor:x}', 'vtable': f'{vt:#x}' if vt else None,
               'eval': None, 'eval_overridden': None}
        if vt:
            s = slots(pe, vt, 25)
            if len(s) == 25:
                row['eval'] = f'{s[8]:#x}'
                row['eval_overridden'] = s[8] != base[8]
        rows.append(row)

    known = [r for r in rows if r['eval']]
    over = [r for r in known if r['eval_overridden']]
    md = ['# CXMap 节点虚表与 eval 覆盖地址（批量静态提取）', '',
          f'- 模块：`{a.dll}`（SHA-256 `{pe.sha256}`）',
          f'- 基类 vftable：`{base_va:#x}`（HWKSciCal.dll `??_7CXMap@XYUtil@@6B@`）',
          f'- 基类 eval（槽 8）：`{base[8]:#x}`',
          f'- 提取到 vftable 的条目：{len(known)} / {len(rows)}；其中 eval 被覆盖：{len(over)}',
          '',
          '启发式说明：vftable 由构造函数里写入对象首字段的 `lea` 目标识别，且要求前 9 个槽都指向代码。'
          '未识别者保留 `UNKNOWN`，不猜值。', '',
          '| 名字 | 构造 | vftable | eval（槽 8） | 覆盖基类 |', '| --- | --- | --- | --- | --- |']
    for r in rows:
        md.append(f"| `{r['name']}` | `{r['ctor']}` | `{r['vtable'] or 'UNKNOWN'}` | "
                  f"`{r['eval'] or 'UNKNOWN'}` | "
                  f"{'是' if r['eval_overridden'] else ('否' if r['eval'] else 'UNKNOWN')} |")
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({'module_sha256': pe.sha256, 'base_vtable': f'{base_va:#x}',
                                        'base_eval': f'{base[8]:#x}', 'rows': rows},
                                       ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  rows={len(rows)}  vtable={len(known)}  eval_overridden={len(over)}')


if __name__ == '__main__':
    sys.exit(main())
