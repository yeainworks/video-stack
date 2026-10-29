"""Финальный звук ролика: голос + звуковые эффекты по якорям + бодрая музыка (sidechain) + нормализация + муксинг.

Запуск из корня video-stack:
  OpenMontage/.venv/bin/python scripts/mix_video.py <slug> <папка-ролика> <voice.wav> [music.wav] [silent.mp4] [out.mp4]
Читает: <папка>/timing.json (якоря) и <папка>/sfx.json (звуковые события), <проект>/sfx/*.wav
Голос сдвигается на offset из timing.json (по умолчанию 0.3 с). Пишет renders/<out> и печатает замеры.
"""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project import project_dir, resolve_arg
wh = project_dir()
# флаги: --sfx (включить звуковые эффекты; по умолчанию ВЫКЛЮЧЕНЫ по правилу проекта), --music=0.10 (громкость музыки)
FLAGS = [a for a in sys.argv[1:] if a.startswith("--")]
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:] if not a.startswith("--")]
SFX_ON = "--sfx" in FLAGS
MUSIC_VOL = next((float(f.split("=")[1]) for f in FLAGS if f.startswith("--music=")), 0.10)
slug, vdir, voice = sys.argv[1], resolve_arg(sys.argv[2]), Path(sys.argv[3]).resolve()
music = Path(sys.argv[4]).resolve() if len(sys.argv) > 4 else wh / "sfx/bgm_upbeat.wav"
silent = sys.argv[5] if len(sys.argv) > 5 else "silent.mp4"
out = sys.argv[6] if len(sys.argv) > 6 else "final_new.mp4"
proj = root / "OpenMontage/projects" / slug
ff = str(root / "OpenMontage/.venv/bin/ffmpeg")
sfxdir = wh / "sfx"
timing = json.loads((vdir / "timing.json").read_text(encoding="utf-8"))
cues = json.loads((vdir / "sfx.json").read_text(encoding="utf-8"))["cues"] if (vdir / "sfx.json").exists() else []  # sfx.json нужен только для --sfx
offset_ms = int(round(timing.get("offset", 0.3) * 1000))
DUR = timing.get("duration", 27.6)

inputs = ["-i", str(voice), "-i", str(music)]
flt = [
    f"[0]aresample=48000,highpass=f=90,afftdn=nr=14:nf=-32:tn=1,loudnorm=I=-17:TP=-2:LRA=7,acompressor=threshold=0.1:ratio=3:attack=8:release=120:makeup=2,"
    f"aformat=channel_layouts=stereo,adelay={offset_ms}:all=1,apad=whole_dur={DUR},atrim=0:{DUR},asplit=2[vo1][vo2]",
    f"[1]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{DUR},volume={MUSIC_VOL}[m]",
]
labels = []
cues = [c for c in cues if "t" in c or c["at"] in timing["anchors"]] if SFX_ON else []  # без --sfx эффектов нет
if SFX_ON:
    cues.append({"sfx": "whoosh", "t": DUR - 0.4, "v": 0.5})  # петля в конце
for i, c in enumerate(cues):
    t = c["t"] if "t" in c else timing["anchors"][c["at"]]["s"] + c.get("d", 0.0)
    t = max(0.0, t)
    inputs += ["-i", str(sfxdir / f"{c['sfx']}.wav")]
    idx = 2 + i
    flt.append(f"[{idx}]aresample=48000,aformat=channel_layouts=stereo,adelay={int(t * 1000)}:all=1,volume={c.get('v', 0.7)}[c{i}]")
    labels.append(f"[c{i}]")
if labels:
    flt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR},volume=0.9[sfx]")
flt.append("[m][vo1]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=500[md]")
flt.append("[vo2]volume=1.2[v]")
if labels:
    flt.append(f"[md][v][sfx]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95,atrim=0:{DUR}[mix]")
else:
    flt.append(f"[md][v]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95,atrim=0:{DUR}[mix]")

mix = proj / "assets/audio/mix_video.wav"
mix.parent.mkdir(parents=True, exist_ok=True)
subprocess.run([ff, "-y", "-nostdin", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", ";".join(flt), "-map", "[mix]", "-ar", "48000", str(mix)], check=True)
dst = proj / "renders" / out
subprocess.run(
    [ff, "-y", "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(proj / "renders" / silent), "-i", str(mix), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
     "-af", "loudnorm=I=-14:TP=-1.0:LRA=7,aresample=48000", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(dst)],
    check=True,
)


def mean_db(t, d):
    r = subprocess.run([ff, "-nostdin", "-hide_banner", "-ss", str(t), "-t", str(d), "-i", str(dst), "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "mean_volume" in line:
            return line.split("mean_volume:")[1].strip()
    return "?"


print("готово:", dst)
sp = timing["speechEnd"]
print(f"SFX: {'вкл' if SFX_ON else 'ВЫКЛ'}, музыка {MUSIC_VOL}")
print(f"замеры (речь должна быть громче пауз): 3-5 с {mean_db(3, 2)} | 12-14 с {mean_db(12, 2)} | после речи {sp + 0.1:.1f}-{sp + 0.9:.1f} с {mean_db(sp + 0.1, 0.8)}")
