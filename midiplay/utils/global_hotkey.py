"""
Global Hotkey Listener for Transparent MuseScore Play-Along Synchronization.
"""

from __future__ import annotations
import threading
from typing import Callable, Optional
from pynput import keyboard


class GlobalHotkeyManager:
    """Monitors OS-level key presses without suppressing them, enabling seamless play-along."""

    def __init__(
        self,
        on_space_toggle: Optional[Callable[[], None]] = None,
        on_copy_shortcut: Optional[Callable[[], None]] = None,
        on_arm_toggle: Optional[Callable[[], None]] = None
    ):
        self.on_space_toggle = on_space_toggle
        self.on_copy_shortcut = on_copy_shortcut
        self.on_arm_toggle = on_arm_toggle

        self.space_sync_enabled = False  # Disabled until user explicitly presses ARM
        self._listener: Optional[keyboard.Listener] = None
        self._ctrl_pressed = False
        self._shift_pressed = False

    def set_space_sync_enabled(self, enabled: bool) -> None:
        self.space_sync_enabled = enabled

    def start(self) -> None:
        if self._listener is not None:
            return

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False  # Do not block keys so MuseScore receives Space normally
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def _on_press(self, key) -> None:
        # Modifier tracking
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self._ctrl_pressed = True
        elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self._shift_pressed = True

        # Check Ctrl+Shift combinations
        if self._ctrl_pressed and self._shift_pressed:
            try:
                if hasattr(key, 'char') and key.char:
                    char_lower = key.char.lower()
                    # Ctrl + Shift + C -> Copy to MuseScore
                    if char_lower == 'c':
                        if self.on_copy_shortcut:
                            self.on_copy_shortcut()
                    # Ctrl + Shift + R -> Toggle ARM
                    elif char_lower == 'r':
                        if self.on_arm_toggle:
                            self.on_arm_toggle()
            except Exception:
                pass

        # Check Space (for Play-along sync with MuseScore)
        if key == keyboard.Key.space:
            if self.space_sync_enabled and self.on_space_toggle:
                self.on_space_toggle()

    def _on_release(self, key) -> None:
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self._ctrl_pressed = False
        elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self._shift_pressed = False
