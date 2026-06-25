#!/usr/bin/env python
"""
Push-to-talk voice dictation into any focused text field (Claude Code, an
editor, a browser, anything that accepts a paste).

Tap the trigger key (default: the ` key, just left of 1), speak, tap again.
The clip is transcribed locally with faster-whisper (CPU, int8), cleaned,
copied to the clipboard, and pasted (Ctrl+V) into whatever window has focus.
Nothing leaves the machine.

The trigger key is consumed system-wide while this runs, so a printable key
like ` never leaks a character into your text. The model stays loaded in
memory for low latency (~1-2s per short utterance).

This is configured for Hebrew out of the box (the ivrit-ai fine-tune), but it
works for any language: change MODEL and LANGUAGE in the config block below.

Usage:  python dictate.py   (or double-click dictate.bat)
Quit:   Ctrl+C in this window.

Windows-focused: the global key hook, the Ctrl+V paste, and the beeps use
Win32 APIs. The faster-whisper core is cross-platform; porting the hotkey
layer to macOS/Linux is left as an exercise.
"""
from __future__ import annotations

import re
import os
import sys
import time
import atexit
import ctypes
import threading

import numpy as np
import sounddevice as sd
import pyperclip
from pynput import keyboard
from faster_whisper import WhisperModel

# ---- config -------------------------------------------------------------
# Pick a model for your hardware and language. The Hebrew fine-tune below is
# the default example; for other languages use a generic size such as
# "large-v3-turbo" or "small", and look for a fine-tune in your language on
# Hugging Face first - it usually beats the generic model of the same size.
MODEL = "ivrit-ai/whisper-large-v3-turbo-ct2"  # e.g. "large-v3-turbo", "small"
DEVICE = "cpu"                 # "cuda" only if you have an NVIDIA GPU
COMPUTE_TYPE = "int8"          # ~2x faster than float on CPU, negligible WER cost
CPU_THREADS = 8                # set to your physical core count
LANGUAGE = "he"               # ISO-639-1 code of the language you speak; None = auto
BEAM_SIZE = 1                  # greedy = fastest; fine for short dictation
SAMPLE_RATE = 16000            # Whisper's native rate

PTT_VKS = (192,)               # trigger keys - ANY of these fires dictation.
                               # 192 = the ` key (left of 1, always on the laptop).
                               # Each is suppressed system-wide while running. To add
                               # a key (e.g. 186 = ; on a US layout), run detectkey.bat
                               # for its vk and add it here, e.g. (192, 186).
PTT_LABEL = "`"                # human label for the trigger, used in messages only
PTT_MODE = "toggle"            # "toggle" (tap to start, tap again to stop) or "hold"

ENABLE_TOGGLE_MODS = ("ctrl", "alt")  # held with a trigger key, flips dictation on/off
                               # (Ctrl+Alt+`). When OFF, the trigger key types normally.
START_ENABLED = True           # dictation active right after launch / boot

AUTO_PASTE = True              # paste into the focused window after transcribe
PASTE_CTRL_SHIFT_V = False     # set True if your terminal pastes with Ctrl+Shift+V
BEEP = True                    # audio cue on record start / stop
MIN_SECONDS = 0.3              # ignore accidental taps shorter than this

# Bias the model toward YOUR domain vocabulary (names, projects, jargon) to cut
# errors on proper nouns. This is only an example - replace it with your own.
INITIAL_PROMPT = (
    "Dictation. Names: Ada Lovelace, Alan Turing. "
    "Terms: faster-whisper, Claude Code, push-to-talk."
)

# Fixed corrections applied to every transcript (case-insensitive). Add terms
# the model keeps mishearing. These examples fix common "Claude Code" mishears.
REPLACEMENTS = {
    "Cloud Code": "Claude Code",
    "Code Code": "Claude Code",
}

# Trailing hallucinations Whisper emits on short or clean clips; filtered out.
# Add the boilerplate your language's model tends to tack on (these cover en/he).
HALLUCINATIONS = (
    "Thank you.", "Thanks for watching", "Please subscribe",
    "תודה רבה", "תודה שצפיתם", "תודה על הצפייה", "כתוביות",
)
# -------------------------------------------------------------------------

# Win32 keyboard messages seen by the low-level hook filter.
_WM_KEYDOWN = {0x0100, 0x0104}   # WM_KEYDOWN, WM_SYSKEYDOWN
_WM_KEYUP = {0x0101, 0x0105}     # WM_KEYUP, WM_SYSKEYUP

try:
    import winsound

    def beep(freq: int) -> None:
        if BEEP:
            try:
                winsound.Beep(freq, 90)
            except Exception:
                pass
except ImportError:  # non-Windows
    def beep(freq: int) -> None:
        pass


TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_MOD_VK = {"ctrl": 0x11, "alt": 0x12, "shift": 0x10}

try:
    _user32 = ctypes.windll.user32
    _user32.GetAsyncKeyState.argtypes = (ctypes.c_int,)
    _user32.GetAsyncKeyState.restype = ctypes.c_short

    def _mods_held(mods) -> bool:
        return all(_user32.GetAsyncKeyState(_MOD_VK[m]) & 0x8000 for m in mods)
except (AttributeError, OSError):  # non-Windows
    def _mods_held(mods) -> bool:
        return False


def _announce(enabled: bool) -> None:
    for f in (600, 1000) if enabled else (1000, 600):
        beep(f)


