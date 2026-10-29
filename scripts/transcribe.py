"""Расшифровка голоса с таймингом слов (faster-whisper, модель small, русский).

Запуск из корня video-stack:
  OpenMontage/.venv/bin/python scripts/transcribe.py <slug> [путь_к_wav]
Результат: OpenMontage/projects/<slug>/assets/audio/human/words.json
"""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

root = Path(__file__).resolve().parent.parent / "OpenMontage"
slug = sys.argv[1]
wav = sys.argv[2] if len(sys.argv) > 2 else str(root / "projects" / slug / "assets/audio/human/raw.wav")

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, _ = model.transcribe(wav, language="ru", word_timestamps=True, vad_filter=False)
words = [
    {"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
    for seg in segments
    for w in seg.words
]
out = root / "projects" / slug / "assets/audio/human/words.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(words, ensure_ascii=False, indent=0), encoding="utf-8")
print(" ".join(f'{x["w"]}[{x["s"]}]' for x in words))
print(f"\n{len(words)} слов -> {out}")
