"""
Persistent configuration manager for midiplay user preferences.
Stores settings (such as active theme) in ~/.midiplay/config.json.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages application settings persisted across sessions."""

    CONFIG_DIR = Path.home() / ".midiplay"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULT_CONFIG: Dict[str, Any] = {
        "theme": "light",  # Default to Modern Clean Light Mode
    }

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Loads configuration from disk, creating defaults if not found."""
        config = cls.DEFAULT_CONFIG.copy()
        try:
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        config.update(data)
        except Exception as e:
            print(f"[ConfigManager] Error reading config file: {e}")
        return config

    @classmethod
    def save_config(cls, data: Dict[str, Any]) -> bool:
        """Saves configuration dictionary to disk."""
        try:
            cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[ConfigManager] Error writing config file: {e}")
            return False

    @classmethod
    def get_theme(cls) -> str:
        cfg = cls.load_config()
        return cfg.get("theme", "light")

    @classmethod
    def set_theme(cls, theme: str) -> None:
        cfg = cls.load_config()
        cfg["theme"] = theme
        cls.save_config(cfg)
