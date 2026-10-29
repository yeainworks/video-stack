"""Склеить кадры (still) в один контактный лист для быстрой приёмки.

Сначала отрендерить кадры:
  cd OpenMontage/remotion-composer
  npx remotion still projects/<slug>/index.tsx <CompositionId> ../projects/<slug>/stills/h<N>.png --frame=<N> --bundle-cache=false
Потом:
  OpenMontage/.venv/bin/python scripts/contact_sheet.py <slug> 60 150 240 375 ...
Результат: OpenMontage/projects/<slug>/stills/contact.png
"""
import sys
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parent.parent / "OpenMontage"
slug, frames = sys.argv[1], [int(x) for x in sys.argv[2:]]
d = root / "projects" / slug / "stills"
w, h, cols = 360, 640, 4
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows), (30, 30, 30))
for i, n in enumerate(frames):
    im = Image.open(d / f"h{n}.png").convert("RGB").resize((w, h))
    sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(d / "contact.png")
print(d / "contact.png")
