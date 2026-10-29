"""Генерация звуковых эффектов и бодрой музыки для роликов (без внешних файлов и лицензий).

Запуск из корня video-stack:
  OpenMontage/.venv/bin/python scripts/make_sfx.py            # SFX -> <проект>/sfx/*.wav
  OpenMontage/.venv/bin/python scripts/make_sfx.py music 30   # музыка 120 BPM, 30 с -> <проект>/sfx/bgm_upbeat.wav
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _project import project_dir
OUT = project_dir() / "sfx"
rng = np.random.default_rng(7)  # детерминированно


def t_(d):
    return np.arange(int(SR * d)) / SR


def save(name, x, gain=0.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def lowpass_sweep(noise, f0, f1):
    """Однополюсный фильтр с плавающей частотой среза (шипящий свист)."""
    y = np.zeros_like(noise)
    fs = np.linspace(f0, f1, len(noise))
    a = 1 - np.exp(-2 * np.pi * fs / SR)
    acc = 0.0
    for i, v in enumerate(noise):
        acc += a[i] * (v - acc)
        y[i] = acc
    return y


def pop():
    t = t_(0.12)
    f = 520 + 520 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 32)


def whoosh():
    d = 0.38
    t = t_(d)
    n = rng.standard_normal(len(t))
    y = lowpass_sweep(n, 300, 5200)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return y * env


def thud():
    t = t_(0.32)
    f = 48 + 90 * np.exp(-t * 22)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 11)
    click = rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.35
    return body + click


def ding():
    t = t_(0.7)
    return (np.sin(2 * np.pi * 1318.5 * t) + 0.55 * np.sin(2 * np.pi * 1975.5 * t) + 0.25 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 6.5)


def tick():
    t = t_(0.05)
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 110)


def sparkle():
    t = t_(0.5)
    y = np.zeros_like(t)
    for k, f in enumerate([1568, 2093, 2637, 3136]):
        s = int(k * 0.06 * SR)
        tt = t[: len(t) - s]
        y[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * (0.8 - 0.12 * k)
    return y


def music(dur=30, bpm=120):
    n = int(SR * dur)
    y = np.zeros(n)
    beat = 60 / bpm
    nb = int(dur / beat)

    def add(sig, at, g=1.0):
        s = int(at * SR)
        e = min(n, s + len(sig))
        if s < n:
            y[s:e] += sig[: e - s] * g

    kt = t_(0.3)
    kick = np.sin(2 * np.pi * np.cumsum(46 + 110 * np.exp(-kt * 40)) / SR) * np.exp(-kt * 9)
    ht = t_(0.06)
    hat = rng.standard_normal(len(ht)) * np.exp(-ht * 90)
    hat = hat - np.concatenate([[0], hat[:-1]])  # грубый highpass
    notes = [65.41, 98.0, 110.0, 87.31]  # C2 G2 A2 F2
    arp = [[261.63, 329.63, 392.0, 523.25], [196.0, 246.94, 392.0, 493.88], [220.0, 261.63, 329.63, 440.0], [174.61, 261.63, 349.23, 440.0]]
    for b in range(nb):
        at = b * beat
        add(kick, at, 0.9)
        add(hat, at + beat / 2, 0.22)
        bar = (b // 4) % 4
        bt = t_(beat * 0.9)
        bass = np.sin(2 * np.pi * notes[bar] * bt) * np.exp(-bt * 3.2)
        add(bass, at, 0.45)
        for k in range(2):  # восьмые: арпеджио
            f = arp[bar][(b * 2 + k) % 4]
            pt = t_(0.22)
            pl = (np.sin(2 * np.pi * f * pt) + 0.3 * np.sin(2 * np.pi * 2 * f * pt)) * np.exp(-pt * 11)
            add(pl, at + k * beat / 2, 0.16)
    fade = np.ones(n)
    fi, fo = int(SR * 0.6), int(SR * 1.2)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    return y * fade


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "music":
        save("bgm_upbeat", music(float(sys.argv[2]) if len(sys.argv) > 2 else 30), 0.8)
        print("music ->", OUT / "bgm_upbeat.wav")
    else:
        for name, fn in [("pop", pop), ("whoosh", whoosh), ("thud", thud), ("ding", ding), ("tick", tick), ("sparkle", sparkle)]:
            save(name, fn())
            print(name)
        print("->", OUT)
