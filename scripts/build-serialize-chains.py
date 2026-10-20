"""Stack the `Serialize` chain of a class: ordered field writes, base edges, version gates.

`?Serialize@Class@@...` bodies follow one compiler shape per layer (see serialize-fields.md §2):
each own field is loaded from `this+off` and handed to a `CbArchive::operator<<` IAT slot, and each
layer calls its base's `Serialize` once, at a known position, which is what fixes the *order* of the
fields inside one `.cwx` record payload. The read half repeats the same list behind
`if (*(int*)(this+0xc) >= gate)` checks.

This tool reads that shape mechanically:

    movsd 0x80(%rdi), %xmm1        ; pending field = +0x80, width 8 (this lives in %rdi here)
    callq *...(%rip) # 0x18034f0e8 ; archive slot -> operator<<(double)  => one write
    callq <base>::Serialize        ; splice the base's list here

The `this` register is not fixed per function, so it is detected per body (the register with the
most member references, excluding `%rsp`/`%rip`). Slots are classified by the mnemonic that feeds
them (`movsd`/`movl`/`movq`/`movzbl` = by-value write, `leaq` = address of an aggregate), and the
body is split into store half / gated load half at the first read of `this+0xc`. Nothing is inferred
beyond the operands: a field is only reported when an instruction names its offset.

Usage:
  python3 scripts/build-serialize-chains.py [--pe <file>] [--root HWKWallContext] [--json out]
"""
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

DEFAULT_PE = Path('evidence/baseline/extracted/cab/_F35DC0979FF04306B20773A25268CC58')
DEFAULT_JSON = Path('migration_workspace/raw/serialize-chains.json')

SYM = re.compile(r'^([0-9a-f]+) <(\?Serialize@[^>]+)>:$')
INSN = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(\S+)\s*(.*)$')
MEMBER = re.compile(r'(?:^|-)?0x([0-9a-f]+)\(%(\w+)\)')
SLOT = re.compile(r'#\s*0x([0-9a-f]+)\s*$')
BASE_CALL = re.compile(r'^(?:callq|jmpq)\s+0x[0-9a-f]+ <(\?Serialize@([A-Za-z0-9_]+)(?:@[A-Za-z0-9_]+)*@@[^>]*)>$')
CLASS_OF = re.compile(r'^\?Serialize@([A-Za-z0-9_]+)(?:@[A-Za-z0-9_]+)*@@')
EAX_FROM_THIS = re.compile(r'^0x([0-9a-f]+)\(%\w+\), %eax$')
IMM_CMP = re.compile(r'^cmpl\s+\$0x([0-9a-f]+),\s*(0x[0-9a-f]+\(%\w+\)|%eax)$')

# width of the value handed to the archive, per move mnemonic (aggregate/String = variable)
WIDTH = {'movsd': 8, 'movq': 8, 'movl': 4, 'movss': 4, 'movb': 1, 'movw': 2, 'movzbl': 1,
         'movzwl': 2}
KIND = {'movsd': 'double', 'movss': 'float', 'movl': 'int32', 'movq': 'int64',
        'movb': 'int8', 'movw': 'int16', 'movzbl': 'bool', 'movzwl': 'int16', 'leaq': 'aggregate'}


def disassemble(pe):
    out = subprocess.run(['objdump', '-d', str(pe)], capture_output=True, text=True, check=False)
    if out.returncode:
        raise SystemExit(f'objdump failed: {out.stderr[:400]}')
    return out.stdout.splitlines()


def bodies(lines):
    """Split objdump output into {symbol: [(address, mnemonic, operands), ...]}."""
    result, current = {}, None
    for line in lines:
        sym = SYM.match(line)
        if sym:
            current = sym.group(2)
            result[current] = []
            continue
        if current is None:
            continue
        insn = INSN.match(line)
        if insn:
            result[current].append((int(insn.group(1), 16), insn.group(3), insn.group(4)))
        elif not line.strip() and result[current]:
            current = None
    return result


def class_of(symbol):
    match = CLASS_OF.match(symbol)
    if match is None:
        raise SystemExit(f'not a Serialize symbol: {symbol}')
    return match.group(1)


def this_register(insns):
    """The register `this` was parked in: the one with the most member references."""
    counts = {}
    for _, mnemonic, operands in insns:
        if not mnemonic.startswith(('mov', 'lea')):
            continue
        for offset, register in MEMBER.findall(operands):
            del offset
            if register in ('rsp', 'rip'):
                continue
            counts[register] = counts.get(register, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda item: item[1])[0]


