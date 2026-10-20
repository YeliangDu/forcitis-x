#!/usr/bin/env python3
"""Bounded static helper/candidate audit. Does not execute target code."""
import hashlib, importlib.util, json, re, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/baseline/b01/framework-helper'
SOURCE=ROOT/'evidence/baseline/extracted/msi/Binary.MSVBDPCADLL'
def audit():
 spec=importlib.util.spec_from_file_location('prior',ROOT/'scripts/audit-framework-slot.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 prior,_=m.audit(); b=SOURCE.read_bytes();base=prior['image_base']
 def off(va):
  for s in prior['sections']:
   if s['rva']<=va-base<s['rva']+s['raw_size']:return s['raw_offset']+va-base-s['rva']
  raise ValueError(va)
 run=subprocess.run(['objdump','-d',str(SOURCE)],capture_output=True,text=True,check=True)
 ins=[]
 for line in run.stdout.splitlines():
  match=re.match(r'^([0-9a-f]+): ([0-9a-f ]+)\t(.*)$',line)
  if not match:continue
  va=int(match[1],16)
  if not (0x1003b151<=va<0x1003b196 or 0x1003be6b<=va<0x1003bfeb):continue
  raw=bytes.fromhex(match[2]);p=off(va);assert b[p:p+len(raw)]==raw
  ins.append(dict(address=va,file_offset=p,hex=raw.hex(),text=match[3]))
 assert ins[0]['address']==0x1003b151
 spec=importlib.util.spec_from_file_location('imports',ROOT/'scripts/audit-framework-static.py');im=importlib.util.module_from_spec(spec);spec.loader.exec_module(im);imports=im.audit()[0]['imports'];by={x['iat_address']:x for x in imports}
 links=[];edges=[]
 for x in ins:
  raw=bytes.fromhex(x['hex']);va=x['address']
  if raw[:2]==b'\xff\x15' or raw[:2]==b'\x8b\x3d':
   address=struct.unpack_from('<I',raw,2)[0];links.append(dict(instruction=x,iat_address=address,declaration=by.get(address),kind='direct_indirect_call' if raw[:2]==b'\xff\x15' else 'register_load'))
  if raw[0] in (0xe8,0xe9):edges.append(dict(address=va,kind='call' if raw[0]==0xe8 else 'jump',target=va+5+struct.unpack_from('<i',raw,1)[0]))
 p=off(0x1000b4c4);end=b.index(b'\0',p)
 return dict(status='PARTIAL',evidence_type='ORDINARY_SOURCE_BYTES_AND_APPLE_OBJDUMP',source=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),ranges=[dict(start=lo,end_exclusive=hi,file_offset=off(lo),hex=b[off(lo):off(lo)+hi-lo].hex()) for lo,hi in [(0x1003b151,0x1003b196),(0x1003be6b,0x1003bfeb)]],instructions=ins,import_links=links,relative_edges=edges,probe_literal=dict(address=0x1000b4c4,file_offset=p,hex=b[p:end+1].hex(),ascii=b[p:end].decode('ascii')),cache_bytes=[dict(address=v,section=next(s for s in prior['sections'] if s['rva']<=v-base<s['rva']+s['virtual_size']),file_offset=None,initial=None,representation='virtual tail beyond raw bytes; process value NOT_RUN') for v in [0x10045aac,0x10045aad]],register_call_sites=[x for x in ins if x['hex']=='ffd7'],limits=['Address windows are bounded static evidence, not independently established function boundaries or complete CFG.','Imported names are declarations; no process binding or Windows API return observed.','GetVersion sign-bit and environment probe static control/data flow does not establish exact framework prerequisite.','Candidate helpers, exceptional paths, conversion semantics, full side effects and runtime remain unknown.']),run.stdout
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);a,d=audit();(OUT/'audit.json').write_text(json.dumps(a,indent=2)+'\n');(OUT/'apple-objdump-disassembly.txt').write_text(d);print(json.dumps({'instructions':len(a['instructions']),'links':a['import_links'],'literal':a['probe_literal'],'cache':a['cache_bytes']}))
