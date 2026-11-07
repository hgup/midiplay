"""
Modern Light and Dark stylesheets and visual palettes for midiplay.
Crafted to blend seamlessly into MuseScore 4's native toolbar geometry.
"""

from typing import Dict, Any

# --- Crisp Modern Studio Light Theme (Clean Off-White with Modern Borders) ---
LIGHT_THEME_QSS = """
QMainWindow {
    background-color: #fcfcfd;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}

QWidget#CentralWidget {
    background-color: #fcfcfd;
    border-radius: 8px;
}

QWidget#ToolbarStrip {
    background-color: #fcfcfd;
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

QLabel#DragHandle {
    color: #94a3b8;
    font-size: 13px;
    font-weight: bold;
    padding: 0 4px;
}

QLabel#DragHandle:hover {
    color: #475569;
}

/* Generic buttons inside drawer / dialogs (Sleek dark-mode inspired contour) */
QPushButton {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 3px 8px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

/* Custom painted circular buttons: transparent to let QPainter render cleanly */
QPushButton#RecordBtn, QPushButton#ArmBtn, QPushButton#PreviewBtn {
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
}

/* Insert Action Button (compact 20px) */
QPushButton#InsertBtn {
    background-color: #10b981;
    border: 1px solid #059669;
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
    padding: 0 8px;
    min-height: 20px;
    max-height: 20px;
    border-radius: 4px;
}

QPushButton#InsertBtn:hover {
    background-color: #059669;
    border-color: #047857;
}

QPushButton#InsertBtn:pressed {
    background-color: #047857;
}

/* Drawer Toggle Button (borderless 20x20) */
QPushButton#DrawerBtn {
    background-color: transparent;
    border: none;
    color: #64748b;
    font-size: 9px;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    border-radius: 10px;
}

QPushButton#DrawerBtn:hover {
    background-color: #f1f5f9;
    color: #1e293b;
}

/* Window Close Button (borderless 20x20) */
QPushButton#WindowCloseBtn {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    font-size: 11px;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    padding: 0;
    border-radius: 10px;
}

QPushButton#WindowCloseBtn:hover {
    background-color: #fee2e2;
    color: #ef4444;
}

/* Tempo BPM Badge: borderless interactive badge */
QLineEdit#BpmBox {
    background-color: transparent;
    color: #0f172a;
    border: none;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
    min-width: 64px;
    max-width: 64px;
    padding: 0;
}

QLineEdit#BpmBox:hover, QLineEdit#BpmBox:focus {
    background-color: #f1f5f9;
    border-radius: 4px;
}

/* Combos without borders */
QComboBox#MeterCombo, QComboBox#GridCombo {
    background-color: transparent;
    color: #0f172a;
    border: none;
    padding: 1px 0px 1px 4px;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
}

QComboBox#MeterCombo:hover, QComboBox#GridCombo:hover {
    background-color: #f1f5f9;
    border-radius: 4px;
}

QComboBox#MeterCombo::drop-down, QComboBox#GridCombo::drop-down {
    border: none;
    width: 12px;
}

/* Drawer combos and spinboxes */
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 11px;
    min-height: 22px;
    max-height: 22px;
}

QSpinBox::up-button, QSpinBox::down-button {
    border: none;
    background: transparent;
    width: 14px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #e2e8f0;
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

/* Modern Sleek Sliders */
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

/* Status Pill: fixed width 64px, 20px height, muted idle */
QLabel#StatusPill {
    border-radius: 4px;
    padding: 0 4px;
    font-weight: bold;
    font-size: 9px;
    text-transform: uppercase;
    min-height: 20px;
    max-height: 20px;
}

QLabel#StatusPill[state="IDLE"] {
    background-color: transparent;
    color: #94a3b8;
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

QLabel#StatusPill[state="INSERTED"] {
    background-color: #dcfce7;
    color: #15803d;
}

QLabel#StatusPill[state="SYNCED"] {
    background-color: #e0f2fe;
    color: #0369a1;
}

QDialog {
    background-color: #f8fafc;
    color: #0f172a;
}
"""

# --- Pro Studio Obsidian Dark Theme (Exact Layout Match with Dark Palette) ---
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

QWidget#ToolbarStrip {
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

QLabel#DragHandle {
    color: #64748b;
    font-size: 13px;
    font-weight: bold;
    padding: 0 4px;
}

QLabel#DragHandle:hover {
    color: #a0a0b8;
}

