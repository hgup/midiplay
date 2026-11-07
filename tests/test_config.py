import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from midiplay.utils.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        self.config_file = self.config_dir / "config.json"

        # Patch ConfigManager paths to use temporary directory
        self.p1 = patch.object(ConfigManager, "CONFIG_DIR", self.config_dir)
        self.p2 = patch.object(ConfigManager, "CONFIG_FILE", self.config_file)
        self.p1.start()
        self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        self.temp_dir.cleanup()

    def test_default_values(self):
        self.assertEqual(ConfigManager.get_sync_delay_ms(), 45.0)
        self.assertEqual(ConfigManager.get_latency_offset_ms(), 0.0)
        self.assertEqual(ConfigManager.get_count_in_bars(), 0)
        self.assertFalse(ConfigManager.get_mute_click())
        self.assertFalse(ConfigManager.get_mute_synth())
        self.assertFalse(ConfigManager.get_split_grand_staff())
        self.assertEqual(ConfigManager.get_recording_mode(), "Chords & Lead")
        self.assertIsNone(ConfigManager.get_midi_port())
        self.assertIsNone(ConfigManager.get_audio_device())

    def test_persist_sync_and_latency(self):
        ConfigManager.set_sync_delay_ms(65.0)
        ConfigManager.set_latency_offset_ms(-18.5)
        ConfigManager.set_count_in_bars(2)
        ConfigManager.set_mute_click(True)
        ConfigManager.set_mute_synth(True)
        ConfigManager.set_split_grand_staff(True)
        ConfigManager.set_recording_mode("Polyphonic")
        ConfigManager.set_midi_port("USB MIDI Keyboard")
        ConfigManager.set_audio_device("Headphones (WASAPI)")

        # Verify disk persistence
        self.assertTrue(self.config_file.exists())
        self.assertEqual(ConfigManager.get_sync_delay_ms(), 65.0)
        self.assertEqual(ConfigManager.get_latency_offset_ms(), -18.5)
        self.assertEqual(ConfigManager.get_count_in_bars(), 2)
        self.assertTrue(ConfigManager.get_mute_click())
        self.assertTrue(ConfigManager.get_mute_synth())
        self.assertTrue(ConfigManager.get_split_grand_staff())
        self.assertEqual(ConfigManager.get_recording_mode(), "Polyphonic")
        self.assertEqual(ConfigManager.get_midi_port(), "USB MIDI Keyboard")
        self.assertEqual(ConfigManager.get_audio_device(), "Headphones (WASAPI)")


if __name__ == "__main__":
    unittest.main()
