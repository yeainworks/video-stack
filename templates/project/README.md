# Шаблон папки проекта

Скопируйте в соседнюю с `video-stack/` папку и заполните. Скрипты находят её по наличию `design/brand.tsx` (или `VIDEO_PROJECT=<путь>`).

```
<проект>/
  CLAUDE.md            правила проекта (бренд, тон, CTA, решения владельца)
  brand.md             кто вы, аудитория, тон, ссылка на канал
  design/brand.tsx     дизайн-система Remotion (цвета, компоненты)
  design/tokens.json   токены
  brand-assets/        аватар, логотип
  templates/           script-template.md, publish-package.md
  videos/NN-slug/      сценарий, spoken.txt, timing.json, composition.tsx
  sfx/                 музыка/звуки (make_sfx.py)
  ready/NN-slug/       готовые пакеты публикации
```
