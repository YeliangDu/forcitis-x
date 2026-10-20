#!/usr/bin/env python3
"""Bounded source audit; no target execution, no claim of complete CFG."""
import hashlib, importlib.util, json, re, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/baseline/b01/framework-properties'
SOURCE=ROOT/'evidence/baseline/extracted/msi/Binary.MSVBDPCADLL'
WINDOWS=[(0x10011449,0x10011574),(0x10011d52,0x10011dda),(0x10012234,0x1001227d),(0x100123a8,0x10012479),(0x100385b9,0x10038729),(0x10038bcc,0x10038c9a),(0x1003c78b,0x1003c797)]
def audit():
 spec=importlib.util.spec_from_file_location('static',ROOT/'scripts/audit-framework-static.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 prior,_=m.audit();b=SOURCE.read_bytes();pe=struct.unpack_from('<I',b,0x3c)[0];n=struct.unpack_from('<H',b,pe+6)[0];opt=pe+24;size=struct.unpack_from('<H',b,pe+20)[0];base=struct.unpack_from('<I',b,opt+28)[0]
 sections=[]
 for i in range(n):
  p=opt+size+i*40;vs,rva,rs,rp=struct.unpack_from('<IIII',b,p+8);sections.append((rva,rs,rp))
 def off(va):
  for r,s,p in sections:
   if r<=va-base<r+s:return p+va-base-r
  raise ValueError(hex(va))
 d=subprocess.run(['objdump','-d',str(SOURCE)],capture_output=True,text=True,check=True).stdout
 ins=[];edges=[];links=[];incoming=[];by={x['iat_address']:x for x in prior['imports']}
 for line in d.splitlines():
  match=re.match(r'^([0-9a-f]+): ([0-9a-f ]+)\t(.*)$',line)
  if not match:continue
  va=int(match[1],16)
  raw=bytes.fromhex(match[2])
  if raw[:1]==b'\xe8' and len(raw)==5:
   target=va+5+struct.unpack_from('<i',raw,1)[0]
   if target in (0x100385b9,0x10038bcc):
    p=off(va);assert b[p:p+5]==raw
    incoming.append(dict(address=va,target=target,file_offset=p,hex=raw.hex()))
  if not any(lo<=va<hi for lo,hi in WINDOWS):continue
  raw=bytes.fromhex(match[2]);p=off(va);assert b[p:p+len(raw)]==raw
  ins.append(dict(address=va,file_offset=p,hex=raw.hex(),text=match[3]))
  if raw[:2] in (b'\xff\x15',b'\xff\x25'):
   iat=struct.unpack_from('<I',raw,2)[0];links.append(dict(address=va,iat_address=iat,declaration=by.get(iat)))
  target=None;kind=None
  if raw[0] in (0xe8,0xe9):target=va+5+struct.unpack_from('<i',raw,1)[0];kind='call' if raw[0]==0xe8 else 'jump'
  elif raw[0]==0xeb or 0x70<=raw[0]<=0x7f:target=va+2+struct.unpack_from('<b',raw,1)[0];kind='short_branch'
  if len(raw)==6 and raw[0]==0x0f and 0x80<=raw[1]<=0x8f:target=va+6+struct.unpack_from('<i',raw,2)[0];kind='near_conditional_branch'
  if target is not None:edges.append(dict(address=va,target=target,kind=kind,target_in_windows=any(lo<=target<hi for lo,hi in WINDOWS)))
 literals=[]
 for va in (0x10001e98,0x10001eac,0x100021a4,0x10001e0c):
  p=off(va);end=p
  while b[end:end+2]!=b'\0\0':end+=2
  literals.append(dict(address=va,file_offset=p,hex=b[p:end+2].hex(),text=b[p:end].decode('utf-16le')))
 return dict(literals=literals,status='PARTIAL',evidence_type='ORDINARY_SOURCE_BYTES_AND_APPLE_OBJDUMP',source=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),ranges=[dict(start=lo,end_exclusive=hi,file_offset=off(lo),hex=b[off(lo):off(lo)+hi-lo].hex()) for lo,hi in WINDOWS],instructions=ins,relative_edges=edges,import_links=links,incoming_direct_calls=incoming,limits=['Windows selected by address and return instructions, not independently established complete function boundaries.','Property helper roles are candidates based on argument flow and ordinal thunks; API names, complete reachability and actual values remain unknown. Incoming references cover decoded E8 direct calls only, not indirect calls/data references.','No target execution, exceptional path coverage, runtime binding, buffer safety or ABI equivalence established.']),d
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);a,d=audit();(OUT/'audit.json').write_text(json.dumps(a,indent=2)+'\n');(OUT/'apple-objdump-disassembly.txt').write_text(d);print(json.dumps({'instructions':len(a['instructions']),'imports':a['import_links'],'edges':len(a['relative_edges'])}))
