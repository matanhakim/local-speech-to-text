# Voice dictation (push-to-talk)

Local push-to-talk dictation into **any focused text field** - Claude Code, an
editor, a browser, anything that accepts a paste. Tap a key, speak, tap again;
~1-2s later the transcribed text appears where your cursor is. Runs on
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) on the CPU. No
cloud, no API key, no limits.

Configured for Hebrew out of the box (the `ivrit-ai` fine-tune); works for any
language - change `MODEL` and `LANGUAGE` at the top of `dictate.py`.

> **Windows-focused.** The global key hook, the auto-paste, and the beeps use
> Win32 APIs. The faster-whisper core is cross-platform; the hotkey layer would
> need porting for macOS/Linux.

## Install

1. Python 3.9+.
2. `pip install -r requirements.txt`
3. The model downloads from HuggingFace on first run (~1.5-3 GB), then runs
   fully offline.

## Run

| Action | How |
|--------|-----|
| Foreground (see status, debug) | double-click `dictate.bat` (Ctrl+C to quit) |
| Hidden background daemon | double-click `start_hidden.vbs` |
| Stop | `stop.bat` |
| Restart (after editing config) | `restart.bat` |
| Read the log (when hidden) | `dictate.log` |

## Use

1. Put the cursor in a text field (Claude Code, editor, browser...).
2. Tap `` ` `` (the key left of **1**), speak, tap `` ` `` again. High beep =
   recording started, low beep = stopped.
3. ~1-2s later the text is pasted (Ctrl+V) into the field.

**Turn dictation on/off: `Ctrl+Alt+` `** - rising beep = on, falling beep =
off. When ON, `` ` `` is captured and dictates; when OFF, `` ` `` types a
normal backtick. So you can leave the daemon always running and toggle it from
the keyboard.

## Start automatically at login

1. Open the Startup folder: `Win+R` -> `shell:startup`.
2. Copy `autostart.vbs.template` there, rename it to `autostart.vbs`, and edit
   the path inside to your clone's `start_hidden.vbs`.
3. It now launches hidden every boot. To disable: delete that file from Startup.

## Tuning (top of `dictate.py`)

- **`PTT_VKS`** - trigger key virtual-key codes (default `(192,)` = `` ` ``).
  Add keys: run `detectkey.bat`, press a key, read its vk, add it - e.g.
  `(192, 186)` to also use `;`.
- **`PTT_MODE`** - `"toggle"` (tap to start, tap to stop) or `"hold"` (record
  while held).
- **`ENABLE_TOGGLE_MODS` / `START_ENABLED`** - the on/off modifier combo, and
  whether dictation is active right after launch.
- **`MODEL` / `LANGUAGE` / `COMPUTE_TYPE` / `CPU_THREADS`** - model and
  performance. `int8` is the fastest compute type on a CPU.
- **`AUTO_PASTE` / `PASTE_CTRL_SHIFT_V`** - set the second to `True` if your
  terminal pastes with Ctrl+Shift+V. The text is always on the clipboard too.
- **`INITIAL_PROMPT`** - bias the model toward your own names/jargon to cut
  errors on proper nouns.
- **`REPLACEMENTS` / `HALLUCINATIONS`** - fixed string corrections, and
  trailing-boilerplate ("thanks for watching") filtering.

## Files

| File | Purpose |
|------|---------|
| `dictate.py` | the daemon (config block at top) |
| `dictate.bat` | run foreground (status + debug) |
| `start_hidden.vbs` | run hidden (no window) |
| `stop.bat` / `restart.bat` | stop / restart the hidden daemon |
| `detectkey.py` / `detectkey.bat` | print a key's vk for `PTT_VKS` |
| `autostart.vbs.template` | drop in Startup to launch at login |
| `requirements.txt` | Python dependencies |
