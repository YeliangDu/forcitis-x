/**
 * Section geometry -> section properties (PoC P1).
 *
 * Scope and rules (see docs/poc-mvp-plan.md P1):
 *  - pure functions, no IO, no clock, no randomness: same input => same output bytes;
 *  - exact polygon formulas (signed areaMm2), so holes are subtracted by orientation, not by guessing;
 *  - a "part" is one polygon with optional holes and an optional rigid transform; a section is a list
 *    of parts combined by parallel-axis accumulation about the global origin;
 *  - everything is reported in the section's own unit system (no unit conversion here).
 *
 * Not implemented on purpose: torsional constant J (needs thin-wall midline + thickness, see
 * `thinWalledOpenJ`) and any plasticity/effective-width logic. Those are out of P1 scope and must be
 * validated separately against the original system's `JA`/`CJ` columns.
 */

export type Point = { readonly x: number; readonly y: number };

export type Transform = {
  /** translation, same unit as the polygon */
  readonly dx?: number;
  readonly dy?: number;
  /** counter-clockwise rotation in radians */
  readonly rotate?: number;
};

export type Part = {
  readonly name?: string;
  /** outer boundary; orientation is normalised internally */
  readonly outline: readonly Point[];
  readonly holes?: readonly (readonly Point[])[];
  readonly transform?: Transform;
};

export type SectionProperties = {
  readonly areaMm2: number;
  /** centroid in input coordinates */
  readonly centroidXMm: number;
  readonly centroidYMm: number;
  /** second moments about the centroidal axes */
  readonly ixMm4: number;
  readonly iyMm4: number;
  readonly ixyMm4: number;
  /** principal second moments and the angle (radians) of the major axis from +x */
  readonly i1Mm4: number;
  readonly i2Mm4: number;
  readonly principalAngleRad: number;
  /** section moduli to the extreme fibres */
  readonly wxTopMm3: number;
  readonly wxBottomMm3: number;
  readonly wyLeftMm3: number;
  readonly wyRightMm3: number;
  /** smallest section modulus of the four fibres */
  readonly wMinMm3: number;
  /** radii of gyration */
  readonly radiusOfGyrationXMm: number;
  readonly radiusOfGyrationYMm: number;
  /** bounding box */
  readonly minXMm: number;
  readonly maxXMm: number;
  readonly minYMm: number;
  readonly maxYMm: number;
  readonly perimeterMm: number;
  readonly boundingWidthMm: number;
  readonly boundingHeightMm: number;
  /** number of polygons actually summed (outline + holes, all parts) */
  readonly contourCount: number;
};

type Accum = {
  areaMm2: number;
  sx: number; // first moment about y axis (A*centroidXMm)
  sy: number; // first moment about x axis (A*centroidYMm)
  ixMm4: number; // second moment about x axis through origin
  iyMm4: number; // second moment about y axis through origin
  ixyMm4: number; // product of inertia about origin
  minXMm: number;
  maxXMm: number;
  minYMm: number;
  maxYMm: number;
  perimeterMm: number;
  contourCount: number;
};

function emptyAccum(): Accum {
  return {
    areaMm2: 0, sx: 0, sy: 0, ixMm4: 0, iyMm4: 0, ixyMm4: 0,
    minXMm: Infinity, maxXMm: -Infinity, minYMm: Infinity, maxYMm: -Infinity,
    perimeterMm: 0, contourCount: 0,
  };
}

/** Bounds-checked read so the numeric loops are sound under strict indexing. */
function pointAt(points: readonly Point[], index: number): Point {
  const point = points[index];
  if (point === undefined) throw new Error(`point ${index} out of range (${points.length} points)`);
  return point;
}

function signedArea(points: readonly Point[]): number {
  let sum = 0;
  for (let i = 0; i < points.length; i += 1) {
    const a = pointAt(points, i);
    const b = pointAt(points, (i + 1) % points.length);
    sum += a.x * b.y - b.x * a.y;
  }
  return sum / 2;
}

function applyTransform(points: readonly Point[], transform: Transform | undefined): Point[] {
  const dx = transform?.dx ?? 0;
  const dy = transform?.dy ?? 0;
  const angle = transform?.rotate ?? 0;
  if (dx === 0 && dy === 0 && angle === 0) return points.map((p) => ({ x: p.x, y: p.y }));
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return points.map((p) => ({
    x: dx + p.x * cos - p.y * sin,
    y: dy + p.x * sin + p.y * cos,
  }));
}

