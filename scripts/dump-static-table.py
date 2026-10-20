"""Dump static lookup tables referenced by a node's decompiled pseudo-code.

The lookup nodes (GetNg / GetSDr / GetSMr ...) read .rdata blobs (DAT_1805xxxxx) through a
shared interpolator (FUN_180299d50). This tool maps those virtual addresses to file offsets
in the shipped PE and prints the raw region as float32/float64 plus a search for anchor
values printed by the original (e.g. eta=0.998228 for theta=5.221494).

Usage:
  python3 scripts/dump-static-table.py --pe <file> --va 0x180543bd0 [--len 512]
  python3 scripts/dump-static-table.py --pe <file> --va 0x180543bd0 --find 0.998228,0.00406
"""
import argparse
import struct
import sys
from pathlib import Path

IMAGE_BASE_DEFAULT = 0x180000000


def read_pe(path):
    data = Path(path).read_bytes()
    if data[:2] != b'MZ':
        raise SystemExit(f'{path} is not a PE file')
    pe_off = struct.unpack_from('<I', data, 0x3C)[0]
    if data[pe_off:pe_off + 4] != b'PE\0\0':
        raise SystemExit('missing PE signature')
    coff = pe_off + 4
    n_sections = struct.unpack_from('<H', data, coff + 2)[0]
    opt_size = struct.unpack_from('<H', data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from('<H', data, opt)[0]
    image_base = (struct.unpack_from('<Q', data, opt + 24)[0] if magic == 0x20B
                  else struct.unpack_from('<I', data, opt + 28)[0])
    sec = opt + opt_size
    sections = []
    for i in range(n_sections):
        off = sec + i * 40
        name = data[off:off + 8].rstrip(b'\0').decode('ascii', 'replace')
        vsize, vaddr, rawsize, rawptr = struct.unpack_from('<IIII', data, off + 8)
        sections.append({'name': name, 'vsize': vsize, 'vaddr': vaddr,
                         'rawsize': rawsize, 'rawptr': rawptr})
    return data, image_base, sections


def va_to_offset(image_base, sections, va):
    rva = va - image_base
    for s in sections:
        if s['vaddr'] <= rva < s['vaddr'] + max(s['vsize'], s['rawsize']):
            delta = rva - s['vaddr']
            if delta >= s['rawsize']:
                raise SystemExit(f'VA {va:#x} falls in {s["name"]} zero-fill beyond raw data')
            return s, s['rawptr'] + delta
    raise SystemExit(f'VA {va:#x} is not inside any section')


def parse_anchors(text):
    """Parse --find values, refusing anything that is not a number."""
    values = []
    for token in [t.strip() for t in text.split(',') if t.strip()]:
        try:
            values.append(float(token))
        except ValueError as error:
            raise SystemExit(f'anchor {token!r} is not a number: {error}') from error
    return values


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--pe', required=True)
    ap.add_argument('--va', required=True, help='hex virtual address, e.g. 0x180543bd0')
    ap.add_argument('--len', type=int, default=256)
    ap.add_argument('--find', default='', help='comma separated anchor values to search')
    ap.add_argument('--json', default='')
    args = ap.parse_args(argv[1:])

    data, image_base, sections = read_pe(args.pe)
    va = int(args.va, 16)
    section, offset = va_to_offset(image_base, sections, va)
    blob = data[offset:offset + args.len]

    print(f'PE       {args.pe}')
    print(f'imagebase {image_base:#x}')
    section_list = ', '.join(f"{s['name']}@{s['vaddr']:#x}" for s in sections)
    print('sections  ' + section_list)
    print(f'VA {va:#x} -> section {section["name"]} file offset {offset:#x}, {len(blob)} bytes')

    f64 = struct.unpack_from('<' + 'd' * (len(blob) // 8), blob, 0)
    f32 = struct.unpack_from('<' + 'f' * (len(blob) // 4), blob, 0)
    print('float64[0:8] ' + ', '.join(f'{v:.10g}' for v in f64[:8]))
    print('float32[0:8] ' + ', '.join(f'{v:.8g}' for v in f32[:8]))

    hits = []
    for target64 in parse_anchors(args.find):
        target32 = struct.unpack('<f', struct.pack('<f', target64))[0]
        for i, value in enumerate(f32):
            if abs(value - target32) <= max(abs(target32) * 1e-6, 1e-12):
                hits.append({'anchor': target64, 'type': 'float32', 'index': i,
                             'va': va + i * 4})
        for i, value in enumerate(f64):
            if abs(value - target64) <= max(abs(target64) * 1e-9, 1e-15):
                hits.append({'anchor': target64, 'type': 'float64', 'index': i,
                             'va': va + i * 8})
    for hit in hits:
        print(f"HIT {hit['anchor']} as {hit['type']} at index {hit['index']} "
              f"(va {hit['va']:#x})")
    if args.json:
        Path(args.json).write_text(
            __import__('json').dumps(
                {'pe': args.pe, 'va': va, 'section': section['name'], 'offset': offset,
                 'float64': f64[:32], 'float32': f32[:32], 'hits': hits},
                ensure_ascii=False, indent=1), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
