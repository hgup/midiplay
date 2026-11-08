"""
Modern Light and Dark stylesheets and visual palettes for midiplay.
Crafted to blend seamlessly into MuseScore 4's native toolbar geometry.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

_RES_PATH = (Path(__file__).parent / "resources").resolve().as_posix()

# --- Crisp Modern Studio Light Theme (Clean Off-White with Modern Borders) ---
LIGHT_THEME_QSS = f"""
QMainWindow {{
    background-color: #f5f6f8;
    color: #1c1f26;
    border: 1px solid #d2d6df;
    border-radius: 8px;
}}

QWidget#CentralWidget {{
    background-color: #f5f6f8;
    border-radius: 8px;
}}

QWidget#ToolbarStrip {{
    background-color: #f5f6f8;
    border-radius: 8px;
}}

QWidget#DrawerWidget {{
    background-color: #ebedf2;
    border-top: 1px solid #dcdfe6;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}}

QLabel {{
    color: #525866;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11px;
    font-weight: 500;
}}

QLabel#DragHandle {{
    color: #9da5b4;
    font-size: 13px;
    font-weight: bold;
    padding: 0 4px;
    min-height: 26px;
    max-height: 26px;
}}

QLabel#DragHandle:hover {{
    color: #525866;
}}

/* Generic buttons inside drawer / dialogs */
QPushButton {{
    background-color: #ffffff;
    color: #1c1f26;
    border: 1px solid #d2d6df;
    border-radius: 4px;
    padding: 1px 8px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
}}

QPushButton:hover {{
    background-color: #f4f6f9;
    border-color: #b8bec9;
    color: #0f1217;
}}

QPushButton:pressed {{
    background-color: #e2e5eb;
    border-color: #9da5b4;
}}

/* Custom painted circular buttons: transparent to let QPainter render cleanly */
QPushButton#RecordBtn, QPushButton#ArmBtn, QPushButton#PreviewBtn {{
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
}}

/* Insert Action Button (exact 26px) */
QPushButton#InsertBtn {{
    background-color: #10b981;
    border: 1px solid #059669;
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
    padding: 1px 10px;
    min-height: 22px;
    max-height: 22px;
    border-radius: 4px;
}}

QPushButton#InsertBtn:hover {{
    background-color: #059669;
    border-color: #047857;
}}

QPushButton#InsertBtn:pressed {{
    background-color: #047857;
}}

/* Drawer Toggle Button (borderless 26x26) */
QPushButton#DrawerBtn {{
    background-color: transparent;
    border: none;
    color: #6b7382;
    font-size: 9px;
    padding: 0;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    border-radius: 13px;
}}

QPushButton#DrawerBtn:hover {{
    background-color: #e2e5eb;
    color: #1c1f26;
}}

/* Window Close Button (borderless 26x26) */
QPushButton#WindowCloseBtn {{
    background-color: transparent;
    border: none;
    color: #8c94a4;
    font-size: 11px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    padding: 0;
    border-radius: 13px;
}}

QPushButton#WindowCloseBtn:hover {{
    background-color: #fee2e2;
    color: #ef4444;
}}

/* Tempo BPM Badge */
QLineEdit#BpmBox {{
    background-color: #ffffff;
    color: #1c1f26;
    border: 1px solid #d2d6df;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
    min-width: 64px;
    max-width: 64px;
    padding: 1px 2px;
}}

QLineEdit#BpmBox:hover, QLineEdit#BpmBox:focus {{
    background-color: #ffffff;
    border-color: #2563eb;
}}

/* Meter and Grid comboboxes in toolbar */
QComboBox#MeterCombo, QComboBox#GridCombo {{
    background-color: #ffffff;
    color: #1c1f26;
    border: 1px solid #d2d6df;
    border-radius: 4px;
    padding: 1px 16px 1px 4px;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
}}

QComboBox#MeterCombo:hover, QComboBox#GridCombo:hover {{
    border-color: #2563eb;
}}

QComboBox#MeterCombo::drop-down, QComboBox#GridCombo::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 14px;
    border: none;
}}

QComboBox#MeterCombo::down-arrow, QComboBox#GridCombo::down-arrow {{
    image: url({_RES_PATH}/chevron_down_light.png);
    width: 8px;
    height: 8px;
}}

