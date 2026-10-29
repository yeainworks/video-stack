# video-stack

**An agent-driven production line for short vertical videos (TikTok, Reels, Shorts).**
Give your AI coding agent a topic. It writes the script, records a scratch voice, builds a motion composition in Remotion, mixes the sound, edits with FFmpeg and hands you a ready-to-publish package.

`video-stack` is not an app. It is a **knowledge and tooling layer** for [Claude Code](https://claude.com/claude-code): one hub skill, a set of battle-tested scripts, and the production rules we learned the hard way, wired on top of [OpenMontage](https://github.com/calesthio/OpenMontage) and [`ffmpeg-skill`](https://github.com/kajisho5/ffmpeg-skill).

---

## Why it exists

Agents are good at video when they are told *what to do, in what order, and what never to do*. Without that they reinvent the palette, add sound effects nobody wanted, ship a 30-second clip with a progress bar, and forget the cover image.

`video-stack` fixes this with one rule: **every video task starts at the hub skill.** The hub loads the non-negotiable rules, then routes each stage to the right skill or script.

```
 request ──▶  video-stack (hub skill)
                │  rules + routing table
                ▼
 script ─▶ voice ─▶ word timing ─▶ Remotion scenes ─▶ render ─▶ mix ─▶ ffmpeg edit ─▶ publish package
 (rules)   (Piper/   (Whisper)     (your design)      (silent)  (voice+   (ffmpeg-skill:  (video, cover,
           ElevenLabs)                                          music)    check, look)     title, tags)
```

## What is inside

| Part | Path | What it does |
|---|---|---|
| **Hub skill** | `.claude/skills/video-stack/` | Mandatory entry point: production rules + stage → skill/script routing |
| **ffmpeg-skill** | `.claude/skills/ffmpeg-skill/` | 42 local FFmpeg tools: cut, join, 9:16 fit, captions, silence removal, loudness, platform export, delivery checks. Python stdlib only, no cloud (MIT, by kajisho5) |
| **Scripts** | `scripts/` | Render, word timing, voice tightening, SFX/music, mixing, contact sheets, design sync |
| **Docs** | `docs/` | Pipeline, audio recipes, visual system, simplicity rules, setup pitfalls, skills inventory |
| **Project template** | `templates/project/` | Skeleton for your brand/design/scripts folder |
| **OpenMontage** | `OpenMontage/` (fetched by `setup.sh`) | The engine plus ~140 domain skills (Remotion, HyperFrames, TTS, music, generation, animation). AGPLv3, **not** vendored here |

## The production rules (baked into the hub)

1. **No progress bar** in the frame.
2. **Voice + very quiet music only** (about 0.10). No sound effects unless asked.
3. **Retention motion in every video:** hook on frame 0, open loop within 4 s, something happens every 1.5-2.5 s, word-by-word captions, the ending returns to the hook.
4. **One design per project.** Colours and components come from the project's design system, never reinvented.
5. **Keep it simple:** one idea, value in the first 3 seconds, a concrete example instead of statistics, the main thought in big text, an action at the end.
6. **Don't wait for the real voice.** Ship the full package with a scratch voice, swap the recording in later.
7. **Done = publish package:** video, cover, title, description with hashtags, channel link.
8. **Measure before claiming.** Compare loudness in speech windows vs pauses; never say "audio is fine" unmeasured.
9. **Numbers need sources.** Say so on screen.

Details: [`CLAUDE.md`](CLAUDE.md), [`docs/simplicity-rules.md`](docs/simplicity-rules.md).

---

## Requirements

- macOS or Linux (Windows via WSL)
- Python 3.10+
- Node.js 18+
- Git and `make`
- **FFmpeg with `ffprobe`** (required by `ffmpeg-skill`)
- 5+ GB of free disk space for rendering
- [Claude Code](https://claude.com/claude-code)

## Quick start

```bash
# 1. Get the repo
git clone https://github.com/yeainworks/video-stack.git
cd video-stack

# 2. Install the engine and dependencies
./setup.sh

# 3. Create your project folder next to video-stack/
cp -R templates/project ../my-project

# 4. Check that FFmpeg tooling works
PATH="$PWD/OpenMontage/.venv/bin:$PATH" \
  python3 .claude/skills/ffmpeg-skill/scripts/_contract.py doctor

# 5. Start the agent
claude
```

Then just ask:

> Make a 30-second vertical video about three mistakes in a CV. Use my project's design.

Claude Code loads the `video-stack` skill, reads your project's `CLAUDE.md`, and walks the pipeline.

### Where is my project folder found?

Scripts look for a **sibling folder of `video-stack/` that contains `design/brand.tsx`**. To point somewhere else:

```bash
export VIDEO_PROJECT=/path/to/my-project
```

Recommended layout:

```
workspace/
├── video-stack/        this repo
└── my-project/         your brand, design, scripts, finished videos
    ├── CLAUDE.md       project rules (brand, tone, CTA)
    ├── brand.md        who you are, audience, tone, channel link
    ├── design/         brand.tsx, tokens.json
    ├── templates/      script-template.md, publish-package.md
    ├── videos/NN-slug/ script, spoken.txt, timing.json, composition.tsx
    ├── sfx/            music and sounds
    └── ready/NN-slug/  publish packages
```

## The pipeline in short

1. **Script.** One idea, simple words, budget about 60-70 words per 30 s.
2. **Scratch voice.** Piper locally, or ElevenLabs/Fish if you have keys.
3. **Word timing.** `scripts/transcribe.py` then `scripts/build_timing.py` align script words to audio.
4. **Design sync + composition.** `scripts/sync_design.sh`, Remotion scenes with retention motion.
5. **Frame check.** `scripts/contact_sheet.py` before the full render.
6. **Render silent video.** `scripts/render.sh <slug> [CompositionId]`.
7. **Mix.** `scripts/mix_video.py` denoises, normalises voice, adds quiet music, measures.
8. **Edit and export.** `ffmpeg-skill` fits 9:16, checks the platform spec, shows contact sheets.
9. **Publish package.** Video, cover, title, description, hashtags.

Full walkthrough: [`docs/pipeline.md`](docs/pipeline.md). Audio recipes and loudness checks: [`docs/audio-recipes.md`](docs/audio-recipes.md).

## Skills map

The hub's routing table sends the agent to:

- **Editing / delivery:** `ffmpeg-skill`
- **Scenes:** `remotion`, `remotion-best-practices`, `hyperframes*`
- **Voice and speech:** `text-to-speech`, `elevenlabs`, `fish-audio-tts`, `speech-to-text`
- **Music:** `music`, `acestep`, `lyria`
- **Generation:** `ltx2`, `ai-video-gen`, `flux-best-practices`, `heygen`, `avatar-video`
- **Animation and data:** `motion-graphics`, `gsap-*`, `lottie-bodymovin`, `d3-viz`, `beautiful-mermaid`

The complete inventory lives in [`docs/skills-inventory.md`](docs/skills-inventory.md).

## Extending

- Add a skill under `.claude/skills/<name>/SKILL.md`, then add a row to the hub's routing table and to the inventory.
- Found a pitfall? Add it to [`docs/setup-and-pitfalls.md`](docs/setup-and-pitfalls.md) (general) or your project's `CLAUDE.md` (specific).
- The hub's rule: **if a stage has no row in the table, the agent must say so instead of improvising silently.**

## Troubleshooting

| Symptom | Fix |
|---|---|
| `doctor` says `ffprobe MISSING` | Install full FFmpeg (`brew install ffmpeg` / `apt install ffmpeg`). On Intel Macs where Homebrew has no bottles, use a static build placed next to the `ffmpeg` in `OpenMontage/.venv/bin` |
| `Папка проекта не найдена` | Create a sibling folder with `design/brand.tsx` or set `VIDEO_PROJECT` |
| `No space left on device` during render | Free 5+ GB, check `df -h /` first |
| Remotion cannot resolve fonts | Fonts need network at render time; avoid symlinked compositions, use real files |
| Voice vanished from the mix | See the filter-label pitfall in `docs/setup-and-pitfalls.md` |

## Licenses

- This repository: **MIT**, see [`LICENSE`](LICENSE).
- `ffmpeg-skill`: MIT (kajisho5).
- OpenMontage: **AGPLv3**, fetched at setup, not redistributed here. If you embed it in a service, AGPLv3 terms apply.

See [`THIRD_PARTY.md`](THIRD_PARTY.md).
