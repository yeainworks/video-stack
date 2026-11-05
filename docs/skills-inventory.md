# Инвентарь скиллов (2026-10-29)

Три слоя. Связку делаем поверх них (см. «Следующий шаг»).

## 1. Проектный: `video-stack/.claude/skills/` (наш, едет на GitHub)
| Скилл | Что делает |
|---|---|
| `ffmpeg-skill` v2.17.3 (kajisho5, MIT) | 42 локальных ffmpeg-инструмента: cut, join, fit 9:16, captions, silence, loudness, sync, export TikTok/Reels/Shorts, check, look. Только stdlib Python, без сети. Установлен копированием, без `npx`. |

Проверено перед установкой: нет сетевых вызовов, `shell=True`, `eval`. Лицензия MIT.

Добавлено 2026-11-05 через `npx skills add <repo> -a claude-code -s '*' -y --copy` (точные версии и хеши в `skills-lock.json`, обновлять `npx skills update -p`):
| Пакет | Скиллы | Для чего |
|---|---|---|
| `heygen-com/hyperframes` (Apache-2.0) | `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `figma`, `remotion-to-hyperframes`, `reverse-any-video`, `slideshow`, `style-sampling` | видео из HTML, ~450 готовых блоков, медиа/озвучка/музыка, перенос из Remotion, разбор чужого ролика |
| `remotion-dev/skills` | `remotion-best-practices` (роутер), `remotion-create`, `-markup`, `-captions`, `-render`, `-studio`, `-docs`, `-maps`, `-multimedia`, `-interactivity`, `-saas`, `-upgrade`, `-license` | официальные скиллы Remotion |
| `Leonxlnx/taste-skill` (MIT) | `design-taste-frontend` | вкус и анти-шаблонность веб-страниц |
| `emilkowalski/skills` (MIT) | `animate`, `choreograph`, `review-animations`, `improve-animations`, `remove-animations`, `find-animation-opportunities`, `animation-vocabulary`, `animation-performance`, `apple-design`, `emil-design-eng`, `break-ui`, `prototype`, `pick-ui-library`, `mobile-native`, `animate-expo`, `ask-sonner`, `write-swift` | решения по моушену: кривые, длительности, хореография, ревью анимаций |

Свои скиллы (2026-11-05): `shorts-ideas` (идеи, хуки, сценарии, контент-план, фильтры по правилам простоты), `voiceover` (выбор голоса, подготовка текста, ударения, Piper, замер звука).

Не установлен: `impeccable` (`npx impeccable install` качает с `impeccable.style`, домен закрыт сетевой политикой облачного окружения). Запасной путь: `npx skills add pbakaus/impeccable` (только скилл, без хуков).
Известно: `doctor` показывает `ffprobe MISSING` (в `OpenMontage/.venv/bin` есть только `ffmpeg` 7.1), нужен `ffprobe`. Запуск: `PATH="OpenMontage/.venv/bin:$PATH"`.

## 2. OpenMontage `.claude/skills/` (49 шт.) и `.agents/skills/` (91 шт., надмножество)
**Монтаж/рендер:** `ffmpeg` (OM, базовый), `remotion`, `remotion-best-practices`, `hyperframes*` (8), `video-edit`, `video-download`, `video-translate`, `video-understand`, `create-video`, `video_toolkit`, `music-to-video`, `website-to-video`, `remotion-to-hyperframes`
**Голос/речь:** `text-to-speech`, `elevenlabs`, `azure-text-to-speech`, `fish-audio-tts`, `doubao-tts`, `speech-to-text`, `azure-speech-to-text`, `agents`, `setup-api-key`
**Музыка/звук:** `music`, `acestep`, `lyria`, `sound-effects`, `media-use`
**Генерация видео/картинок:** `ltx2`, `ai-video-gen`, `seedance-2-0/2-5`, `kling-official`, `grok-media`, `atlas-cloud`, `dashscope`, `comfyui`, `minimax-h3`, `gemini-omni`, `flux-best-practices`, `bfl-api`, `faceswap`, `heygen`, `avatar-video`
**Анимация/моушен:** `motion-graphics`, `framer-motion`, `lottie-bodymovin`, `gsap-*` (9), `svg-character-animation`, `canvas-procedural-animation`, `character-rigging`, `character-animation-qa`, `pose-library-design`, `manim-*` (3), `threejs-*` (12)
**Дизайн/ревью:** `visual-style`, `tailwind-design-system`, `web-design-guidelines`, `vercel-*` (2), `d3-viz`, `beautiful-mermaid`, `playwright-recording`, `synthetic-screen-recording`
**Служебные:** `provider-model-refresh`

## 3. OpenMontage `skills/` (свои markdown-инструкции, индекс `skills/INDEX.md`, 329 строк)
- `core/` (6): color-grading, ffmpeg, hyperframes, remotion, subtitle-sync, whisperx
- `creative/` (36): short-form, video-editing, video-stitching, sound-design, typography, broll-planning, storytelling и др.
- `meta/` (11): reviewer, checkpoint-protocol, creative-intake, taste-direction, skill-creator и др.
- `pipelines/` (103 файла, 12 пайплайнов): clip-factory, talking-head, explainer, screen-demo, localization-dub, podcast-repurpose и др.

## 4. Глобальные (`~/.claude/skills`, не наши, на GitHub не едут)
gstack (browse, qa, review, ship…), caveman, sigma-code, ub-mode и т.д. К видео не относятся.

## Наблюдения
- Пересечение: `ffmpeg` (OM `.claude`), `skills/core/ffmpeg.md` и новый `ffmpeg-skill`. Нужно решить, кто главный: предлагаю `ffmpeg-skill` для исполнения, OM-файлы для рецептов.
- Правила проекта (его CLAUDE.md и папка проекта) нигде не связаны со скиллами.
- Для GitHub: `OpenMontage/` это чужой клон (AGPLv3), в наш репозиторий его вкладывать нельзя без учёта лицензии; лучше ссылаться на него.

## Следующий шаг
Один входной скилл `video-stack` (хаб): при любой видеозадаче агент обязан сначала открыть его. Хаб содержит таблицу «этап → скилл/скрипт» и наши жёсткие правила.
