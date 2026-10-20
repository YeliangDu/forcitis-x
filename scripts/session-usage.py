#!/usr/bin/env python3
"""Report the session's token usage from PI_SESSION_FILE (same source as the status line).

Used as the single, measured trigger for handoff (docs/engineering-standards.md ES-09).
Exit code: 0 below threshold, 3 at/above threshold (>= 75% of the model context).

Usage: python3 scripts/session-usage.py [--threshold 0.75]
"""
import json
import os
import sys

THRESHOLD = 0.75


def main(argv):
    threshold = float(argv[argv.index('--threshold') + 1]) if '--threshold' in argv else THRESHOLD
    path = os.environ.get('PI_SESSION_FILE')
    if not path or not os.path.isfile(path):
        print('unknown: PI_SESSION_FILE not readable (cannot measure, do not guess)')
        return 2
    tin = tout = cache_read = cache_write = cost = 0
    last = 0
    with open(path, encoding='utf-8') as handle:
        lines = handle.readlines()
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = (record.get('message') or {}).get('usage')
        if not usage:
            continue
        tin += usage.get('input', 0)
        tout += usage.get('output', 0)
        cache_read += usage.get('cacheRead', 0)
        cache_write += usage.get('cacheWrite', 0)
        cost += (usage.get('cost') or {}).get('total', 0)
        last = usage.get('totalTokens', last)
    hit = cache_read / max(1, cache_read + tin)
    used = last / 1_000_000
    print(f'↑ input      {tin/1000:9.1f} k')
    print(f'↓ output     {tout/1000:9.1f} k')
    print(f'R cacheRead  {cache_read/1e6:9.2f} M')
    print(f'CH hit rate  {hit*100:9.2f} %')
    print(f'$ cost       {cost:9.4f}')
    print(f'context      {used*100:9.2f} % of 1.0M  (threshold {threshold*100:.0f}%)')
    if used >= threshold:
        print('HANDOFF: threshold reached — write HANDOFF.md before continuing')
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
