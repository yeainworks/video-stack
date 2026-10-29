---
name: video-stack
description: Mandatory entry point for ANY video work in this repo: making, editing, cutting, captioning, voicing, scoring, rendering or publishing short vertical videos (TikTok, Reels, Shorts), video montage, Remotion/HyperFrames compositions, voiceover, subtitles, music, mixing, covers, publish packages. Load this FIRST, before touching ffmpeg, Remotion, OpenMontage or any other video skill. It routes each stage to the right skill/script and holds the non-negotiable production rules. Also use for "монтаж", "ролик", "видео", "субтитры", "озвучка", "рендер".
---

# video-stack: хаб

Любая видеозадача начинается здесь. Не лезь сразу в ffmpeg, Remotion или OpenMontage: сначала правила (раздел 1), затем маршрут (раздел 2), затем только нужный скилл.

## 0. Перед стартом (всегда)
1. Прочитай `CLAUDE.md` репозитория и `CLAUDE.md` папки проекта (соседняя с `video-stack/` папка с `design/brand.tsx`; явно: `VIDEO_PROJECT=<путь>`). Нет проекта: спроси бренд, аудиторию, тон, CTA и создай папку по образцу `templates/project/`.
2. `export PATH="$PWD/OpenMontage/.venv/bin:$PATH"`; проверь `df -h /` (рендер нужно 5+ ГБ).
3. Открой `docs/simplicity-rules.md`, если пишешь или правишь сценарий.

## 1. Жёсткие правила (нарушать нельзя)
- Без полоски прогресса/длительности в кадре.
- Звук: голос + очень тихая музыка (≈0.10). Без SFX, пока прямо не попросят (`--sfx`).
- Motion удержания: хук с 0-го кадра, открытая петля до 4 с, событие в кадре каждые 1,5–2,5 с, субтитры по словам, концовка возвращает хук.
- Дизайн только из дизайн-системы проекта; перед рендером `scripts/sync_design.sh`.
- Просто: одна идея, польза за 3 с, пример вместо статистики, мысль крупно, действие в конце.
- Не ждать запись голоса: сразу полный пакет со скрэтч-голосом (Piper), настоящий голос подставить потом.
- Готово = пакет публикации (видео, обложка, название, описание+хештеги, ссылка на канал).
- Звук/видео «в порядке» только после замера (речь vs пауза, `docs/audio-recipes.md`).
- Цифры только с источником. Инструмент молча не подменять. Громкость −14 LUFS.

## 2. Маршрут: этап → что использовать
| Этап | Использовать |
|---|---|
| Идея, сценарий | `docs/simplicity-rules.md`, шаблон сценария проекта, `OpenMontage/skills/creative/short-form.md`, `storytelling.md` |
| Весь процесс по шагам | `docs/pipeline.md` |
| Референс-видео («сделай как это») | `OpenMontage/AGENT_GUIDE.md` (Reference Video Entry Point), `skills/meta/video-reference-analyst.md` |
| Озвучка (скрэтч) | Piper через OpenMontage; `OpenMontage/.claude/skills/text-to-speech`, `elevenlabs`, `fish-audio-tts` (если есть ключи) |
| Расшифровка, тайминги слов | `scripts/transcribe.py`, `scripts/build_timing.py`; `OpenMontage/.claude/skills/speech-to-text` |
| Сжать паузы в голосе | `scripts/tighten_voice.py` |
| Визуал, композиция | Remotion: `OpenMontage/.claude/skills/remotion`, `remotion-best-practices`, `OpenMontage/skills/core/remotion.md`; дизайн: `docs/visual-system.md` + `design/brand.tsx` проекта; альтернатива HTML-рендеру: `hyperframes*` |
| Проверка кадров до рендера | `scripts/contact_sheet.py` |
| Рендер немого видео | `scripts/render.sh` |
| Музыка | `OpenMontage/.claude/skills/music`, `acestep`, `lyria`; `scripts/make_sfx.py music` |
| Микс голоса и музыки | `scripts/mix_video.py`, `scripts/mix_human_voice.sh`, `docs/audio-recipes.md` |
| Монтаж готового файла: резка, склейка, 9:16, субтитры, громкость, экспорт, проверка | **`ffmpeg-skill`** (42 инструмента; `render.py --template tiktok|reels|shorts`, `check.py`, `look.py`) |
| Цвет | `ffmpeg-skill` `color.py`, `OpenMontage/skills/core/color-grading.md` |
| Генерация клипов/картинок/аватаров | `OpenMontage/.claude/skills/ltx2`, `ai-video-gen`, `flux-best-practices`, `heygen`, `avatar-video` и др. (нужны ключи) |
| Анимация | `motion-graphics`, `gsap-*`, `lottie-bodymovin`, `framer-motion`, `svg-character-animation` |
| Диаграммы, данные | `d3-viz`, `beautiful-mermaid` |
| Приёмка и публикация | `docs/pipeline.md` (чек-лист), шаблон `publish-package.md` проекта |
| Ревью работы | `OpenMontage/skills/meta/reviewer.md` |

Полный перечень: `docs/skills-inventory.md`. OpenMontage-скиллы читаются по пути (`OpenMontage/.claude/skills/<имя>/SKILL.md`, `OpenMontage/skills/INDEX.md`), это не глобальные скиллы.

## 3. ffmpeg-skill: заметки для этого репозитория
- Запуск: `python3 .claude/skills/ffmpeg-skill/scripts/<tool>.py` (stdlib, без сети). Рабочий процесс описан в его `SKILL.md`: probe, dry-run, выполнить, `check.py`, `look.py`.
- Требуется `ffprobe`. Если его нет (`doctor` показывает `ffprobe MISSING`), скилл не работает: поставь ffmpeg с ffprobe (`brew install ffmpeg`, либо статическая сборка в `OpenMontage/.venv/bin`). Не подменяй молча: скажи пользователю.
- Для Remotion-конвейера ffmpeg берётся из `OpenMontage/.venv/bin/ffmpeg` (imageio-ffmpeg, без ffprobe).

## 4. Правило роста
Нашёл новую грабли или решение → допиши в `docs/setup-and-pitfalls.md` (общее) или в `CLAUDE.md` проекта (специфичное). Обновил набор скиллов → обнови `docs/skills-inventory.md` и таблицу выше.
