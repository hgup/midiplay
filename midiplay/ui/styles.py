"""
Modern Light and Dark stylesheets and visual palettes for midiplay.
Crafted to blend seamlessly into MuseScore 4's native toolbar geometry.
"""

from typing import Dict, Any

# --- Crisp Modern Studio Light Theme (Matches MuseScore 4 Toolbar) ---
LIGHT_THEME_QSS = """
QMainWindow {
    background-color: #f0f2f5;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
}

QWidget#CentralWidget {
    background-color: #f0f2f5;
    border-radius: 6px;
}

QWidget#ToolbarStrip {
    background-color: #f0f2f5;
    border-radius: 6px;
}

QWidget#DrawerWidget {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
}

QLabel {
    color: #334155;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11px;
    font-weight: 500;
}

QLabel#DragHandle {
    color: #94a3b8;
    font-size: 13px;
    font-weight: bold;
    padding: 0 2px;
}

QLabel#DragHandle:hover {
    color: #475569;
}

QPushButton {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 3px 6px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton#RecordBtn {
    background-color: #ffffff;
    border: 1px solid #f87171;
    color: #dc2626;
    font-size: 14px;
    font-weight: bold;
    min-width: 28px;
    max-width: 28px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#RecordBtn:hover {
    background-color: #fee2e2;
    border-color: #ef4444;
}

QPushButton#RecordBtn[recording="true"] {
    background-color: #dc2626;
    border: 1px solid #b91c1c;
    color: #ffffff;
}

QPushButton#ArmBtn {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #64748b;
    font-weight: bold;
    font-size: 11px;
    min-width: 26px;
    max-width: 26px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#ArmBtn:hover {
    background-color: #fef3c7;
    border-color: #d97706;
    color: #d97706;
}

QPushButton#ArmBtn[armed="true"] {
    background-color: #d97706;
    border: 1px solid #b45309;
    color: #ffffff;
}

QPushButton#PreviewBtn {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #334155;
    font-size: 10px;
    min-width: 26px;
    max-width: 26px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#PreviewBtn:hover {
    background-color: #e0f2fe;
    border-color: #0284c7;
    color: #0284c7;
}

QPushButton#InsertBtn {
    background-color: #16a34a;
    border: 1px solid #15803d;
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
    padding: 3px 8px;
    min-height: 24px;
    border-radius: 4px;
}

QPushButton#InsertBtn:hover {
    background-color: #22c55e;
}

QPushButton#InsertBtn:pressed {
    background-color: #15803d;
}

QPushButton#WindowCloseBtn {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    font-size: 11px;
    min-width: 18px;
    max-width: 18px;
    padding: 0;
}

QPushButton#WindowCloseBtn:hover {
    background-color: #ef4444;
    color: #ffffff;
    border-radius: 3px;
}

QPushButton#SnapBtn {
    background-color: transparent;
    border: 1px solid #cbd5e1;
    color: #64748b;
    font-size: 11px;
    min-width: 22px;
    max-width: 22px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#SnapBtn:hover {
    background-color: #e2e8f0;
    color: #0f172a;
}

QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 11px;
    min-height: 22px;
}

QComboBox::drop-down {
    border: none;
    width: 14px;
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
    width: 13px;
    height: 13px;
    border-radius: 3px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background: #2563eb;
    border-color: #1d4ed8;
}

QLabel#StatusPill {
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: bold;
    font-size: 9px;
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
"""

# --- Pro Studio Obsidian Dark Theme ---
DARK_THEME_QSS = """
QMainWindow {
    background-color: #1e1e24;
    color: #e0e0e0;
    border: 1px solid #33333e;
    border-radius: 6px;
}

QWidget#CentralWidget {
    background-color: #1e1e24;
    border-radius: 6px;
}

QWidget#ToolbarStrip {
    background-color: #1e1e24;
    border-radius: 6px;
}

QWidget#DrawerWidget {
    background-color: #17171c;
    border-top: 1px solid #2a2a34;
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
}

QLabel {
    color: #cfd2d6;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11px;
    font-weight: 500;
}

QLabel#DragHandle {
    color: #525266;
    font-size: 13px;
    font-weight: bold;
    padding: 0 2px;
}

QLabel#DragHandle:hover {
    color: #a0a0b8;
}

QPushButton {
    background-color: #2b2b36;
    color: #f0f0f5;
    border: 1px solid #3d3d4d;
    border-radius: 4px;
    padding: 3px 6px;
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
    background-color: #2b2b36;
    border: 1px solid #c92a2a;
    color: #ff6b6b;
    font-size: 14px;
    font-weight: bold;
    min-width: 28px;
    max-width: 28px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#RecordBtn:hover {
    background-color: #611317;
}

QPushButton#RecordBtn[recording="true"] {
    background-color: #c92a2a;
    border: 1px solid #ffffff;
    color: #ffffff;
}

QPushButton#ArmBtn {
    background-color: #2b2b36;
    border: 1px solid #3d3d4d;
    color: #a0a0b8;
    font-weight: bold;
    font-size: 11px;
    min-width: 26px;
    max-width: 26px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#ArmBtn:hover {
    background-color: #451a03;
    border-color: #d97706;
    color: #f59e0b;
}

QPushButton#ArmBtn[armed="true"] {
    background-color: #d97706;
    border: 1px solid #fbbf24;
    color: #ffffff;
}

QPushButton#PreviewBtn {
    background-color: #2b2b36;
    border: 1px solid #3d3d4d;
    color: #f0f0f5;
    font-size: 10px;
    min-width: 26px;
    max-width: 26px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#PreviewBtn:hover {
    background-color: #1864ab;
    border-color: #339af0;
    color: #ffffff;
}

QPushButton#InsertBtn {
    background-color: #2f9e44;
    border: 1px solid #37b24d;
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
    padding: 3px 8px;
    min-height: 24px;
    border-radius: 4px;
}

QPushButton#InsertBtn:hover {
    background-color: #37b24d;
}

QPushButton#InsertBtn:pressed {
    background-color: #2b8a3e;
}

QPushButton#WindowCloseBtn {
    background-color: transparent;
    border: none;
    color: #6c757d;
    font-size: 11px;
    min-width: 18px;
    max-width: 18px;
    padding: 0;
}

QPushButton#WindowCloseBtn:hover {
    background-color: #c92a2a;
    color: #ffffff;
    border-radius: 3px;
}

QPushButton#SnapBtn {
    background-color: transparent;
    border: 1px solid #3d3d4d;
    color: #adb5bd;
    font-size: 11px;
    min-width: 22px;
    max-width: 22px;
    min-height: 24px;
    max-height: 24px;
    border-radius: 4px;
}

QPushButton#SnapBtn:hover {
    background-color: #363645;
    color: #f0f0f5;
}

QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #262630;
    color: #f0f0f5;
    border: 1px solid #3d3d4d;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 11px;
    min-height: 22px;
}

QComboBox::drop-down {
    border: none;
    width: 14px;
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
    width: 13px;
    height: 13px;
    border-radius: 3px;
    border: 1px solid #3d3d4d;
    background: #262630;
}

QCheckBox::indicator:checked {
    background: #3b5bdb;
    border-color: #4dabf7;
}

QLabel#StatusPill {
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: bold;
    font-size: 9px;
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
