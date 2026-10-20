import assert from 'node:assert/strict';
import test from 'node:test';

import {
  clipAbove,
  hollowRectangle,
  iSection,
  rectangle,
  sectionProperties,
  staticMomentAt,
  thinWalledOpenJ,
} from '../src/index.ts';

const close = (actual: number, expected: number, relTol = 1e-12, label = '') => {
  const scale = Math.max(Math.abs(expected), 1e-12);
  const rel = Math.abs(actual - expected) / scale;
  assert.ok(rel <= relTol, `${label} expected ${expected}, got ${actual} (rel ${rel.toExponential(2)})`);
};

test('rectangle: areaMm2, centroid, second moments, moduli', () => {
  const p = sectionProperties([rectangle(100, 200)]);
  close(p.areaMm2, 100 * 200, 1e-12, 'areaMm2');
  close(p.centroidXMm, 50, 1e-12, 'centroidXMm');
  close(p.centroidYMm, 100, 1e-12, 'centroidYMm');
  close(p.ixMm4, (100 * 200 ** 3) / 12, 1e-12, 'ixMm4');
  close(p.iyMm4, (200 * 100 ** 3) / 12, 1e-12, 'iyMm4');
  close(p.ixyMm4, 0, 1e-12, 'ixyMm4');
  close(p.wxTopMm3, (100 * 200 ** 2) / 6, 1e-12, 'wxTopMm3');
  close(p.wxBottomMm3, (100 * 200 ** 2) / 6, 1e-12, 'wxBottomMm3');
  close(p.boundingWidthMm, 100, 1e-12, 'width');
  close(p.boundingHeightMm, 200, 1e-12, 'height');
  close(p.perimeterMm, 2 * (100 + 200), 1e-12, 'perimeterMm');
});

test('hollow rectangle: holes are subtracted (CCW and CW holes agree)', () => {
  const t = 5;
  const outer = 100 * 200;
  const inner = (100 - 2 * t) * (200 - 2 * t);
  const expectedIx = (100 * 200 ** 3 - (100 - 2 * t) * (200 - 2 * t) ** 3) / 12;
  const props = sectionProperties([hollowRectangle(100, 200, t)]);
  close(props.areaMm2, outer - inner, 1e-12, 'areaMm2');
  close(props.ixMm4, expectedIx, 1e-12, 'ixMm4');
  close(props.centroidYMm, 100, 1e-12, 'centroidYMm');

  // the same geometry with the hole wound the other way must give identical numbers
  const reversed = sectionProperties([{
    outline: [
      { x: 0, y: 0 }, { x: 100, y: 0 }, { x: 100, y: 200 }, { x: 0, y: 200 },
    ],
    holes: [[
      { x: t, y: 200 - t }, { x: 100 - t, y: 200 - t }, { x: 100 - t, y: t }, { x: t, y: t },
    ]],
  }]);
  close(reversed.areaMm2, props.areaMm2, 1e-12, 'reversed areaMm2');
  close(reversed.ixMm4, props.ixMm4, 1e-12, 'reversed ixMm4');
});

test('I-section: flanges + web match the closed form', () => {
  const [bf, tf, tw, hw] = [100, 10, 8, 180];
  const props = sectionProperties(iSection(bf, tf, tw, hw));
  const h = hw + 2 * tf;
  const expectedIx = (bf * h ** 3 - (bf - tw) * hw ** 3) / 12;
  const expectedIy = (2 * tf * bf ** 3 + hw * tw ** 3) / 12;
  close(props.areaMm2, 2 * bf * tf + hw * tw, 1e-12, 'areaMm2');
  close(props.ixMm4, expectedIx, 1e-12, 'ixMm4');
  close(props.iyMm4, expectedIy, 1e-12, 'iyMm4');
  close(props.centroidYMm, h / 2, 1e-12, 'centroid y');
  close(props.i1Mm4 + props.i2Mm4, props.ixMm4 + props.iyMm4, 1e-12, 'principal sum invariant');
});