/* Drawer combos and spinboxes */
QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: #ffffff;
    color: #1c1f26;
    border: 1px solid #d2d6df;
    border-radius: 4px;
    padding: 1px 20px 1px 6px;
    font-size: 11px;
    min-height: 22px;
    max-height: 22px;
}}

QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: #b8bec9;
}}

QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #2563eb;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 18px;
    border: none;
}}

QComboBox::down-arrow {{
    image: url({_RES_PATH}/chevron_down_light.png);
    width: 9px;
    height: 9px;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border: none;
    background: transparent;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url({_RES_PATH}/spin_up_light.png);
    width: 7px;
    height: 6px;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border: none;
    background: transparent;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url({_RES_PATH}/spin_down_light.png);
    width: 7px;
    height: 6px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: #e5e8ef;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #1c1f26;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    border: 1px solid #d2d6df;
    outline: none;
    padding: 2px;
}}

/* Modern Sleek Sliders */
QSlider {{
    min-height: 26px;
    max-height: 26px;
}}

QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: #dcdfe6;
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: #2563eb;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: #2563eb;
    border: 2px solid #ffffff;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}}

QSlider::handle:horizontal:hover {{
    background: #1d4ed8;
}}

QCheckBox {{
    color: #525866;
    font-size: 11px;
    spacing: 6px;
    min-height: 26px;
    max-height: 26px;
}}

QCheckBox:hover {{
    color: #1c1f26;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid #cbd2dc;
    background: #ffffff;
}}

QCheckBox::indicator:hover {{
    border-color: #2563eb;
}}

QCheckBox::indicator:checked {{
    background: #2563eb;
    border-color: #1d4ed8;
    image: url({_RES_PATH}/check_white.png);
}}

/* Status Pill: fixed width 68px, exact 26px height */
QLabel#StatusPill {{
    border-radius: 4px;
    padding: 0 4px;
    font-weight: 700;
    font-size: 9px;
    text-transform: uppercase;
    min-height: 24px;
    max-height: 24px;
    letter-spacing: 0.5px;
}}

QLabel#StatusPill[state="IDLE"] {{
    background-color: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
}}

QLabel#StatusPill[state="COUNT_IN"] {{
    background-color: #fef3c7;
    color: #b45309;
    border: 1px solid #fde68a;
}}

QLabel#StatusPill[state="RECORDING"] {{
    background-color: #fee2e2;
    color: #dc2626;
    border: 1px solid #fca5a5;
}}

QLabel#StatusPill[state="QUANTIZING"] {{
    background-color: #e0f2fe;
    color: #0284c7;
    border: 1px solid #bae6fd;
}}

QLabel#StatusPill[state="COPIED"] {{
    background-color: #dcfce7;
    color: #16a34a;
    border: 1px solid #bbf7d0;
}}

QLabel#StatusPill[state="INSERTED"] {{
    background-color: #dcfce7;
    color: #16a34a;
    border: 1px solid #bbf7d0;
}}

QLabel#StatusPill[state="SYNCED"] {{
    background-color: #ede9fe;
    color: #7c3aed;
    border: 1px solid #ddd6fe;
}}

QDialog {{
    background-color: #f5f6f8;
    color: #1c1f26;
}}

QLabel#CalibrationStatus {{
    color: #0284c7;
    font-weight: bold;
    font-size: 11px;
}}

QProgressBar {{
    background-color: #e2e5eb;
    border: 1px solid #d2d6df;
    border-radius: 4px;
    height: 12px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: #2563eb;
    border-radius: 3px;
}}
"""

# --- Pro Studio Obsidian Dark Theme (Exact Layout Match with Dark Palette) ---
DARK_THEME_QSS = f"""
QMainWindow {{
    background-color: #2d2d30;
    color: #e2e4e6;
    border: 1px solid #3e3e44;
    border-radius: 8px;
}}

QWidget#CentralWidget {{
    background-color: #2d2d30;
    border-radius: 8px;
}}

QWidget#ToolbarStrip {{
    background-color: #2d2d30;
    border-radius: 8px;
}}

