#!/usr/bin/env python3
"""Compare two `.cwx` files byte-by-byte and interpret difference runs as fields.

実測 (2026-10-19, `run-20261019-cwx`):
  b.cwx -> c.cwx : 1 run, offset 0x5E, double 0.4 -> 0.5   (城市基本雪压)
  c.cwx -> d.cwx : 1 run, offset 0xA0, double 0.45 -> 0.55 (城市基本风压)

Usage:
  python3 scripts/cwx-diff-fields.py old.cwx new.cwx [--json out.json]
"""
import argparse
import json
import math
import struct
import sys
from pathlib import Path


def read(path):
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise SystemExit(f'cannot read {path}: {exc}') from exc


def diff_runs(old, new):
    """Return [(offset, length)] of differing byte runs, plus the size delta."""
    runs = []
    i = 0
    span = min(len(old), len(new))
    while i < span:
        if old[i] != new[i]:
            j = i
            while j < span and old[j] != new[j]:
                j += 1
            runs.append((i, j - i))
            i = j
        else:
            i += 1
    return runs, len(new) - len(old)


def as_double(buf, offset):
    """Decode an 8-byte little-endian double starting at offset, or None."""
    if offset + 8 > len(buf):
        return None
    value = struct.unpack_from('<d', buf, offset)[0]
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def classify(old, new, offset, length):
    """Best-effort interpretation of one difference run."""
    if length <= 8:
        old_double = as_double(old, offset)
        new_double = as_double(new, offset)
        if old_double is not None and new_double is not None:
            return {'kind': 'double', 'old': old_double, 'new': new_double}
    if length <= 4:
        old_int = struct.unpack_from('<i', old, offset)[0]
        new_int = struct.unpack_from('<i', new, offset)[0]
        return {'kind': 'int32-or-partial', 'old': old_int, 'new': new_int}
    return {'kind': 'blob', 'old_hex': old[offset:offset + length].hex(), 'new_hex': new[offset:offset + length].hex()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('old')
    ap.add_argument('new')
    ap.add_argument('--json')
    ap.add_argument('--max-print', type=int, default=20, help='cap printed diff runs (default 20)')
    args = ap.parse_args()
    old = read(args.old)
    new = read(args.new)
    runs, delta = diff_runs(old, new)
    rows = []
    for offset, length in runs:
        rows.append({'offset': offset, 'length': length, **classify(old, new, offset, length)})
    report = {
        'old': str(args.old),
        'new': str(args.new),
        'old_size': len(old),
        'new_size': len(new),
        'size_delta': delta,
        'run_count': len(rows),
        'differing_bytes': sum(length for _, length in runs),
        'runs': rows,
    }
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f'{args.old} -> {args.new}: {len(old)} -> {len(new)} bytes, {len(rows)} diff run(s)')
    for row in rows[:args.max_print]:
        if row['kind'] == 'double':
            print(f"  off={row['offset']:#08x} len={row['length']} double {row['old']!r} -> {row['new']!r}")
        elif row['kind'] == 'blob':
            print(f"  off={row['offset']:#08x} len={row['length']} blob {row['old_hex'][:48]} -> {row['new_hex'][:48]}")
        else:
            print(f"  off={row['offset']:#08x} len={row['length']} {row['kind']} {row['old']} -> {row['new']}")
    if len(rows) > args.max_print:
        print(f'  ... {len(rows) - args.max_print} more run(s); full list in --json output')


if __name__ == '__main__':
    sys.exit(main())
