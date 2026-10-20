#!/usr/bin/env python3
"""Render candidate profile blocks of a DWG/DXF into contact sheets for visual verification."""
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / f'scripts/poc/{name}.py')
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_blocks = load('dwg-blocks')
_dxf = load('dxf-section')


def draw(ax, segs, title):
    for seg in segs:
        pts = _dxf.polyline_of(seg)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#12263a', lw=0.7)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#ccc')
    ax.set_title(title, fontsize=6.5)


def main(argv):
    path = next((a for a in argv[1:] if not a.startswith('--')), None) or 'evidence/poc/P1/sections/real-profiles.dwg'
    dxf_path, _conv = _blocks.to_dxf_path(path)
    pairs = _blocks.pairs_of(dxf_path)
    names = _blocks.block_record_names(pairs)
    blocks, _ = _blocks.scan_blocks(pairs, names)
    rows = []
    for name, segs in blocks.items():
        if not segs:
            continue
        loops = _dxf.build_loops([_dxf.polyline_of(seg) for seg in segs])
        try:
            props = _dxf.properties(loops)
        except ValueError:
            continue
        w = props['bboxMm'][2] - props['bboxMm'][0]
        h = props['bboxMm'][3] - props['bboxMm'][1]
        if props['areaMm2'] < 50 or max(w, h) > 200:
            continue
        rows.append((name, segs, props, w, h))
    rows.sort(key=lambda r: -r[2]['areaMm2'])
    out_dir = ROOT / 'evidence/poc/P1/sections'
    out_dir.mkdir(parents=True, exist_ok=True)
    per_sheet, cols = 15, 5
    made = []
    for sheet in range((len(rows) + per_sheet - 1) // per_sheet):
        chunk = rows[sheet * per_sheet:(sheet + 1) * per_sheet]
        rows_n = (len(chunk) + cols - 1) // cols
        fig, axes = plt.subplots(rows_n, cols, figsize=(cols * 2.4, rows_n * 2.6))
        axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
        for ax in axes:
            ax.axis('off')
        for ax, (name, segs, props, w, h) in zip(axes, chunk, strict=False):
            ax.axis('on')
            draw(ax, segs, f"{name}\nA={props['areaMm2']:.1f}mm² rings={props['rings']}\n{w:.0f}×{h:.0f}mm")
        fig.tight_layout()
        out = out_dir / f'profiles-sheet-{sheet + 1}.png'
        fig.savefig(out, dpi=130, facecolor='white')
        plt.close(fig)
        made.append(str(out.relative_to(ROOT)))
    print(json.dumps({'file': path, 'candidates': len(rows), 'sheets': made,
                      'names': [r[0] for r in rows]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