def _setup_io() -> None:
    # Under pythonw there is no console, so route output to a log file. Also write
    # a pid file so stop.bat / restart.bat can find and kill this process.
    if sys.stdout is None or sys.stderr is None:
        f = open(os.path.join(TOOL_DIR, "dictate.log"), "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = f
    try:
        pid_path = os.path.join(TOOL_DIR, "dictate.pid")
        with open(pid_path, "w") as p:
            p.write(str(os.getpid()))
        atexit.register(lambda: os.path.exists(pid_path) and os.remove(pid_path))
    except OSError:
        pass


class Dictation:
    def __init__(self) -> None:
        print(f"loading model {MODEL} on {DEVICE}/{COMPUTE_TYPE} ...", flush=True)
        t0 = time.time()
        self.model = WhisperModel(
            MODEL, device=DEVICE, compute_type=COMPUTE_TYPE, cpu_threads=CPU_THREADS
        )
        hint = (
            f"tap {PTT_LABEL} to start, tap again to insert"
            if PTT_MODE == "toggle"
            else f"hold {PTT_LABEL} to talk, release to insert"
        )
        print(
            f"model ready in {time.time() - t0:.1f}s. {hint}. Ctrl+C to quit.",
            flush=True,
        )
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._recording = False
        self._busy = False
        self._kbd = keyboard.Controller()

    def is_recording(self) -> bool:
        return self._recording

    def _audio_cb(self, indata, frames, time_info, status) -> None:
        self._frames.append(indata.copy())

    def start(self) -> None:
        if self._recording or self._busy:
            return
        self._recording = True
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="float32",
            callback=self._audio_cb,
        )
        self._stream.start()
        beep(880)
        print("● recording...", flush=True)

    def stop(self) -> None:
        if not self._recording:
            return
        self._recording = False
        self._busy = True
        try:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
            self._stream = None
            beep(440)
            self._process()
        finally:
            self._busy = False

    def _process(self) -> None:
        if not self._frames:
            print("(empty)", flush=True)
            return
        audio = np.concatenate(self._frames, axis=0).flatten()
        dur = len(audio) / SAMPLE_RATE
        if dur < MIN_SECONDS:
            print(f"(too short: {dur:.2f}s)", flush=True)
            return
        print(f"transcribing {dur:.1f}s...", flush=True)
        t0 = time.time()
        segments, _ = self.model.transcribe(
            audio, language=LANGUAGE, beam_size=BEAM_SIZE,
            vad_filter=True, initial_prompt=INITIAL_PROMPT,
        )
        text = self._clean(" ".join(s.text.strip() for s in segments))
        elapsed = time.time() - t0
        if not text:
            print(f"(no speech, {elapsed:.1f}s)", flush=True)
            return
        print(f'→ "{text}"  ({elapsed:.1f}s)', flush=True)
        pyperclip.copy(text)
        if AUTO_PASTE:
            self._paste()

    def _paste(self) -> None:
        time.sleep(0.05)
        mods = [keyboard.Key.ctrl]
        if PASTE_CTRL_SHIFT_V:
            mods.append(keyboard.Key.shift)
        if len(mods) == 2:
            with self._kbd.pressed(mods[0]), self._kbd.pressed(mods[1]):
                self._kbd.tap("v")
        else:
            with self._kbd.pressed(mods[0]):
                self._kbd.tap("v")

    @staticmethod
    def _clean(text: str) -> str:
        text = " ".join(text.split())
        for wrong, right in REPLACEMENTS.items():
            text = re.sub(re.escape(wrong), right, text, flags=re.IGNORECASE)
        changed = True
        while changed and text:
            changed = False
            for h in HALLUCINATIONS:
                if text == h or text.endswith(" " + h) or text.endswith(h):
                    text = text[: -len(h)].strip(" .,،")
                    changed = True
        return text.strip()


def main() -> int:
    _setup_io()
    d = Dictation()
    state = {"enabled": START_ENABLED}
    held: set = set()  # trigger vks currently down (debounces keydown auto-repeat)
    box: list = []     # holds the Listener so the filter can call suppress_event()

    mods = "+".join(m.capitalize() for m in ENABLE_TOGGLE_MODS)
    print(
        f"dictation {'ON' if state['enabled'] else 'OFF'} at launch. "
        f"{PTT_LABEL} = dictate, {mods}+{PTT_LABEL} = on/off.",
        flush=True,
    )

    def _bg(fn):
        threading.Thread(target=fn, daemon=True).start()

    def _suppress():
        if box:
            box[0].suppress_event()  # raises SuppressException -> consume the key
        return False

    def win32_filter(msg, data):
        # Non-trigger keys (including the plain modifiers) pass straight through.
        vk = data.vkCode
        if vk not in PTT_VKS:
            return True
        is_down = msg in _WM_KEYDOWN

        # Modifier combo + trigger -> flip dictation on/off (and consume the key).
        if is_down and _mods_held(ENABLE_TOGGLE_MODS):
            if vk not in held:
                held.add(vk)
                state["enabled"] = not state["enabled"]
                en = state["enabled"]
                print(f"dictation {'ON' if en else 'OFF'}", flush=True)
                _bg(lambda: _announce(en))
            return _suppress()

        # Dictation active -> run the trigger logic and consume the key.
        if state["enabled"]:
            if is_down and vk not in held:
                held.add(vk)
                if PTT_MODE == "hold" or not d.is_recording():
                    _bg(d.start)
                else:
                    _bg(d.stop)
            elif msg in _WM_KEYUP:
                held.discard(vk)
                if PTT_MODE == "hold":
                    _bg(d.stop)
            return _suppress()

        # Disabled and no combo -> let the key type normally.
        held.discard(vk)
        return True

    try:
        listener = keyboard.Listener(
            on_press=lambda k: None, win32_event_filter=win32_filter
        )
        box.append(listener)
        with listener:
            listener.join()
    except KeyboardInterrupt:
        print("\nbye.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
