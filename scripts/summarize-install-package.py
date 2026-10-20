#!/usr/bin/env python3
"""汇总安装包全量内容（只读静态清点）。

输入（已存在的取证产物，不重复解包）：
  evidence/baseline/b01/msi-decoded/file-map.json   MSI File 表：CAB 哈希名 → 安装目标路径/大小/sha256
  evidence/baseline/b01/file-inventory.json         CAB 成员字节与 PE 版本资源
  migration_workspace/raw/module-names.json         PE 成员导出表自报 DLL 名（102 个）
  vendor/<版本>/                                     顶层安装产物（本次现场哈希）

输出：markdown 清点 + JSON。所有数字均为静态清点，不代表运行验证。
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXT = {'.txt', '.ini', '.xml', '.cfg', '.log', '.csv', '.json', '.md', '.rtf'}
DOC_EXT = {'.chm', '.hlp', '.pdf', '.doc', '.docx'}
IMG_EXT = {'.bmp', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.cur'}
BIN_EXT = {'.dll', '.exe', '.ocx', '.arx', '.xdl', '.sys', '.drv', '.cpl'}


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        raise SystemExit(f'无法读取 JSON：{path}（{exc}）') from exc


def sha256(path):
    """流式计算 SHA-256；读取失败时给出明确文件而不是抛裸异常。"""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b''):
                h.update(chunk)
    except OSError as exc:
        raise SystemExit(f'无法读取文件：{path}（{exc}）') from exc
    return h.hexdigest()


def long_name(file_name):
    """MSI FileName 形如 'SHORT~1.DLL|long name.dll'，取长名。"""
    if not file_name:
        return ''
    parts = file_name.split('|')
    return parts[-1].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vendor', required=True, help='顶层安装包目录')
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    a = ap.parse_args()

    fm = read_json(ROOT / 'evidence/baseline/b01/msi-decoded/file-map.json')
    inv = {r['sha256']: r for r in read_json(
        ROOT / 'evidence/baseline/b01/file-inventory.json')['files'] if r.get('sha256')}
    mods = {r['sha256']: r for r in read_json(
        ROOT / 'migration_workspace/raw/module-names.json') if r.get('sha256')}

    rows = []
    for r in fm:
        target = r.get('symbolic_target') or ''
        name = long_name(r.get('FileName'))
        ext = Path(name).suffix.lower()
        pe = inv.get(r.get('sha256'), {}).get('pe_metadata') or {}
        mod = mods.get(r.get('sha256')) or {}
        rows.append({
            'member': r.get('File'), 'name': name, 'ext': ext,
            'bytes': r.get('FileSize'), 'sha256': r.get('sha256'),
            'target': target,
            'dir': target.rsplit('/', 1)[0].replace('[TARGETDIR]/', '') if '/' in target else '',
            'pe': bool(pe), 'cpu': pe.get('CPU'), 'dll_name': mod.get('dll'),
            'exports': mod.get('exports'),
            'product': (pe.get('ProductName') or [None])[0] if pe.get('ProductName') else None,
            'company': (pe.get('CompanyName') or [None])[0] if pe.get('CompanyName') else None,
        })

    total = sum(r['bytes'] or 0 for r in rows)
    by_ext = collections.Counter(r['ext'] or '(无扩展名)' for r in rows)
    size_by_ext = collections.Counter()
    for r in rows:
        size_by_ext[r['ext'] or '(无扩展名)'] += r['bytes'] or 0
    by_dir = collections.defaultdict(lambda: {'n': 0, 'bytes': 0})
    for r in rows:
        d = by_dir[r['dir'] or '(根)']
        d['n'] += 1
        d['bytes'] += r['bytes'] or 0

    top = []
    vdir = Path(a.vendor)
    for p in sorted(vdir.iterdir()):
        if p.name.startswith('.'):
            continue
        if p.is_dir():
            inner = [q for q in p.rglob('*') if q.is_file()]
            top.append({'name': p.name + '/', 'files': len(inner),
                        'bytes': sum(q.stat().st_size for q in inner), 'sha256': None})
        else:
            top.append({'name': p.name, 'files': 1, 'bytes': p.stat().st_size,
                        'sha256': sha256(p)})

    md = ['# 安装包全量清点（静态，不含运行）', '',
          f'- 顶层目录：`{a.vendor}`',
          f'- MSI File 表条目：{len(rows)}；合计 {total / 1048576:.1f} MB',
          f'- 其中 PE 二进制：{sum(1 for r in rows if r["pe"])}；非 PE：{sum(1 for r in rows if not r["pe"])}',
          '', '## 1. 顶层安装产物（现场哈希）', '',
          '| 名称 | 文件数 | 大小 | SHA-256 |', '| --- | --- | --- | --- |']
    for t in top:
        md.append(f"| `{t['name']}` | {t['files']} | {t['bytes'] / 1048576:.1f} MB | "
                  f"`{t['sha256'] or '（目录）'}` |")

    md += ['', '## 2. 安装布局（MSI 目标路径，按目录聚合）', '',
           '| 目标目录 | 文件数 | 大小 |', '| --- | --- | --- |']
    for d, v in sorted(by_dir.items(), key=lambda kv: -kv[1]['bytes']):
        md.append(f"| `{d}` | {v['n']} | {v['bytes'] / 1048576:.1f} MB |")

    md += ['', '## 3. 扩展名分布', '', '| 扩展名 | 数量 | 合计大小 |', '| --- | --- | --- |']
    for ext, n in by_ext.most_common():
        md.append(f'| `{ext}` | {n} | {size_by_ext[ext] / 1048576:.1f} MB |')

    pe_rows = [r for r in rows if r['pe']]
    md += ['', f'## 4. PE 二进制（{len(pe_rows)} 个）', '',
           '| 安装名 | 大小 | 导出数 | 自报 DLL 名 | 产品名 |', '| --- | --- | --- | --- | --- |']
    for r in sorted(pe_rows, key=lambda x: -(x['bytes'] or 0)):
        md.append(f"| `{r['name']}` | {r['bytes'] or 0} | {r['exports'] if r['exports'] is not None else '—'} | "
                  f"`{r['dll_name'] or '—'}` | {r['product'] or '—'} |")

    data_rows = [r for r in rows if not r['pe'] and r['ext'] not in (BIN_EXT | DOC_EXT | IMG_EXT | TEXT_EXT)]
    md += ['', f'## 5. 非 PE 数据/资源文件（{len(data_rows)} 个，按扩展名）', '']
    ext_n = collections.Counter(r['ext'] or '(无扩展名)' for r in data_rows)
    md.append('| 扩展名 | 数量 | 示例 |')
    md.append('| --- | --- | --- |')
    for ext, n in ext_n.most_common():
        sample = next(r['name'] or r['member'] for r in data_rows if (r['ext'] or '(无扩展名)') == ext)
        md.append(f'| `{ext}` | {n} | `{sample}` |')

    md += ['', '## 6. 口径与未验项', '',
           '- 成员名在 CAB 内是 `_<32位十六进制>`，真实名只能由 MSI `File` 表的 `FileName` 得到；'
           '本表用 `symbolic_target` 作为安装落点，未经安装验证。',
           '- 大小与 sha256 来自既有取证产物 `file-map.json` / `file-inventory.json`，本轮未重新解包。',
           '- 目录聚合是字符串聚合，不代表 MSI 实际目录层级（Feature/Component 结构未展开）。',
           '- 未做：DLL 依赖闭合、注册表写入、服务/COM 注册、字体与运行库安装顺序、卸载清理。']
    Path(a.out).write_text('\n'.join(md) + '\n')
    Path(a.json).write_text(json.dumps({'top_level': top, 'entries': rows}, ensure_ascii=False, indent=1) + '\n')
    print(f'{a.out}  entries={len(rows)}  pe={len(pe_rows)}  data={len(data_rows)}')


if __name__ == '__main__':
    sys.exit(main())