test('composite parts combine by parallel axis (two 50x50 offset by +-100)', () => {
  const parts = [
    rectangle(50, 50, 0, 0),
    rectangle(50, 50, 0, 150),
  ];
  const props = sectionProperties(parts);
  const a = 50 * 50;
  // each centroid is at y=25 and y=175 -> mean 100
  close(props.areaMm2, 2 * a, 1e-12, 'areaMm2');
  close(props.centroidYMm, 100, 1e-12, 'centroidYMm');
  close(props.ixMm4, 2 * ((50 * 50 ** 3) / 12) + 2 * a * 75 ** 2, 1e-12, 'ixMm4');
  close(props.iyMm4, 2 * ((50 * 50 ** 3) / 12), 1e-12, 'iyMm4');
});

test('L-section: product of inertia is non-zero and principal axes are consistent', () => {
  const part = {
    outline: [
      { x: 0, y: 0 }, { x: 100, y: 0 }, { x: 100, y: 10 },
      { x: 10, y: 10 }, { x: 10, y: 100 }, { x: 0, y: 100 },
    ],
  };
  const p = sectionProperties([part]);
  assert.ok(Math.abs(p.ixyMm4) > 1, `ixyMm4 should be significant, got ${p.ixyMm4}`);
  close(p.i1Mm4 + p.i2Mm4, p.ixMm4 + p.iyMm4, 1e-12, 'principal sum invariant');
  assert.ok(p.i1Mm4 > p.i2Mm4);
});

test('translation and 90-degree rotation do not change centroidal properties', () => {
  const base = sectionProperties([hollowRectangle(100, 200, 5)]);
  const moved = sectionProperties([{
    outline: [
      { x: 1000, y: -500 }, { x: 1100, y: -500 }, { x: 1100, y: -300 }, { x: 1000, y: -300 },
    ],
    holes: [[
      { x: 1005, y: -495 }, { x: 1095, y: -495 }, { x: 1095, y: -305 }, { x: 1005, y: -305 },
    ]],
  }]);
  close(moved.areaMm2, base.areaMm2, 1e-12, 'translated areaMm2');
  close(moved.ixMm4, base.ixMm4, 1e-12, 'translated ixMm4');
  close(moved.iyMm4, base.iyMm4, 1e-12, 'translated iyMm4');

  const rotated = sectionProperties([{
    outline: [
      { x: 0, y: 0 }, { x: 0, y: 100 }, { x: -200, y: 100 }, { x: -200, y: 0 },
    ],
    holes: [[
      { x: -5, y: 5 }, { x: -5, y: 95 }, { x: -195, y: 95 }, { x: -195, y: 5 },
    ]],
  }]);
  close(rotated.areaMm2, base.areaMm2, 1e-12, 'rotated areaMm2');
  close(rotated.ixMm4, base.iyMm4, 1e-9, 'rotated ixMm4 == base iyMm4');
  close(rotated.iyMm4, base.ixMm4, 1e-9, 'rotated iyMm4 == base ixMm4');
});

test('static moment above the neutral axis equals the plastic modulus contribution', () => {
  const parts = [rectangle(100, 200)];
  // bisected by the centroid: S = A/2 * (h/4) = 100*100*50
  close(staticMomentAt(parts, 100), 100 * 100 * 50, 1e-12, 'S at mid-height');
  // whole areaMm2 above y=0 equals A * (h/2) = 20000 * 100
  close(staticMomentAt(parts, 0), 20000 * 100, 1e-12, 'S at bottom fibre');
});

test('clipAbove returns the surviving polygon for a convex slice', () => {
  const square = [
    { x: 0, y: 0 }, { x: 10, y: 0 }, { x: 10, y: 10 }, { x: 0, y: 10 },
  ];
  const clipped = clipAbove(square, 5);
  const props = sectionProperties([{ outline: clipped }]);
  close(props.areaMm2, 50, 1e-12, 'clipped areaMm2');
  close(props.centroidYMm, 7.5, 1e-12, 'clipped centroid');
});

test('thin-walled open J: three identical legs equal 3*(b*t^3/3)', () => {
  const midline = [{ x: 0, y: 0 }, { x: 100, y: 0 }, { x: 100, y: 100 }, { x: 0, y: 100 }];
  const t = 5;
  close(thinWalledOpenJ(midline, t), (100 * t ** 3 * 3) / 3, 1e-12, 'J');
});
