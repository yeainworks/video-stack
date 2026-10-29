# Звук: рецепты

Везде: `cd OpenMontage/projects/<slug>` и `FF=../../.venv/bin/ffmpeg`. Все команды проверены на ролике 01.

## 1. Голос записал пользователь (основной путь)
```bash
mkdir -p assets/audio/human
cp "<путь к файлу>" assets/audio/human/raw.ogg
$FF -y -nostdin -i assets/audio/human/raw.ogg -ar 48000 -ac 1 assets/audio/human/raw.wav
```
**Расшифровка с таймингом слов** (скрипт `scripts/transcribe.py`): faster-whisper, модель `small`, `language="ru"`, `word_timestamps=True`. Результат `words.json` (слово, start, end). В ролике 01 текст совпал со сценарием дословно (53 токена, "%" считается отдельным токеном).
Автоопределение пауз по тишине не работает: у записи шумовой пол около −29 дБ, речь около −14 дБ. Тайминги брать из расшифровки.

**Очистка голоса:**
```bash
$FF -y -nostdin -i assets/audio/human/raw.wav \
 -af "highpass=f=90,afftdn=nr=14:nf=-32:tn=1,acompressor=threshold=0.1:ratio=3:attack=8:release=120:makeup=2,alimiter=limit=0.95" \
 -ar 48000 assets/audio/human/voice_clean.wav
```

**Микс с музыкой** (голос сдвинут на 0,3 с, музыка приглушается sidechain):
```bash
$FF -y -nostdin -i assets/audio/human/voice_clean.wav -i assets/music/bgm.wav -filter_complex \
"[0]aformat=channel_layouts=stereo,adelay=300:all=1,apad=whole_dur=30,atrim=0:30,asplit=2[vo1][vo2];\
[1]aresample=48000,aformat=channel_layouts=stereo,volume=0.33[m];\
[m][vo1]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=500[md];\
[vo2]volume=1.2[v];\
[md][v]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95,atrim=0:30[mix]" \
 -map "[mix]" -ar 48000 assets/audio/mix_human.wav
```
**Муксинг и нормализация:**
```bash
$FF -y -nostdin -i renders/silent.mp4 -i assets/audio/mix_human.wav -map 0:v -map 1:a -c:v copy \
 -af "loudnorm=I=-14:TP=-1.0:LRA=7,aresample=48000" -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart renders/final.mp4
```
Целевая громкость −14 LUFS. После нормализации речь около −15 дБ среднее, пик около −1 дБ.

### Тихая или шумная запись
Пример: запись была очень тихой (среднее −39,5 дБ, пик −17 дБ). `scripts/mix_video.py` сначала чистит шум (`afftdn`), затем нормализует голос до −17 LUFS, и только потом смешивает с музыкой. Без этого музыка заглушает голос. Всегда проверять окна речи против пауз.
Живую запись пользователя Whisper распознаёт с ошибками («резюме» → «Розиме»), это нормально: `build_timing.py` берёт слова из сценария (`spoken.txt`), а не из распознавания. `spoken.txt` должен отражать то, что человек реально сказал.

## 2. Синтетический голос Piper (запасной)
Голос: `ru_RU-ruslan-medium` (мужской). Инструмент `tools/audio/piper_tts.py`, `model` = полный путь к `.onnx`.
- `length_scale` — темп: **меньше = быстрее**. 0.95 даёт медленно (24 с на 5 фраз), **0.83 утверждён пользователем** (~15% быстрее 0.95), 0.78 слишком быстро, 0.90 слишком медленно.
- `sentence_silence` 0.18–0.25.
- Синтез по фразам (s1..s5), потом `adelay` на нужные моменты. Каждую фразу приводить к 48 кГц стерео (`aresample=48000,aformat=channel_layouts=stereo`), `adelay=<мс>:all=1`.
- Тайминги фраз в ролике 01: 0,3 / 4,0 / 11,8 / 18,3 / 25,1 с.

### Русское произношение в Piper (espeak)
- «резюме»: по умолчанию читается как «резюмЕ» (мягкое м). Писать **`резюмэ` + U+0301 на э**: `"резюмэ́"`. Фонетика проверена: `rʲiʑu"mˈɛ`.
- Знак `+` для ударения не работает. Знак U+0301 после гласной работает.
- Бренд писать кириллицей: **«Воркхак»** (латиница читается по-английски).
- Числа писать словами: «двенадцать процентов», «девяносто три».
- Проверка фонетики без озвучки:
  ```python
  from piper.phonemize_espeak import EspeakPhonemizer
  print("".join(sum(EspeakPhonemizer().phonemize("ru", "резюмэ́"), [])))
  ```
- Слова проверять на слух нельзя (мы не слышим звук): отправлять пользователю sample и спрашивать.

## 3. Музыка
Pixabay автоматически не скачивается (403). Варианты: трек пользователя в `OpenMontage/music_library/` или синтез. Синтезированный тёмный пульс (100 BPM, 30 с, без лицензионных проблем):
```bash
cd assets/music && $FF -y -nostdin \
 -f lavfi -i "aevalsrc='0.9*sin(2*PI*52*t)*exp(-7*mod(t,0.6))':d=30:s=44100" \
 -f lavfi -i "aevalsrc='0.22*sin(2*PI*55*t)+0.14*sin(2*PI*82.6*t)+0.08*sin(2*PI*110.4*t)':d=30:s=44100" \
 -f lavfi -i "anoisesrc=d=30:c=white:r=44100:a=0.5" \
 -filter_complex "[0]lowpass=f=140[k];[1]tremolo=f=0.25:d=0.5,lowpass=f=300[d];[2]highpass=f=6500,volume='0.10*exp(-40*mod(t+0.3,0.6))':eval=frame[h];[k][d][h]amix=inputs=3:normalize=0,volume=0.9,afade=t=in:d=1.5,afade=t=out:st=27.5:d=2.5,aformat=sample_fmts=s16:channel_layouts=stereo[o]" \
 -map "[o]" bgm.wav
```
(`alowpass` — не фильтр, использовать `lowpass`.) Звучит просто; для следующих роликов лучше реальный трек.

## 3a. Правило: без звуковых эффектов
По умолчанию в роликах только голос и очень тихая музыка (`mix_video.py` без `--sfx`, `--music=0.10`). Файл со SFX сохраняется как `final_with_sfx.mp4`, если нужен.

## 4. ПРОВЕРКА ЗВУКА (обязательно перед отправкой)
Общая громкость файла ничего не доказывает. Сравнить окно с речью и паузу без речи:
```bash
m(){ echo -n "$1+$2: "; $FF -nostdin -ss $1 -t $2 -i renders/final.mp4 -vn -af volumedetect -f null - 2>&1 | grep mean_volume; }
m 5 2     # речь: около −15…−18 дБ
m 28 1.5  # после речи (только музыка): заметно тише, около −21…−27 дБ
```
Если речь и пауза одинаково громкие, голоса в миксе нет.
Метки в `-filter_complex` нельзя использовать дважды: для повторного использования сигнала делать `asplit`.
В циклах `for` давать ffmpeg `-nostdin`, иначе он съедает stdin.
