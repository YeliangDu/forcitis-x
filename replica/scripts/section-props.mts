/**
 * CLI: contours JSON -> section properties JSON (used by scripts/poc/compare-profiles.py).
 *   node scripts/section-props.mts <request.json> <result.json>
 * request: { sections: [ { profile_id, parts: [ {outline:[[x,y],...], holes:[[[x,y],...]], transform?} ] } ] }
 */
import { readFileSync, writeFileSync } from 'node:fs';

import { sectionProperties } from '../packages/section/src/index.ts';

type RawPoint = [number, number];
type RawPart = { outline: RawPoint[]; holes?: RawPoint[][]; transform?: { dx?: number; dy?: number; rotate?: number } };
type RawSection = { profile_id: number | string; parts: RawPart[] };

const [, , requestPath, resultPath] = process.argv;
if (!requestPath || !resultPath) {
  process.stderr.write('usage: node scripts/section-props.mts <request.json> <result.json>\n');
  process.exit(64);
}

const toPoints = (raw: RawPoint[]) => raw.map(([x, y]) => ({ x, y }));
const request = JSON.parse(readFileSync(requestPath, 'utf8')) as { sections: RawSection[] };
const sections = request.sections.map((section) => ({
  profile_id: section.profile_id,
  properties: sectionProperties(section.parts.map((part) => ({
    outline: toPoints(part.outline),
    holes: (part.holes ?? []).map(toPoints),
    transform: part.transform,
  }))),
}));
writeFileSync(resultPath, `${JSON.stringify({ sections }, null, 1)}\n`, 'utf8');
process.stdout.write(`sections=${sections.length}\n`);
