#!/usr/bin/env bash
# Подготовка окружения: клонирует OpenMontage (закреплённый коммит), ставит зависимости.
set -euo pipefail
cd "$(dirname "$0")"
PIN=c8066452325cb57c8fc1ba8c2a71b6e8842e6b65
if [ ! -d OpenMontage ]; then
  git clone https://github.com/calesthio/OpenMontage.git OpenMontage
fi
git -C OpenMontage checkout "$PIN"
(cd OpenMontage && make setup)
# ffmpeg для OpenMontage-инструментов (если нет системного ffmpeg)
if ! command -v ffmpeg >/dev/null; then
  OpenMontage/.venv/bin/python -m pip install imageio-ffmpeg
  ln -sf "$(OpenMontage/.venv/bin/python -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')" OpenMontage/.venv/bin/ffmpeg
fi
command -v ffprobe >/dev/null || echo "ВНИМАНИЕ: нет ffprobe. ffmpeg-skill не заработает: установите полный ffmpeg (brew install ffmpeg / apt install ffmpeg)."
OpenMontage/.venv/bin/python -m pip install faster-whisper numpy
echo "Готово. Проверка скилла: PATH=\"\$PWD/OpenMontage/.venv/bin:\$PATH\" python3 .claude/skills/ffmpeg-skill/scripts/_contract.py doctor"
