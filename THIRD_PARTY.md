# Сторонние компоненты

| Компонент | Источник | Лицензия | Как подключён |
|---|---|---|---|
| ffmpeg-skill 2.17.3 | https://github.com/kajisho5/ffmpeg-skill | MIT | скопирован в `.claude/skills/ffmpeg-skill/` (лицензия внутри) |
| OpenMontage (коммит `c8066452325cb57c8fc1ba8c2a71b6e8842e6b65`) | https://github.com/calesthio/OpenMontage | AGPLv3 | НЕ входит в репозиторий; `setup.sh` клонирует его рядом. При встраивании в сервис действуют условия AGPLv3. |
| FFmpeg | https://ffmpeg.org | LGPL/GPL | системная установка |
