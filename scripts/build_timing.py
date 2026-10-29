"""Строит timing.json для ролика: тайминги слов сценария и якорей для анимации.

Идея: распознавание (faster-whisper) даёт тайминги, но ошибается в словах. Поэтому берём слова из
СЦЕНАРИЯ (<проект>/videos/NN-slug/spoken.txt) и выравниваем их по распознанным (динамическое
программирование), тайминги переносим на слова сценария. Работает и для синтетического, и для живого голоса.

Запуск из корня video-stack:
  OpenMontage/.venv/bin/python scripts/build_timing.py <slug> <папка-ролика-в-проекте/videos> [offset_sec]
Нужно: OpenMontage/projects/<slug>/assets/audio/human/words.json (scripts/transcribe.py)
       <папка>/spoken.txt (что говорим), <папка>/anchors.json ({имя: "слово"|["слово", n-е вхождение]}),
       <папка>/display.json (необязательно: {"тридцать процентов": "30%"})
Результат: <папка>/timing.json + копия в remotion-composer/projects/<slug>/timing.json
"""
import difflib
import json
import re
import shutil
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project import resolve_arg
slug, vdir = sys.argv[1], resolve_arg(sys.argv[2])
offset = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

heard = json.loads((root / "OpenMontage/projects" / slug / "assets/audio/human/words.json").read_text(encoding="utf-8"))
norm = lambda s: re.sub(r"[^\wё]+", "", s.lower().replace("ё", "е"))
spoken_text = (vdir / "spoken.txt").read_text(encoding="utf-8")
script = [w for w in re.findall(r"\S+", spoken_text)]
A = [norm(w) for w in script]
B = [norm(h["w"]) for h in heard]

# --- выравнивание (Needleman-Wunsch по сходству слов) ---
n, m = len(A), len(B)
GAP = -0.45
sim = lambda a, b: (difflib.SequenceMatcher(None, a, b).ratio() * 2 - 1) if a and b else -1
dp = [[0.0] * (m + 1) for _ in range(n + 1)]
bk = [[None] * (m + 1) for _ in range(n + 1)]
for i in range(1, n + 1):
    dp[i][0], bk[i][0] = i * GAP, "u"
for j in range(1, m + 1):
    dp[0][j], bk[0][j] = j * GAP, "l"
for i in range(1, n + 1):
    for j in range(1, m + 1):
        opts = [(dp[i - 1][j - 1] + sim(A[i - 1], B[j - 1]), "d"), (dp[i - 1][j] + GAP, "u"), (dp[i][j - 1] + GAP, "l")]
        dp[i][j], bk[i][j] = max(opts)
pair = {}
i, j = n, m
while i > 0 or j > 0:
    mv = bk[i][j]
    if mv == "d":
        if sim(A[i - 1], B[j - 1]) > 0.0:
            pair[i - 1] = j - 1
        i, j = i - 1, j - 1
    elif mv == "u":
        i -= 1
    else:
        j -= 1

# --- тайминги слов сценария ---
S = [None] * n
E = [None] * n
for i, j in pair.items():
    S[i], E[i] = heard[j]["s"], heard[j]["e"]
known = [i for i in range(n) if S[i] is not None]
assert known, "не удалось выровнять ни одного слова"
for i in range(n):
    if S[i] is not None:
        continue
    prev = max([k for k in known if k < i], default=None)
    nxt = min([k for k in known if k > i], default=None)
    t0 = E[prev] if prev is not None else (S[nxt] - 0.3 * (nxt - i) if nxt is not None else 0)
    t1 = S[nxt] if nxt is not None else t0 + 0.3 * (i - (prev or 0))
    idx_gap = [k for k in range(n) if S[k] is None and (prev is None or k > prev) and (nxt is None or k < nxt)]
    pos = idx_gap.index(i)
    step = (t1 - t0) / max(1, len(idx_gap))
    S[i], E[i] = t0 + pos * step, t0 + (pos + 1) * step
words = [{"w": script[i], "s": round(S[i] + offset, 3), "e": round(max(E[i], S[i] + 0.12) + offset, 3)} for i in range(n)]

# --- display: замена фраз (тридцать процентов -> 30%) ---
disp = {}
if (vdir / "display.json").exists():
    disp = {tuple(norm(x) for x in k.split()): v for k, v in json.loads((vdir / "display.json").read_text(encoding="utf-8")).items()}
out, i = [], 0
while i < len(words):
    hit = None
    for key, val in disp.items():
        k = len(key)
        if tuple(norm(words[i + d]["w"]) for d in range(k) if i + d < len(words)) == key:
            hit = (k, val)
            break
    if hit:
        k, val = hit
        tail = re.search(r"[.,!?:…]+$", words[i + k - 1]["w"])
        out.append({"w": val + (tail.group(0) if tail else ""), "s": words[i]["s"], "e": words[i + k - 1]["e"]})
        i += k
    else:
        out.append(words[i])
        i += 1

# --- якоря ---
anchors = {}
spec = json.loads((vdir / "anchors.json").read_text(encoding="utf-8"))
for name, key in spec.items():
    word, nth = (key, 1) if isinstance(key, str) else (key[0], key[1])
    cnt = 0
    for w in words:
        if norm(w["w"]) == norm(word):
            cnt += 1
            if cnt == nth:
                anchors[name] = {"s": w["s"], "e": w["e"]}
                break
    else:
        raise SystemExit(f"якорь '{name}': слово '{word}' (#{nth}) не найдено")
duration = round(words[-1]["e"], 3)
result = {"words": out, "anchors": anchors, "speechEnd": duration, "offset": offset, "duration": round(duration + 0.8, 2)}
js = json.dumps(result, ensure_ascii=False, indent=1)
(vdir / "timing.json").write_text(js, encoding="utf-8")
dst = root / "OpenMontage/remotion-composer/projects" / slug
dst.mkdir(parents=True, exist_ok=True)
(dst / "timing.json").write_text(js, encoding="utf-8")
print(f"слов {len(out)}, якорей {len(anchors)}, речь до {duration} с")
for k, v in anchors.items():
    print(f"  {k:12s} {v['s']:.2f}")
bad = n - len(pair)
print(f"не совпало с распознаванием: {bad} из {n} слов (тайминги интерполированы)")