def store_ranges(insns):
    """Per-field guards: `cmpb $0x0,0x8(%rdi)` + `je T`; the fall-through (je_addr, T) is storing."""
    ranges = []
    for index, (addr, mnemonic, insn_operands) in enumerate(insns):
        if mnemonic != 'cmpb' or '0x8(%rdi)' not in insn_operands:
            continue
        for probe in range(index + 1, min(index + 4, len(insns))):
            mn, ops = insns[probe][1], insns[probe][2]
            if mn in ('je', 'jne', 'jz', 'jnz') and ops.split()[0].startswith('0x'):
                ranges.append((addr, int(ops.split()[0], 16)))
                break
    return ranges


def in_store_range(addr, ranges):
    return any(start < addr < end for start, end in ranges)


def storing_split(insns):
    """Address where the read half starts: the branch target after the `testb`-checked predicate call.

    Shape in this binary: callq *<IAT slot>; testb %al,%al; je 0x<read half>. The predicate is
    CbArchive::IsStoring, so everything from the branch target on is the load path.
    """
    for index, (_, mnemonic, operands) in enumerate(insns):
        if mnemonic != 'callq' or index + 2 >= len(insns):
            continue
        nxt_mnemonic, nxt_ops = insns[index + 1][1], insns[index + 1][2]
        if nxt_mnemonic != 'testb' or not nxt_ops.startswith('%al'):
            continue
        branch_mnemonic, branch_ops = insns[index + 2][1], insns[index + 2][2]
        if branch_mnemonic not in ('je', 'jne', 'jz', 'jnz'):
            continue
        target = branch_ops.split()[0]
        if target.startswith('0x'):
            return int(target, 16)
    return None


def gate_markers(insns, register):
    """Instruction indices where the class version at this+0xc is compared, and the value."""
    markers = {}
    if register is None:
        return markers
    for index, (_, mnemonic, operands) in enumerate(insns):
        if mnemonic != 'cmpl':
            continue
        match = IMM_CMP.match(f'{mnemonic} {operands}')
        if match is None:
            continue
        value, where = int(match.group(1), 16), match.group(2)
        if where.startswith('0x'):
            member_offset = where.split('(')[0]
            if member_offset in ('0xc', '0x28', '0x2c', '0x30') and register in where:
                markers[index] = value
        elif index:
            previous = EAX_FROM_THIS.match(insns[index - 1][2])
            if previous and previous.group(1) == 'c':
                markers[index] = value
    return markers


def parse_body(insns):
    """Return {'base', 'writes', 'reads', 'this_register', 'gates'} for one Serialize body."""
    register = this_register(insns)
    markers = gate_markers(insns, register)
    ranges = store_ranges(insns)
    branch = storing_split(insns)
    addresses = [insn[0] for insn in insns]
    split_index = min(markers) if markers else len(insns)
    if branch is not None:
        split_index = next((i for i, addr in enumerate(addresses) if addr >= branch), split_index)

    base, writes, reads = None, [], []
    gate, pending = None, None
    for index, (_, mnemonic, operands) in enumerate(insns):
        if index in markers:
            gate = markers[index]
            pending = None
            continue
        call = BASE_CALL.match(f'{mnemonic} {operands}')
        if call is not None:
            if base is None and call.group(1).startswith('?Serialize@'):
                base = call.group(1)
            pending = None
            continue
        member = None
        if mnemonic.startswith(('mov', 'lea')) and register is not None:
            for offset, where in MEMBER.findall(operands):
                if where == register:
                    member = int(offset, 16)
        if member is not None:
            pending = (member, mnemonic)
            continue
        if mnemonic in ('callq', 'jmpq'):
            slot = SLOT.search(operands)
            if slot and pending is not None:
                from_kind = KIND.get(pending[1], 'unknown')
                storing = in_store_range(addresses[index], ranges) if ranges else (index < split_index)
                if storing or (not ranges and pending[1] == 'leaq'):
                    entry = {'offset': pending[0], 'from': pending[1], 'kind': from_kind,
                             'width': WIDTH.get(pending[1]), 'slot': '0x' + slot.group(1)}
                    if pending[0] == 0xc:
                        # this+0xc is the class version, not a payload value: archive writes it
                        # through its own slot (0x18034f288) so keep it out of the field list
                        entry['kind'] = 'version_tag'
                        (writes if storing else reads).append(entry)
                    elif storing:
                        writes.append(entry)
                    else:
                        entry['gate'] = gate
                        reads.append(entry)
            pending = None
    return {'base': base, 'writes': writes, 'reads': reads, 'this_register': register,
            'gates': sorted(set(markers.values()))}


