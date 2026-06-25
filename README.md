# local-voice-llm

**Free, offline speech-to-text for any language, running entirely on your own
machine.** No cloud, no API key, no per-minute meter.

Voice input in AI tools is almost always English-first. Most built-in dictation
and voice features cover English and a short list of major languages; many
languages aren't covered at all. The moment you want to dictate or transcribe in,
say, Hebrew, you get pushed toward a paid provider, an API key, and a meter.

This repo needs none of that. Everything runs locally on
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) - on a regular CPU
laptop - so you can dictate and transcribe in a language the big tools leave out.

## Three standalone tools

Each works on its own; pick what you need.

| # | Part | What it does |
|---|------|--------------|
| 1 | [**install-whisper/**](install-whisper/) | Set up the local transcription model (Whisper via faster-whisper). The foundation for the other two. |
| 2 | [**dictation/**](dictation/) | System-wide push-to-talk: tap a key, speak, and your words are pasted into whatever field has focus - an editor, a browser, the Claude Code prompt. |
| 3 | [**skill/**](skill/) | Turn a recording (meeting, call, voice memo) into a timestamped Markdown transcript. Ships as a drop-in Claude Code skill, and runs standalone too. |

## Why bother talking instead of typing

The bottleneck to good output from a language model is often how much context you
bother to give it. Typing pushes you toward short, pruned input; speaking lets
you spill everything that's actually in your head. The dictation tool (part 2)
exists to remove that bottleneck: tap a key, think out loud, and the model gets
the full paragraph you would never have typed. The skill (part 3) does the same
for context captured earlier - record a long voice memo, hand over the
transcript.

## Hardware

The default model (`ivrit-ai/whisper-large-v3-turbo-ct2`, a Hebrew fine-tune)
runs comfortably on a CPU laptop with 16-32 GB RAM - no GPU needed. For other
languages or smaller machines, see the model guide in
[`install-whisper/`](install-whisper/). Only **NVIDIA** GPUs accelerate this
stack; on everything else it runs on the CPU, which is fine - transcription runs
at roughly real time.

## Adapt it to your language

Hebrew is the worked example throughout. To switch languages, change `MODEL` and
`LANGUAGE` in `dictation/dictate.py`, and pass `-l <code>` / `-m <model>` to
`skill/transcribe.py`. For any non-English language, prefer `large-v3-turbo` over
the tiny/base models, and check Hugging Face for a fine-tune in your language
first - it usually beats the generic model of the same size.

## Privacy

The speech-to-text is **fully local** - audio never leaves the machine. Models
download once from Hugging Face, then run offline.

## Platform note

The dictation daemon (part 2) is **Windows-focused** (global key hook,
auto-paste, and beeps use Win32 APIs). The model setup (part 1) and the
transcription script (part 3) are cross-platform.

## Background

Companion to the blog post
[*Free, Offline Speech-to-Text for Non-English Languages*](https://www.matanhakim.com/posts/2026-06-25-local-transcription/).

## License

[MIT](LICENSE) © Matan Hakim
