# Transcription

Turn a recording - a meeting, a call, a voice memo, an interview - into a
timestamped Markdown transcript with [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper),
locally. Hebrew uses the state-of-the-art `ivrit-ai` fine-tune by default; any
other language works too. Nothing leaves the machine.

## Install

```bash
pip install -r requirements.txt
# plus ffmpeg from your system package manager:
#   macOS:   brew install ffmpeg
#   Debian:  sudo apt install ffmpeg
#   Windows: winget install Gyan.FFmpeg
```

## Use

```bash
# Hebrew (forces the ivrit-ai model)
python transcribe.py "recording.m4a" -l he -o transcript.md

# Any other language / auto-detect
python transcribe.py "recording.m4a" -o transcript.md
```

Full flag reference, performance expectations, and quality notes are in
[`SKILL.md`](SKILL.md).

## What's here

| File | Purpose |
|------|---------|
| `transcribe.py` | the transcription script (timestamped Markdown, RTL-aware) |
| `SKILL.md` | full docs - also a drop-in [Claude Code skill](https://code.claude.com/docs/en/skills) |
| `setup-local-transcription.md` | a recipe you can hand to a coding agent to set this up from scratch |
| `requirements.txt` | Python dependency |

## Use it as a Claude Code skill

Copy this folder to `~/.claude/skills/audio-transcription/`. Then Claude Code
picks it up whenever you ask it to transcribe a recording, and writes the
transcript into your current project.
