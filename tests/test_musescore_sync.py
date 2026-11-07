import tempfile
import time
import unittest
from pathlib import Path

from midiplay.utils.musescore_sync import MuseScoreSyncManager


class TestMuseScoreSyncManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "musescore_state.json"
        self.sync = MuseScoreSyncManager(state_file=self.state_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_plugin_state_file_valid(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            f.write('{"bpm": 95, "time_sig_num": 7, "time_sig_den": 8, "title": "Plugin Score", "timestamp": 12345}')

        res = self.sync.get_active_state()
        self.assertIsNotNone(res)
        self.assertEqual(res["bpm"], 95)
        self.assertEqual(res["time_sig_num"], 7)
        self.assertEqual(res["time_sig_den"], 8)
        self.assertEqual(res["title"], "Plugin Score")
        self.assertEqual(res["source"], "plugin")

    def test_missing_file_returns_none(self):
        res = self.sync.get_active_state()
        self.assertIsNone(res)

    def test_stale_file_returns_none(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            f.write('{"bpm": 120, "time_sig_num": 4, "time_sig_den": 4, "title": "Old Score"}')

        # Fake old mtime (1000 seconds ago)
        old_time = time.time() - 1000
        import os
        os.utime(self.state_file, (old_time, old_time))

        res = self.sync.get_active_state(max_age_seconds=300)
        self.assertIsNone(res)

    def test_invalid_json_returns_none(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            f.write('{"bpm": 120, "broken')

        res = self.sync.get_active_state()
        self.assertIsNone(res)

    def test_missing_required_keys_returns_none(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            f.write('{"bpm": 120, "title": "No Meter"}')

        res = self.sync.get_active_state()
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
