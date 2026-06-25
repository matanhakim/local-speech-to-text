# local-voice-llm

**Talk to your LLM in any language - with the speech part running entirely on
your own machine.** Free, offline, no API key, no per-minute meter.

Voice input in AI tools is almost always English-first. Claude Code's built-in
dictation and most voice features cover English and a short list of major
languages; many languages aren't covered at all. The moment you want to dictate
in, say, Hebrew, you get pushed toward a paid provider, an API key, and a meter.

This repo is the setup that needs none of that. The speech-to-text runs locally
on [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) - on a regular
CPU laptop - so you can **hand a language model the full context by talking
instead of typing**, in a language the big tools leave out.

> Why talk instead of type? Typing pushes you toward short, pruned input.
> Speaking lets you spill everything that's actually in your head, so the model
> gets the full picture. The bottleneck to good LLM output is often how much
> context you bother to give it - and voice removes that bottleneck.

Companion to the blog post:
[*Free, Offline Speech-to-Text for Non-English Languages*](https://www.matanhakim.com/posts/2026-06-25-local-transcription/).

## What's inside

Three parts, in order:

| # | Part | What it does |
|---|------|--------------|
| 1 | [**install-claude-code.md**](install-claude-code.md) | Install the LLM agent (Claude Code) you'll be talking to. |
| 2 | [**dictation/**](dictation/) | System-wide push-to-talk dictation: tap a key, speak, and your words are pasted into whatever field has focus - Claude Code, an editor, a browser. |
| 3 | [**transcription/**](transcription/) | Turn a recording (meeting, call, voice memo) into a timestamped Markdown transcript. Also a drop-in Claude Code skill. |

Parts 2 and 3 are independent - use either on its own. Together with part 1 they
make one loop: **install the agent, then feed it context by voice**, live
(dictation) or from a recording (transcription).

## Two ways to feed context by voice

- **Live dictation** (`dictation/`) - for talking *to* the agent in real time.
  Tap `` ` ``, say your prompt out loud, tap again; it lands in the input box.
  Best for long, rambly, high-context prompts you'd never type out.
- **Recording -> transcript** (`transcription/`) - for context captured
  *earlier*. Record a long voice memo (e.g. while driving), drop the file into
  Claude Code, and it transcribes locally and works from the full transcript.
  Also the way to transcribe meetings and calls.

## Hardware

The default model (`ivrit-ai/whisper-large-v3-turbo-ct2`, a Hebrew fine-tune)
runs comfortably on a CPU laptop with 16-32 GB RAM - no GPU needed. For other
languages, or smaller machines, see the model guide in
[`transcription/setup-local-transcription.md`](transcription/setup-local-transcription.md).
Only **NVIDIA** GPUs accelerate this stack; on everything else it runs on the CPU,
which is fine: transcription runs at roughly real time.

## Adapt it to your language

Hebrew is the worked example throughout. To switch languages, change `MODEL` and
`LANGUAGE` in `dictation/dictate.py` (and pass `-l <code>` / `-m <model>` to
`transcription/transcribe.py`). For any non-English language, prefer
`large-v3-turbo` over the tiny/base models, and check Hugging Face for a
fine-tune in your language first - it usually beats the generic model of the
same size.

## Privacy

The speech-to-text is **fully local** - audio never leaves the machine. Models
download once from Hugging Face, then run offline. (Claude Code itself is a
cloud service; only the voice layer in this repo is local.)

## Platform note

The dictation daemon is **Windows-focused** (global key hook, auto-paste, and
beeps use Win32 APIs). The transcription script and the faster-whisper core are
cross-platform.

## License

[MIT](LICENSE) © Matan Hakim