QWidget#DrawerWidget {{
    background-color: #252528;
    border-top: 1px solid #38383e;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}}

QLabel {{
    color: #909296;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11px;
    font-weight: 500;
}}

QLabel#DragHandle {{
    color: #6a6a72;
    font-size: 13px;
    font-weight: bold;
    padding: 0 4px;
    min-height: 26px;
    max-height: 26px;
}}

QLabel#DragHandle:hover {{
    color: #dce2de;
}}

/* Generic buttons inside drawer / dialogs */
QPushButton {{
    background-color: #333338;
    color: #e2e4e6;
    border: 1px solid #44444c;
    border-radius: 4px;
    padding: 1px 8px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
}}

QPushButton:hover {{
    background-color: #3e3e46;
    border-color: #555560;
    color: #ffffff;
}}

QPushButton:pressed {{
    background-color: #28282c;
    border-color: #3e3e44;
}}

/* Custom painted circular buttons: transparent to let QPainter render cleanly */
QPushButton#RecordBtn, QPushButton#ArmBtn, QPushButton#PreviewBtn {{
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
}}

/* Insert Action Button: MuseScore 4 signature accent blue */
QPushButton#InsertBtn {{
    background-color: #2474c0;
    border: 1px solid #1f6cb6;
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
    padding: 1px 10px;
    min-height: 22px;
    max-height: 22px;
    border-radius: 4px;
}}

QPushButton#InsertBtn:hover {{
    background-color: #2c83d6;
    border-color: #2474c0;
}}

QPushButton#InsertBtn:pressed {{
    background-color: #1c5f9e;
}}

/* Drawer Toggle Button (borderless 26x26) */
QPushButton#DrawerBtn {{
    background-color: transparent;
    border: none;
    color: #909296;
    font-size: 9px;
    padding: 0;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    border-radius: 13px;
}}

QPushButton#DrawerBtn:hover {{
    background-color: #38383e;
    color: #ffffff;
}}

/* Window Close Button (borderless 26x26) */
QPushButton#WindowCloseBtn {{
    background-color: transparent;
    border: none;
    color: #787880;
    font-size: 11px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    padding: 0;
    border-radius: 13px;
}}

QPushButton#WindowCloseBtn:hover {{
    background-color: #4a1d1d;
    color: #fca5a5;
}}

/* Tempo BPM Badge */
QLineEdit#BpmBox {{
    background-color: #222225;
    color: #e2e4e6;
    border: 1px solid #3e3e44;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
    min-width: 64px;
    max-width: 64px;
    padding: 1px 2px;
}}

QLineEdit#BpmBox:hover, QLineEdit#BpmBox:focus {{
    background-color: #222225;
    border-color: #2474c0;
}}

/* Meter and Grid comboboxes in toolbar */
QComboBox#MeterCombo, QComboBox#GridCombo {{
    background-color: #222225;
    color: #e2e4e6;
    border: 1px solid #3e3e44;
    border-radius: 4px;
    padding: 1px 16px 1px 4px;
    font-size: 11px;
    font-weight: 600;
    min-height: 22px;
    max-height: 22px;
}}

QComboBox#MeterCombo:hover, QComboBox#GridCombo:hover {{
    border-color: #2474c0;
}}

QComboBox#MeterCombo::drop-down, QComboBox#GridCombo::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 14px;
    border: none;
}}

QComboBox#MeterCombo::down-arrow, QComboBox#GridCombo::down-arrow {{
    image: url({_RES_PATH}/chevron_down_dark.png);
    width: 8px;
    height: 8px;
}}

/* Drawer combos and spinboxes */
QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: #222225;
    color: #e2e4e6;
    border: 1px solid #3e3e44;
    border-radius: 4px;
    padding: 1px 20px 1px 6px;
    font-size: 11px;
    min-height: 22px;
    max-height: 22px;
}}

QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: #555560;
}}

QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #2474c0;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 18px;
    border: none;
}}

QComboBox::down-arrow {{
    image: url({_RES_PATH}/chevron_down_dark.png);
    width: 9px;
    height: 9px;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border: none;
    background: transparent;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url({_RES_PATH}/spin_up_dark.png);
    width: 7px;
    height: 6px;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border: none;
    background: transparent;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url({_RES_PATH}/spin_down_dark.png);
    width: 7px;
    height: 6px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: #38383e;
}}

