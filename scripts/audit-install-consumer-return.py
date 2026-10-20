#!/usr/bin/env python3
"""Bounded B01-03 callback/epilogue source audit; never executes target."""
import argparse
import importlib.util
import json
import struct
from pathlib import Path
spec = importlib.util.spec_from_file_location('base', Path(__file__).with_name('summarize-install-prerequisites.py'))
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
EXTRA = [('consumer traversal envelope', 0x100379dc, 0x10037be7),
         ('condition import thunk', 0x1003c779, 0x1003c77f),
         ('shared epilogue envelope', 0x1001a8cf, 0x1001a917)]
def collect():
 old = base.WINDOWS
 try:
  base.WINDOWS = old + EXTRA
  data = base.collect()
 finally: base.WINDOWS = old
 # F2 is an instruction prefix, not an opcode. Preserve the old graph as input,
 # replace candidate fallthrough at the prefixed transfers with decoded edges.
 for graph in data['ranges']:
  for ins in graph['instructions']:
   raw = bytes.fromhex(ins['hex']); va = ins['address']; nxt = va + len(raw)
   if raw[:1] != b'\xf2': continue
   body = raw[1:]
   if body[0] not in (0xe8, 0xe9, 0x75, 0xc3):
    raise ValueError(f'unhandled prefixed transfer {va:x}')
   graph['edges'] = [e for e in graph['edges'] if e['from'] != va]
   if body[0] == 0xc3:
    graph['boundaries'].append({'address': va, 'kind': 'prefixed_ret', 'text': ins['text']})
   else:
    delta = struct.unpack('<b' if body[0] == 0x75 else '<i', body[1:])[0]
    graph['edges'].append({'from': va, 'to': nxt+delta,
      'kind': {0xe8:'direct_call',0xe9:'jump',0x75:'conditional'}[body[0]],
      'target_in_envelope': graph['start'] <= nxt+delta < graph['end_exclusive']})
    if body[0] != 0xe9:
     graph['edges'].append({'from':va,'to':nxt,'kind':'lexical_fallthrough_candidate',
       'target_in_envelope':graph['start'] <= nxt < graph['end_exclusive']})
 source = (base.ROOT/base.INPUTS[7]).read_bytes()
 pe = struct.unpack_from('<I', source, 0x3c)[0]; opt = pe+24
 image = struct.unpack_from('<I',source,opt+28)[0]
 sec = opt + struct.unpack_from('<H',source,pe+20)[0]
 sections = [struct.unpack_from('<IIII',source,sec+i*40+8) for i in range(struct.unpack_from('<H',source,pe+6)[0])]
 def off(rva):
  for _, start, size, raw in sections:
   if start <= rva < start+size: return raw+rva-start
  raise ValueError('RVA outside source')
 def cstr(rva):
  p = off(rva); return source[p:source.index(b'\0',p)].decode('ascii')
 imports = []; rva = struct.unpack_from('<I',source,opt+104)[0]; p=off(rva)
 while source[p:p+20] != bytes(20):
  original,_,_,name,iat = struct.unpack_from('<IIIII',source,p)
  n=0
  while True:
   at=off((original or iat)+n*4); value=struct.unpack_from('<I',source,at)[0]
   if not value: break
   slot=image+iat+n*4
   if slot == 0x10046268:
    imports.append({'iat_va':slot,'descriptor_file_offset':p,'lookup_file_offset':at,
     'lookup_value':value,'dll':cstr(name),'ordinal':value & 0xffff if value & 0x80000000 else None,
     'name':None if value & 0x80000000 else cstr(value+2)})
   n+=1
  p+=20
 if len(imports)!=1: raise ValueError('condition import identity missing or ambiguous')
 data['condition_import'] = imports[0]
 data['status']='BLOCKED'
 data['limits'].append('Callback dispatch/loop and prefixed epilogue are local source facts; exception recovery, setup binding, CheckFX producer paths and HWKInstallDo remain unclosed.')
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=True); d=collect()
 (a.out/'consumer-return.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':d['status'],'instructions':sum(len(g['instructions']) for g in d['ranges']),'condition_import':d['condition_import']}))
