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
    def is_musescore_or_self_focused(cls, self_pid: int) -> bool:
        """Returns True if the active foreground window is MuseScore 4 or midiplay itself."""
        fg = user32.GetForegroundWindow()
        if not fg:
            return False
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(fg, ctypes.byref(pid))
        if pid.value == self_pid:
            return True
        pname = cls.get_process_name(pid.value)
        return "musescore" in pname

    @classmethod
    def set_window_topmost(cls, hwnd: int, topmost: bool) -> bool:
        """Dynamically updates window z-order (HWND_TOPMOST vs HWND_NOTOPMOST) with zero visual flicker."""
        HWND_TOPMOST = -1
        HWND_NOTOPMOST = -2
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040

        if topmost:
            flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            res = user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, flags)
            user32.BringWindowToTop(hwnd)
            return bool(res)
        else:
            flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            return bool(user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, flags))

    @classmethod
    def find_musescore_hwnd(cls) -> Optional[int]:
        """Finds active MuseScore 4 top-level window handle."""
        # 1. Quick check if MuseScore is currently the active foreground window
        fg = user32.GetForegroundWindow()
        if fg:
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(fg, ctypes.byref(pid))
            if "musescore" in cls.get_process_name(pid.value):
                return fg

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
            return 1

        from ctypes import wintypes
        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

        return found_windows[0] if found_windows else None

    @classmethod
    def get_window_title(cls, hwnd: int) -> str:
        """Returns the title text of the given window."""
        if not hwnd or not user32.IsWindow(hwnd):
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value

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
