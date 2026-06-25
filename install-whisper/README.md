# 1. Install a local transcription model (Whisper)

The foundation the other two parts build on: offline speech-to-text on your own
machine with [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper). No
cloud, no API key, no per-minute billing. The model downloads once from Hugging
Face, then runs fully offline.

Do it yourself in a few minutes with the steps below, **or** hand this file to
Claude Code (or any coding agent) and say *"follow this to set up local
transcription for me"* - it will inspect your machine and pick a model for you.

## 1. Check your machine

- **Operating system** and architecture.
- **CPU**: model and number of physical / logical cores.
- **RAM**: total, in GB.
- **GPU**: is there one, and is it an **NVIDIA** card? Only NVIDIA GPUs
  accelerate this stack (via CUDA). Apple Silicon, AMD, and Intel integrated
  graphics do **not** help here, so those machines run on the CPU - which is
  fine, transcription runs at roughly real time.

## 2. Pick a model for your hardware and language

| Machine | Model | `compute_type` |
|---|---|---|
| 8 GB RAM, no NVIDIA GPU | `small` | `int8` |
| 16 GB RAM, no NVIDIA GPU | `large-v3-turbo` | `int8` |
| 32 GB RAM, no NVIDIA GPU | `large-v3-turbo` or `large-v3` | `int8` |
| NVIDIA GPU, 6 GB+ VRAM | `large-v3` | `float16` |

**Language matters more than people expect.** The `tiny` and `base` models are
weak outside English; for any non-English language use `small` at the very
least, and prefer `large-v3-turbo`. Before defaulting to a generic model, check
whether a **fine-tune for your language** exists on Hugging Face - a dedicated
fine-tune usually beats the generic model of the same size. For Hebrew, use
[`ivrit-ai/whisper-large-v3-turbo-ct2`](https://huggingface.co/ivrit-ai/whisper-large-v3-turbo-ct2).

## 3. Install

```bash
# Python 3.9+ assumed.
pip install faster-whisper

# ffmpeg decodes the audio. Install it with your system package manager:
#   macOS:    brew install ffmpeg
#   Debian:   sudo apt install ffmpeg
#   Windows:  winget install Gyan.FFmpeg   (or: choco install ffmpeg)
```

The model downloads automatically from Hugging Face the first time it runs and
is cached after that, so only the first run needs the internet.

## 4. A minimal transcribe script

```python
from faster_whisper import WhisperModel

# Fill these in from steps 1-2.
MODEL = "ivrit-ai/whisper-large-v3-turbo-ct2"  # or "large-v3-turbo", "small", ...
COMPUTE = "int8"        # "int8" on CPU, "float16" on an NVIDIA GPU
DEVICE = "cpu"          # "cuda" only if an NVIDIA GPU is present
LANGUAGE = "he"         # ISO code of the spoken language, or None to auto-detect

model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE)

segments, info = model.transcribe(
    "recording.m4a",
    language=LANGUAGE,
    beam_size=8,          # raise for noisy phone audio
    vad_filter=True,      # skip long silences; speeds up real recordings
)

for s in segments:
    print(f"[{s.start:6.1f}s] {s.text.strip()}")
```

A fuller version - argument parsing, timestamped Markdown output, RTL wrapping
for Hebrew - lives in [`../skill/transcribe.py`](../skill/transcribe.py).

## 5. Good to know

- **`vad_filter=True`** drops long silences before decoding. On real meetings
  and voice memos this is most of the speed win.
- **`compute_type`**: `int8` is the fastest option on a CPU. `float16` is for
  NVIDIA GPUs; if you ask for it on a CPU the library quietly falls back to
  `float32`, which is slower, so set `int8` explicitly on CPU machines.
- **Speed on a CPU**: about real time, give or take - a 10-minute recording
  takes on the order of 10 minutes. An NVIDIA GPU is several times faster.

## Where to go next

- **[`../dictation/`](../dictation/)** - tap a key, speak, and your words are
  pasted into whatever field has focus.
- **[`../skill/`](../skill/)** - drop-in Claude Code skill that transcribes a
  recording into a timestamped Markdown file.
