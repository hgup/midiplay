import unittest
import json
import tempfile
from pathlib import Path
from midiplay.core.clock import Clock


class TestMuseScoreStateSync(unittest.TestCase):

    def setUp(self):
        self.clock = Clock(bpm=120.0, time_sig_num=4, time_sig_den=4)

    def test_sync_tempo_and_meter(self):
        sample_payload = {
            "bpm": 88,
            "time_sig_num": 3,
            "time_sig_den": 4,
            "title": "Waltz in A minor"
        }

        # Simulating state file read
        bpm = sample_payload.get("bpm")
        num = sample_payload.get("time_sig_num")
        den = sample_payload.get("time_sig_den")

        self.clock.set_bpm(float(bpm))
        self.clock.set_time_signature(num, den)

        self.assertEqual(self.clock.bpm, 88.0)
        self.assertEqual(self.clock.time_sig_num, 3)
        self.assertEqual(self.clock.time_sig_den, 4)


if __name__ == "__main__":
    unittest.main()
