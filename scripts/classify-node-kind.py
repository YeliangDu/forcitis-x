#!/usr/bin/env python3
"""给 378 个 CXMap 节点做结构分类（L5/A 路线第 2 步）。

目的：`nodes-expr` 里 292 个 `NO_ARITH` 并不等于"不可透明"——它们大多不是数值算术节点。
本脚本只按**反编译结构**归类，不推断语义：

| 类别 | 判定信号（任一即可，按优先级取第一个命中） |
| --- | --- |
| `PREDICATE` | 有比较/逻辑分支且返回 0/1 常量（`CXConstant::CXConstant(...,0/1,...)`），无算术赋值 |
| `COLLECTION` | 出现 `CXMapVariableArguments`/`CXParameter`，或 `Add/Del/Insert` 类虚表调用 |
| `DRAW` | 名字以 `Draw`/`FEDraw`/`DoDraw` 开头，或出现 `HWKPlot`/`g_bEmfOut`/`CDC` |
| `STRING` | 出现 `CXStringDefine` 或只做 `String` 拼接 |
| `FE_DATA` | 名字以 `FE` 开头且无算术（纯 FE 数据装填/取值） |
| `GETTER` | 只做 `look_string` 取值并直接返回（无算术） |
| `UNKNOWN` | 以上都不命中 |

输出：`migration_workspace/raw/node-kinds.json` + `migration_workspace/node-kinds.md`
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'migration_workspace' / 'raw'
NODES = RAW / 'nodes'

CMP = re.compile(r'[<>]=?|\bif\s*\(')
BOOL_CTOR = re.compile(r'CXConstant::CXConstant\([^,]+,\s*(?:\(double\)bVar\d+|0x0|0x1|0|1)\s*,')
# 许可校验门：`if ((int)(fVarN * 46.0) == 0x2c) { GetHMMxValue(...) }`，不是业务算术
LICENSE_GATE = re.compile(r'if \(\(int\)\(fVar\d+ \* 4[0-9]\.0\) == 0x2c\)')
ASG = re.compile(r'^([df]Var\d+)\s*=\s*(.+)$')
COLLECTION = re.compile(r'CXMapVariableArguments|CXParameter|MMgt::Allocate\(0x[0-9a-f]+\)\s*;')
ADD_DEL = re.compile(r'\b(?:Add|Del|Insert|Remove|Append)\w*\s*\(')
DRAW = re.compile(r'HWKPlot|g_bEmfOut|\bCDC\b|::Draw')
STRING_DEF = re.compile(r'CXStringDefine')
LOOK = re.compile(r'look_string\(')
ARITH = re.compile(r'\b[df]Var\d+\s*=\s*[^;]*[+\-*/][^;]*;')


PRIORITY = ('ARITH', 'COLLECTION', 'DRAW', 'STRING', 'FE_DATA', 'PREDICATE', 'GETTER')


def statements(pseudo):
    text = pseudo.replace('{', ' ; ').replace('}', ' ; ')
    out, buf = [], []
    for line in text.splitlines():
        code = line.split('//')[0].rstrip()
        if not code.strip():
            continue
        buf.append(code.strip())
        joined = ' '.join(buf)
        if joined.endswith(';'):
            out += [part.strip() for part in joined.split(';') if part.strip()]
            buf = []
    return out


def strip_derefs(text):
    """删掉 `*(类型 *)(表达式)` 整个取址片段，避免把 `+ 8` / `+ 0x98` 这类偏移当算术。"""
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r'\*\s*\([^()]*\)\s*\([^()]*\)', '', text)
    return text


def has_arithmetic(pseudo):
    """只看形如 `dVarN = <含运算符表达式>` 的语句；许可校验门、取址偏移、if 条件都不算。"""
    for st in statements(pseudo):
        if LICENSE_GATE.search(st):
            continue
        m = ASG.match(st)
        if not m:
            continue
        rhs = strip_derefs(m.group(2))
        rhs = re.sub(r'\(\s*(?:double|float|int|uint|char|bool|ulong|longlong|undefined\d*|code|CX\w+|String)\s*\*?\s*\)', '', rhs)
        if re.search(r'[A-Za-z0-9_$)]\s*[-+*/]\s*[A-Za-z0-9_$(]', rhs) and not re.search(r'0x[0-9a-fA-F]+', rhs):
            return True
    return False


def classify(name, pseudo, expr_status=None):
    """返回 (主类别, 全部命中类别)。主类别按 PRIORITY 取第一个命中——数值算术优先，
    因为它决定该节点是否需要算式抽取；绘图/字符串等标签仍完整保留在 secondary 里。"""
    hits = set()
    name_l = name.lower()
    # 两个独立信号任一成立即视为有数值算术：结构正则，或算式抽取已产出步骤
    if has_arithmetic(pseudo) or expr_status in ('EXPR', 'PARTIAL'):
        hits.add('ARITH')
    if COLLECTION.search(pseudo) and (ADD_DEL.search(pseudo) or 'CXMapVariableArguments' in pseudo):
        hits.add('COLLECTION')
    if name_l.startswith(('draw', 'fedraw', 'dodraw')) or DRAW.search(pseudo):
        hits.add('DRAW')
    if STRING_DEF.search(pseudo):
        hits.add('STRING')
    if name_l.startswith('fe'):
        hits.add('FE_DATA')
    if CMP.search(pseudo) and BOOL_CTOR.search(pseudo):
        hits.add('PREDICATE')
    if LOOK.search(pseudo):
        hits.add('GETTER')
    primary = next((k for k in PRIORITY if k in hits), 'UNKNOWN')
    return primary, sorted(hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=str(RAW / 'node-kinds.json'))
    ap.add_argument('--md', default=str(ROOT / 'migration_workspace' / 'node-kinds.md'))
    args = ap.parse_args()

    expr_path = RAW / 'nodes-expr.json'
    expr = {}
    if expr_path.exists():
        try:
            expr = {row['name']: row for row in json.loads(expr_path.read_text()).get('rows', [])}
        except json.JSONDecodeError:
            expr = {}

    rows, errors = [], []
    for path in sorted(NODES.glob('*.rea.json')):
        name = path.stem.replace('.rea', '')
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({'name': name, 'error': str(exc)})
            continue
        pseudo = data.get('normalized_result') or ''
        prior = expr.get(name, {})
        kind, kinds = classify(name, pseudo, prior.get('status'))
        rows.append({
            'name': name,
            'kind': kind,
            'kinds': kinds,
            'expr_status': prior.get('status'),
            'has_expr': bool(prior.get('fused')),
            'evidence_id': data.get('evidence_id'),
        })

    counts = {}
    for row in rows:
        counts[row['kind']] = counts.get(row['kind'], 0) + 1
    Path(args.json).write_text(json.dumps(
        {'counts': counts, 'rows': rows, 'errors': errors}, ensure_ascii=False, indent=1) + '\n')

    md = ['# 节点头分类（L5 / A 路线第 2 步，结构判定）', '',
          f'- 输入：`migration_workspace/raw/nodes/*.rea.json`（{len(rows)} 个）',
          '- 分布：' + '、'.join(f'`{k}`={v}' for k, v in sorted(counts.items(), key=lambda kv: -kv[1])),
          '',
          '判定只看反编译结构，**不推断语义**；`ARITH` 表示有数值算术（已在 `nodes-expr.md` 里抽算式）。',
          '',
          '| 类别 | 数量 | 含义 |',
          '| --- | --- | --- |',
          f"| `ARITH` | {counts.get('ARITH', 0)} | 有数值算术赋值 |",
          f"| `DRAW` | {counts.get('DRAW', 0)} | 绘图/输出类（`HWKPlot`/`g_bEmfOut`/`Draw*`） |",
          f"| `COLLECTION` | {counts.get('COLLECTION', 0)} | 集合/参数容器操作 |",
          f"| `FE_DATA` | {counts.get('FE_DATA', 0)} | FE 数据装填/取值（无算术） |",
          f"| `PREDICATE` | {counts.get('PREDICATE', 0)} | 判定，返回 0/1 |",
          f"| `GETTER` | {counts.get('GETTER', 0)} | 只取字典值 |",
          f"| `STRING` | {counts.get('STRING', 0)} | 字符串定义/拼接 |",
          f"| `UNKNOWN` | {counts.get('UNKNOWN', 0)} | 未命中任何信号（待人工看） |",
          '',
          '## 明细', '',
          '| 节点 | 类别 | 算式状态 |', '| --- | --- | --- |']
    for row in sorted(rows, key=lambda r: (r['kind'], r['name'])):
        md.append(f"| `{row['name']}` | {row['kind']} | {row['expr_status'] or '—'} |")
    if errors:
        md += ['', '## 失败', ''] + [f"- `{e['name']}`：{e['error']}" for e in errors]
    Path(args.md).write_text('\n'.join(md) + '\n')
    print(json.dumps(counts, ensure_ascii=False))
    print(f'rows={len(rows)} -> {args.md}')


if __name__ == '__main__':
    sys.exit(main())
