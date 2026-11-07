"""
Modern dark-theme stylesheet and visual constants for midiplay.
"""

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
"""
