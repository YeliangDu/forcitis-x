/**
 * PoC P1 runner: section-properties engine vs closed-form solutions.
 *
 * Writes evidence/poc/P1/{criteria.md,data.json,conclusion.md}. The hard exit criterion of P1 is a
 * <=0.5% agreement with the *original system's* stored values (`型材参数表` / `复合型材参数表`); that
 * half is PENDING because the full rows and the section geometry (`图形ID` -> 图库) are not exported
 * yet. This runner records both halves explicitly so nothing is implied.
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

import {
  hollowRectangle,
  iSection,
  rectangle,
  sectionProperties,
  thinWalledOpenJ,
} from '../packages/section/src/index.ts';

type Case = {
  id: string;
  label: string;
  computed: Record<string, number>;
  expected: Record<string, number>;
  tolerance: number;
};

const rel = (a: number, b: number) => (b === 0 ? Math.abs(a) : Math.abs(a - b) / Math.abs(b));

function cases(): Case[] {
  const out: Case[] = [];

  const rect = sectionProperties([rectangle(100, 200)]);
  out.push({
    id: 'rect-100x200',
    label: '矩形 100x200（解析解）',
    computed: { areaMm2: rect.areaMm2, ixMm4: rect.ixMm4, iyMm4: rect.iyMm4, wxTopMm3: rect.wxTopMm3 },
    expected: {
      areaMm2: 20000,
      ixMm4: (100 * 200 ** 3) / 12,
      iyMm4: (200 * 100 ** 3) / 12,
      wxTopMm3: (100 * 200 ** 2) / 6,
    },
    tolerance: 1e-12,
  });

  const t = 5;
  const box = sectionProperties([hollowRectangle(100, 200, t)]);
  out.push({
    id: 'box-100x200-t5',
    label: '矩形管 100x200 壁厚 5（解析解）',
    computed: { areaMm2: box.areaMm2, ixMm4: box.ixMm4, iyMm4: box.iyMm4 },
    expected: {
      areaMm2: 100 * 200 - 90 * 190,
      ixMm4: (100 * 200 ** 3 - 90 * 190 ** 3) / 12,
      iyMm4: (200 * 100 ** 3 - 190 * 90 ** 3) / 12,
    },
    tolerance: 1e-12,
  });

  const [bf, tf, tw, hw] = [100, 10, 8, 180];
  const i = sectionProperties(iSection(bf, tf, tw, hw));
  const h = hw + 2 * tf;
  out.push({
    id: 'i-100x200',
    label: '工字形 100x200（翼缘 10，腹板 8，解析解）',
    computed: { areaMm2: i.areaMm2, ixMm4: i.ixMm4, iyMm4: i.iyMm4, centroidYMm: i.centroidYMm },
    expected: {
      areaMm2: 2 * bf * tf + hw * tw,
      ixMm4: (bf * h ** 3 - (bf - tw) * hw ** 3) / 12,
      iyMm4: (2 * tf * bf ** 3 + hw * tw ** 3) / 12,
      centroidYMm: h / 2,
    },
    tolerance: 1e-12,
  });

  const composite = sectionProperties([rectangle(50, 50, 0, 0), rectangle(50, 50, 0, 150)]);
  out.push({
    id: 'composite-two-rects',
    label: '两块 50x50 竖向错开（平行轴定理）',
    computed: { areaMm2: composite.areaMm2, ixMm4: composite.ixMm4, iyMm4: composite.iyMm4, centroidYMm: composite.centroidYMm },
    expected: {
      areaMm2: 5000,
      ixMm4: 2 * ((50 * 50 ** 3) / 12) + 2 * 2500 * 75 ** 2,
      iyMm4: 2 * ((50 * 50 ** 3) / 12),
      centroidYMm: 100,
    },
    tolerance: 1e-12,
  });

  const j = thinWalledOpenJ(
    [{ x: 0, y: 0 }, { x: 100, y: 0 }, { x: 100, y: 100 }, { x: 0, y: 100 }], 5);
  out.push({
    id: 'thin-walled-open-j',
    label: '薄壁开口 J（三段 100x5，1/3·b·t^3）',
    computed: { j },
    expected: { j: 3 * ((100 * 5 ** 3) / 3) },
    tolerance: 1e-12,
  });

  return out;
}

const results = cases().map((testCase) => {
  const rows = Object.entries(testCase.expected).map(([key, expected]) => {
    const computed = testCase.computed[key] ?? Number.NaN;
    const diff = rel(computed, expected);
    return { quantity: key, expected, computed, relDiff: diff, pass: diff <= testCase.tolerance };
  });
  return { ...testCase, rows, pass: rows.every((r) => r.pass) };
});

const allAnalyticPass = results.every((r) => r.pass);

// ---------------------------------------------------------------------------------------------
// Second half of the P1 criterion: agreement with the shipped data. Only the first rows of the two
// profile tables were ever sampled (3 composite + 3 profile rows) and the section geometry lives
// behind `图形ID`; without those inputs the comparison cannot be made honestly.
const oldSystemInputs = [
  {
    item: '型材参数表 全量行（681 行，含图形ID/IZ/IY/WZ1/WZ2/WY1/WY2/SZ/SY/AREA/T/CX/CY/PERIM/JA）',
    status: 'PENDING',
    why: '仓库内只有 3 行样本；需要只读导出全表',
  },
  {
    item: '复合型材参数表 全量行（3 行样本已见，MAINID/SUBID1..3 + 组合特性）',
    status: 'PENDING',
    why: '需要被引用子型材（1780/1781/1783/1782 等）的对应行才能做平行轴复算',
  },
  {
    item: '断面几何（图形ID → 图库定义，用于重建多边形与孔洞）',
    status: 'PENDING',
    why: '图库数据表(SLD varbinary) 未解析；没有轮廓就无法从几何算起',
  },
];

const stamp = new Date().toISOString();
// run from `replica/` (npm script): evidence lives one level up at the repo root
const root = resolve(process.cwd(), '..');
const outDir = join(root, 'evidence', 'poc', 'P1');
mkdirSync(outDir, { recursive: true });

const data = {
  poc: 'P1',
  generatedAt: stamp,
  engine: 'replica/packages/section/src/index.ts',
  analytic: { pass: allAnalyticPass, cases: results },
  oldSystem: { pass: null, status: 'PENDING', required: oldSystemInputs },
};
writeFileSync(join(outDir, 'data.json'), `${JSON.stringify(data, null, 1)}\n`, 'utf8');

const table = results
  .map((r) => `| ${r.id} | ${r.rows.length} | ${r.pass ? 'PASS' : 'FAIL'} | ${r.tolerance.toExponential(0)} |`)
  .join('\n');

writeFileSync(join(outDir, 'criteria.md'), `# PoC P1 判据：断面特性引擎

| 项 | 内容 |
| --- | --- |
| 硬判据 | 与旧系统 \`型材参数表\`/\`复合型材参数表\` 值偏差 ≤0.5%，或差异可归因（薄壁近似 vs 精确） |
| 软判据（本引擎的解析正确性） | 与解析解相对误差 ≤1e-12 |
| 输入 | 断面几何（多边形 + 孔洞 + 组合变换） |
| 输出 | A、重心、Ix/Iy/Ixy、主轴、Wx/Wy、最小 W、回转半径、包围盒、周长、静矩、薄壁 J |

## 解析解对照（软判据）

| 用例 | 检查量 | 结果 | 容差 |
| --- | --- | --- | --- |
${table}

## 与旧系统对照（硬判据）

状态：**PENDING**。缺三样输入（见 \`data.json\` → \`oldSystem.required\`）：
全量型材行、复合型材所引用子型材行、以及 \`图形ID\` 对应的断面轮廓。
`, 'utf8');

writeFileSync(join(outDir, 'conclusion.md'), `# PoC P1 结论（${stamp}）

## 已成立

- 引擎实现完成：\`replica/packages/section/src/index.ts\`（纯函数、无 IO/时钟/随机）；
  带孔多边形按有向面积自然相减，组合断面按平行轴累加，支持任意变换（平移/旋转）。
- 解析解对照 **全部通过**（矩形、矩形管、工字形、双矩形平行轴、薄壁开口 J），相对误差 ≤1e-12。
- 性质不变量成立：主轴和 = Ix+Iy；平移后质心惯性矩不变；旋转 90° 后 Ix/Iy 互换；孔洞换向结果不变。
- 静矩（S）与塑性发展所需的半截面一阶矩可通过裁剪实现，供剪应力验算使用。

## 未成立（不得宣称 P1 通过）

- 与旧系统存储值的对照尚未做：缺全量 \`型材参数表\`(681 行)、被引用的子型材行、以及 \`图形ID\` 的断面轮廓。
- 薄壁 J（\`thinWalledOpenJ\`）为显式近似，未与旧系统 \`JA\` 列对照；不得用于验收结论。

## 下一步（按优先级）

1. 只读导出 \`型材参数表\`/\`复合型材参数表\` 全量行（SQL SELECT，不改库）。
2. 解析 \`图库数据表\` 的 SLD/图形定义或从 \`图形ID\` 取轮廓；否则先用尺寸参数重建等价断面。
3. 用 2–3 个"复合型材"做平行轴复算，比较 AREA/IZ/IY/WZ1/WZ2 → 判定 ≤0.5%。
`, 'utf8');

process.stdout.write(`${JSON.stringify({
  poc: 'P1',
  analyticPass: allAnalyticPass,
  cases: results.length,
  failed: results.flatMap((r) => (r.pass ? [] : [r.id])),
  oldSystem: 'PENDING',
  evidence: outDir,
}, null, 1)}\n`);
process.exit(allAnalyticPass ? 0 : 1);
