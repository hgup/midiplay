"""
Windows API Integration for MuseScore 4 window discovery, geometry tracking,
auto-focusing, and programmatic clipboard insertion.
"""

from __future__ import annotations
import ctypes
import os
import time
from typing import Optional, Tuple

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
VK_CONTROL = 0x11
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002
SW_RESTORE = 9


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("showCmd", ctypes.c_uint),
        ("ptMinPosition", ctypes.c_long * 2),
        ("ptMaxPosition", ctypes.c_long * 2),
        ("rcNormalPosition", RECT)
    ]


class MuseScoreWindowManager:
    """Manages finding, tracking, focusing, and pasting into MuseScore 4."""

    @classmethod
    def get_process_name(cls, pid: int) -> str:
        h_proc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_proc:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = ctypes.c_ulong(1024)
            if kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(size)):
                return os.path.basename(buf.value).lower()
        finally:
            kernel32.CloseHandle(h_proc)
        return ""

    @classmethod
    def find_musescore_hwnd(cls) -> Optional[int]:
        """Finds active MuseScore 4 top-level window handle."""
        found_windows = []

        def enum_cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd) and not user32.GetParent(hwnd):
                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                pname = cls.get_process_name(pid.value)
                if "musescore" in pname:
                    rect = RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    w = rect.right - rect.left
                    h = rect.bottom - rect.top
                    # Filter out small background splash/helper windows
                    if w > 400 and h > 300:
                        found_windows.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

        return found_windows[0] if found_windows else None

    @classmethod
    def get_window_rect(cls, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """Returns (left, top, right, bottom) of the window."""
        if not hwnd or not user32.IsWindow(hwnd):
            return None
        rect = RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return (rect.left, rect.top, rect.right, rect.bottom)
        return None

    @classmethod
    def is_maximized(cls, hwnd: int) -> bool:
        wp = WINDOWPLACEMENT()
        wp.length = ctypes.sizeof(WINDOWPLACEMENT)
        if user32.GetWindowPlacement(hwnd, ctypes.byref(wp)):
            return wp.showCmd == 3  # SW_SHOWMAXIMIZED
        return False

    @classmethod
    def calculate_toolbar_notch_pos(
        cls,
        hwnd: int,
        strip_width: int,
        strip_height: int
    ) -> Optional[Tuple[int, int]]:
        """
        Calculates screen (x, y) to position midiplay in the empty notch
        of MuseScore 4's top toolbar area.
        """
        rect = cls.get_window_rect(hwnd)
        if not rect:
            return None

        left, top, right, bottom = rect
        maximized = cls.is_maximized(hwnd)

        # In MuseScore 4:
        # Title bar + Menus + Tabs are ~64-70px from top
        # Right edge has playback toolbar (~300px wide) above the notch
        y_offset = 64 if maximized else 68
        target_x = right - strip_width - 16
        target_y = top + y_offset

        return (target_x, target_y)

    @classmethod
    def focus_and_paste(cls, hwnd: Optional[int] = None) -> bool:
        """Focuses MuseScore window and simulates Ctrl + V to insert notes."""
        target_hwnd = hwnd or cls.find_musescore_hwnd()
        if not target_hwnd or not user32.IsWindow(target_hwnd):
            return False

        if user32.IsIconic(target_hwnd):
            user32.ShowWindow(target_hwnd, SW_RESTORE)

        # Attach thread inputs to allow setting foreground window reliably
        cur_thread = kernel32.GetCurrentThreadId()
        target_thread = user32.GetWindowThreadProcessId(target_hwnd, None)

        if cur_thread != target_thread:
            user32.AttachThreadInput(cur_thread, target_thread, True)

        try:
            user32.SetForegroundWindow(target_hwnd)
            user32.SetFocus(target_hwnd)
            time.sleep(0.05)

            # Send Ctrl + V
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            time.sleep(0.02)
            user32.keybd_event(VK_V, 0, 0, 0)
            time.sleep(0.02)
            user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            return True
        finally:
            if cur_thread != target_thread:
                user32.AttachThreadInput(cur_thread, target_thread, False)