def find_record(path, type_name):
    """Locate one `<tag><name>A<payload>` record in a `.cwx` (see cwx-field-widths.md §2)."""
    data = Path(path).read_bytes()
    needle = type_name.encode('utf-16-le')
    position = data.find(needle)
    if position < 0:
        raise SystemExit(f'{path}: no record for {type_name}')
    tag_at = position - 2
    tag = int.from_bytes(data[tag_at:tag_at + 2], 'little')
    if tag != 0x8000 | len(needle) // 2:
        raise SystemExit(f'{path}: unexpected tag {tag:#x} before {type_name}')
    after = position + len(needle)
    return {'path': str(path), 'payload': after + 4,  # u32 A follows the name
            'tag': tag, 'a': int.from_bytes(data[after:after + 4], 'little'), 'data': data}


def walk_payload(record, fields):
    """Read the payload with the recovered field list; aggregate = u32 char count + UTF-16."""
    data, cursor, out = record['data'], record['payload'], []
    for field in fields:
        kind = field['kind']
        if cursor + 4 > len(data):
            out.append({**field, 'at': cursor - record['payload'], 'error': 'past end'})
            break
        if kind == 'double':
            value = struct.unpack_from('<d', data, cursor)[0]
            size = 8
        elif kind == 'float':
            value = struct.unpack_from('<f', data, cursor)[0]
            size = 4
        elif kind == 'int32':
            value = struct.unpack_from('<i', data, cursor)[0]
            size = 4
        elif kind == 'int64':
            value = struct.unpack_from('<q', data, cursor)[0]
            size = 8
        elif kind in ('bool', 'int8'):
            value = data[cursor]
            size = 1
        elif kind == 'int16':
            value = struct.unpack_from('<h', data, cursor)[0]
            size = 2
        else:
            count = struct.unpack_from('<I', data, cursor)[0]
            if count > 4096:
                out.append({**field, 'at': cursor - record['payload'],
                            'error': f'implausible string count {count}'})
                break
            raw = data[cursor + 4:cursor + 4 + 2 * count]
            value = raw.decode('utf-16-le', 'replace')
            size = 4 + 2 * count
        out.append({'class': field['class'], 'class_offset': field['offset'], 'kind': kind,
                    'at': cursor - record['payload'], 'width': size, 'value': value})
        cursor += size
    return out, cursor - record['payload']


