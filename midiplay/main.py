"""
Entry point for the midiplay desktop application.
"""

import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from midiplay.ui.main_window import MainWindow
from midiplay.ui.styles import DARK_THEME_QSS


def main() -> int:
    # Allow terminal Ctrl+C to terminate cleanly
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("midiplay")
    app.setApplicationDisplayName("midiplay — MuseScore Bridge")
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
