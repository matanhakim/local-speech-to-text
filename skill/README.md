# 3. Transcription skill (download & install)

A drop-in [Claude Code skill](https://code.claude.com/docs/en/skills) that turns
any recording - a meeting, a call, a voice memo, an interview - into a
timestamped Markdown transcript with [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper),
locally. Hebrew uses the state-of-the-art `ivrit-ai` fine-tune by default; any
language works. Nothing leaves the machine.

## Install as a Claude Code skill

```bash
pip install -r requirements.txt        # plus ffmpeg (see ../install-whisper/)
```

Then copy this folder into your skills directory as `audio-transcription`:

```bash
# macOS / Linux
cp -r . ~/.claude/skills/audio-transcription
```

```powershell
# Windows
Copy-Item -Recurse . "$env:USERPROFILE\.claude\skills\audio-transcription"
```

Claude Code now picks it up whenever you ask it to transcribe a recording, and
writes the transcript into your current project.

## Or use it standalone (no skill, no agent)

```bash
# Hebrew (forces the ivrit-ai model)
python transcribe.py "recording.m4a" -l he -o transcript.md

# any other language / auto-detect
python transcribe.py "recording.m4a" -o transcript.md
```

Full flag reference, performance numbers, and quality notes are in
[`SKILL.md`](SKILL.md). New to local Whisper? Start with
[`../install-whisper/`](../install-whisper/).

## Files

| File | Purpose |
|------|---------|
| `transcribe.py` | the transcription script (timestamped Markdown, RTL-aware) |
| `SKILL.md` | the skill definition + full docs |
| `requirements.txt` | Python dependency |
