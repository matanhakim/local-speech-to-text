---
name: audio-transcription
description: >
  Transcribe audio or video files (Hebrew or any language) into timestamped
  Markdown using faster-whisper, with the ivrit-ai/whisper-large-v3-turbo-ct2
  fine-tune as the default Hebrew model. Triggers whenever the user asks to
  transcribe, tafmel, תמלל, תמלול, or analyze a recording — phone calls,
  meetings, Google Meet recordings, voice memos, lectures, interviews. Saves
  transcripts to a project-local path (default: `transcripts/` or alongside
  the source) and Hebrew transcripts are auto-wrapped in `<div dir="rtl">` so
  they render correctly.
metadata:
  author: Matan Hakim (@matanhakim)
  version: "1.0"
license: MIT
---

# Audio Transcription

Reusable local audio transcription via faster-whisper. Hebrew-first (uses the
ivrit-ai fine-tune by default), but works for any language. Designed to be
invoked from any project: point it at a recording, get a timestamped Markdown
transcript. Nothing leaves the machine.

## When to use

- The user has a recording (phone call, Google Meet, voice memo, interview,
  lecture, podcast) and wants it transcribed.
- The user asks to "תמלל", "תמלול", "transcribe", "convert speech to text".
- A workflow needs to read what was said in audio/video before proceeding
  (e.g. drafting a document from a kickoff call, extracting decisions from a
  meeting).

## When NOT to use

- The recording is already transcribed (.txt / .srt / .vtt / .md beside it) —
  read that instead.
- The user asks for **diarization** (who-said-what speaker labels). This
  skill does not do diarization out of the box (see "Future work" below).
  Acknowledge the limitation and offer either: timestamped transcript +
  context-based attribution, or a separate pyannote.audio setup.
- The audio is on a remote service requiring API auth (YouTube link, Zoom
  cloud, etc.) — first get a local file.

## Setup

```bash
pip install faster-whisper
# plus ffmpeg from your system package manager (see setup-local-transcription.md)
```

## Quickstart

```powershell
# Hebrew (default model: ivrit-ai/whisper-large-v3-turbo-ct2)
python transcribe.py "<path-to-audio>" -l he -o transcripts\<name>.md

# English / auto-detect
python transcribe.py "<path-to-audio>" -o transcripts\<name>.md
```

The script is also invokable from bash:

```bash
python transcribe.py "<path-to-audio>" -l he -o transcripts/<name>.md
```

To install it as a Claude Code skill, copy this folder to
`~/.claude/skills/audio-transcription/` and point the commands at
`~/.claude/skills/audio-transcription/transcribe.py`.

## Defaults & flags

| Flag | Default | Notes |
|------|---------|-------|
| `-l/--language` | auto-detect | Pass `he` for Hebrew to force the ivrit-ai model |
| `-m/--model` | `ivrit-ai/whisper-large-v3-turbo-ct2` for he, else `large-v3` | Any HF CT2 model or built-in size (`tiny`/`base`/`small`/`medium`/`large-v3`) |
| `-o/--output` | `<audio>.transcript.md` | Prefer an explicit path under `<project>/transcripts/` |
| `--device` | `auto` | `cuda` if available, else `cpu` |
| `--compute-type` | `default` | CPU: `int8` is fastest. GPU: `float16`. |
| `--beam-size` | `5` | Raise to 8 for noisy phone audio; lower to 1 for speed |
| `--no-vad` | off (VAD on) | Silero VAD pre-filter is on by default — helps phone calls with long silences |
| `--initial-prompt` | none | Bias the decoder toward proper nouns: `--initial-prompt "Ada, Lin, ACME, roadmap"` |
| `--word-timestamps` | off | Adds word-level timing inside each segment (slower) |

## Output format

Markdown with one segment per paragraph:

```markdown
# Transcript: <filename>

- Source: ...
- Model: ...
- Language: he (99%) (forced)
- Duration: 0:14:36
- VAD: Silero (on)
- Beam size: 5

---

<div dir="rtl">

`00:00:00` שלום, אז דיברנו על...

`00:00:08` כן, אני חושב שצריך לבדוק...

</div>
```

Hebrew transcripts are automatically wrapped in `<div dir="rtl">` for correct
RTL rendering on GitHub and in Markdown previewers.

## Recipe: project-local placement

When invoked inside a project, save the transcript under the project's
working tree, not next to the source file in Downloads. Pick the most
specific subdirectory available:

1. If the recording is conference/event-related → `conference/transcripts/`
2. If it's interview source material for a review → `sources/transcripts/`
3. Generic working call → `transcripts/`

Filename convention: `<YYYY-MM-DD>-<short-slug>.md`. Example:
`2026-05-27-team-call.md`.

## Performance expectations

On CPU (no GPU), expect roughly:
- `large-v3` / `ivrit-ai/...turbo-ct2`: 0.3-1.4× realtime depending on CPU and
  how much silence the VAD skips
- `medium`: 1-2× realtime
- `small`: 4-6× realtime

The first run downloads the model (~1.5-3 GB) into the HuggingFace cache.
Subsequent runs are warm and fully offline.

If you have an NVIDIA GPU, `--device cuda --compute-type float16` is 5-20×
faster than CPU.

## Hebrew quality notes

- **ivrit-ai/whisper-large-v3-turbo-ct2** is the state-of-the-art Hebrew
  Whisper fine-tune. It significantly outperforms vanilla `large-v3` on
  Hebrew WER, especially for spontaneous speech and accented Hebrew.
- For mixed Hebrew/English calls, the ivrit-ai model handles code-switching
  well; English-only segments will transcribe correctly too.
- Numbers/dates often come out as words; let the user polish if they need
  digits.
- Phone-line audio (8 kHz) is noticeably worse than meeting-quality audio.
  Consider `--beam-size 8` and revisit segments with low semantic coherence.

## Future work (not implemented)

- **Speaker diarization** (who-said-what): would require `pyannote.audio` +
  PyTorch + a HF-gated model accept. For two-speaker calls, an LLM can often
  re-attribute speakers post-hoc from context.
- **SRT/VTT output**: easy to add — currently only Markdown is emitted.
- **Force-alignment / phrase-level confidence**: faster-whisper exposes
  `word_timestamps` and per-segment probabilities; not surfaced in MD yet.

## Privacy

The transcription is **fully local** — audio never leaves the machine.
Models are downloaded once from HuggingFace; runtime is offline.
