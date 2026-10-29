#!/usr/bin/env bash
# Синхронизирует дизайн-систему канала в папку, откуда её видит Remotion.
# Источник правды: <проект>/design/ (brand.tsx, preview.tsx, tokens.json) + <проект>/brand-assets/avatar.png
# Результат: OpenMontage/remotion-composer/projects/_brand/ (физические файлы, симлинк не работает).
# Использование: scripts/sync_design.sh   (запускать после любой правки дизайна и перед рендером ролика)
# В композиции: import { C, Background, Captions, ... } from "../_brand/brand";
set -euo pipefail
V="$(cd "$(dirname "$0")/.." && pwd)"
WH="$(python3 -c "import sys; sys.path.insert(0,'$V/scripts'); from _project import project_dir; print(project_dir())")"
DST="$V/OpenMontage/remotion-composer/projects/_brand"
mkdir -p "$DST"
cp "$WH/design/brand.tsx" "$WH/design/preview.tsx" "$WH/design/tokens.json" "$DST/"
# аватар зашивается в код как data URI (импорт png из вне remotion-composer не работает)
python3 - "$WH/brand-assets/avatar.png" "$DST/avatar.ts" <<'EOF'
import base64, sys
data = base64.b64encode(open(sys.argv[1], "rb").read()).decode()
open(sys.argv[2], "w").write(f'export const AVATAR_DATA_URI = "data:image/png;base64,{data}";\n')
EOF
echo "дизайн синхронизирован: $DST"
