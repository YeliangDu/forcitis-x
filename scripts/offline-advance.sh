#!/bin/sh
# 离线无人值守推进器（幂等、可中断、失败不破坏已有产物）
#
# 做的事（只用离线能力，不碰实机 GUI、不写数据库）：
#   1. 把尚未反编译的 CXMap 节点 eval 分批跑完（已缓存的自动跳过）
#   2. 每批产出 migration_workspace/nodes-<族>.md
#   3. 把进展追加到 migration_workspace/UNATTENDED.log 与 状态文件
#
# 不做的事：不连 Windows 实机、不改数据库、不安装/重启任何服务、不动 vendor/。
#
# 用法：  sh scripts/offline-advance.sh            # 跑一轮（每轮约 30–60 分钟）
#         LOCK=/tmp/x.lock sh scripts/offline-advance.sh
set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT" || exit 1
LOG="$ROOT/migration_workspace/UNATTENDED.log"
STATE="$ROOT/migration_workspace/UNATTENDED.state"
LOCK="${LOCK:-$ROOT/migration_workspace/.cache/offline-advance.lock}"
mkdir -p "$ROOT/migration_workspace/.cache"

: "${GHIDRA_INSTALL_DIR:=$HOME/tools/ghidra_12.1.4_PUBLIC}"
export GHIDRA_INSTALL_DIR

# 单实例：已在跑就直接退出，避免并发 Ghidra 抢 CPU
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "$(date -u +%FT%TZ) skip: 已有实例在运行" >>"$LOG"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT INT TERM

echo "$(date -u +%FT%TZ) start" >>"$LOG"

# 分批推进：每批一个族，跑完即写产物；任一批失败不阻断后续批次
for spec in \
  "calc-check-do|^Cal(l)?Glass|^CalcGlass|^Check|^Do|^GetRGlass" \
  "glassmesh|^Get(Glass|RGlass|DSlope|Layout)" \
  "pole|Pole" \
  "venetian-grille|Venetian|Grille" \
  "fe-a|^FEAdd[ABCDLNP]" \
  "fe-b|^FEAdd" \
  "other-a|^Get" \
  "other-b|." ; do
  family=${spec%%|*}
  pattern=${spec#*|}
  echo "$(date -u +%FT%TZ) batch $family" >>"$LOG"
  python3 scripts/batch-node-dossier.py --family "$family" --pattern "$pattern" \
      >>"$LOG" 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) batch $family exit=$rc" >>"$LOG"
done

python3 - <<'PY' >"$STATE"
import json, glob, os
done = len(glob.glob('migration_workspace/raw/nodes/*.rea.json'))
print(json.dumps({'nodes_decompiled': done, 'target': 379,
                  'updated': __import__('datetime').datetime.utcnow().isoformat() + 'Z'},
                 ensure_ascii=False))
PY

echo "$(date -u +%FT%TZ) done nodes=$(python3 -c "import json;print(json.load(open('$STATE'))['nodes_decompiled'])")" >>"$LOG"