/** Sum one contour (already orientation-normalised by the caller) into the accumulator. */
function accumulateContour(acc: Accum, points: readonly Point[]): void {
  const n = points.length;
  if (n < 3) throw new Error(`contour needs >= 3 points, got ${n}`);
  let a2 = 0; // 2*areaMm2
  let centroidXMm = 0;
  let centroidYMm = 0;
  let ixMm4 = 0;
  let iyMm4 = 0;
  let ixyMm4 = 0;
  let perimeterMm = 0;
  for (let i = 0; i < n; i += 1) {
    const p = pointAt(points, i);
    const q = pointAt(points, (i + 1) % n);
    const cross = p.x * q.y - q.x * p.y;
    a2 += cross;
    centroidXMm += (p.x + q.x) * cross;
    centroidYMm += (p.y + q.y) * cross;
    ixMm4 += (p.y * p.y + p.y * q.y + q.y * q.y) * cross;
    iyMm4 += (p.x * p.x + p.x * q.x + q.x * q.x) * cross;
    ixyMm4 += (p.x * q.y + 2 * p.x * p.y + 2 * q.x * q.y + q.x * p.y) * cross;
    perimeterMm += Math.hypot(q.x - p.x, q.y - p.y);
  }
  const areaMm2 = a2 / 2;
  if (areaMm2 === 0) throw new Error('degenerate contour (zero areaMm2)');
  acc.areaMm2 += areaMm2;
  acc.sx += centroidXMm / 6; // (1/6)*sum((x_i+x_j)*cross) == A*centroidXMm
  acc.sy += centroidYMm / 6;
  acc.ixMm4 += ixMm4 / 12;
  acc.iyMm4 += iyMm4 / 12;
  acc.ixyMm4 += ixyMm4 / 24;
  acc.perimeterMm += perimeterMm;
  acc.contourCount += 1;
  for (const p of points) {
    if (p.x < acc.minXMm) acc.minXMm = p.x;
    if (p.x > acc.maxXMm) acc.maxXMm = p.x;
    if (p.y < acc.minYMm) acc.minYMm = p.y;
    if (p.y > acc.maxYMm) acc.maxYMm = p.y;
  }
}

export function sectionProperties(parts: readonly Part[]): SectionProperties {
  if (parts.length === 0) throw new Error('empty section');
  const acc = emptyAccum();
  for (const part of parts) {
    const outline = applyTransform(part.outline, part.transform);
    // outer boundary must be counter-clockwise (positive signed areaMm2)
    const outer = signedArea(outline) >= 0 ? outline : outline.toReversed();
    accumulateContour(acc, outer);
    for (const hole of part.holes ?? []) {
      const ring = applyTransform(hole, part.transform);
      // holes must be clockwise so their signed contributions subtract exactly
      const ring2 = signedArea(ring) <= 0 ? ring : ring.toReversed();
      accumulateContour(acc, ring2);
    }
  }
  const areaMm2 = acc.areaMm2;
  if (!(areaMm2 > 0)) throw new Error(`non-positive total areaMm2 (${areaMm2}); check outline/hole orientation`);
  const centroidXMm = acc.sx / areaMm2;
  const centroidYMm = acc.sy / areaMm2;
  const ixMm4 = acc.ixMm4 - areaMm2 * centroidYMm * centroidYMm;
  const iyMm4 = acc.iyMm4 - areaMm2 * centroidXMm * centroidXMm;
  const ixyMm4 = acc.ixyMm4 - areaMm2 * centroidXMm * centroidYMm;
  const mean = (ixMm4 + iyMm4) / 2;
  const radius = Math.hypot((ixMm4 - iyMm4) / 2, ixyMm4);
  const i1Mm4 = mean + radius;
  const i2Mm4 = mean - radius;
  const principalAngleRad = 0.5 * Math.atan2(-2 * ixyMm4, iyMm4 - ixMm4);
  const yTop = acc.maxYMm - centroidYMm;
  const yBottom = centroidYMm - acc.minYMm;
  const xRight = acc.maxXMm - centroidXMm;
  const xLeft = centroidXMm - acc.minXMm;
  const wxTopMm3 = yTop > 0 ? ixMm4 / yTop : Infinity;
  const wxBottomMm3 = yBottom > 0 ? ixMm4 / yBottom : Infinity;
  const wyLeftMm3 = xLeft > 0 ? iyMm4 / xLeft : Infinity;
  const wyRightMm3 = xRight > 0 ? iyMm4 / xRight : Infinity;
  return {
    areaMm2, centroidXMm, centroidYMm, ixMm4, iyMm4, ixyMm4, i1Mm4, i2Mm4, principalAngleRad,
    wxTopMm3, wxBottomMm3, wyLeftMm3, wyRightMm3,
    wMinMm3: Math.min(wxTopMm3, wxBottomMm3, wyLeftMm3, wyRightMm3),
    radiusOfGyrationXMm: Math.sqrt(ixMm4 / areaMm2),
    radiusOfGyrationYMm: Math.sqrt(iyMm4 / areaMm2),
    minXMm: acc.minXMm, maxXMm: acc.maxXMm, minYMm: acc.minYMm, maxYMm: acc.maxYMm,
    perimeterMm: acc.perimeterMm,
    boundingWidthMm: acc.maxXMm - acc.minXMm,
    boundingHeightMm: acc.maxYMm - acc.minYMm,
    contourCount: acc.contourCount,
  };
}