/* Generic buttons inside drawer / dialogs (Sleek dark-mode inspired contour) */
QPushButton {
    background-color: #2b2b36;
    color: #f0f0f5;
    border: 1px solid #3d3d4d;
    border-radius: 4px;
    padding: 3px 8px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #363645;
    border-color: #525266;
}

QPushButton:pressed {
    background-color: #24242e;
}

/* Custom painted circular buttons: transparent to let QPainter render cleanly */
QPushButton#RecordBtn, QPushButton#ArmBtn, QPushButton#PreviewBtn {
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
}

/* Insert Action Button (compact 20px) */
QPushButton#InsertBtn {
    background-color: #10b981;
    border: 1px solid #059669;
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
    padding: 0 8px;
    min-height: 20px;
    max-height: 20px;
    border-radius: 4px;
}

QPushButton#InsertBtn:hover {
    background-color: #059669;
    border-color: #047857;
}

QPushButton#InsertBtn:pressed {
    background-color: #047857;
}

/* Drawer Toggle Button (borderless 20x20) */
QPushButton#DrawerBtn {
    background-color: transparent;
    border: none;
    color: #a0a0b8;
    font-size: 9px;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    border-radius: 10px;
}

QPushButton#DrawerBtn:hover {
    background-color: #27272a;
    color: #ffffff;
}

/* Window Close Button (borderless 20x20) */
QPushButton#WindowCloseBtn {
    background-color: transparent;
    border: none;
    color: #71717a;
    font-size: 11px;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    padding: 0;
    border-radius: 10px;
}

QPushButton#WindowCloseBtn:hover {
    background-color: #450a0a;
    color: #fca5a5;
}

/* Tempo BPM Badge: borderless interactive badge — Dark */
QLineEdit#BpmBox {
    background-color: transparent;
    color: #f4f4f5;
    border: none;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
    min-width: 64px;
    max-width: 64px;
    padding: 0;
}

QLineEdit#BpmBox:hover, QLineEdit#BpmBox:focus {
    background-color: #27272a;
    border-radius: 4px;
}

/* Combos without borders — Dark */
QComboBox#MeterCombo, QComboBox#GridCombo {
    background-color: transparent;
    color: #f4f4f5;
    border: none;
    padding: 1px 0px 1px 4px;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
}

QComboBox#MeterCombo:hover, QComboBox#GridCombo:hover {
    background-color: #27272a;
    border-radius: 4px;
}

QComboBox#MeterCombo::drop-down, QComboBox#GridCombo::drop-down {
    border: none;
    width: 12px;
}

/* Drawer combos and spinboxes — Dark */
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #27272a;
    color: #f4f4f5;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 11px;
    min-height: 22px;
    max-height: 22px;
}

QSpinBox::up-button, QSpinBox::down-button {
    border: none;
    background: transparent;
    width: 14px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #3f3f46;
}

QComboBox::drop-down {
    border: none;
    width: 14px;
}

QComboBox QAbstractItemView {
    background-color: #27272a;
    color: #f4f4f5;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    border: 1px solid #3f3f46;
}

/* Modern Sleek Sliders — Dark */
QSlider::groove:horizontal {
    border: 1px solid #33333e;
    height: 4px;
    background: #2a2a36;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #3b82f6;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #60a5fa;
    border: 1px solid #2563eb;
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
    background: #3b82f6;
    border-color: #60a5fa;
}

/* Status Pill: fixed width 64px, 20px height, muted idle — Dark */
QLabel#StatusPill {
    border-radius: 4px;
    padding: 0 4px;
    font-weight: bold;
    font-size: 9px;
    text-transform: uppercase;
    min-height: 20px;
    max-height: 20px;
}

QLabel#StatusPill[state="IDLE"] {
    background-color: transparent;
    color: #64748b;
}

QLabel#StatusPill[state="COUNT_IN"] {
    background-color: #451a03;
    color: #ffd43b;
}

QLabel#StatusPill[state="RECORDING"] {
    background-color: #450a0a;
    color: #ff6b6b;
}

QLabel#StatusPill[state="QUANTIZING"] {
    background-color: #1e3a8a;
    color: #93c5fd;
}

QLabel#StatusPill[state="COPIED"] {
    background-color: #064e3b;
    color: #6ee7b7;
}

QLabel#StatusPill[state="INSERTED"] {
    background-color: #064e3b;
    color: #6ee7b7;
}

QLabel#StatusPill[state="SYNCED"] {
    background-color: #082f49;
    color: #38bdf8;
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
