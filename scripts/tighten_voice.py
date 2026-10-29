"""Сжимает длинные паузы в записи голоса (удержание: короткие паузы = динамичнее) и пересчитывает тайминги слов.

Запуск из корня video-stack:
  OpenMontage/.venv/bin/python scripts/tighten_voice.py <slug> [макс_пауза=0.5] [оставить=0.32]
Читает:  OpenMontage/projects/<slug>/assets/audio/human/raw.wav + words.json (scripts/transcribe.py)
Пишет:   raw.wav (сжатый), words.json (новые тайминги); оригиналы в raw_orig.wav и words_orig.json
Паузой считается промежуток между словами длиннее макс_пауза; он укорачивается до «оставить» (середина вырезается, стык 15 мс кроссфейдом).
"""
import json
import shutil
import sys
import wave
from pathlib import Path

import numpy as np

root = Path(__file__).resolve().parent.parent
slug = sys.argv[1]
max_gap = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
keep = float(sys.argv[3]) if len(sys.argv) > 3 else 0.32
d = root / "OpenMontage/projects" / slug / "assets/audio/human"
if not (d / "raw_orig.wav").exists():  # повторный запуск не должен сжимать уже сжатое
    shutil.copy(d / "raw.wav", d / "raw_orig.wav")
    shutil.copy(d / "words.json", d / "words_orig.json")
words = json.loads((d / "words_orig.json").read_text(encoding="utf-8"))
with wave.open(str(d / "raw_orig.wav")) as w:
    sr, n = w.getframerate(), w.getnframes()
    x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32)

# вырезаемые интервалы (сек): середина каждой длинной паузы
cuts = []
for a, b in zip(words, words[1:]):
    gap = b["s"] - a["e"]
    if gap > max_gap:
        cut = gap - keep
        c0 = a["e"] + keep / 2
        cuts.append((c0, c0 + cut))
# дополнительно: пауза в начале
lead = words[0]["s"]
if lead > 0.25:
    cuts.insert(0, (0.0, lead - 0.15))

pieces, pos = [], 0.0
for c0, c1 in cuts:
    pieces.append((pos, c0))
    pos = c1
pieces.append((pos, n / sr))
xf = int(0.015 * sr)
out = np.zeros(0, dtype=np.float32)
for i, (p0, p1) in enumerate(pieces):
    seg = x[int(p0 * sr): int(p1 * sr)].copy()
    if i > 0 and len(out) > xf and len(seg) > xf:
        fade = np.linspace(0, 1, xf)
        out[-xf:] = out[-xf:] * (1 - fade) + seg[:xf] * fade
        seg = seg[xf:]
    out = np.concatenate([out, seg])
with wave.open(str(d / "raw.wav"), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(np.clip(out, -32768, 32767).astype(np.int16).tobytes())


def shift(t):
    s = 0.0
    for c0, c1 in cuts:
        if t >= c1:
            s += c1 - c0
        elif t > c0:
            s += t - c0
    return t - s


new = [{"w": w_["w"], "s": round(shift(w_["s"]), 3), "e": round(shift(w_["e"]), 3)} for w_ in words]
(d / "words.json").write_text(json.dumps(new, ensure_ascii=False, indent=0), encoding="utf-8")
removed = sum(c1 - c0 for c0, c1 in cuts)
print(f"вырезано пауз: {len(cuts)}, убрано {removed:.2f} с; длина {n / sr:.2f} -> {len(out) / sr:.2f} с")
