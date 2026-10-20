#!/usr/bin/env python3
"""P1 s4: try to consume a BREP Arc body with the recovered field order (closure test).

Field order comes from build-serialize-chains.py --root HWKCADGraphArc:
  int32, aggregate, int32, double, int32, double, double, double, aggregate, aggregate, aggregate
An aggregate is assumed to be `u32 count` + count*element; the element width is unknown, so each
record is tried with the candidate widths {1, 2, 4, 8, 4+2*len} and the run that ends exactly at the
body end wins. Prints the winning combination per record; exit 0 if every record closes.

Output: evidence/poc/P1/brep-closure.json
"""
import base64
import importlib.util
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location('decode_brep', ROOT / 'scripts/poc/decode-brep.py')
if _spec is None or _spec.loader is None:
    raise SystemExit('cannot load scripts/poc/decode-brep.py')
_brep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_brep)
HEADER = 16  # u32 version + u32 ordinal + 8 zero bytes, before the field payload
IN = ROOT / 'evidence/poc/P1/input/gallery.json'
OUT = ROOT / 'evidence/poc/P1/brep-closure.json'
LAYOUT = ['int32', 'agg', 'int32', 'double', 'int32', 'double', 'double', 'double',
          'agg', 'agg', 'agg']
WIDTH = {'int32': 4, 'double': 8}


def walk(body, widths):
    """Return end offset if the layout consumes `body` exactly with the given aggregate widths."""
    cursor = 0
    for kind in LAYOUT:
        if kind == 'agg':
            if cursor + 4 > len(body):
                return None
            count = struct.unpack_from('<I', body, cursor)[0]
            cursor += 4
            width = widths.pop(0) if widths else 8
            if width is None:
                return None
            step = width if isinstance(width, int) else width
            if count > 100000:
                return None
            cursor += count * step if isinstance(step, int) else 0
        else:
            cursor += WIDTH[kind]
        if cursor > len(body):
            return None
    return cursor if cursor == len(body) else None


def main():
    if not IN.is_file():
        print('BLOCKED: gallery.json missing')
        return 2
    rows = json.loads(IN.read_text(encoding='utf-8'))
    report, closed = [], 0
    for row in rows:
        blob = base64.b64decode(row['BREP'])
        recs = _brep.find_records(blob)
        arcs = [r for r in recs if r['name'].endswith('HWKCADGraphArc')]
        if not arcs:
            report.append({'gallery_iid': row['IID'], 'status': 'no-arc'})
            continue
        arc = arcs[-1]
        body = blob[arc['payload'] + HEADER:arc['payload'] + arc['payload_len']]
        hit = None
        for w0 in (1, 2, 4, 8):
            for w1 in (1, 2, 4, 8):
                for w2 in (1, 2, 4, 8):
                    end = walk(body, [w0, w1, w2])
                    if end is not None:
                        hit = {'widths': [w0, w1, w2], 'end': end}
                        break
                if hit:
                    break
            if hit:
                break
        closed += 1 if hit else 0
        report.append({'gallery_iid': row['IID'], 'name': row.get('name'), 'body_bytes': len(body),
                       'closed': bool(hit), 'widths': (hit or {}).get('widths'),
                       'end': (hit or {}).get('end')})
        print(f"{row['IID']:>5} {row.get('name',''):<12} body={len(body):>6} "
              f"{'CLOSED widths=' + str(hit['widths']) if hit else 'NOT CLOSED'}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'layout': LAYOUT, 'rows': report}, ensure_ascii=False, indent=1) + '\n',
                   encoding='utf-8')
    print(f'closed {closed}/{len(report)}  → {OUT.relative_to(ROOT)}')
    return 0 if closed == len(report) else 1


if __name__ == '__main__':
    sys.exit(main())
