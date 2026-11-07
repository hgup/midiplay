import unittest
from midiplay.utils.musescore_window import MuseScoreWindowManager
from midiplay.utils.bpm_detector import detect_musescore_bpm

class TestMuseScoreIntegration(unittest.TestCase):
    def test_calculate_toolbar_notch_pos_no_crash(self):
        # Even with invalid/dummy HWND, must safely return None without throwing exceptions
        pos = MuseScoreWindowManager.calculate_toolbar_notch_pos(0, 400, 34)
        self.assertIsNone(pos)

    def test_focus_and_paste_no_crash_on_invalid_hwnd(self):
        res = MuseScoreWindowManager.focus_and_paste(hwnd=99999999)
        self.assertFalse(res)

    def test_bpm_detector_no_crash_on_invalid_hwnd(self):
        res = detect_musescore_bpm(hwnd=99999999)
        self.assertIsNone(res)

if __name__ == "__main__":
    unittest.main()
