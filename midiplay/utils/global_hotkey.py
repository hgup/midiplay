"""
Global Hotkey Listener with Context-Aware Recording State Machine.
Supports Shift+Space (start / restart take) and Space (stop & insert).
"""

from __future__ import annotations
import threading
from typing import Callable, Optional
from pynput import keyboard


class GlobalHotkeyManager:
    """Monitors OS-level key presses without suppressing them, enabling seamless play-along."""

    def __init__(
        self,
        on_start_record: Optional[Callable[[], None]] = None,
        on_stop_record: Optional[Callable[[], None]] = None,
        on_restart_record: Optional[Callable[[], None]] = None,
        on_copy_shortcut: Optional[Callable[[], None]] = None,
        on_arm_toggle: Optional[Callable[[], None]] = None
    ):
        self.on_start_record = on_start_record
        self.on_stop_record = on_stop_record
        self.on_restart_record = on_restart_record
        self.on_copy_shortcut = on_copy_shortcut
        self.on_arm_toggle = on_arm_toggle

        self.armed: bool = False
        self.is_recording: bool = False
        self._listener: Optional[keyboard.Listener] = None
        self._ctrl_pressed = False
        self._shift_pressed = False
        self._alt_pressed = False

    def set_armed(self, armed: bool) -> None:
        self.armed = armed

    def set_recording(self, recording: bool) -> None:
        self.is_recording = recording

    # Backward-compatible alias
    def set_space_sync_enabled(self, enabled: bool) -> None:
        self.set_armed(enabled)

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
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self._alt_pressed = True

        # Check Space key
        if key == keyboard.Key.space:
            if self.is_recording:
                if self._shift_pressed:
                    # Shift + Space while recording: RESTART take without inserting
                    if self.on_restart_record:
                        self.on_restart_record()
                else:
                    # Plain Space while recording: STOP and auto-insert
                    if self.on_stop_record:
                        self.on_stop_record()
            else:
                # While idle: Shift + Space when ARM=on starts recording
                if self._shift_pressed and self.armed:
                    if self.on_start_record:
                        self.on_start_record()
                # Plain Space while idle does NOTHING in midiplay (passes to MuseScore)

        # Check Ctrl + Alt + R -> Toggle ARM manually
        if self._ctrl_pressed and self._alt_pressed:
            try:
                if hasattr(key, 'char') and key.char and key.char.lower() == 'r':
                    if self.on_arm_toggle:
                        self.on_arm_toggle()
            except Exception:
                pass

        # Check Ctrl + Shift + C -> Copy to MuseScore
        if self._ctrl_pressed and self._shift_pressed:
            try:
                if hasattr(key, 'char') and key.char and key.char.lower() == 'c':
                    if self.on_copy_shortcut:
                        self.on_copy_shortcut()
            except Exception:
                pass

    def _on_release(self, key) -> None:
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self._ctrl_pressed = False
        elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self._shift_pressed = False
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self._alt_pressed = False
