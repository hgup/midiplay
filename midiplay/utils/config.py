"""
Persistent configuration manager for midiplay user preferences.
Stores settings (theme, window position, sync delay, latency offset/calibration, audio/MIDI devices)
in ~/.midiplay/config.json.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class ConfigManager:
    """Manages application settings persisted across sessions."""

    CONFIG_DIR = Path.home() / ".midiplay"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULT_CONFIG: Dict[str, Any] = {
        "theme": "light",
        "sync_delay_ms": 45.0,
        "latency_offset_ms": 0.0,
        "count_in_bars": 0,
        "mute_click": False,
        "mute_synth": False,
        "split_grand_staff": False,
        "recording_mode": "Chords & Lead",
        "auto_sync_musescore": True,
        "midi_port": None,
        "audio_device": None,
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

    @classmethod
    def get_window_pos(cls) -> Optional[Tuple[int, int]]:
        cfg = cls.load_config()
        pos = cfg.get("window_pos")
        if isinstance(pos, list) and len(pos) == 2:
            return (pos[0], pos[1])
        return None

    @classmethod
    def set_window_pos(cls, x: int, y: int) -> None:
        cfg = cls.load_config()
        cfg["window_pos"] = [x, y]
        cls.save_config(cfg)

    @classmethod
    def get_sync_delay_ms(cls) -> float:
        cfg = cls.load_config()
        try:
            return float(cfg.get("sync_delay_ms", 45.0))
        except (ValueError, TypeError):
            return 45.0

    @classmethod
    def set_sync_delay_ms(cls, val: float) -> None:
        cfg = cls.load_config()
        cfg["sync_delay_ms"] = float(val)
        cls.save_config(cfg)

    @classmethod
    def get_latency_offset_ms(cls) -> float:
        cfg = cls.load_config()
        try:
            return float(cfg.get("latency_offset_ms", 0.0))
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def set_latency_offset_ms(cls, val: float) -> None:
        cfg = cls.load_config()
        cfg["latency_offset_ms"] = float(val)
        cls.save_config(cfg)

    @classmethod
    def get_count_in_bars(cls) -> int:
        cfg = cls.load_config()
        try:
            return int(cfg.get("count_in_bars", 0))
        except (ValueError, TypeError):
            return 0

    @classmethod
    def set_count_in_bars(cls, val: int) -> None:
        cfg = cls.load_config()
        cfg["count_in_bars"] = int(val)
        cls.save_config(cfg)

    @classmethod
    def get_mute_click(cls) -> bool:
        cfg = cls.load_config()
        return bool(cfg.get("mute_click", False))

    @classmethod
    def set_mute_click(cls, val: bool) -> None:
        cfg = cls.load_config()
        cfg["mute_click"] = bool(val)
        cls.save_config(cfg)

    @classmethod
    def get_mute_synth(cls) -> bool:
        cfg = cls.load_config()
        return bool(cfg.get("mute_synth", False))

    @classmethod
    def set_mute_synth(cls, val: bool) -> None:
        cfg = cls.load_config()
        cfg["mute_synth"] = bool(val)
        cls.save_config(cfg)

    @classmethod
    def get_split_grand_staff(cls) -> bool:
        cfg = cls.load_config()
        return bool(cfg.get("split_grand_staff", False))

    @classmethod
    def set_split_grand_staff(cls, val: bool) -> None:
        cfg = cls.load_config()
        cfg["split_grand_staff"] = bool(val)
        cls.save_config(cfg)

    @classmethod
    def get_recording_mode(cls) -> str:
        cfg = cls.load_config()
        return str(cfg.get("recording_mode", "Chords & Lead"))

    @classmethod
    def set_recording_mode(cls, val: str) -> None:
        cfg = cls.load_config()
        cfg["recording_mode"] = str(val)
        cls.save_config(cfg)

    @classmethod
    def get_midi_port(cls) -> Optional[str]:
        cfg = cls.load_config()
        return cfg.get("midi_port")

    @classmethod
    def set_midi_port(cls, val: Optional[str]) -> None:
        cfg = cls.load_config()
        cfg["midi_port"] = val
        cls.save_config(cfg)

    @classmethod
    def get_audio_device(cls) -> Optional[str]:
        cfg = cls.load_config()
        return cfg.get("audio_device")

    @classmethod
    def set_audio_device(cls, val: Optional[str]) -> None:
        cfg = cls.load_config()
        cfg["audio_device"] = val
        cls.save_config(cfg)

    @classmethod
    def get_auto_sync_musescore(cls) -> bool:
        cfg = cls.load_config()
        return bool(cfg.get("auto_sync_musescore", True))

    @classmethod
    def set_auto_sync_musescore(cls, val: bool) -> None:
        cfg = cls.load_config()
        cfg["auto_sync_musescore"] = bool(val)
        cls.save_config(cfg)
