#!/usr/bin/env python3
"""Bounded source-byte decoder for the observed installer DLL resources only."""
import hashlib
import json
from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/baseline/b01/installer-resources'
def u16(b,p):
    if p<0 or p+2>len(b): raise ValueError('truncated word')
    return struct.unpack_from('<H',b,p)[0]
def block(b,start=0,limit=None):
    limit=len(b) if limit is None else limit
    size=u16(b,start); count=u16(b,start+2); kind=u16(b,start+4)
    end=start+size
    if size<6 or end>limit: raise ValueError('invalid block extent')
    p=start+6; key=[]
    while True:
        if p+2>end: raise ValueError('unterminated key')
        c=u16(b,p); p+=2
        if not c: break
        key.append(c)
    key=struct.pack('<'+'H'*len(key),*key).decode('utf-16le')
    p=(p+3)&~3; n=count*(2 if kind==1 else 1)
    if p+n>end: raise ValueError('value outside block')
    value=b[p:p+n]
    result={'offset':start,'bytes':size,'key':key,'type':kind,'value_offset':p,'value_bytes':n,'value_hex':value.hex(),'children':[]}
    if kind==1: result['text']=value.decode('utf-16le').rstrip('\0')
    p=(p+n+3)&~3
    while p<end:
        if not any(b[p:end]): break
        child=block(b,p,end); result['children'].append(child); p=(p+child['bytes']+3)&~3
    return result
def strings(b,base):
    p=0; out=[]
    for i in range(16):
        count=u16(b,p); begin=p; p+=2
        if p+count*2>len(b): raise ValueError('truncated string')
        out.append({'id':base+i,'offset':begin,'code_units':count,'text':b[p:p+count*2].decode('utf-16le')}); p+=count*2
    if p!=len(b): raise ValueError('trailing string bytes')
    return out
def exports(raw):
    pe=struct.unpack_from('<I',raw,60)[0]; n=u16(raw,pe+6); opt=pe+24
    if u16(raw,opt)!=0x10b: raise ValueError('only observed PE32 supported')
    sections=opt+u16(raw,pe+20)
    def offset(rva):
        for i in range(n):
            pos=sections+i*40; vs,va,size,ptr=struct.unpack_from('<4I',raw,pos+8)
            if va<=rva<va+size and ptr+rva-va<len(raw): return ptr+rva-va
        raise ValueError('unmapped RVA')
    def text(rva):
        p=offset(rva); end=raw.find(b'\0',p)
        if end<0: raise ValueError('unterminated export')
        return raw[p:end].decode('ascii')
    rva,size=struct.unpack_from('<2I',raw,opt+96); p=offset(rva)
    dll,base,nfunc,nnames,funcs,names,ords=struct.unpack_from('<7I',raw,p+12)
    out=[]
    for i in range(nnames):
        np=offset(names)+4*i; op=offset(ords)+2*i; ordinal=u16(raw,op)
        if ordinal>=nfunc: raise ValueError('export ordinal overflow')
        fp=offset(funcs)+4*ordinal; address=struct.unpack_from('<I',raw,fp)[0]
        out.append({'name':text(struct.unpack_from('<I',raw,np)[0]),'ordinal':base+ordinal,'rva':address,'name_pointer_offset':np,'ordinal_offset':op,'function_offset':fp,'forwarded':rva<=address<rva+size})
    return {'dll_name':text(dll),'entries':out}
def audit():
    e=json.loads((OUT/'rea-resources.json').read_text()); raw=Path(e['subject']['local_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=e['subject']['digest']['sha256']: raise ValueError('artifact hash mismatch')
    results=[]
    for r in e['normalized_result']['resources']:
        loc=r['payload']['location']; b=raw[loc['offset']:loc['offset']+loc['bytes']]
        if len(b)!=loc['bytes'] or hashlib.sha256(b).hexdigest()!=r['payload']['sha256']: raise ValueError('resource hash mismatch')
        record={'type':r['type']['id'],'name':r['name']['id'],'language':r['language']['id'],'source_range':loc,'sha256':r['payload']['sha256']}
        if record['type']==6: record['strings']=strings(b,(record['name']-1)*16)
        elif record['type']==16:
            tree=block(b)
            if tree['bytes']!=len(b) or tree['key']!='VS_VERSION_INFO': raise ValueError('unexpected version root')
            fixed=bytes.fromhex(tree['value_hex'])
            if len(fixed)!=52: raise ValueError('unexpected fixed info')
            fields=struct.unpack('<13I',fixed)
            if fields[0]!=0xfeef04bd: raise ValueError('invalid version signature')
            record['fixed_words']=list(fields)
            for key,ms,ls in [('file_version',fields[2],fields[3]),('product_version',fields[4],fields[5])]: record[key]='.'.join(map(str,[ms>>16,ms&65535,ls>>16,ls&65535]))
            record['tree']=tree
        else: raise ValueError('unsupported resource')
        results.append(record)
    return {'status':'PARTIAL','evidence_type':'STATIC_SOURCE_BYTES','source_sha256':hashlib.sha256(raw).hexdigest(),'rea_evidence_id':e['evidence_id'],'resources':results,'exports':exports(raw),'limitations':['Offsets inside strings/tree are relative to source_range.offset.','Resource text is a declaration; no target code or condition evaluation executed.','Decoder covers observed blocks only; not a general Windows resource implementation.']}
if __name__=='__main__':
    result=audit(); (OUT/'decoded.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False))
