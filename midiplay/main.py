"""
Entry point for the midiplay desktop application.
"""

import sys
from pathlib import Path

# Ensure repo root is always in sys.path regardless of how script was invoked
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from midiplay.ui.main_window import MainWindow
from midiplay.ui.styles import LIGHT_THEME_QSS, DARK_THEME_QSS
from midiplay.utils.config import ConfigManager


def main() -> int:
    # Allow terminal Ctrl+C to terminate cleanly
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("midiplay")
    app.setApplicationDisplayName("midiplay — MuseScore Bridge")
    
    initial_theme = ConfigManager.get_theme()
    app.setStyleSheet(LIGHT_THEME_QSS if initial_theme == "light" else DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
