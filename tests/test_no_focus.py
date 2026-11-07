import unittest
from ctypes import wintypes
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

# Ensure single headless QApplication instance
app = QApplication.instance() or QApplication([])

class DummyNoFocusWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _apply_no_focus_recursively(self, root: QWidget) -> None:
        root.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for child in root.findChildren(QWidget):
            child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def nativeEvent(self, eventType, message):
        try:
            msg = wintypes.MSG.from_address(int(message))
            WM_MOUSEACTIVATE = 0x0021
            MA_NOACTIVATE = 3
            if msg.message == WM_MOUSEACTIVATE:
                return True, MA_NOACTIVATE
        except Exception:
            pass
        return False, 0

    def keyPressEvent(self, event) -> None:
        event.ignore()

    def keyReleaseEvent(self, event) -> None:
        event.ignore()


class TestNoFocusHUD(unittest.TestCase):
    def test_apply_no_focus_recursively(self):
        win = DummyNoFocusWindow()
        layout = QVBoxLayout(win)
        btn1 = QPushButton("1", win)
        btn2 = QPushButton("2", win)
        # Explicitly set click focus before recursive call
        btn1.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        btn2.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(btn1)
        layout.addWidget(btn2)

        win._apply_no_focus_recursively(win)

        self.assertEqual(win.focusPolicy(), Qt.FocusPolicy.NoFocus)
        self.assertEqual(btn1.focusPolicy(), Qt.FocusPolicy.NoFocus)
        self.assertEqual(btn2.focusPolicy(), Qt.FocusPolicy.NoFocus)

    def test_key_events_ignored(self):
        win = DummyNoFocusWindow()
        press_ev = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
        win.keyPressEvent(press_ev)
        self.assertFalse(press_ev.isAccepted())

        release_ev = QKeyEvent(QKeyEvent.Type.KeyRelease, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
        win.keyReleaseEvent(release_ev)
        self.assertFalse(release_ev.isAccepted())

    def test_native_event_mouse_activate_handling(self):
        win = DummyNoFocusWindow()
        # Simulate MSG struct with WM_MOUSEACTIVATE
        msg = wintypes.MSG()
        msg.message = 0x0021  # WM_MOUSEACTIVATE
        import ctypes
        ptr = ctypes.addressof(msg)
        handled, lresult = win.nativeEvent(b"windows_generic_MSG", ptr)
        self.assertTrue(handled)
        self.assertEqual(lresult, 3)  # MA_NOACTIVATE

        # Simulate MSG struct with other message
        msg_other = wintypes.MSG()
        msg_other.message = 0x000F  # WM_PAINT
        ptr_other = ctypes.addressof(msg_other)
        handled_other, lresult_other = win.nativeEvent(b"windows_generic_MSG", ptr_other)
        self.assertFalse(handled_other)
        self.assertEqual(lresult_other, 0)


if __name__ == "__main__":
    unittest.main()
