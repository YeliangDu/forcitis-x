#!/usr/bin/env python3
"""Restricted CFB v3 MSI reader; source bytes only, never executes package code."""
from pathlib import Path
import hashlib, json, struct, importlib.util
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'evidence/baseline/work/installer/XWallClientX64.msi'
OUT = ROOT/'evidence/baseline/b01/ole-bindings'
END = 0xfffffffe

def digest(b): return hashlib.sha256(b).hexdigest()
def u32(b, p): return struct.unpack_from('<I', b, p)[0]
def decode_name(name):
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._'
    out = ''
    for ch in name:
        n = ord(ch)
        if 0x3800 <= n < 0x4800:
            n -= 0x3800
            out += alphabet[n & 63] + alphabet[n >> 6]
        elif 0x4800 <= n < 0x4840: out += alphabet[n - 0x4800]
        elif n == 0x4840: out += '!'
        elif n < 32: out += '['+str(n)+']'
        else: out += ch
    return out

class Compound:
    def __init__(self, data):
        self.data = data
        if len(data) < 512 or data[:8] != bytes.fromhex('d0cf11e0a1b11ae1'):
            raise ValueError('Invalid CFB signature/header')
        if struct.unpack_from('<4H', data, 26) != (3, 0xfffe, 9, 6):
            raise ValueError('Only little-endian CFB v3 512/64 supported')
        if len(data) % 512: raise ValueError('Partial sector')
        def sector(sid):
            if sid >= len(data)//512 - 1: raise ValueError('Sector outside file')
            return data[(sid+1)*512:(sid+2)*512]
        self.sector = sector
        ids = list(struct.unpack_from('<109I', data, 76))
        nxt = u32(data,68)
        seen = set()
        for _ in range(u32(data,72)):
            if nxt in seen: raise ValueError('DIFAT cycle')
            seen.add(nxt)
            block = sector(nxt)
            ids.extend(struct.unpack_from('<127I',block))
            nxt = u32(block,508)
        if nxt != END: raise ValueError('DIFAT termination')
        ids = [i for i in ids if i != 0xffffffff]
        if len(ids) != u32(data,44) or len(ids) != len(set(ids)):
            raise ValueError('FAT count/duplicate')
        self.fat = [v for i in ids for v in struct.unpack('<128I',sector(i))]
        directory, self.directory_chain = self.chain(u32(data,48), self.fat, sector)
        self.entries = []
        for off in range(0,len(directory),128):
            raw = directory[off:off+128]
            typ = raw[66]
            if not typ: continue
            length = struct.unpack_from('<H',raw,64)[0]
            if length < 2 or length > 64 or length % 2 or raw[length-2:length] != b'\0\0':
                raise ValueError('Invalid directory name')
            name = raw[:length-2].decode('utf-16le')
            self.entries.append(dict(id=off//128, raw_name=name, name=decode_name(name),
                type=typ, start=u32(raw,116), size=struct.unpack_from('<Q',raw,120)[0],
                left=u32(raw,68),right=u32(raw,72),child=u32(raw,76)))
        roots = [e for e in self.entries if e['type']==5]
        if len(roots)!=1 or roots[0]['id']!=0: raise ValueError('Root mismatch')
        root = roots[0]
        self.mini, _ = self.chain(root['start'],self.fat,sector,root['size'])
        mf, ids = self.chain(u32(data,60),self.fat,sector)
        if len(ids)!=u32(data,64): raise ValueError('MiniFAT count')
        self.minifat = list(struct.unpack('<'+'I'*(len(mf)//4),mf))
        self.cutoff = u32(data,56)
        if self.cutoff != 4096: raise ValueError('Unexpected mini cutoff')
        # This package is a flat MSI, not an arbitrary nested storage reader.
        if any(e['type'] not in (2,5) for e in self.entries): raise ValueError('Nested storage unsupported')
        byid = {e['id']:e for e in self.entries}
        visited=set()
        def visit(i):
            if i==0xffffffff: return
            if i in visited or i not in byid or i==0: raise ValueError('Directory tree invalid')
            visited.add(i)
            e=byid[i]
            if e['child']!=0xffffffff: raise ValueError('Stream child')
            visit(e['left']); visit(e['right'])
        visit(root['child'])
        if visited != set(byid)-{0}: raise ValueError('Unreachable directory entry')

    @staticmethod
    def chain(start, fat, sector, size=None):
        ids=[]; chunks=[]; seen=set(); sid=start
        while sid != END:
            if sid in seen or sid >= len(fat): raise ValueError('Chain cycle/out of range')
            seen.add(sid); ids.append(sid); chunks.append(sector(sid)); sid=fat[sid]
        b=b''.join(chunks)
        if size is not None:
            if size>len(b) or (size and len(b)-size>=len(chunks[-1])): raise ValueError('Chain size mismatch')
            b=b[:size]
        return b,ids

    def stream(self,e):
        mini=e['size']<self.cutoff
        def minisector(sid):
            b=self.mini[sid*64:(sid+1)*64]
            if len(b)!=64: raise ValueError('Mini sector outside root')
            return b
        raw,ids=self.chain(e['start'],self.minifat if mini else self.fat,
                           minisector if mini else self.sector,e['size'])
        return raw,ids,mini

def audit(data=None):
    data=SOURCE.read_bytes() if data is None else data
    c=Compound(data); streams={}; details=[]
    base=ROOT/'evidence/baseline/extracted/msi'
    for e in c.entries:
        if e['type']!=2: continue
        raw,chain,mini=c.stream(e)
        if e['name'] in streams: raise ValueError('Duplicate decoded stream')
        streams[e['name']]=raw
        extracted=base/e['name']
        if not extracted.is_file() or extracted.read_bytes()!=raw: raise ValueError('Extracted stream differs: '+e['name'])
        details.append(dict(e,sha256=digest(raw),sector_chain=chain,mini=mini))
    if set(streams)!={p.name for p in base.iterdir() if p.is_file()}: raise ValueError('Stream inventory differs')
    spec=importlib.util.spec_from_file_location('msi_audit', ROOT/'scripts/audit-msi-streams.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    pool=m.strings(streams['!_StringPool'],streams['!_StringData'])
    actions=m.table(streams['!CustomAction'],m.SCHEMAS['CustomAction'],pool)
    binary=m.table(streams['!Binary'], [('Name','s'),('Data','i2')],pool)
    for row in binary:
        # Object column is opaque; do not present its storage word as an integer value.
        del row['values']['Data']
    bindings=[]
    keys={r['values']['Name'] for r in binary}
    for row in actions:
        v=row['values']
        if v['Type'] & 0x30 == 0:
            key=v['Source']; name='Binary.'+key
            if key not in keys or name not in streams: raise ValueError('Unbound Binary action')
            bindings.append(dict(action=v,source_cells=row['cells'],binary_stream=name,
                                 size=len(streams[name]),sha256=digest(streams[name])))
    return dict(status='PARTIAL',evidence_type='STATIC_PACKAGE_SOURCE_BYTES',
                source=str(SOURCE.relative_to(ROOT)),source_sha256=digest(data),
                scope='Restricted flat CFB v3; all extracted streams byte compared; Binary source actions only',
                directory_chain=c.directory_chain,streams=details,binary_rows=binary,bindings=bindings,
                unknowns=['No installer execution, control flow, return values or side effects observed',
                          'Reader limited to this observed CFB layout; independent review pending'])

if __name__=='__main__':
    result=audit(); OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],streams=len(result['streams']),binary_rows=len(result['binary_rows']),bindings=result['bindings']),ensure_ascii=False,indent=2))