QComboBox QAbstractItemView {{
    background-color: #222225;
    color: #e2e4e6;
    selection-background-color: #2474c0;
    selection-color: #ffffff;
    border: 1px solid #3e3e44;
    outline: none;
    padding: 2px;
}}

/* Modern Sleek Sliders */
QSlider {{
    min-height: 26px;
    max-height: 26px;
}}

QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: #38383e;
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: #2474c0;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: #2474c0;
    border: 2px solid #252528;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}}

QSlider::handle:horizontal:hover {{
    background: #3a8be0;
}}

QCheckBox {{
    color: #909296;
    font-size: 11px;
    spacing: 6px;
    min-height: 26px;
    max-height: 26px;
}}

QCheckBox:hover {{
    color: #e2e4e6;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid #44444c;
    background: #222225;
}}

QCheckBox::indicator:hover {{
    border-color: #2474c0;
}}

QCheckBox::indicator:checked {{
    background: #2474c0;
    border-color: #1f6cb6;
    image: url({_RES_PATH}/check_white.png);
}}

/* Status Pill: fixed width 68px, exact 26px height */
QLabel#StatusPill {{
    border-radius: 4px;
    padding: 0 4px;
    font-weight: 700;
    font-size: 9px;
    text-transform: uppercase;
    min-height: 24px;
    max-height: 24px;
    letter-spacing: 0.5px;
}}

QLabel#StatusPill[state="IDLE"] {{
    background-color: #252528;
    color: #909296;
    border: 1px solid #3e3e44;
}}

QLabel#StatusPill[state="COUNT_IN"] {{
    background-color: #3b2805;
    color: #fbbf24;
    border: 1px solid #78350f;
}}

QLabel#StatusPill[state="RECORDING"] {{
    background-color: #3d1419;
    color: #f87171;
    border: 1px solid #7f1d1d;
}}

QLabel#StatusPill[state="QUANTIZING"] {{
    background-color: #132a42;
    color: #38bdf8;
    border: 1px solid #1f6cb6;
}}

QLabel#StatusPill[state="COPIED"] {{
    background-color: #0d3322;
    color: #4ade80;
    border: 1px solid #166534;
}}

QLabel#StatusPill[state="INSERTED"] {{
    background-color: #0d3322;
    color: #4ade80;
    border: 1px solid #166534;
}}

QLabel#StatusPill[state="SYNCED"] {{
    background-color: #1b2f4a;
    color: #60a5fa;
    border: 1px solid #2474c0;
}}

QDialog {{
    background-color: #2d2d30;
    color: #e2e4e6;
}}

QLabel#CalibrationStatus {{
    color: #38bdf8;
    font-weight: bold;
    font-size: 11px;
}}

QProgressBar {{
    background-color: #222225;
    border: 1px solid #3e3e44;
    border-radius: 4px;
    height: 12px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: #2474c0;
    border-radius: 3px;
}}"""

# Color palettes for custom-rendered widgets (such as PianoRoll)
PIANO_ROLL_PALETTES: Dict[str, Dict[str, str]] = {
    "light": {
        "background": "#ffffff",
        "border": "#d2d6df",
        "placeholder": "#8c94a4",
        "barline": "#d2d6df",
        "beatline": "#e8ebf0",
        "measure_label": "#6b7382",
        "note_fill": "#2563eb",
        "note_border": "#1d4ed8",
        "note_text": "#ffffff",
        "triplet_note_fill": "#7c3aed",
        "triplet_note_border": "#6d28d9",
        "playhead": "#ef4444",
    },
    "dark": {
        "background": "#1c1c1f",
        "border": "#3e3e44",
        "placeholder": "#787880",
        "barline": "#38383e",
        "beatline": "#252528",
        "measure_label": "#909296",
        "note_fill": "#2474c0",
        "note_border": "#1b5d9b",
        "note_text": "#ffffff",
        "triplet_note_fill": "#9333ea",
        "triplet_note_border": "#7e22ce",
        "playhead": "#ef4444",
    }
}
