#!/usr/bin/env python3
"""Observed PE32 literal/import references; ordinary source bytes + Apple objdump."""
import hashlib, importlib.util, json, re, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/baseline/b01/framework-static'
SOURCE=ROOT/'evidence/baseline/extracted/msi/Binary.MSVBDPCADLL'
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def audit():
 b=SOURCE.read_bytes(); pe=struct.unpack_from('<I',b,60)[0]; opt=pe+24
 if struct.unpack_from('<H',b,opt)[0]!=0x10b: raise ValueError('requires observed PE32')
 base=struct.unpack_from('<I',b,opt+28)[0]; n=struct.unpack_from('<H',b,pe+6)[0]; sh=opt+struct.unpack_from('<H',b,pe+20)[0]
 sections=[]
 for i in range(n):
  p=sh+40*i; vs,va,size,ptr=struct.unpack_from('<4I',b,p+8); sections.append(dict(name=b[p:p+8].rstrip(b'\0').decode(),rva=va,size=size,offset=ptr))
 def offset(rva):
  for s in sections:
   if s['rva']<=rva<s['rva']+s['size']: return s['offset']+rva-s['rva']
  raise ValueError('unmapped RVA')
 def address(p):
  for s in sections:
   if s['offset']<=p<s['offset']+s['size']: return base+s['rva']+p-s['offset']
  raise ValueError('unmapped offset')
 def z(p):
  end=b.find(b'\0',p)
  if end<0: raise ValueError('unterminated name')
  return b[p:end].decode('ascii')
 imports=[]; irva,isize=struct.unpack_from('<II',b,opt+104)
 for p in range(offset(irva),offset(irva)+isize,20):
  oft,stamp,chain,name,iat=struct.unpack_from('<5I',b,p)
  if not any((oft,stamp,chain,name,iat)):break
  i=0
  while True:
   tp=offset(oft or iat)+4*i; v=struct.unpack_from('<I',b,tp)[0]
   if not v:break
   imports.append(dict(dll=z(offset(name)),name=None if v&0x80000000 else z(offset(v)+2),ordinal=v&65535 if v&0x80000000 else None,lookup_offset=tp,lookup_hex=b[tp:tp+4].hex(),iat_address=base+iat+4*i)); i+=1
 run=subprocess.run(['objdump','-d',str(SOURCE)],capture_output=True,text=True)
 if run.returncode:raise ValueError(run.stderr)
 lines=run.stdout.splitlines(); instructions=[]
 for line in lines:
  m=re.match(r'^([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(.*)$',line)
  if m:
   a=int(m[1],16); raw=bytes.fromhex(m[2]); pos=offset(a-base)
   if b[pos:pos+len(raw)]!=raw:raise ValueError('disassembly bytes differ')
   instructions.append(dict(address=a,file_offset=pos,hex=raw.hex(),text=m[3],raw_line=line))
 props=load('audit-launch-search').audit()['tables']['Property']
 names=['VSDFrameworkVersion','VSDAllowLaterFrameworkVersions','VSDFXAvailable','VSDFrameworkProfile','VSDNetCoreVersion','VSDNetCoreDisabled','VSDNETCoreAvailable','CorBindToRuntime','mscoree.dll']
 literals=[]
 for name in names:
  for enc in ['ascii','utf-16le']:
   needle=(name+'\0').encode(enc); start=0
   while (pos:=b.find(needle,start))>=0:
    va=address(pos); refs=[x for x in instructions if re.search(r'(?:\$|\*)0x'+format(va,'x')+r'\b',x['text'])]
    literals.append(dict(text=name,encoding=enc,file_offset=pos,bytes=len(needle),hex=needle.hex(),address=va,preceding_bytes_hex=b[max(0,pos-4):pos].hex(),instruction_literal_matches=refs)); start=pos+1
 window=[x for x in instructions if base+0x11359<=x['address']<base+0x129ce]
 calls=[]
 byiat={x['iat_address']:x for x in imports}
 for x in window:
  raw=bytes.fromhex(x['hex'])
  if len(raw)==6 and raw[:2]==b'\xff\x15':
   a=int.from_bytes(raw[2:],'little'); calls.append(dict(instruction=x,import_declaration=byiat.get(a),iat_address=a))
 return dict(status='PARTIAL',evidence_type='ORDINARY_SOURCE_BYTES_AND_APPLE_OBJDUMP',source=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),image_base=base,sections=sections,properties=[r for r in props if r['values']['Property'].startswith('VSD')],imports=imports,literals=literals,checkfx_address_window={'start':base+0x11359,'end_exclusive':base+0x129ce,'boundary_basis':'CheckFX export to next exported CheckNETCore address; not proven function extent or CFG','iat_call_matches':calls},limits=['Literal instruction operand matches do not establish reachability, argument semantics or property assignment.','Exact suffix search can start inside a longer string; preceding bytes retained.','Ordinal imports remain ordinals; no guessed MSI API names. One absolute indirect call operand 0x10043884 is outside the decoded normal import IAT and remains unresolved.','Native REA provider/readiness and GNU objdump route unavailable in this sandbox; no decompilation Evidence claimed.','No original target execution, exact prerequisites, solver or architecture decision.']),run.stdout
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True); a,dis=audit(); (OUT/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n'); (OUT/'apple-objdump-disassembly.txt').write_text(dis); print(json.dumps({'status':a['status'],'imports':len(a['imports']),'literals':len(a['literals']),'window_iat_calls':len(a['checkfx_address_window']['iat_call_matches'])}))
