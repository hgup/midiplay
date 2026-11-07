import unittest
import tempfile
from pathlib import Path
from midiplay.utils.config import ConfigManager
from midiplay.ui.styles import LIGHT_THEME_QSS, DARK_THEME_QSS, PIANO_ROLL_PALETTES

class TestThemeAndConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_config_dir = ConfigManager.CONFIG_DIR
        self.orig_config_file = ConfigManager.CONFIG_FILE
        ConfigManager.CONFIG_DIR = Path(self.temp_dir.name)
        ConfigManager.CONFIG_FILE = ConfigManager.CONFIG_DIR / "config.json"

    def tearDown(self):
        ConfigManager.CONFIG_DIR = self.orig_config_dir
        ConfigManager.CONFIG_FILE = self.orig_config_file
        self.temp_dir.cleanup()

    def test_default_theme_is_light(self):
        theme = ConfigManager.get_theme()
        self.assertEqual(theme, "light")

    def test_set_and_persist_theme(self):
        ConfigManager.set_theme("dark")
        self.assertEqual(ConfigManager.get_theme(), "dark")
        # Ensure written to file
        self.assertTrue(ConfigManager.CONFIG_FILE.exists())
        
        ConfigManager.set_theme("light")
        self.assertEqual(ConfigManager.get_theme(), "light")

    def test_palettes_exist(self):
        self.assertIn("light", PIANO_ROLL_PALETTES)
        self.assertIn("dark", PIANO_ROLL_PALETTES)
        for mode in ("light", "dark"):
            p = PIANO_ROLL_PALETTES[mode]
            self.assertIn("background", p)
            self.assertIn("note_fill", p)
            self.assertIn("playhead", p)

    def test_qss_stylesheets_contain_key_elements(self):
        for qss in (LIGHT_THEME_QSS, DARK_THEME_QSS):
            self.assertIn("RecordBtn", qss)
            self.assertIn("ArmBtn", qss)
            self.assertIn("InsertBtn", qss)
            self.assertIn("StatusPill", qss)

if __name__ == "__main__":
    unittest.main()
