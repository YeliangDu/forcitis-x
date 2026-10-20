#!/usr/bin/env python3
"""把 `计算模板` 里的内联公式链拆成"候选计算单元"。

背景：2,079 条公式里只有 27 条通过 `${SYMBOL}` 互相引用，2,052 条把子步骤**内联**在同一段文本
（例如 `WLS` 里 μz/μf/βgz 都写在一起）。要做"按单元协作"，得先把这些内联链切成单元。

切分规则（保守、可复核）：
  · 步骤头：行首一个短标识符后跟 `:`，如 `   μz: ... (GB50009-2001 7.2.1)`
  · 赋值：`名字=表达式`（允许 μ/γ/β/ω 等希腊字母与中文）
  · 单元的输入 = 该步骤引用、但不是同一公式内**先前已产出**的 `${变量}`
  · 单元的条文 = 步骤头里括号中的规范号

输出：候选单元清单（markdown），以及每个单元的输入/输出/条文。
不做语义推断，不判断粒度是否合理——那是工程师的决策。
"""
import argparse
import json
import re
import sys
from pathlib import Path

HEAD = re.compile(r'^\s*([A-Za-z\u0370-\u03ff\u4e00-\u9fff][\w\u0370-\u03ff]{0,11})\s*[:：]\s*(.*)$')
ASSIGN = re.compile(r'([A-Za-z\u0370-\u03ff][\w\u0370-\u03ff]{0,15})\s*=\s*([^=].*)$')
REF = re.compile(r'\$\{([^\s${}():,;，；、+\-*/=<>\[\]]{1,20})')
CODE = re.compile(r'[（(]\s*((?:GB|JGJ|JG|CECS|GB/T)[^)）]{3,30})[)）]')


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        raise SystemExit(f'无法读取 JSON：{path}（{exc}）') from exc


def split_one(entry):
    """返回候选单元列表。"""
    units = []
    cur = None
    for raw in entry['text'].splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        hm = HEAD.match(line)
        if hm:
            cm = CODE.search(line)
            cur = {'step': hm.group(1), 'header': hm.group(2).strip(),
                   'code': cm.group(1).strip() if cm else None,
                   'expr': [], 'assigns': []}
            units.append(cur)
        am = ASSIGN.search(line)
        if am and cur is not None:
            lhs, rhs = am.group(1), am.group(2).strip()
            cur['assigns'].append(lhs)
            cur['expr'].append(f'{lhs}={rhs}')
    # 计算每个单元的输入：引用但不由此前单元产出
    out = []
    seen = set()
    for u in units:
        refs = [m.group(1) for e in u['expr'] for m in REF.finditer(e)
                if e[m.end():m.end() + 1] != '(']   # 形如 ${IsLess(...)} 是函数调用，不是数据输入
        inputs = sorted({r for r in refs if r not in seen and r not in u['assigns']})
        outputs = sorted(set(u['assigns']))
        seen.update(outputs)
        out.append({'step': u['step'], 'code': u['code'], 'inputs': inputs,
                    'outputs': outputs, 'expr': u['expr'][:6]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--formulas', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--pick', default='WLS,WLD,WAREA,WWEIGHT,SGPGLS_DISP,BREASTGLS_DISP2,GLS_ASTMDISPMENT,LOAD_CALRESULT,VENET_BOLT,GRILLE_BOLT')
    a = ap.parse_args()

    rows = read_json(a.formulas)
    by = {r.get('symbol'): r for r in rows if r.get('symbol')}
    picks = [s.strip() for s in a.pick.split(',') if s.strip() in by]

    md = ['# 内联公式链 → 候选计算单元（样例）', '',
          f'- 源：`{a.formulas}`（{len(rows)} 条）',
          '- 切分规则：步骤头（`名字:`）+ 赋值（`名字=表达式`）；输入 = 引用但非本式先前产出。',
          '- **粒度是否合理由工程师判定**，本文件只是候选。', '']
    for sym in picks:
        e = by[sym]
        units = split_one(e)
        md += [f'## `{sym}`（{len(units)} 个候选单元）', '',
               f"- 标题：{e.get('title', '')}" if e.get('title') else '',
               '', '| # | 单元 | 输入 | 输出 | 条文 |', '| --- | --- | --- | --- | --- |']
        for i, u in enumerate(units, 1):
            md.append(f"| {i} | `{u['step']}` | "
                      f"{', '.join(f'`{x}`' for x in u['inputs']) or '—'} | "
                      f"{', '.join(f'`{x}`' for x in u['outputs']) or '—'} | "
                      f"{u['code'] or '—'} |")
        for u in units:
            if not u['expr']:
                continue
            md += ['', f"**`{u['step']}`** 的表达式：", '```text']
            md += u['expr']
            md += ['```']
        md.append('')

    md += ['## 统计', '',
           f'- 样例数：{len(picks)}',
           f"- 平均候选单元数：{sum(len(split_one(by[s])) for s in picks) / max(1, len(picks)):.1f}"]
    Path(a.out).write_text('\n'.join(md) + '\n')
    print(f'{a.out}  samples={len(picks)}')


if __name__ == '__main__':
    sys.exit(main())
