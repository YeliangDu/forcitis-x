#!/usr/bin/env python3
"""Bounded ordinary PE source-byte/Apple objdump audit; no target execution."""
import hashlib, importlib.util, json, re, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/baseline/b01/framework-slot'
SOURCE=ROOT/'evidence/baseline/extracted/msi/Binary.MSVBDPCADLL'
def audit():
 b=SOURCE.read_bytes(); u16=lambda p:struct.unpack_from('<H',b,p)[0]; u32=lambda p:struct.unpack_from('<I',b,p)[0]
 pe=u32(60); opt=pe+24; assert u16(opt)==0x10b
 base=u32(opt+28); sh=opt+u16(pe+20); sections=[]
 for i in range(u16(pe+6)):
  p=sh+i*40; vs,va,rs,rp=struct.unpack_from('<4I',b,p+8)
  sections.append(dict(name=b[p:p+8].rstrip(b'\0').decode(),virtual_size=vs,rva=va,raw_size=rs,raw_offset=rp,characteristics=u32(p+36)))
 def off(va):
  r=va-base
  for s in sections:
   if s['rva']<=r and r+4<=s['rva']+s['raw_size']:return s['raw_offset']+r-s['rva']
  raise ValueError('not raw-backed')
 slot=0x10043884; p=off(slot); initial=u32(p)
 rr,sz=struct.unpack_from('<II',b,opt+96+5*8); rel=[]; q=off(base+rr); end=q+sz
 while q<end:
  page,size=struct.unpack_from('<II',b,q); assert size>=8 and size%2==0 and q+size<=end
  for t in range(q+8,q+size,2):
   v=u16(t)
   if v>>12:rel.append(dict(entry_offset=t,type=v>>12,address=base+page+(v&4095)))
  q+=size
 assert q==end
 run=subprocess.run(['objdump','-d',str(SOURCE)],capture_output=True,text=True,check=True)
 instructions=[]
 for line in run.stdout.splitlines():
  m=re.match(r'^([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(.*)$',line)
  if m:
   va=int(m[1],16); raw=bytes.fromhex(m[2]); pos=off(va)
   assert b[pos:pos+len(raw)]==raw
   instructions.append(dict(address=va,file_offset=pos,hex=raw.hex(),text=m[3],raw_line=line))
 refs=[x for x in instructions if re.search(r'\b0x10043884\b',x['text'])]
 windows=[]
 for lo,hi in [(0x1003b09d,0x1003b0bb),(0x1003be6b,0x1003beeb),(0x1003b151,0x1003b220)]:
  windows.append(dict(start=lo,end_exclusive=hi,instructions=[x for x in instructions if lo<=x['address']<hi]))
 spec=importlib.util.spec_from_file_location('framework',ROOT/'scripts/audit-framework-static.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 prior,_=mod.audit(); imp=next(x for x in prior['imports'] if x['iat_address']==0x10046060)
 return dict(status='PARTIAL',evidence_type='ORDINARY_SOURCE_BYTES_AND_APPLE_OBJDUMP',source=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),image_base=base,sections=sections,slot=dict(address=slot,file_offset=p,hex=b[p:p+4].hex(),initial_value=initial,section=next(s for s in sections if s['rva']<=slot-base<s['rva']+s['raw_size']),initial_target_hex=b[off(initial):off(initial)+30].hex()),relocation_directory=dict(rva=rr,size=sz,non_absolute_entries=len(rel)),slot_relocation=[r for r in rel if r['address']==slot],operand_relocations=[r for r in rel if any(x['address']<=r['address']<x['address']+len(bytes.fromhex(x['hex'])) for x in refs)],slot_literal_references=refs,windows=windows,alternate_iat_declaration=imp,limits=['Static disassembly and literal references do not prove executed paths or exhaustive computed/aliased writes.','Helper 0x1003b151 semantics and branch selection remain unknown; no exact framework prerequisite inferred.','Source initial pointer and HIGHLOW relocations describe file/loader representation, not observed process state.','No original execution, REA native decompilation, solver or architecture decision.']),run.stdout
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);a,d=audit();(OUT/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');(OUT/'apple-objdump-disassembly.txt').write_text(d);print(json.dumps({k:a[k] for k in ['slot','slot_relocation','alternate_iat_declaration']}))
