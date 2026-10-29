#!/usr/bin/env bash
# Очистка записи голоса, микс с музыкой, муксинг в видео, проверка звука замерами.
# Использование: scripts/mix_human_voice.sh <slug> <голос.(ogg|wav|mp3|m4a)> [silent.mp4] [bgm.wav]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)/OpenMontage"
SLUG="${1:?slug}"; VOICE="${2:?файл голоса}"; SILENT="${3:-silent.mp4}"; BGM="${4:-assets/music/bgm.wav}"
FF="$ROOT/.venv/bin/ffmpeg"
VOICE="$(cd "$(dirname "$VOICE")" && pwd)/$(basename "$VOICE")"  # абсолютный путь до cd
cd "$ROOT/projects/$SLUG"
mkdir -p assets/audio/human
RAW="$PWD/assets/audio/human/raw.wav"
if [ "$VOICE" != "$RAW" ]; then   # не конвертировать файл сам в себя
  "$FF" -y -nostdin -hide_banner -loglevel error -i "$VOICE" -ar 48000 -ac 1 "$RAW"
fi
"$FF" -y -nostdin -hide_banner -loglevel error -i assets/audio/human/raw.wav \
  -af "highpass=f=90,afftdn=nr=14:nf=-32:tn=1,acompressor=threshold=0.1:ratio=3:attack=8:release=120:makeup=2,alimiter=limit=0.95" \
  -ar 48000 assets/audio/human/voice_clean.wav
# голос сдвинут на 0.3 с, музыка приглушается под речью (sidechain), итог 30 с
"$FF" -y -nostdin -hide_banner -loglevel error -i assets/audio/human/voice_clean.wav -i "$BGM" -filter_complex \
"[0]aformat=channel_layouts=stereo,adelay=300:all=1,apad=whole_dur=30,atrim=0:30,asplit=2[vo1][vo2];\
[1]aresample=48000,aformat=channel_layouts=stereo,volume=0.33[m];\
[m][vo1]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=500[md];\
[vo2]volume=1.2[v];\
[md][v]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95,atrim=0:30[mix]" \
  -map "[mix]" -ar 48000 assets/audio/mix_human.wav
"$FF" -y -nostdin -hide_banner -loglevel error -i "renders/$SILENT" -i assets/audio/mix_human.wav \
  -map 0:v -map 1:a -c:v copy -af "loudnorm=I=-14:TP=-1.0:LRA=7,aresample=48000" \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart renders/final_new.mp4
echo "--- проверка: речь должна быть заметно громче музыки в паузе ---"
m(){ printf "%s+%s c: " "$1" "$2"; "$FF" -nostdin -hide_banner -ss "$1" -t "$2" -i renders/final_new.mp4 -vn -af volumedetect -f null - 2>&1 | grep mean_volume | sed 's/.*mean_volume: //'; }
m 5 2; m 12 2; m 28 1.5
echo "готово: $PWD/renders/final_new.mp4 (переименуй в final.mp4 после проверки)"
