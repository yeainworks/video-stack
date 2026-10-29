#!/usr/bin/env bash
# Рендер немого видео из Remotion-композиции.
# Использование: scripts/render.sh <slug> [CompositionId] [out-name]
#   slug           папка в OpenMontage/projects/<slug> (например my-video-01)
#   CompositionId  по умолчанию Main (или COMPOSITION_ID)
#   out-name       по умолчанию silent.mp4
# Композиция должна лежать реальным файлом в remotion-composer/projects/<slug>/index.tsx.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)/OpenMontage"
SLUG="${1:?slug}"; COMP="${2:-${COMPOSITION_ID:-Main}}"; OUT="${3:-silent.mp4}"
SRC="$ROOT/projects/$SLUG/index.tsx"; DST="$ROOT/remotion-composer/projects/$SLUG/index.tsx"
[ -f "$SRC" ] || { echo "нет $SRC"; exit 1; }
mkdir -p "$(dirname "$DST")" "$ROOT/projects/$SLUG/renders"
cp "$SRC" "$DST"                       # симлинк не работает: бандлер теряет node_modules
echo "свободно на диске:"; df -h / | tail -1
cd "$ROOT/remotion-composer"
npx remotion render "projects/$SLUG/index.tsx" "$COMP" "../projects/$SLUG/renders/$OUT" --crf=18 --bundle-cache=false
