#!/usr/bin/env python3
"""Validate the `.cwx` container framing and list record tokens / class inventory.

実測 (2026-10-19):
  header  = ff fe | ff | u8 nameLen | UTF-16 product name | u32 version(2) | u32 payloadTotal
            payloadTotal == fileSize - 40 (checked on every sample below)
  record  = u16 (0x8000|len(nameInChars)) | UTF-16 name | u32 A | payload

Payload length is NOT stored in any field decoded so far, so record boundaries are found by
scanning for the next plausible tag (this script does exactly that) and not by arithmetic.
A is NOT a payload length and NOT a per-class constant: in the same build the same class
carries A=773 in a.cwx and A=1058 in b.cwx, while many different classes share one A value
within a file (a: 773 / 399 / 6; b: 1058 / 597 / 6). Its meaning is still unknown.

Field widths therefore have to be measured by differential saves
(see scripts/cwx-diff-fields.py).

Usage:
  python3 scripts/cwx-frame.py FILE [FILE...] [--json out.json]
"""
import argparse
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

NAME = re.compile(r'HWK[A-Za-z0-9_]{1,60}')
MIN_RECORD_OFFSET = 0x28


def read(path):
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise SystemExit(f'cannot read {path}: {exc}') from exc


def parse_header(data):
    """Return header fields or raise ValueError when the framing does not match."""
    if len(data) < MIN_RECORD_OFFSET:
        raise ValueError('file shorter than minimum header')
    if data[0:2] != b'\xff\xfe':
        raise ValueError('missing UTF-16LE BOM')
    name_len = data[3]
    name_end = 4 + name_len * 2
    if name_end + 8 > len(data):
        raise ValueError('product name overruns file')
    try:
        product = data[4:name_end].decode('utf-16-le')
    except UnicodeDecodeError as exc:
        raise ValueError(f'product name not UTF-16LE: {exc}') from exc
    version, total = struct.unpack_from('<II', data, name_end)
    return {
        'marker': data[2],
        'name_length': name_len,
        'product': product,
        'version': version,
        'declared_payload': total,
        'expected_payload': len(data) - (name_end + 8),
        'consistent': total == len(data) - (name_end + 8),
        'record_stream_offset': name_end + 8,
    }


def tokens(data, start):
    """Yield (offset, name, A, B) for every plausible record tag + name + 2x u32."""
    out = []
    i = start
    span = len(data)
    while i + 6 <= span:
        tag = struct.unpack_from('<H', data, i)[0]
        length = tag & 0x7fff
        if (tag & 0x8000) and 3 <= length <= 64:
            body = i + 2
            if body + 2 * length + 8 <= span:
                try:
                    name = data[body:body + 2 * length].decode('utf-16-le')
                except UnicodeDecodeError:
                    name = None
                if name and NAME.fullmatch(name):
                    a, b = struct.unpack_from('<II', data, body + 2 * length)
                    out.append((i, name, a, b))
                    i = body + 2 * length + 8
                    continue
        i += 1
    return out


def summarise(path):
    data = read(path)
    info = {'file': str(path), 'size': len(data)}
    try:
        info['header'] = parse_header(data)
    except ValueError as exc:
        info['header_error'] = str(exc)
        return info
    rows = tokens(data, info['header']['record_stream_offset'])
    instances = Counter(name for _, name, _, _ in rows)
    per_class_a = {}
    for _, name, a, _ in rows:
        per_class_a.setdefault(name, set()).add(a)
    info['token_count'] = len(rows)
    info['class_count'] = len(instances)
    info['classes'] = dict(sorted(instances.items()))
    info['single_value_a'] = all(len(v) == 1 for v in per_class_a.values())
    info['a_by_class'] = {k: sorted(v) for k, v in sorted(per_class_a.items())}
    info['a_values'] = sorted({a for _, _, a, _ in rows})
    info['a_shared_across_classes'] = any(len(v) > 1 for v in per_class_a.values())
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--json')
    args = ap.parse_args()
    reports = [summarise(path) for path in args.files]
    if args.json:
        Path(args.json).write_text(json.dumps(reports, indent=2, ensure_ascii=False) + '\n')
    for report in reports:
        print(f"=== {report['file']} ({report['size']} bytes)")
        header = report.get('header')
        if not header:
            print(f"  header ERROR: {report.get('header_error')}")
            continue
        print(f"  product={header['product']!r} version={header['version']} "
              f"payload={header['declared_payload']} consistent={header['consistent']}")
        print(f"  tokens={report['token_count']} classes={report['class_count']} "
              f"a_values={report['a_values']} shared_a={report['a_shared_across_classes']}")
    if len(reports) == 2 and all('classes' in r for r in reports):
        left, right = reports
        only_left = sorted(set(left['classes']) - set(right['classes']))
        only_right = sorted(set(right['classes']) - set(left['classes']))
        print(f'--- class diff {left["file"]} -> {right["file"]}')
        print(f'  only-left={only_left}')
        print(f'  only-right={only_right}')


if __name__ == '__main__':
    sys.exit(main())
