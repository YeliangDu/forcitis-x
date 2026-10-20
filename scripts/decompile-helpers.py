#!/usr/bin/env python3
"""反编译节点算式里被引用的辅助函数 `FUN_*`，并分类（L5/A 路线第 1 步）。

输入：`migration_workspace/raw/nodes/*.rea.json`（已归档的节点反编译）
输出：`migration_workspace/raw/helpers/<addr>.rea.json` + `migration_workspace/raw/helpers.json`

分类（只看反编译结构，不做语义推断）：
- `GLOBAL_GETTER`：函数体里 `String::String(local,"名")` + `look_string(全局字典, local, …)`，
  说明它取的是一个**具名全局量**，可直接用该名字替代；
- `NODE_CTOR`：往 `param_1` 写某个节点类 `vftable` → **节点构造函数**（符号回退分支用，不是取值）；
- `COEF_TABLE`：函数体里成对的十六进制常量 ≥2 对 → **系数查表**（每对拼一个 double）；
- `VARARG_GET`：`+0x180`/`+0x188` 取变参 + 十六进制默认返回 → **带默认值的变参取值**；
- `INTERPOLATE`：形参含 `double *` 且对参数做区间扫描 → **线性查表/插值**，表由调用方传入；
- `STRING_TABLE`：`String::find` 分支后 `return` 多个常数（十进制或 16 位十六进制打包的 double）→ **字符串键常量表**；
- `TABLE_BUILDER`：`void` 函数、多次 `+0x180` 取向变参再 `+0xa8` 取值 → **表装填/回填过程**（有副作用，不返回数值）；
- `RNG`：函数体里出现 `_time64`/`rand`/`srand` 等时间播种调用（`CalGlassDisp` 的许可校验用的就是它）；
- `ARITH`：函数体里存在 dVar/fVar 算术赋值；
- `OTHER`：以上都不是。

用法：
  GHIDRA_INSTALL_DIR=$HOME/Tools/ghidra_12.1.4_PUBLIC python3 scripts/decompile-helpers.py
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
NODES = RAW / 'nodes'
HELPERS = RAW / 'helpers'
BINARY = 'evidence/baseline/extracted/cab/_1D7374B2004D4FE39A79BCDFC9340FB8'
SNAPSHOT = 'migration_workspace/.cache/snap-hwkwallutil'

NUM_ASSIGN = re.compile(r'\b[df]Var\d+\s*=\s*[^;]*?(FUN_[0-9a-f]+)\s*\(')
STR_CREATE = re.compile(r'XYUtil::String::String\(\s*(\w+)\s*,\s*L?"([^"]+)"\s*\)')
LOOK_GLOBAL = re.compile(r'look_string\(\s*\*\(CXGDict \*\*\)m_pDictMaps_exref[^;]*?(\w+)\s*,')
RNG_HINT = re.compile(r'_time64|__time64|\brand\(|\bsrand\(')
ARITH = re.compile(r'\b[df]Var\d+\s*=\s*[^;]*[-+*/][^;]*;')


def collect_targets():
    """节点里被赋值给数值变量的 FUN_* 地址（去重、保序）。"""
    seen = []
    for path in sorted(NODES.glob('*.rea.json')):
        try:
            text = json.loads(path.read_text()).get('normalized_result') or ''
        except (OSError, json.JSONDecodeError):
            continue
        for m in NUM_ASSIGN.finditer(text):
            addr = m.group(1)
            if addr not in seen:
                seen.append(addr)
    return seen


def decompile(addr):
    out = HELPERS / f'{addr.lower()}.rea.json'
    if out.exists():
        try:
            return json.loads(out.read_text())
        except json.JSONDecodeError:
            out.unlink()
    env = os.environ.copy()
    if not env.get('GHIDRA_INSTALL_DIR'):
        raise SystemExit('GHIDRA_INSTALL_DIR is not set (rea provider_unavailable otherwise)')
    cmd = ['rea', 'decompile', BINARY, '--procedure', f'0x{addr.split("_")[1]}',
           '--provider', 'ghidra', '--snapshot', SNAPSHOT, '--format', 'json']
    run = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    if not run.stdout.strip().startswith('{'):
        return {'error': (run.stderr or run.stdout)[:300]}
    try:
        data = json.loads(run.stdout)
    except json.JSONDecodeError as exc:
        return {'error': f'REA 输出不是 JSON：{exc}'}
    if not data.get('normalized_result'):
        return {'error': data.get('message') or data.get('code') or 'no normalized_result'}
    HELPERS.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data


DAT_WRITE = re.compile(r'\bDAT_[0-9a-f]+\s*[-+*/]?=')
# 线性查表/插值：形参里有 `double *table`，函数体里对参数做区间扫描
INTERP_HINT = re.compile(r'double \*param_\d+')
INTERP_LOOP = re.compile(r'param_1\s*<=\s*\w+\[|\w+\[\w+\]\s*<\s*param_1')
# 字符串键常量表：`String::find` 分支后 return 常数
STRLIT_HINT = re.compile(r'String::find\(')
RET_CONST = re.compile(r'^\s*return\s+(-?\d+\.\d+|-?\d+);', re.M)
RET_HEX = re.compile(r'^\s*return\s+(0x[0-9a-f]{16});', re.M)
HEX_CONST = re.compile(r'\b\w+\s*=\s*0x[0-9a-f]{8}\b')
# 表装填/回填：void、多次 `+0x180` 取变参后 `+0xa8` 取值
BUILDER_HINT = re.compile(r'^\s*void\s+FUN_[0-9a-f]+', re.M)
# 节点构造函数：往 param_1 上写某个 CXMap 节点类的 vftable（符号回退分支用）
NODE_CTOR = re.compile(r'\*\(undefined \*\*\*\)param_1\s*=\s*[\w:]+::vftable')
SIGNATURE_VOID = re.compile(r'^\s*void\s+FUN_[0-9a-f]+\(\s*(?:void)?\s*\)', re.M)


def classify(pseudo):
    if NODE_CTOR.search(pseudo):
        return 'NODE_CTOR', None
    if RNG_HINT.search(pseudo):
        return 'RNG', None
    # PRNG 结构：无入参、无字符串字面量、无 look_string，但反复读/写 DAT_ 全局状态
    if SIGNATURE_VOID.search(pseudo) and not STR_CREATE.search(pseudo) and 'look_string' not in pseudo \
            and len(DAT_WRITE.findall(pseudo)) >= 2:
        return 'RNG', None
    names = [m.group(2) for m in STR_CREATE.finditer(pseudo)]
    if INTERP_HINT.search(pseudo) and INTERP_LOOP.search(pseudo):
        return 'INTERPOLATE', None
    if BUILDER_HINT.search(pseudo) and pseudo.count('+ 0x180') >= 2 and pseudo.count('+ 0xa8') >= 2:
        return 'TABLE_BUILDER', None
    if STRLIT_HINT.search(pseudo) and (len(RET_CONST.findall(pseudo)) + len(RET_HEX.findall(pseudo)) >= 1):
        return 'STRING_TABLE', None
    # 变参取值（带默认值）：`+0x180`/`+0x188` 索引取元 + 十六进制默认返回
    if ('+ 0x180' in pseudo or '+ 0x188' in pseudo) and RET_HEX.search(pseudo) \
            and not STRLIT_HINT.search(pseudo):
        return 'VARARG_GET', None
    if names and LOOK_GLOBAL.search(pseudo):
        return 'GLOBAL_GETTER', names[0]
    # 系数查表：大量成对的十六进制常量（每个 double 拆两个 u32 写入）
    if len(HEX_CONST.findall(pseudo)) >= 4:
        return 'COEF_TABLE', None
    if ARITH.search(pseudo):
        return 'ARITH', None
    return 'OTHER', names[0] if names else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=str(RAW / 'helpers.json'))
    args = ap.parse_args()
    targets = collect_targets()
    # 已归档的辅助函数也要重新分类（规则可能更新）
    for path in sorted(HELPERS.glob('fun_*.rea.json')):
        addr = 'FUN_' + path.stem.split('_')[1].replace('.rea', '')
        if addr not in targets:
            targets.append(addr)
    print(f'待反编译辅助函数：{len(targets)} 个')
    rows, errors = [], []
    for addr in targets:
        data = decompile(addr)
        if 'error' in data:
            errors.append({'addr': addr, 'error': data['error']})
            print(f'  {addr}: 失败 {data["error"][:80]}')
            continue
        kind, name = classify(data['normalized_result'])
        rows.append({'addr': addr, 'kind': kind, 'global_name': name,
                     'evidence_id': data.get('evidence_id')})
        print(f'  {addr}: {kind}' + (f' ({name})' if name else ''))
    Path(args.json).write_text(json.dumps(
        {'binary': BINARY, 'rows': rows, 'errors': errors}, ensure_ascii=False, indent=1) + '\n')
    kinds = {}
    for row in rows:
        kinds[row['kind']] = kinds.get(row['kind'], 0) + 1
    print(json.dumps(kinds, ensure_ascii=False))
    if errors:
        print(f'失败 {len(errors)} 个，见 {args.json}', file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main())