/** Rectangle helper: width along x, height along y, origin at the lower-left corner. */
export function rectangle(width: number, height: number, dx = 0, dy = 0): Part {
  return {
    outline: [
      { x: 0, y: 0 }, { x: width, y: 0 }, { x: width, y: height }, { x: 0, y: height },
    ],
    transform: { dx, dy },
  };
}

/** Rectangle with a concentric rectangular hole (box section), origin at the lower-left corner. */
export function hollowRectangle(width: number, height: number, thickness: number): Part {
  const t = thickness;
  return {
    outline: [
      { x: 0, y: 0 }, { x: width, y: 0 }, { x: width, y: height }, { x: 0, y: height },
    ],
    holes: [[
      { x: t, y: t }, { x: width - t, y: t }, { x: width - t, y: height - t }, { x: t, y: height - t },
    ]],
  };
}

/** I-section: two flanges (b x tf) plus a web (tw x hw), overall height = hw + 2*tf. */
export function iSection(flangeWidth: number, flangeThickness: number, webThickness: number,
                         webHeight: number): Part[] {
  const tf = flangeThickness;
  const bw = (flangeWidth - webThickness) / 2;
  return [
    rectangle(flangeWidth, tf, 0, 0),                          // bottom flange
    rectangle(webThickness, webHeight, bw, tf),                 // web
    rectangle(flangeWidth, tf, 0, tf + webHeight),              // top flange
  ];
}

/**
 * Clip a polygon to the half plane y >= y0 (Sutherland-Hodgman) and return the clipped outline.
 * Used for the first moment of areaMm2 above/below a level (`staticMomentAt`).
 */
export function clipAbove(points: readonly Point[], y0: number): Point[] {
  const out: Point[] = [];
  for (let i = 0; i < points.length; i += 1) {
    const a = pointAt(points, i);
    const b = pointAt(points, (i + 1) % points.length);
    const aIn = a.y >= y0;
    const bIn = b.y >= y0;
    if (aIn) out.push({ x: a.x, y: a.y });
    if (aIn !== bIn) {
      const t = (y0 - a.y) / (b.y - a.y);
      out.push({ x: a.x + t * (b.x - a.x), y: y0 });
    }
  }
  return out;
}

/**
 * First moment of the areaMm2 above level y about the horizontal axis at y, i.e. S(y) = sum(A_i * d_i)
 * where d_i is the distance of each sub-areaMm2 centroid above y. Needed for shear stress tau = Q*S/(I*t).
 */
export function staticMomentAt(parts: readonly Part[], y: number): number {
  let moment = 0;
  for (const part of parts) {
    const outline = applyTransform(part.outline, part.transform);
    const rings: Point[][] = [outline];
    for (const hole of part.holes ?? []) rings.push(applyTransform(hole, part.transform));
    for (const ring of rings) {
      const clipped = clipAbove(ring, y);
      if (clipped.length < 3) continue;
      const props = sectionProperties([{ outline: clipped }]);
      moment += props.areaMm2 * (props.centroidYMm - y);
    }
  }
  return moment;
}

/**
 * Thin-walled *open* section torsion constant, J = (1/3) * sum(b_i * t_i^3), from a midline polyline
 * with a constant thickness. Explicitly approximate: it ignores corner fillets, closed-cell (Bredt)
 * behaviour and warping restraint, so it must be checked against the original system's JA column
 * before it is used in a verdict.
 */
export function thinWalledOpenJ(midline: readonly Point[], thickness: number): number {
  if (thickness <= 0) throw new Error('thickness must be positive');
  let sum = 0;
  for (let i = 0; i < midline.length - 1; i += 1) {
    const a = pointAt(midline, i);
    const b = pointAt(midline, i + 1);
    sum += Math.hypot(b.x - a.x, b.y - a.y) * thickness ** 3;
  }
  return sum / 3;
}
