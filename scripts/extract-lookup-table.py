"""Decode the piecewise lookup tables that the lookup nodes interpolate.

Layout recovered from the shipped PE (evidence: the blobs and the anchors below):

    [int64 count][count × float64]      one axis, followed by the value axis in the same form

The interpolator (FUN_180299d50) is shared by GetNg / GetSDr / GetSMr; the node code picks a
pair of blob addresses per branch. This tool parses a pair, interpolates, and checks the
result against a value the original itself printed. The coefficient pairs of GetSDr / GetSMr
are decoded by `extract-coefficient-tables.py`; this tool owns the η tables only.

Usage: python3 scripts/extract-lookup-table.py [--json <out>]
"""
import json
import struct
import sys
from pathlib import Path

PE = Path('evidence/baseline/extracted/cab/_1D7374B2004D4FE39A79BCDFC9340FB8')
OUT = Path('migration_workspace/raw/lookup-tables.json')
IMAGE_BASE = 0x180000000

# (label, x axis VA, y axis VA) — addresses taken verbatim from the GetNg pseudo-code branches
TABLES = [
    ('eta.default', 0x180543bd0, 0x180544b20),   # θ<=10.99999 or >=15.00001, 1-arg path
    ('eta.wide', 0x180543cd0, 0x180543d60),      # 11 < θ < 15 branch
    ('eta.narrow', 0x180543bd0, 0x180543c50),    # θ≈11 boundary branch
]

ANCHORS = [
    # (label, table, x value, expected y, tolerance) — expected y printed by the original
    ('η(θ=5.221494)', 'eta.default', 5.221494, 0.998228, 5e-7),
    # the strength section prints θ and η for both panes, so the η table has a second anchor
    ('η(θ1=5.894204)', 'eta.default', 5.894204, 0.992846, 5e-7),
    ('η(θ2=5.358368)', 'eta.default', 5.358368, 0.997133, 5e-7),
]


def sections(data):
    pe_off = struct.unpack_from('<I', data, 0x3C)[0]
    coff = pe_off + 4
    n = struct.unpack_from('<H', data, coff + 2)[0]
    opt_size = struct.unpack_from('<H', data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from('<H', data, opt)[0]
    base = (struct.unpack_from('<Q', data, opt + 24)[0] if magic == 0x20B
            else struct.unpack_from('<I', data, opt + 28)[0])
    out = []
    sec = opt + opt_size
    for i in range(n):
        off = sec + i * 40
        name = data[off:off + 8].rstrip(b'\0').decode('ascii', 'replace')
        vsize, vaddr, rawsize, rawptr = struct.unpack_from('<IIII', data, off + 8)
        out.append((name, vaddr, vsize, rawptr, rawsize))
    return base, out


def read_axis(data, secs, base, va):
    for name, vaddr, vsize, rawptr, rawsize in secs:
        rva = va - base
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            delta = rva - vaddr
            if delta >= rawsize:
                raise SystemExit(f'VA {va:#x} in {name} is zero-fill, no file bytes')
            offset = rawptr + delta
            # the element count is stored as a double, not an integer (0x402c... == 14.0)
            try:
                raw_count = struct.unpack_from('<d', data, offset)[0]
            except struct.error as error:
                raise SystemExit(f'VA {va:#x}: cannot read element count ({error})') from error
            try:
                count = int(raw_count)
            except (ValueError, OverflowError) as error:
                raise SystemExit(f'VA {va:#x}: element count is not an integer ({error})') from error
            if not (0 < count <= 64) or count != raw_count:
                raise SystemExit(f'VA {va:#x}: implausible element count {raw_count}')
            raw_count = None  # only the integer form is used below
            try:
                values = struct.unpack_from('<' + 'd' * count, data, offset + 8)
            except struct.error as error:
                raise SystemExit(f'VA {va:#x}: table runs past the end of the file ({error})') from error
            return {'va': va, 'section': name, 'offset': offset, 'count': count,
                    'values': list(values)}
    raise SystemExit(f'VA {va:#x} not inside any section')


def interpolate(xs, ys, x):
    if x <= xs[0]:
        return ys[0], 'clamp-low'
    if x >= xs[-1]:
        return ys[-1], 'clamp-high'
    for i in range(1, len(xs)):
        if x <= xs[i]:
            span = xs[i] - xs[i - 1]
            t = 0.0 if span == 0 else (x - xs[i - 1]) / span
            return ys[i - 1] + t * (ys[i] - ys[i - 1]), f'between {xs[i - 1]:g} and {xs[i]:g}'
    return ys[-1], 'clamp-high'


def main(argv):
    data = PE.read_bytes()
    base, secs = sections(data)
    if base != IMAGE_BASE:
        raise SystemExit(f'unexpected image base {base:#x}')
    tables, report = {}, {'pe': str(PE), 'image_base': base, 'tables': {}, 'anchors': []}
    for label, x_va, y_va in TABLES:
        xs = read_axis(data, secs, base, x_va)
        ys = read_axis(data, secs, base, y_va)
        if xs['count'] != ys['count']:
            raise SystemExit(f'{label}: x count {xs["count"]} != y count {ys["count"]}')
        tables[label] = {'x': xs, 'y': ys}
        report['tables'][label] = {'x_va': x_va, 'y_va': y_va, 'count': xs['count'],
                                   'x': xs['values'], 'y': ys['values']}
    ok = True
    for label, table, x, expected, tol in ANCHORS:
        entry = tables[table]
        value, how = interpolate(entry['x']['values'], entry['y']['values'], x)
        good = abs(value - expected) <= tol
        ok = ok and good
        report['anchors'].append({'label': label, 'table': table, 'x': x,
                                  'expected': expected, 'computed': value,
                                  'rule': how, 'tolerance': tol, 'match': good})
        print(f"{'OK ' if good else 'FAIL'} {label:18s} table={table:12s} x={x:<10g} "
              f"computed={value:.9f} expected={expected:<10} ({how})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'tables': len(tables), 'anchors': len(ANCHORS), 'all_matched': ok}))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
