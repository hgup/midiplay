"""
Modern Light and Dark stylesheets and visual palettes for midiplay.
"""

from typing import Dict, Any

# --- Crisp Modern Studio Light Theme ---
LIGHT_THEME_QSS = """
QMainWindow {
    background-color: #f8fafc;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}

QWidget#CentralWidget {
    background-color: #f8fafc;
    border-radius: 8px;
}

QWidget#DrawerWidget {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}

QLabel {
    color: #334155;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11px;
    font-weight: 500;
}

QPushButton {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 5px 10px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton#RecordBtn {
    background-color: #dc2626;
    border: 1px solid #b91c1c;
    color: #ffffff;
    font-weight: bold;
    min-width: 60px;
}

QPushButton#RecordBtn:hover {
    background-color: #ef4444;
}

QPushButton#RecordBtn[recording="true"] {
    background-color: #b91c1c;
    border: 2px solid #ffffff;
}

QPushButton#ArmBtn {
    background-color: #ffffff;
    border: 1px solid #d97706;
    color: #d97706;
    font-weight: bold;
    min-width: 52px;
}

QPushButton#ArmBtn:hover {
    background-color: #fef3c7;
    border-color: #b45309;
}

QPushButton#ArmBtn[armed="true"] {
    background-color: #d97706;
    border: 1px solid #b45309;
    color: #ffffff;
}

QPushButton#CopyBtn {
    background-color: #16a34a;
    border: 1px solid #15803d;
    color: #ffffff;
    font-weight: bold;
    min-width: 90px;
}

QPushButton#CopyBtn:hover {
    background-color: #22c55e;
}

QPushButton#CopyBtn:pressed {
    background-color: #15803d;
}

QPushButton#ThemeBtn {
    background-color: #ffffff;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    font-size: 12px;
    padding: 4px 6px;
    min-width: 28px;
    max-width: 28px;
}

QPushButton#ThemeBtn:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}

QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 3px 6px;
    font-size: 11px;
}

QComboBox::drop-down {
    border: none;
    width: 16px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    border: 1px solid #cbd5e1;
}

QSlider::groove:horizontal {
    border: 1px solid #cbd5e1;
    height: 4px;
    background: #e2e8f0;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #3b82f6;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #2563eb;
    border: 1px solid #1d4ed8;
    width: 12px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 6px;
}

QCheckBox {
    color: #334155;
    font-size: 11px;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background: #2563eb;
    border-color: #1d4ed8;
}

QLabel#StatusPill {
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 10px;
    text-transform: uppercase;
}

QLabel#StatusPill[state="IDLE"] {
    background-color: #e2e8f0;
    color: #475569;
}

QLabel#StatusPill[state="COUNT_IN"] {
    background-color: #fef3c7;
    color: #b45309;
}

QLabel#StatusPill[state="RECORDING"] {
    background-color: #fee2e2;
    color: #b91c1c;
}

QLabel#StatusPill[state="QUANTIZING"] {
    background-color: #dbeafe;
    color: #1d4ed8;
}

QLabel#StatusPill[state="COPIED"] {
    background-color: #dcfce7;
    color: #15803d;
}

QDialog {
    background-color: #f8fafc;
    color: #0f172a;
}

QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    text-align: center;
    background-color: #e2e8f0;
    color: #0f172a;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 3px;
}
"""

