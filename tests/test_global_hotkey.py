import unittest
from unittest.mock import MagicMock
from pynput import keyboard
from midiplay.utils.global_hotkey import GlobalHotkeyManager


class TestGlobalHotkeyManager(unittest.TestCase):

    def setUp(self):
        self.start_mock = MagicMock()
        self.stop_mock = MagicMock()
        self.restart_mock = MagicMock()
        self.copy_mock = MagicMock()
        self.arm_mock = MagicMock()

        self.mgr = GlobalHotkeyManager(
            on_start_record=self.start_mock,
            on_stop_record=self.stop_mock,
            on_restart_record=self.restart_mock,
            on_copy_shortcut=self.copy_mock,
            on_arm_toggle=self.arm_mock
        )

    def test_idle_disarmed_ignores_space_and_shift_space(self):
        self.mgr.set_armed(False)
        self.mgr.set_recording(False)

        # Plain Space -> does nothing
        self.mgr._on_press(keyboard.Key.space)
        self.start_mock.assert_not_called()
        self.stop_mock.assert_not_called()

        # Shift + Space when disarmed -> does nothing
        self.mgr._on_press(keyboard.Key.shift)
        self.mgr._on_press(keyboard.Key.space)
        self.mgr._on_release(keyboard.Key.shift)
        self.start_mock.assert_not_called()
        self.stop_mock.assert_not_called()

    def test_idle_armed_plain_space_does_nothing(self):
        """Plain space while idle should pass to MuseScore without starting recording."""
        self.mgr.set_armed(True)
        self.mgr.set_recording(False)

        self.mgr._on_press(keyboard.Key.space)
        self.start_mock.assert_not_called()
        self.stop_mock.assert_not_called()

    def test_idle_armed_shift_space_starts_recording(self):
        self.mgr.set_armed(True)
        self.mgr.set_recording(False)

        self.mgr._on_press(keyboard.Key.shift)
        self.mgr._on_press(keyboard.Key.space)
        self.mgr._on_release(keyboard.Key.shift)

        self.start_mock.assert_called_once()
        self.stop_mock.assert_not_called()
        self.restart_mock.assert_not_called()

    def test_recording_plain_space_stops_and_inserts(self):
        self.mgr.set_armed(True)
        self.mgr.set_recording(True)

        self.mgr._on_press(keyboard.Key.space)

        self.stop_mock.assert_called_once()
        self.start_mock.assert_not_called()
        self.restart_mock.assert_not_called()

    def test_recording_shift_space_restarts_take(self):
        self.mgr.set_armed(True)
        self.mgr.set_recording(True)

        self.mgr._on_press(keyboard.Key.shift)
        self.mgr._on_press(keyboard.Key.space)
        self.mgr._on_release(keyboard.Key.shift)

        self.restart_mock.assert_called_once()
        self.stop_mock.assert_not_called()
        self.start_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