# measured by the single-field diffs recorded in cwx-field-widths.md §3 (b.cwx baseline)
CWX_ANCHORS = [
    {'at': 0x14, 'kind': 'double', 'value': 0.4, 'label': '城市基本雪压（b vs c: 0.4→0.5）'},
    {'at': 0x1c, 'kind': 'aggregate', 'count': 10, 'label': '工程名称（b→e: 10→11 字符）'},
    {'at': 0x56, 'kind': 'double', 'value': 0.45, 'label': '城市基本风压（b vs d: 0.45→0.55）'},
]


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--pe', default=str(DEFAULT_PE))
    parser.add_argument('--root', action='append', default=[],
                        help='class whose chain is resolved (repeatable)')
    parser.add_argument('--json', default=str(DEFAULT_JSON))
    parser.add_argument('--cwx', default=None, help='cross-check a .cwx record against the chain')
    parser.add_argument('--cwx-type', default='HWKWallContext')
    args = parser.parse_args(argv[1:])

    pe = Path(args.pe)
    if not pe.is_file():
        raise SystemExit(f'PE not found: {pe}')
    all_bodies = bodies(disassemble(pe))
    parsed = {name: parse_body(insns) for name, insns in all_bodies.items()}

    by_class = {}
    for name, body in parsed.items():
        by_class.setdefault(class_of(name), []).append({'symbol': name, 'body': body})

    # a class may expose several Serialize overloads; prefer the virtual one as the chain node
    chosen, duplicates = {}, []
    for cls, entries in by_class.items():
        entries.sort(key=lambda e: ('' if '@UEAA' in e['symbol'] else '@MEAA' not in e['symbol'],
                                    e['symbol']))
        chosen[cls] = entries[0]
        if len(entries) > 1:
            duplicates.append({'class': cls, 'overloads': [e['symbol'] for e in entries]})

    roots = sorted(cls for cls, entry in chosen.items() if entry['body']['base'] is None)

    def layout(cls, seen=()):
        """Ordered field list of one class, with the base list spliced at the base-call position."""
        entry = chosen.get(cls)
        if entry is None:
            return [], [f'{cls}: no Serialize in this module']
        if cls in seen:
            return [], [f'cycle at {cls}']
        body = entry['body']
        own = [{'class': cls, 'offset': item['offset'], 'kind': item['kind'],
                'width': item['width'], 'slot': item['slot']}
               for item in body['writes'] if item['kind'] != 'version_tag']
        base_fields, problems = [], []
        if body['base'] is not None:
            base_fields, problems = layout(class_of(body['base']), seen + (cls,))
        # how many of this class's own writes are issued *before* the base call?
        base_position, staged = len(own), 0
        for _, mnemonic, operands in all_bodies[entry['symbol']]:
            if BASE_CALL.match(f'{mnemonic} {operands}') is not None:
                base_position = staged
                break
            if mnemonic.startswith(('mov', 'lea')) and body['this_register'] is not None:
                for offset, where in MEMBER.findall(operands):
                    del offset
                    if where == body['this_register'] and mnemonic.startswith('mov'):
                        staged += 1
        return own[:base_position] + base_fields + own[base_position:], problems

    report = {'pe': str(pe), 'pe_sha256': None, 'classes_with_serialize': len(chosen),
              'roots': roots, 'duplicate_overloads': duplicates, 'slots': {}, 'chains': {},
              'problems': []}

    report['pe_sha256'] = hashlib.sha256(pe.read_bytes()).hexdigest()

    slot_mnemonics = {}
    for entry in parsed.values():
        for item in entry['writes'] + entry['reads']:
            slot_mnemonics.setdefault(item['slot'], set()).add(item['from'])
    for slot, mnemonics in sorted(slot_mnemonics.items()):
        report['slots'][slot] = {'mnemonics': sorted(mnemonics),
                                 'kinds': sorted({KIND.get(m, 'unknown') for m in mnemonics}),
                                 'write_by_value': bool({'movsd', 'movl', 'movq', 'movzbl'} & mnemonics
                                                        and 'leaq' not in mnemonics)}

    for cls in args.root or roots:
        fields, problems = layout(cls)
        chain, node, seen = [], cls, set()
        while node and node not in seen:
            seen.add(node)
            chain.append(node)
            base = chosen.get(node, {}).get('body', {}).get('base')
            node = class_of(base) if base else None
        cursor, positions = 0, []
        for field in fields:
            positions.append({'class': field['class'], 'offset': field['offset'],
                              'kind': field['kind'], 'width': field['width'], 'at': cursor})
            cursor += field['width'] or 0
        report['chains'][cls] = {'chain': chain, 'fields': positions, 'problems': problems}
        print(f'== {cls}: chain {" <- ".join(chain)}   fields: {len(fields)}')
        for item in positions[:20]:
            print(f"   payload +0x{item['at']:03x}  {item['kind']:9s} w={item['width']}  "
                  f"{item['class']}+0x{item['offset']:x}")
        if len(positions) > 20:
            print(f'   ... {len(positions) - 20} more')
        report['problems'].extend(problems)
        for problem in problems:
            print('   PROBLEM', problem)

    if args.cwx:
        record = find_record(args.cwx, args.cwx_type)
        chain = report['chains'].get(args.cwx_type)
        if chain is None:
            raise SystemExit(f'--cwx needs --root {args.cwx_type}')
        walked, used = walk_payload(record, chain['fields'])
        report['cwx_check'] = {'file': record['path'], 'type': args.cwx_type,
                               'payload_offset': record['payload'], 'a_field': record['a'],
                               'fields_read': len(walked), 'bytes_read': used,
                               'fields': walked, 'anchors': []}
        print(f"\n== .cwx cross-check {record['path']} :: {args.cwx_type} "
              f"payload@{record['payload']:#x} A={record['a']} fields={len(walked)} bytes={used}")
        for item in walked[:16]:
            print(f"   +0x{item['at']:03x}  {item['kind']:9s} {item['class']}+0x{item['class_offset']:x}"
                  f" = {item['value']!r}")
        ok = True
        for anchor in CWX_ANCHORS:
            hit = next((f for f in walked if f['at'] == anchor['at']), None)
            good = False
            if hit is not None and hit['kind'] == anchor['kind']:
                if 'value' in anchor:
                    good = isinstance(hit['value'], float) and abs(hit['value'] - anchor['value']) < 1e-9
                else:
                    good = len(hit['value']) == anchor['count']
            ok = ok and good
            report['cwx_check']['anchors'].append({**anchor, 'found': hit, 'match': good})
            print(f"   {'OK ' if good else 'FAIL'} anchor +0x{anchor['at']:02x} {anchor['label']}"
                  f" -> {hit['kind'] + ' ' + repr(hit['value']) if hit else 'no field'}")
        report['cwx_check']['passed'] = ok
        if not ok:
            report['problems'].append('cwx cross-check failed')

    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n',
                               encoding='utf-8')
    print(f'\nclasses with Serialize: {len(chosen)}  roots: {len(roots)}  json: {args.json}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