# --- Pro Studio Obsidian Dark Theme ---
DARK_THEME_QSS = """
QMainWindow {
    background-color: #1e1e24;
    color: #e0e0e0;
    border: 1px solid #33333e;
    border-radius: 8px;
}

QWidget#CentralWidget {
    background-color: #1e1e24;
    border-radius: 8px;
}

QWidget#DrawerWidget {
    background-color: #17171c;
    border-top: 1px solid #2a2a34;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}

QLabel {
    color: #cfd2d6;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11px;
    font-weight: 500;
}

QPushButton {
    background-color: #2b2b36;
    color: #f0f0f5;
    border: 1px solid #3d3d4d;
    border-radius: 5px;
    padding: 5px 10px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #363645;
    border-color: #525266;
}

QPushButton:pressed {
    background-color: #24242e;
}

QPushButton#RecordBtn {
    background-color: #c92a2a;
    border: 1px solid #e03131;
    color: #ffffff;
    font-weight: bold;
    min-width: 60px;
}

QPushButton#RecordBtn:hover {
    background-color: #e03131;
}

QPushButton#RecordBtn[recording="true"] {
    background-color: #ff4757;
    border: 2px solid #ffffff;
}

QPushButton#ArmBtn {
    background-color: #2b2b36;
    border: 1px solid #78350f;
    color: #f59e0b;
    font-weight: bold;
    min-width: 52px;
}

QPushButton#ArmBtn:hover {
    background-color: #451a03;
    border-color: #d97706;
}

QPushButton#ArmBtn[armed="true"] {
    background-color: #d97706;
    border: 1px solid #fbbf24;
    color: #ffffff;
}

QPushButton#CopyBtn {
    background-color: #2f9e44;
    border: 1px solid #37b24d;
    color: #ffffff;
    font-weight: bold;
    min-width: 90px;
}

QPushButton#CopyBtn:hover {
    background-color: #37b24d;
}

QPushButton#CopyBtn:pressed {
    background-color: #2b8a3e;
}

QPushButton#ThemeBtn {
    background-color: #2b2b36;
    color: #f0f0f5;
    border: 1px solid #3d3d4d;
    border-radius: 5px;
    font-size: 12px;
    padding: 4px 6px;
    min-width: 28px;
    max-width: 28px;
}

QPushButton#ThemeBtn:hover {
    background-color: #363645;
    border-color: #525266;
}

QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #262630;
    color: #f0f0f5;
    border: 1px solid #3d3d4d;
    border-radius: 4px;
    padding: 3px 6px;
    font-size: 11px;
}

QComboBox::drop-down {
    border: none;
    width: 16px;
}

QComboBox QAbstractItemView {
    background-color: #262630;
    color: #e0e0e0;
    selection-background-color: #3b5bdb;
    border: 1px solid #3d3d4d;
}

QSlider::groove:horizontal {
    border: 1px solid #33333e;
    height: 4px;
    background: #2a2a36;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #4dabf7;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #74c0fc;
    border: 1px solid #3b5bdb;
    width: 12px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 6px;
}

QCheckBox {
    color: #b0b4ba;
    font-size: 11px;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid #3d3d4d;
    background: #262630;
}

QCheckBox::indicator:checked {
    background: #3b5bdb;
    border-color: #4dabf7;
}

QLabel#StatusPill {
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 10px;
    text-transform: uppercase;
}

QLabel#StatusPill[state="IDLE"] {
    background-color: #2d3139;
    color: #8c95a0;
}

QLabel#StatusPill[state="COUNT_IN"] {
    background-color: #5c3b12;
    color: #ffd43b;
}

QLabel#StatusPill[state="RECORDING"] {
    background-color: #611317;
    color: #ff6b6b;
}

QLabel#StatusPill[state="QUANTIZING"] {
    background-color: #364fc7;
    color: #91a7ff;
}

QLabel#StatusPill[state="COPIED"] {
    background-color: #1e4620;
    color: #51cf66;
}

QDialog {
    background-color: #1e1e24;
    color: #e0e0e0;
}

QProgressBar {
    border: 1px solid #3d3d4d;
    border-radius: 4px;
    text-align: center;
    background-color: #262630;
    color: #f0f0f5;
}

QProgressBar::chunk {
    background-color: #3b5bdb;
    border-radius: 3px;
}
"""

# Color palettes for custom-rendered widgets (such as PianoRoll)
PIANO_ROLL_PALETTES: Dict[str, Dict[str, str]] = {
    "light": {
        "background": "#ffffff",
        "border": "#e2e8f0",
        "placeholder": "#94a3b8",
        "barline": "#cbd5e1",
        "measure_label": "#64748b",
        "note_fill": "#2563eb",
        "note_border": "#1d4ed8",
        "note_text": "#ffffff",
        "playhead": "#dc2626",
    },
    "dark": {
        "background": "#141418",
        "border": "#2a2a34",
        "placeholder": "#5c5f66",
        "barline": "#3d424d",
        "measure_label": "#6d7582",
        "note_fill": "#339af0",
        "note_border": "#1c7ed6",
        "note_text": "#ffffff",
        "playhead": "#ff6b6b",
    }
}
