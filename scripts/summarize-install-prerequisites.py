#!/usr/bin/env python3
"""B01-03 bounded retained-evidence graph. Never executes installer code."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'evidence/stages/B01/B01-03'
INPUTS = [
 'evidence/baseline/b01/msi-decoded/tables.json',
 'evidence/baseline/b01/framework-static/apple-objdump-disassembly.txt',
 'evidence/baseline/b01/installer-resources/decoded.json',
 'evidence/baseline/b01/launch-search/audit.json',
 'evidence/baseline/b01/framework-properties/audit.json',
 'evidence/baseline/b01/framework-properties/flow-gaps.json',
 'evidence/scheduler-reviews/20261018T110100Z/review.md',
 'evidence/baseline/extracted/msi/Binary.MSVBDPCADLL',
 'evidence/scheduler/20261018T124146979850Z/stage-assignment.json',
 'evidence/scheduler/20261018T124146979850Z/rea-preflight/version-check.json',
]
# Explicit lexical envelopes, not inferred whole-function boundaries.
WINDOWS = [('CheckFX envelope', 0x10011359, 0x100124bf),
 ('condition callback envelope', 0x100124bf, 0x100129ce),
 ('VsdLaunchConditions envelope', 0x10016c3e, 0x10016ea4)]
def load(p):
 return json.loads((ROOT / p).read_text())
def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
def collect():
 frozen = {p: sha(ROOT / p) for p in INPUTS}
 source = (ROOT / INPUTS[7]).read_bytes()
 pe = struct.unpack_from('<I', source, 0x3c)[0]
 n = struct.unpack_from('<H', source, pe+6)[0]
 opt = pe+24
 base = struct.unpack_from('<I', source, opt+28)[0]
 section_start = opt + struct.unpack_from('<H', source, pe+20)[0]
 sections = [struct.unpack_from('<IIII', source, section_start+i*40+8) for i in range(n)]
 def offset(va):
  for _, rva, size, raw in sections:
   if rva <= va-base < rva+size:
    return raw+va-base-rva
  raise ValueError(f'VA outside file-backed section: {va:x}')
 def wide(va):
  p = offset(va); e = p
  while source[e:e+2] != b'\0\0':
   if e+2 > len(source): raise ValueError('unterminated literal')
   e += 2
  return {'address': va, 'file_offset': p, 'text': source[p:e].decode('utf-16le'), 'hex': source[p:e+2].hex()}
 decoded = []
 for line in (ROOT / INPUTS[1]).read_text().splitlines():
  m = re.match(r'^([0-9a-f]+): ([0-9a-f ]+)\t(.*)$', line)
  if not m: continue
  va = int(m[1], 16)
  if not any(lo <= va < hi for _, lo, hi in WINDOWS): continue
  raw = bytes.fromhex(m[2]); p = offset(va)
  if source[p:p+len(raw)] != raw: raise ValueError(f'source mismatch at {va:x}')
  decoded.append({'address': va, 'file_offset': p, 'hex': raw.hex(), 'text': m[3]})
 by = {i['address']: i for i in decoded}
 graphs = []
 for name, lo, hi in WINDOWS:
  ins = [i for i in decoded if lo <= i['address'] < hi]
  cursor = lo
  for i in ins:
   if i['address'] != cursor: raise ValueError(f'decode gap {cursor:x}')
   cursor += len(bytes.fromhex(i['hex']))
  if cursor != hi: raise ValueError(f'end mismatch {cursor:x}/{hi:x}')
  edges = []; boundaries = []
  def edge(va, target, kind):
   edges.append({'from': va, 'to': target, 'kind': kind, 'target_in_envelope': target in by and lo <= target < hi})
  for i in ins:
   va = i['address']; raw = bytes.fromhex(i['hex']); nxt = va+len(raw)
   if raw[0] in (0xc2, 0xc3, 0xcc):
    boundaries.append({'address': va, 'kind': 'ret_or_trap', 'text': i['text']}); continue
   if raw[0] in (0xe8, 0xe9):
    edge(va, nxt+struct.unpack_from('<i', raw, 1)[0], 'direct_call' if raw[0]==0xe8 else 'jump')
    if raw[0]==0xe9: continue
   elif raw[0]==0xeb:
    edge(va, nxt+struct.unpack_from('<b', raw, 1)[0], 'jump'); continue
   elif 0x70 <= raw[0] <= 0x7f:
    edge(va, nxt+struct.unpack_from('<b', raw, 1)[0], 'conditional')
   elif raw[:1]==b'\x0f' and 0x80 <= raw[1] <= 0x8f:
    edge(va, nxt+struct.unpack_from('<i', raw, 2)[0], 'conditional')
   elif raw[0]==0xff and ((raw[1] >> 3) & 7) in (2, 3, 4, 5):
    boundaries.append({'address': va, 'kind': 'unresolved_indirect_transfer', 'text': i['text']})
    if ((raw[1] >> 3) & 7) in (4,5): continue
   edge(va, nxt, 'lexical_fallthrough_candidate')
  graphs.append({'name': name, 'start': lo, 'end_exclusive': hi, 'instructions': ins, 'edges': edges, 'boundaries': boundaries})
 tables = load(INPUTS[0])['tables']
 launch = load(INPUTS[3])
 sequences = {k: sorted(v, key=lambda r:r['Sequence']) for k,v in tables.items() if k.endswith('Sequence')}
 actions = tables['CustomAction']
 action_links = [{'declaration': a, 'sequence_sites': [{'table': k, **r} for k,v in sequences.items() for r in v if r['Action']==a['Action']]} for a in actions]
 exports = load(INPUTS[2])['exports']['entries']
 flags = [i for i in graphs[0]['instructions'] if '-0x569(%ebp)' in i['text']]
 # Query SQL and callback passed by address; keep literals distinct from executed effects.
 literal_vas = sorted({int(m[1],16) for i in graphs[2]['instructions'] for m in [re.search(r'\$0x(100022c0|10001228)', i['text'])] if m})
 return {'status': 'PARTIAL', 'evidence_type': 'RETAINED_DISASSEMBLY_SOURCE_BYTE_CHECK_AND_MSI_JOIN',
  'inputs_sha256': frozen, 'ranges': graphs, 'flag_references': flags,
  'sequences': sequences, 'custom_action_links': action_links,
  'framework_properties': [r for r in tables['Property'] if r['Property'].startswith('VSD')],
  'launch_condition_rows': launch['tables']['_VsdLaunchCondition'],
  'export_links': [r for r in exports if r['name'] in ('CheckFX','VsdLaunchConditions')],
  'consumer_literals': [wide(va) for va in literal_vas],
  'limits': ['Envelopes are lexical, not certified function boundaries or complete CFGs.',
   'Fallthrough after a call is a candidate only: nonreturning calls, exceptions and unwinding are unresolved.',
   'Indirect calls, callback invocation and condition evaluation are not established by argument addresses.',
   'Sequence rows are declarations, not successful installation traces. No installer or business code executed.']}
def main():
 parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, default=DEFAULT); args = parser.parse_args()
 args.out.mkdir(parents=True, exist_ok=True)
 result = collect()
 (args.out/'control-flow.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
 print(json.dumps({'status': result['status'], 'instructions': sum(len(g['instructions']) for g in result['ranges']),
  'edges': sum(len(g['edges']) for g in result['ranges']), 'flag_references': len(result['flag_references']),
  'consumer_literals': result['consumer_literals']}, ensure_ascii=False))
if __name__ == '__main__': main()
