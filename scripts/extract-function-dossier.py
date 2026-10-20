#!/usr/bin/env python3
"""单函数取证包生成器（只读静态分析，不运行目标）。

产出 migration_workspace/<Function>.md，包含：
 1. 函数签名元数据（导出表 + MSVC 修饰名原文；形参名/参数个数在无 PDB 时标 UNKNOWN）
 2. 已解析常量表（把 objdump 里的 0x180... 直接解析成 float/字符串，不让下游猜十六进制）
 3. 涉及的全局变量（命中本 DLL 导出数据符号；--watch 名单单独核对）
 4. 机器码直译（objdump 反汇编，非 C 伪代码；反编译需要 Ghidra/IDA 等 provider）

限制（必须如实随包输出）：
 - 没有 decompiler provider 时无法给出 C 伪代码，也无法给形参名；
 - 只解析 .rdata/.data 内可判定长度的常量，未知一律标 UNKNOWN。
"""
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSN = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*([^\s#]+)\s*(.*)$')
REF = re.compile(r'#\s*0x([0-9a-f]+)')
SYMENT = re.compile(r'<([^>]+)>')
FLOAT_OPS = ('movss', 'movsd', 'addss', 'addsd', 'subss', 'subsd', 'mulss', 'mulsd',
             'divss', 'divsd', 'comiss', 'comisd', 'ucomiss', 'ucomisd',
             'cvtss2sd', 'cvtsd2ss')


class Mapping(Exception):
    """RVA 未被任何节覆盖。"""


class PE:
    def __init__(self, path):
        self.path = Path(path)
        self.b = self.path.read_bytes()
        b = self.b
        self.sha256 = hashlib.sha256(b).hexdigest()
        pe = self.u32(60)
        opt = pe + 24
        magic = self.u16(opt)
        if magic not in (0x10b, 0x20b):
            raise SystemExit(f'unsupported optional header magic {magic:#x}')
        self.pe32 = magic == 0x10b
        if self.pe32:
            self.base = struct.unpack_from('<I', b, opt + 28)[0]
        else:
            self.base = struct.unpack_from('<Q', b, opt + 24)[0]
        nsec = self.u16(pe + 6)
        sh = opt + self.u16(pe + 20)
        self.sections = []
        for i in range(nsec):
            q = sh + 40 * i
            vs, va, rs, rp = struct.unpack_from('<4I', b, q + 8)
            name = b[q:q + 8].rstrip(b'\0').decode('ascii', 'replace')
            self.sections.append({'name': name, 'va': va, 'vs': vs, 'rs': rs, 'rp': rp})
        dd = opt + (96 if self.pe32 else 112)
        self.dirs = [struct.unpack_from('<II', b, dd + 8 * i) for i in range(16)]
        self.exports = self._exports()
        self.iat = self._imports()

    def u16(self, p):
        return struct.unpack_from('<H', self.b, p)[0]

    def u32(self, p):
        return struct.unpack_from('<I', self.b, p)[0]

    def maybe_off(self, rva):
        for s in self.sections:
            if s['va'] <= rva < s['va'] + max(s['vs'], s['rs']):
                return s['rp'] + rva - s['va']
        return None

    def off(self, rva):
        o = self.maybe_off(rva)
        if o is None:
            raise Mapping(f'unmapped RVA {rva:#x}')
        return o

    def section_of(self, rva):
        for s in self.sections:
            if s['va'] <= rva < s['va'] + max(s['vs'], s['rs']):
                return s
        return None

    def zstr(self, rva, limit=400):
        o = self.maybe_off(rva)
        if o is None:
            return None
        end = self.b.find(b'\0', o, o + limit)
        if end < 0:
            return None
        raw = self.b[o:end]
        if len(raw) < 2 or any(c < 0x20 or c > 0x7E for c in raw):
            return None
        return raw.decode('ascii')

    def _exports(self):
        rva, _size = self.dirs[0]
        if not rva:
            return []
        e = self.off(rva)
        _nameRVA, _ordbase, _nfun, nname, afunc, anames, anord = struct.unpack_from(
            '<IIIIIII', self.b, e + 12)
        names_base = self.off(anames)
        ord_base = self.off(anord)
        func_base = self.off(afunc)
        out = []
        for i in range(nname):
            no = self.maybe_off(self.u32(names_base + 4 * i))
            if no is None:
                continue
            end = self.b.find(b'\0', no, no + 512)
            if end < 0:
                continue
            try:
                name = self.b[no:end].decode('ascii')
            except UnicodeDecodeError:
                continue
            oi = self.u16(ord_base + 2 * i)
            frva = self.u32(func_base + 4 * oi)
            if frva >= len(self.b) * 4:
                continue
            out.append((name, frva))
        return out

    def _imports(self):
        rva, size = self.dirs[1]
        if not rva:
            return {}
        tbl = {}
        o = self.off(rva)
        for i in range(size // 20):
            oft, _ts, _fc, nm, iat = struct.unpack_from('<5I', self.b, o + 20 * i)
            dll = self.zstr(nm)
            j = 0
            while True:
                tp = self.maybe_off((oft or iat) + 8 * j)
                if tp is None or tp + 8 > len(self.b):
                    break
                v = struct.unpack_from('<Q', self.b, tp)[0]
                if not v:
                    break
                if v & (1 << 63):
                    fn = f'ordinal#{v & 0xffff}'
                else:
                    fn = self.zstr((v & 0x7FFFFFFF) + 2)
                tbl[self.base + iat + 8 * j] = {'dll': dll, 'name': fn}
                j += 1
        return tbl


def find_export(pe, needle):
    hits = [(n, r) for n, r in pe.exports if needle in n]
    if not hits:
        raise SystemExit(f'export not found: {needle}')
    return hits


def pdata_ranges(pe):
    """解析 .pdata 的 RUNTIME_FUNCTION 表，得到编译器声明的精确函数区间（含尾）。"""
    rva, size = pe.dirs[3]
    o = pe.maybe_off(rva) if rva else None
    if o is None:
        return []
    rows = []
    for i in range(size // 12):
        begin, end, unwind = struct.unpack_from('<III', pe.b, o + 12 * i)
        if 0 < begin < end:
            rows.append((begin, end, bool(unwind & 0x1)))
    rows.sort()
    return rows


def function_range(pe, rva, ranges=None):
    """优先用 .pdata 精确区间；缺失时才退回「下一个导出」的邻接推断。"""
    if ranges is None:
        ranges = pdata_ranges(pe)
    for begin, end, _chained in ranges:
        if begin == rva:
            return rva, end
    for begin, end, _chained in ranges:
        if begin < rva < end:
            return rva, end
    end = None
    for a in sorted({r for _, r in pe.exports}):
        if a > rva:
            end = a
            break
    sec = pe.section_of(rva)
    sec_end = sec['va'] + sec['rs'] if sec else None
    if end is None or (sec_end is not None and end > sec_end):
        end = sec_end
    if end is None:
        raise SystemExit('function end unresolved')
    return rva, end


def disassemble(pe, start_rva, end_rva):
    start, end = pe.base + start_rva, pe.base + end_rva
    cache_dir = ROOT / 'migration_workspace' / '.cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f'objdump-{pe.sha256[:16]}.txt'
    if not cache.exists():
        run = subprocess.run(['objdump', '-d', str(pe.path)],
                             capture_output=True, text=True, check=False)
        if run.returncode:
            raise SystemExit(run.stderr)
        cache.write_text(run.stdout)
    insns = []
    for line in cache.read_text().splitlines():
        m = INSN.match(line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        if not start <= addr < end:
            continue
        rest = m.group(4)
        refs = []
        rm = REF.search(rest)
        if rm:
            sm = SYMENT.search(rest, rm.end())
            refs.append({'addr': int(rm.group(1), 16),
                         'sym': sm.group(1) if sm else None})
        insns.append({'addr': addr, 'bytes': m.group(2).strip(),
                      'op': m.group(3), 'args': rest, 'refs': refs})
    while insns and insns[-1]['op'] == 'int3':
        insns.pop()
    return insns


def classify_const(pe, addr, op, sym=None):
    """把引用目标解析成可读常量：import / 字符串 / float32 / float64 / 数据 / 符号 / 未知。"""
    if addr in pe.iat:
        it = pe.iat[addr]
        return {'kind': 'import', 'text': f"{it['dll']}!{it['name']}"}
    rva = addr - pe.base
    sec = pe.section_of(rva)
    o = pe.maybe_off(rva)
    if sec is None or o is None:
        return {'kind': 'unmapped', 'text': f'{addr:#x}'}
    if sec['name'] == '.rdata':
        s = pe.zstr(rva, 200)
        if s and len(s) >= 2 and op.startswith('lea'):
            return {'kind': 'string', 'text': json.dumps(s, ensure_ascii=False)}
        if op in FLOAT_OPS:
            if 'ss' in op:
                return {'kind': 'float32', 'text': repr(struct.unpack_from('<f', pe.b, o)[0])}
            return {'kind': 'float64', 'text': repr(struct.unpack_from('<d', pe.b, o)[0])}
        if sym:
            return {'kind': 'symbol', 'text': sym}
        return {'kind': 'rdata-hex', 'text': pe.b[o:o + 8].hex()}
    if sec['name'] == '.data':
        f32 = struct.unpack_from('<f', pe.b, o)[0]
        f64 = struct.unpack_from('<d', pe.b, o)[0]
        return {'kind': 'data', 'text': f'f32={f32!r} f64={f64!r}'}
    return {'kind': sec['name'], 'text': f'{addr:#x}'}


def mangled_tail(name):
    """取 @@ 之后的编码尾部，并按 MSVC 的 X=void 形参表规则判 0 参。"""
    i = name.find('@@')
    return name[i + 2:] if i >= 0 else ''


def arg_count_guess(name):
    tail = mangled_tail(name)
    if tail.endswith('XZ'):
        return 0
    if tail.endswith('ZZ'):
        return '>=1（可变参数，未解码）'
    return '>=1（未解码）'


SIG = re.compile(r'^[A-Za-z_][\w \*]*__[a-z]+\s+(.+?)\(([^()]*)\)\s*$')


def split_params(text):
    out, depth, cur = [], 0, ''
    for ch in text:
        if ch == ',':
            if depth == 0:
                out.append(cur.strip())
                cur = ''
                continue
        elif ch in '(<[':
            depth += 1
        elif ch in ')>]':
            depth -= 1
        cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def parse_signature(pseudo):
    """从伪代码里的函数头取 调用约定 / 返回类型 / 形参（含 Ghidra 命名）。"""
    for line in pseudo.splitlines():
        m = SIG.match(line.strip())
        if not m or '::' not in m.group(1) and '__' not in line:
            continue
        head = line.strip()
        cc = re.search(r'__(\w+)', head)
        params = [p for p in split_params(m.group(2)) if p and p != 'void']
        is_this = cc is not None and cc.group(1) == 'thiscall'
        args = params[1:] if is_this and params else params
        ret = head[:head.index(cc.group(0))].strip() if cc else ''
        return {'head': head, 'cc': cc.group(1) if cc else None, 'ret': ret,
                'params': params, 'args': args, 'is_this': is_this}
    return None


def rea_decompile(dll, mangled, snapshot, out_json, gh):
    """调用 REA/Ghidra 反编译单个过程；命中本地缓存则复用；失败不伪造结果。"""
    if out_json.exists():
        try:
            cached = json.loads(out_json.read_text())
        except Exception as exc:
            raise SystemExit(
                f'本地缓存不可解析，请删除后重跑：{out_json}（{exc}）') from exc
        if 'normalized_result' in cached:
            return {'ok': True, 'json': out_json,
                    'sha256': hashlib.sha256(out_json.read_bytes()).hexdigest(),
                    'data': cached, 'cached': True}
    cmd = ['rea', 'decompile', str(dll), '--procedure', mangled, '--provider', 'ghidra',
           '--snapshot', str(snapshot), '--format', 'json']
    env = os.environ.copy()
    if gh:
        env['GHIDRA_INSTALL_DIR'] = str(gh)
    run = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    text = run.stdout.strip()
    if not text.startswith('{'):
        return {'ok': False, 'error': (run.stderr or text).strip()[:400]}
    try:
        data = json.loads(text)
    except Exception as exc:
        return {'ok': False, 'error': f'rea 输出无法解析为 JSON: {exc}'}
    if run.returncode != 0 or 'normalized_result' not in data:
        return {'ok': False, 'error': data.get('message') or data.get('code') or 'unknown'}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return {'ok': True, 'json': out_json,
            'sha256': hashlib.sha256(out_json.read_bytes()).hexdigest(),
            'data': data}


def build(pe, needle, out_path, watch, gh=None, decompile=True):
    hits = find_export(pe, needle)
    ranges = pdata_ranges(pe)
    aliases = {}
    for name, rva in pe.exports:
        aliases.setdefault(rva, set()).add(name)
    consts = {}
    globals_ = {}
    body = []
    for mangled, rva in hits:
        start, end = function_range(pe, rva, ranges)
        insns = disassemble(pe, start, end)
        body.append((mangled, start, end, insns))
        for ins in insns:
            for ref in ins['refs']:
                c = classify_const(pe, ref['addr'], ins['op'], ref['sym'])
                consts.setdefault(f"{ref['addr']:#x}", c)
                if c['kind'] == 'data':
                    globals_.setdefault(f"{ref['addr']:#x}", {'op': ins['op']})

    watch_rows = []
    ref_addrs = {ref['addr'] for _, _, _, insns in body for ins in insns for ref in ins['refs']}
    for w in watch:
        here = [(n, r) for n, r in pe.exports if n == w]
        watch_rows.append({
            'name': w,
            'exported': [f'{n}@{r:#x}' for n, r in here],
            'used': any(r in ref_addrs for _, r in here),
        })

    raw_dir = ROOT / 'migration_workspace' / 'raw'
    snap = ROOT / 'migration_workspace' / '.cache' / f'snap-{pe.sha256[:12]}'
    decomp = []
    for mangled, _start, _end, _insns in body:
        if not decompile:
            decomp.append({'ok': False, 'error': '--no-decompile'})
            continue
        res = rea_decompile(pe.path, mangled, snap, raw_dir / f'{mangled.replace("?", "").replace("@", "-")[:80]}.rea.json', gh)
        decomp.append(res)

    sig = None
    for d in decomp:
        if d['ok']:
            sig = parse_signature(d['data']['normalized_result'])
            if sig:
                break

    md = [f'# {needle} — 单函数取证包（生成物，勿手改）\n', '',
          f'来源 DLL：`{pe.path}`', '',
          f'- SHA-256：`{pe.sha256}`',
          f'- ImageBase：`{pe.base:#x}`',
          f'- 导出命中：{len(hits)} 个带 `{needle}` 的导出', '',
          '## 1. 函数签名元数据', '',
          '| 项 | 值 | 证据等级 |', '| --- | --- | --- |']
    for mangled, start, end, _insns in body:
        md.append(f'| 修饰名（原文） | `{mangled}` | 导出表实测 |')
        same = sorted(aliases.get(start, set()) - {mangled})
        if same:
            md.append('| 同址别名 | ' + ', '.join(f'`{x}`' for x in same)
                      + '（导出表里同一地址多个名字，语义归属需人工判断） | 导出表实测 |')
        md.append(f'| 修饰名尾部 | `{mangled_tail(mangled)}` | 导出表实测 |')
        exact = any(b == start for b, _e, _c in ranges)
        md.append(f'| 地址 | `start={start:#x}` `end={end:#x}` `len={end - start:#x}` | '
                  + ('.pdata RUNTIME_FUNCTION 实测（编译器声明区间） |' if exact
                     else '导出表邻接推断（.pdata 无对应条目） |'))
    short = hits[0][0].split('@')[0].lstrip('?0123456789_$')
    mangled_n = arg_count_guess(hits[0][0])
    md.append(f'| 函数名 | `{short}` | 导出表字符串 |')
    md.append('| 固定/可变参数 | 尾部以 `ZZ` 结尾=可变参数；否则未见 varargs 标记 | 修饰名规则 |')
    if sig:
        md.append(f'| 调用约定 / 返回类型 | `{sig["cc"]}` / `{sig["ret"]}` | Ghidra 反编译 |')
        md.append(f'| nArgs（不含 this） | {len(sig["args"])}；形参原文 `{sig["head"]}` | Ghidra 反编译 |')
        md.append('| 形参名列表 | '
                  + ', '.join(f'`{p.split()[-1].lstrip("*")}`' for p in sig['args'])
                  + ' | Ghidra 反编译 |' if sig['args'] else '| 形参名列表 | 无（无形参） | Ghidra 反编译 |')
        if mangled_n != len(sig['args']) and not sig['is_this']:
            md.append(f'| 交叉核对 | 修饰名规则给 {mangled_n}，反编译给 {len(sig["args"])}，两者不一致需人工复核 | 冲突 |')
    else:
        md += ['| 调用约定 / 返回类型 | UNKNOWN（反编译未取得） | NOT_RUN |',
               f'| nArgs | {mangled_n}（仅修饰名规则） | 部分 NOT_RUN |',
               '| 形参名列表 | UNKNOWN | NOT_RUN |']
    md += ['', '## 2. 已解析常量表', '',
           'objdump 的 `# 0x180...` 注释在此处已解析为实际值，下游不要自行猜测十六进制。', '']
    if consts:
        md += ['| 引用地址 | 类别 | 已解析值 |', '| --- | --- | --- |']
        for addr in sorted(consts):
            c = consts[addr]
            md.append(f"| `{addr}` | {c['kind']} | `{c['text']}` |")
    else:
        md.append('无（本函数未引用可解析常量）')
    md += ['', '## 3. 涉及的全局变量', '']
    wrote = False
    for w in watch_rows:
        md.append(f"- `{w['name']}`：本 DLL 导出={', '.join(w['exported']) or '否'}；"
                  f"本函数引用={'是' if w['used'] else '否'}")
        wrote = True
    for addr, g in sorted(globals_.items()):
        md.append(f"- `{addr}`：.data 数据引用（指令 `{g['op']}`）")
        wrote = True
    if not wrote:
        md.append('无（未命中可识别的全局数据引用）')
    md += ['', '## 4. 代码正文', '', '### 4.1 eval 反编译伪代码（Ghidra 输出，非原始源码）', '']
    got = False
    for (_mangled, _start, _e, _i), d in zip(body, decomp, strict=True):
        if d['ok']:
            got = True
            data = d['data']
            prov = data.get('provider', {})
            prof = data.get('analysis_profile', {})
            md += ['| 取证项 | 值 |', '| --- | --- |',
                   f"| evidence_id | `{data.get('evidence_id')}` |",
                   f"| provider | `{prov.get('id')}` {prov.get('name')} {prov.get('version')} |",
                   f"| operation | `{data.get('operation')}` |",
                   f"| analysis_profile.digest | `{prof.get('digest')}` |",
                   f"| 原始 Evidence | `{d['json']}`（sha256 `{d['sha256']}`） |",
                   f"| confidence / authority | `{data.get('confidence')}` / `{data.get('authority')}` |",
                   '', '```c', data['normalized_result'].rstrip(), '```', '']
            lim = data.get('limitations') or []
            if lim:
                md += ['反编译自带限制（原文摘录）：', '']
                md += [f'- {str(x)}' for x in lim]
                md.append('')
        else:
            md += ['NOT_RUN：`rea decompile` 未取得伪代码 — ' + str(d.get('error'))[:300], '']
    if not got:
        md += ['NOT_RUN：本包未包含反编译结果，**不得**把 4.2 的机器码直译当作语义结论。', '']
    md += ['### 4.2 机器码直译（objdump 反汇编，用于核对常量与引用）', '', '```asm']
    for mangled, start, _end, insns in body:
        md.append(f'; {mangled} @ {start:#x}')
        for ins in insns:
            md.append(f"{ins['addr']:x}: {ins['bytes']:<30} {ins['op']} {ins['args']}")
    md += ['```', '']
    out_path.write_text('\n'.join(md))
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dll')
    ap.add_argument('--export', required=True, help='导出名子串，例如 Solve@HWKCalc_GlassDisp')
    ap.add_argument('--out', required=True)
    ap.add_argument('--watch', action='append', default=[],
                    help='需要单独核对的全局符号修饰名')
    ap.add_argument('--ghidra', default=os.environ.get('GHIDRA_INSTALL_DIR'),
                    help='Ghidra 安装目录（默认取 GHIDRA_INSTALL_DIR）')
    ap.add_argument('--no-decompile', action='store_true', help='跳过 REA/Ghidra 反编译')
    a = ap.parse_args()
    pe = PE(a.dll)
    print(build(pe, a.export, Path(a.out), a.watch,
                gh=a.ghidra, decompile=not a.no_decompile))


if __name__ == '__main__':
    sys.exit(main())
