#!/usr/bin/env python
"""
Transcribe an audio or video file using faster-whisper.

Hebrew default uses the ivrit-ai fine-tune (ivrit-ai/whisper-large-v3-turbo-ct2),
which is the state-of-the-art Hebrew Whisper model. Other languages use
OpenAI's large-v3.

Output is a Markdown file with segment-level timestamps. Hebrew transcripts are
wrapped in <div dir="rtl"> so they render right-to-left in GitHub and previewers.

Usage:
    python transcribe.py <audio> [-l he] [-o transcript.md] [-m MODEL]

Environment:
    HF_HUB_CACHE       HuggingFace cache directory (model storage)
    CT2_USE_EXPERIMENTAL_PACKED_GEMM=1   slight speedup on some CPUs
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import timedelta
from pathlib import Path


HE_MODEL = "ivrit-ai/whisper-large-v3-turbo-ct2"
DEFAULT_MODEL = "large-v3"


def fmt_ts(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> int:
    p = argparse.ArgumentParser(
        prog="transcribe",
        description="Transcribe audio/video to a Markdown transcript via faster-whisper.",
    )
    p.add_argument("audio", type=Path, help="Path to audio or video file")
    p.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output path (default: <audio>.transcript.md next to the source)",
    )
    p.add_argument(
        "-l", "--language", default=None,
        help="ISO-639-1 language code (e.g. 'he', 'en'). Default: auto-detect.",
    )
    p.add_argument(
        "-m", "--model", default=None,
        help=f"Model name. Default: {HE_MODEL} for he, {DEFAULT_MODEL} otherwise.",
    )
    p.add_argument(
        "--device", default="auto",
        help="cpu / cuda / auto (faster-whisper picks).",
    )
    p.add_argument(
        "--compute-type", default="default",
        help="int8 / int8_float16 / float16 / float32 / default.",
    )
    p.add_argument(
        "--beam-size", type=int, default=5,
        help="Beam search width (higher = better, slower). Default 5.",
    )
    p.add_argument(
        "--no-vad", action="store_true",
        help="Disable Silero VAD pre-filter (default: VAD on).",
    )
    p.add_argument(
        "--initial-prompt", default=None,
        help="Optional initial prompt to bias vocabulary/style (e.g. proper names).",
    )
    p.add_argument(
        "--word-timestamps", action="store_true",
        help="Emit word-level timestamps inside each segment.",
    )
    args = p.parse_args()

    audio_path = args.audio
    if not audio_path.exists():
        print(f"error: audio file not found: {audio_path}", file=sys.stderr)
        return 2

    lang = args.language
    model_name = args.model
    if model_name is None:
        model_name = HE_MODEL if lang == "he" else DEFAULT_MODEL

    from faster_whisper import WhisperModel

    t0 = time.perf_counter()
    print(
        f"[transcribe] loading model={model_name} device={args.device} "
        f"compute_type={args.compute_type}",
        file=sys.stderr,
    )
    model = WhisperModel(model_name, device=args.device, compute_type=args.compute_type)
    print(f"[transcribe] model loaded in {time.perf_counter() - t0:.1f}s", file=sys.stderr)

    segments_iter, info = model.transcribe(
        str(audio_path),
        language=lang,
        vad_filter=not args.no_vad,
        beam_size=args.beam_size,
        initial_prompt=args.initial_prompt,
        word_timestamps=args.word_timestamps,
    )

    detected = info.language
    prob = info.language_probability
    duration = info.duration
    print(
        f"[transcribe] language={detected} ({prob:.0%}); "
        f"duration={timedelta(seconds=int(duration))}",
        file=sys.stderr,
    )

    out_path = args.output or audio_path.with_suffix(".transcript.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    is_hebrew = (lang == "he") or (detected == "he")

    header = []
    header.append(f"# Transcript: {audio_path.name}")
    header.append("")
    header.append(f"- **Source**: `{audio_path}`")
    header.append(f"- **Model**: `{model_name}`")
    header.append(f"- **Language**: {detected} ({prob:.0%}){' (forced)' if lang else ''}")
    header.append(f"- **Duration**: {timedelta(seconds=int(duration))}")
    header.append(f"- **VAD**: {'off' if args.no_vad else 'Silero (on)'}")
    header.append(f"- **Beam size**: {args.beam_size}")
    header.append("")
    header.append("---")
    header.append("")

    body_lines: list[str] = []
    seg_count = 0
    text_chars = 0
    t_seg = time.perf_counter()
    for seg in segments_iter:
        seg_count += 1
        ts = fmt_ts(seg.start)
        text = (seg.text or "").strip()
        text_chars += len(text)
        body_lines.append(f"`{ts}` {text}")
        body_lines.append("")
        # live echo for long files
        print(f"[{ts}] {text}", file=sys.stderr)
    elapsed = time.perf_counter() - t_seg
    rate = duration / elapsed if elapsed > 0 else 0
    print(
        f"[transcribe] {seg_count} segments, {text_chars} chars "
        f"in {elapsed:.1f}s ({rate:.1f}x realtime)",
        file=sys.stderr,
    )

    content = "\n".join(header + body_lines).rstrip() + "\n"
    if is_hebrew:
        content = (
            content.split("\n", 1)[0]  # heading line
            + "\n\n<div dir=\"rtl\">\n\n"
            + "\n".join(content.split("\n")[1:])
            + "\n\n</div>\n"
        )

    out_path.write_text(content, encoding="utf-8")
    print(f"[transcribe] wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
