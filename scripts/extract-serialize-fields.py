"""Recover the field-level shape of `Serialize` methods from the shipped binary.

The classes in the HWKCalc chain each add a few fields and delegate to their base. The
compiler leaves the pattern visible, so it can be read without guessing:

    movl  0x98(%rbx), %edx          ; storing: load field at +0x98
    ...
    jmpq  *<operator<< thunk>       ; pass it to CbArchive::operator<<

    cmpl  $0x20, 0xc(%rbx)          ; loading: version gate at +0xc
    callq *<operator>> thunk
    movl  %eax, 0x98(%rbx)          ; store the read value back into +0x98

This tool scans objdump output for `?Serialize@...` symbols and reports, per method, the
field offsets/sizes touched, the version gate, and the thunks it calls. It never invents a
field: only what the instruction operands state.

Usage: python3 scripts/extract-serialize-fields.py --pe <file> [--filter Glass] [--json out]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SYM = re.compile(r'^([0-9a-f]+) <(\?Serialize@[^>]+)>:$')
INSN = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(\S+)\s*(.*)$')
FIELD_STORE = re.compile(r'0x([0-9a-f]+)\(%rbx\)')
VERSION = re.compile(r'cmpl\s+\$0x([0-9a-f]+),\s*0x([0-9a-f]+)\(%rbx\)')
THUNK = re.compile(r'#\s*0x([0-9a-f]+)$')


def disassemble(pe):
    out = subprocess.run(['objdump', '-d', str(pe)], capture_output=True, text=True, check=False)
    if out.returncode:
        raise SystemExit(f'objdump failed: {out.stderr[:400]}')
    return out.stdout.splitlines()


def parse(lines, name_filter):
    methods = []
    current = None
    for line in lines:
        sym = SYM.match(line)
        if sym:
            if current:
                methods.append(current)
            current = {'address': '0x' + sym.group(1), 'symbol': sym.group(2),
                       'fields': [], 'version_gate': None, 'thunks': [], 'instructions': 0}
            continue
        if current is None:
            continue
        insn = INSN.match(line)
        if not insn:
            if line.strip() == '' and current['instructions']:
                methods.append(current)
                current = None
                continue
            continue
        current['instructions'] += 1
        mnemonic, operands = insn.group(3), insn.group(4)
        # operand order in objdump AT&T syntax: source, destination
        dest_is_member = FIELD_STORE.search(operands.split(',')[-1]) if ',' in operands else None
        if mnemonic.startswith('mov') and dest_is_member:
            size = {'movl': 4, 'movq': 8, 'movsd': 8, 'movss': 4, 'movb': 1}.get(mnemonic, 0)
            current['fields'].append({'offset': int(dest_is_member.group(1), 16),
                                      'size': size, 'direction': 'write',
                                      'mnemonic': mnemonic})
        elif mnemonic.startswith('mov') and ',' in operands:
            src = FIELD_STORE.search(operands.split(',')[0])
            if src:
                size = {'movl': 4, 'movq': 8, 'movsd': 8, 'movss': 4, 'movb': 1}.get(mnemonic, 0)
                current['fields'].append({'offset': int(src.group(1), 16),
                                          'size': size, 'direction': 'read',
                                          'mnemonic': mnemonic})
        version = VERSION.search(f'{mnemonic} {operands}')
        if version:
            current['version_gate'] = {'value': int(version.group(1), 16),
                                       'offset': int(version.group(2), 16)}
        if mnemonic in ('jmpq', 'callq') and '*' in operands:
            thunk = THUNK.search(operands)
            if thunk:
                current['thunks'].append({'kind': mnemonic, 'thunk': '0x' + thunk.group(1)})
    if current:
        methods.append(current)
    if name_filter:
        methods = [m for m in methods if name_filter in m['symbol']]
    return methods


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--pe', required=True)
    ap.add_argument('--filter', default='')
    ap.add_argument('--json', default='')
    args = ap.parse_args(argv[1:])
    methods = parse(disassemble(args.pe), args.filter)
    for m in methods:
        reads = [(f['offset'], f['size']) for f in m['fields'] if f['direction'] == 'read']
        writes = [(f['offset'], f['size']) for f in m['fields'] if f['direction'] == 'write']
        gate = m['version_gate']
        print(f"{m['address']:>12} {m['symbol'][:70]:<70} reads={reads} writes={writes} "
              f"gate={gate['value'] if gate else '-'} thunks={len(m['thunks'])}")
    payload = {'pe': args.pe, 'methods': methods}
    if args.json:
        Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'methods': len(methods)}))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
