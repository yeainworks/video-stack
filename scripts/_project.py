"""Находит папку проекта: соседнюю с video-stack папку с design/brand.tsx.
Явно: переменная окружения VIDEO_PROJECT (путь к папке проекта)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def project_dir():
    env = os.environ.get("VIDEO_PROJECT")
    if env:
        return Path(env).expanduser().resolve()
    for d in sorted(ROOT.parent.iterdir()):
        if d != ROOT and (d / "design" / "brand.tsx").exists():
            return d
    raise SystemExit("Папка проекта не найдена: задайте VIDEO_PROJECT=/путь/к/проекту (внутри design/brand.tsx)")


def resolve_arg(arg):
    """Путь ролика: абсолютный, либо относительно папки проекта, либо относительно video-stack."""
    p = Path(arg)
    if p.is_absolute():
        return p
    pd = project_dir()
    return pd / p if (pd / p).exists() else ROOT / p
