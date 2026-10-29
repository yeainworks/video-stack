# Окружение и грабли

Записано на macOS 26. Node v22.16, Python системный 3.13, venv OpenMontage на Python 3.10.

## Что установлено и как
- **OpenMontage** склонирован в `OpenMontage/`, `make setup` прошёл. Окружение `OpenMontage/.venv`.
- **ffmpeg:** `brew install ffmpeg` **не работает** (Command Line Tools не поддерживают macOS 26, нужен `sudo xcode-select --install`, пользователь не делал). Обход: `pip install imageio-ffmpeg` в venv и симлинк:
  ```bash
  cd OpenMontage
  .venv/bin/python -m pip install imageio-ffmpeg
  ln -sf "$(.venv/bin/python -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')" .venv/bin/ffmpeg
  ```
  Это ffmpeg 7.1. Нет `ffprobe`. Перед работой: `export PATH="$PWD/.venv/bin:$PATH"` (иначе инструменты OpenMontage считают ffmpeg недоступным).
- **Piper TTS** модели в `~/.piper/models/` (скачаны ruslan, denis, dmitri по ~63 МБ). Скачивание: `.venv/bin/python -m piper.download_voices --download-dir ~/.piper/models ru_RU-ruslan-medium`.
- **faster-whisper** (модель `small`, скачивается в кэш HF) для расшифровки с тайм-кодами слов.
- Шрифты Unbounded и Onest через `@remotion/google-fonts` (нужна сеть при рендере).

## Грабли и решения
| Проблема | Причина | Решение |
|---|---|---|
| `No space left on device` | диск почти полный (137 МБ) | освободить 5+ ГБ, проверять `df -h /` перед рендером |
| Pixabay Music: HTTP 403 | сайт блокирует автопоиск | либо пользователь скачивает трек в `OpenMontage/music_library/`, либо синтез пульса ffmpeg (см. audio-recipes) |
| Piper: `Unable to find voice` | инструмент не передаёт `--data-dir` | в `model` передавать **полный путь** к `.onnx` |
| Remotion: `Can't resolve '@remotion/google-fonts/...'` | симлинк на проект ломает поиск node_modules | положить `index.tsx` реальным файлом в `remotion-composer/projects/<slug>/` |
| Remotion продолжает старую ошибку после правки | кэш бандла | `--bundle-cache=false` |
| `sed -i` падает на Mac | BSD sed | `sed -i '' ...` или править Python/Edit |
| Голос исчез из микса | один лейбл фильтра использован дважды, моно 22 кГц не приведён к стерео | см. рабочий рецепт в audio-recipes, всегда мерить окна |
| `sleep` в цикле блокируется | ограничение среды | ждать через фоновую команду или Monitor |
| Браузер gstack browse не стартует | не установлен Chromium Playwright | использовать встроенный браузер Claude или `npx playwright install` |
| Instagram без логина не отдаёт видео | нужен вход | брать только превью-кадр (og:image) и комментарии |

## Лицензии и чужие материалы
- OpenMontage: AGPLv3. Для внутренней работы нормально; при встраивании в свой сервис код придётся открывать.
- Pixabay Music: бесплатное использование, но автоскачивание заблокировано.
- Референсы из соцсетей: только вдохновение, не копировать.
