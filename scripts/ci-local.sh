#!/bin/sh
# Local equivalent of .github/workflows/ci.yml — same steps, same order, fails fast.
set -eu
echo "== install"
(cd replica && npm ci --no-audit --no-fund >/dev/null)
echo "== build + lint + test"
(cd replica && npm run check)
echo "== python syntax"
python3 -m compileall -q scripts
echo "== standards gate"
python3 scripts/check-standards.py
echo "== acceptance ledger self-test"
python3 scripts/check-acceptance.py --self-test
echo "CI-LOCAL: PASS"
