#!/usr/bin/env python3
"""Independent CLI table cursor/attribute corroboration, no assembly execution.
ECMA-335 II.22/24; headers reused from existing PE range validator only.
Never consumes REA row offsets to construct cursors.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pe_headers', ROOT/'scripts/test-clr-evidence.py')
pe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pe)
OUT = ROOT/'evidence/baseline/b01/clr-independent'
# Coded indices: tag bits and all target tables (reserved tags omitted).
CODES = {
 'ResolutionScope': (2,[0,26,35,1]), 'TypeDefOrRef': (2,[2,1,27]),
 'HasConstant': (2,[4,8,23]),
 'HasCustomAttribute': (5,[6,4,1,2,8,9,10,0,14,23,20,17,26,27,32,35,38,39,40,42,44,43]),
 'CustomAttributeType': (3,[6,10]), 'MemberRefParent': (3,[2,1,26,6,27]),
 'HasFieldMarshal': (1,[4,8]), 'HasDeclSecurity': (2,[2,6,32]),
 'HasSemantics': (1,[20,23]), 'MethodDefOrRef': (1,[6,10]),
 'MemberForwarded': (1,[4,6]), 'Implementation': (2,[38,35,39]),
 'TypeOrMethodDef': (1,[2,6])}
# Literal byte widths; heap names; table IDs; coded index names.
SCHEMAS = [
 [2,'s','g','g','g'], ['ResolutionScope','s','s'],
 [4,'s','s','TypeDefOrRef',4,6], [4], [2,'s','b'], [6],
 [4,2,2,'s','b',8], [8], [2,2,'s'], [2,'TypeDefOrRef'],
 ['MemberRefParent','s','b'], [2,'HasConstant','b'],
 ['HasCustomAttribute','CustomAttributeType','b'], ['HasFieldMarshal','b'],
 [2,'HasDeclSecurity','b'], [2,4,2], [4,4], ['b'], [2,20], [20],
 [2,'s','TypeDefOrRef'], [2,23], [23], [2,'s','b'],
 [2,6,'HasSemantics'], [2,'MethodDefOrRef','MethodDefOrRef'], ['s'], ['b'],
 [2,'MemberForwarded','s',26], [4,4], [4,4], [4],
 [4,2,2,2,2,4,'b','s','s'], [4], [4,4,4],
 [2,2,2,2,4,'b','s','s','b'], [4,35], [4,4,4,35],
 [4,'s','b'], [4,4,'s','s','Implementation'],
 [4,4,'s','Implementation'], [2,2], [2,2,'TypeOrMethodDef','s'],
 ['MethodDefOrRef','b'], [42,'TypeDefOrRef']]
# Disambiguate integer constants versus table indices explicitly.
TABLE_COLUMNS = {2:{4,5},3:{0},5:{0},6:{5},7:{0},9:{0},15:{2},16:{1},18:{0,1},19:{0},21:{0,1},22:{0},24:{1},25:{0},28:{3},29:{1},36:{1},37:{3},41:{0,1},44:{0}}


def decode(data):
 h = pe.headers(data)
 start, size = h['streams'].get('#~', h['streams'].get('#-'))
 valid = struct.unpack_from('<Q',data,start+8)[0]
 counts = {}; cursor=start+24
 for t in range(64):
  if valid >> t & 1:
   assert t < len(SCHEMAS), f'unsupported metadata table {t}'
   counts[t] = int.from_bytes(data[cursor:cursor+4],'little'); cursor+=4
 def width(t,col,item):
  if isinstance(item,int):
   return (4 if counts.get(item,0)>=65536 else 2) if col in TABLE_COLUMNS.get(t,set()) else item
  if item in 'sgb' and len(item)==1:
   return 4 if h['heap_sizes'] & {'s':1,'g':2,'b':4}[item] else 2
  bits, targets=CODES[item]
  return 4 if max((counts.get(x,0) for x in targets),default=0) >= 1 << (16-bits) else 2
 tables={}; layouts={}
 for t,n in counts.items():
  widths=[width(t,i,x) for i,x in enumerate(SCHEMAS[t])]
  row_size=sum(widths); end=cursor+n*row_size
  assert end<=start+size, 'table extends beyond stream'
  rows=[]
  for r in range(n):
   pos=cursor+r*row_size; values=[]
   for w in widths:
    values.append(int.from_bytes(data[pos:pos+w],'little')); pos+=w
   rows.append({'offset':cursor+r*row_size,'values':values})
  layouts[str(t)]={'offset':cursor,'rows':n,'row_size':row_size}
  tables[t]=rows; cursor=end
 def string(i):
  at,n=h['streams']['#Strings']; assert 0<=i<n
  return data[at+i:data.index(0,at+i,at+n)].decode('utf-8')
 def compressed(at,end):
  assert at<end
  first=data[at]
  if first<128: return first,at+1
  if first<192:
   assert at+2<=end
   return ((first&63)<<8)|data[at+1],at+2
  assert first<224 and at+4<=end, 'invalid compressed integer'
  return ((first&31)<<24)|int.from_bytes(data[at+1:at+4],'big'),at+4
 def blob(i):
  at,n=h['streams']['#Blob']; assert 0<=i<n
  length,p=compressed(at+i,at+n); assert p+length<=at+n
  return p,data[p:p+length]
 attrs=[]
 for row in tables.get(12,[]):
  parent,typ,value=row['values']
  if parent != (1<<5)|14: continue # Assembly row 1, HasCustomAttribute tag14
  if typ&7 != 3: continue # MemberRef constructor
  ref=tables[10][(typ>>3)-1]; owner,name,sig=ref['values']
  if owner&7 != 1: continue # TypeRef
  tr=tables[1][(owner>>3)-1]; scope,tn,ns=tr['values']
  if (string(ns),string(tn),string(name)) != ('System.Runtime.Versioning','TargetFrameworkAttribute','.ctor'): continue
  at,b=blob(value); assert b[:2]==b'\x01\x00'
  length,p=compressed(at+2,at+len(b)); assert p+length<=at+len(b)
  framework=data[p:p+length].decode('utf-8')
  attrs.append({'row_offset':row['offset'],'constructor_offset':ref['offset'],
    'type_ref_offset':tr['offset'],'blob_offset':at,'blob_hex':b.hex(),
    'signature_hex':blob(sig)[1].hex(),'framework':framework,
    'named_arguments_hex':data[p+length:at+len(b)].hex()})
 return {'source_sha256':hashlib.sha256(data).hexdigest(),'layouts':layouts,
  'table_data_end':cursor,'stream_end':start+size,'attributes':attrs,
  'assembly_offsets':[x['offset'] for x in tables.get(32,[])],
  'reference_offsets':[x['offset'] for x in tables.get(35,[])]}

class Tests(unittest.TestCase):
 def test_real_corpus(self):
  inventory=json.loads((ROOT/'evidence/baseline/b01/clr/inventory.json').read_text())
  records=[]
  for r in inventory['records']:
   a=decode((ROOT/r['source']).read_bytes())
   self.assertEqual(a['source_sha256'],r['sha256'])
   self.assertEqual(a['assembly_offsets'],[r['assembly']['row_offset']])
   self.assertEqual(a['reference_offsets'],[x['row_offset'] for x in r['references']])
   self.assertEqual([x['framework'] for x in a['attributes']],r['target_frameworks'])
   self.assertTrue(all(x['signature_hex']=='2001010e' for x in a['attributes']))
   records.append({'source':r['source'],'comparison_evidence':r['raw'],**a})
  OUT.mkdir(parents=True,exist_ok=True)
  (OUT/'audit.json').write_text(json.dumps({'status':'PARTIAL','evidence_type':'STATIC_PACKAGE','records':records},indent=2)+'\n')
 def test_corrupt_table_count_rejected(self):
  r=json.loads((ROOT/'evidence/baseline/b01/clr/inventory.json').read_text())['records'][0]
  data=bytearray((ROOT/r['source']).read_bytes()); h=pe.headers(data)
  at=h['streams']['#~'][0]
  data[at+24:at+28]=(0xffffffff).to_bytes(4,'little')
  with self.assertRaises(AssertionError): decode(data)

if __name__=='__main__': unittest.main()
