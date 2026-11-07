"""
MuseScore Synchronization Manager.

Provides dedicated, real-time score tracking powered exclusively by the
MidiplaySync MuseScore companion plugin (Documents/MuseScore4/Plugins/musescore_state.json).
"""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import tempfile


class MuseScoreSyncManager:
    """Discovers and reads MuseScore score state written by MidiplaySync.qml."""

    def __init__(self, state_file: Optional[Path] = None) -> None:
        self._custom_state_file = state_file
        self.state_file: Path = state_file or (Path.home() / "Documents" / "MuseScore4" / "Plugins" / "musescore_state.json")

    def _get_candidate_paths(self) -> List[Path]:
        if self._custom_state_file is not None:
            return [self._custom_state_file]
        return [
            self.state_file,
            Path.home() / "Documents" / "MuseScore4" / "Plugins" / "musescore_state.json",
            Path.home() / "Documents" / "MuseScore4" / "musescore_state.json",
            Path(tempfile.gettempdir()) / "musescore_state.json",
            Path(tempfile.gettempdir()) / "midiplay_musescore_state.json",
            Path.home() / ".midiplay" / "musescore_state.json",
        ]

    def _get_active_file(self) -> Optional[Path]:
        candidates = self._get_candidate_paths()
        existing = [p for p in candidates if p and p.exists()]
        if not existing:
            return None
        return max(existing, key=lambda p: p.stat().st_mtime)

    def get_active_state(self, window_title: str = "", max_age_seconds: float = 600.0) -> Optional[Dict[str, Any]]:
        """
        Reads the most recent MuseScore state from the plugin sync file.
        Returns state dict if valid and within max_age_seconds, otherwise None.
        """
        state_path = self._get_active_file()
        if not state_path or not state_path.exists():
            return None

        try:
            mtime = state_path.stat().st_mtime
            now = time.time()
            if (now - mtime) > max_age_seconds:
                return None

            with open(state_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            bpm = data.get("bpm")
            num = data.get("time_sig_num")
            den = data.get("time_sig_den")

            if bpm is None or num is None or den is None:
                return None

            return {
                "bpm": int(bpm),
                "time_sig_num": int(num),
                "time_sig_den": int(den),
                "title": str(data.get("title", "MuseScore Score")),
                "timestamp": data.get("timestamp", mtime),
                "version_id": f"plugin_{bpm}_{num}_{den}_{data.get('timestamp', mtime)}",
                "source": "plugin"
            }
        except Exception:
            return None
