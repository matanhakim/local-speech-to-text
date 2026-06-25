#!/usr/bin/env python
"""Press any key to see the value to put in dictate.py's PTT_VKS. Esc to quit."""
from pynput import keyboard

print("Press the key you'd like to use for dictation (Esc to quit)...\n", flush=True)


def on_press(key):
    if key == keyboard.Key.esc:
        return False
    vk = getattr(key, "vk", None)
    if vk is None:  # special keys carry the vk on key.value, not key
        vk = getattr(getattr(key, "value", None), "vk", None)
    char = getattr(key, "char", None)
    label = char if (char and char.isprintable()) else str(key).replace("Key.", "")
    print(f"  vk = {vk}    (key: {label})", flush=True)


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
