"""
Compact Transport Control Bar Widget.
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSpinBox,
    QComboBox, QLabel, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from midiplay.core.clock import TransportState
from midiplay.core.quantizer import QuantizeGrid


class TransportBar(QWidget):
    """Compact single-line horizontal transport surface."""

    record_toggled = pyqtSignal(bool)
    arm_toggled = pyqtSignal(bool)
    preview_clicked = pyqtSignal()
    bpm_changed = pyqtSignal(float)
    tap_tempo_clicked = pyqtSignal()
    time_sig_changed = pyqtSignal(int, int)
    grid_changed = pyqtSignal(QuantizeGrid)
    copy_clicked = pyqtSignal()
    drawer_toggled = pyqtSignal(bool)
    theme_toggled = pyqtSignal()
    clear_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawer_expanded = False
        self.setFixedHeight(46)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        # Record / Stop
        self.record_btn = QPushButton("● REC")
        self.record_btn.setObjectName("RecordBtn")
        self.record_btn.setCheckable(True)
        self.record_btn.setToolTip("Start/Stop Recording (Space or MIDI trigger)")
        self.record_btn.toggled.connect(self.record_toggled.emit)
        layout.addWidget(self.record_btn)

        # ARM button for global spacebar trigger
        self.arm_btn = QPushButton("ARM")
        self.arm_btn.setObjectName("ArmBtn")
        self.arm_btn.setCheckable(True)
        self.arm_btn.setToolTip("Arm Global Spacebar (Ctrl+Alt+R): When enabled, Space in MuseScore starts/stops recording.\nWhen disabled, Space does not accidentally record while typing.")
        self.arm_btn.toggled.connect(self._on_arm_toggled)
        layout.addWidget(self.arm_btn)

        # Preview button
        self.preview_btn = QPushButton("▶ Preview")
        self.preview_btn.setToolTip("Play back recorded phrase through built-in synthesizer")
        self.preview_btn.clicked.connect(self.preview_clicked.emit)
        layout.addWidget(self.preview_btn)

        # BPM SpinBox (widened for clear 3-digit visibility)
        layout.addWidget(QLabel("BPM:"))
        self.bpm_box = QSpinBox()
        self.bpm_box.setRange(20, 320)
        self.bpm_box.setValue(120)
        self.bpm_box.setFixedWidth(78)
        self.bpm_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bpm_box.valueChanged.connect(lambda v: self.bpm_changed.emit(float(v)))
        layout.addWidget(self.bpm_box)

        # Tap button
        self.tap_btn = QPushButton("Tap")
        self.tap_btn.setFixedWidth(36)
        self.tap_btn.setToolTip("Click repeatedly to set BPM")
        self.tap_btn.clicked.connect(self.tap_tempo_clicked.emit)
        layout.addWidget(self.tap_btn)

        # Time Signature Combo
        layout.addWidget(QLabel("Meter:"))
        self.meter_combo = QComboBox()
        self.meter_combo.addItems(["4/4", "3/4", "2/4", "6/8", "5/4", "7/8"])
        self.meter_combo.currentTextChanged.connect(self._on_meter_change)
        layout.addWidget(self.meter_combo)

        # Quantize Grid Combo
        layout.addWidget(QLabel("Grid:"))
        self.grid_combo = QComboBox()
        for g in QuantizeGrid:
            self.grid_combo.addItem(g.value, g)
        self.grid_combo.setCurrentText("1/16")
        self.grid_combo.currentIndexChanged.connect(self._on_grid_change)
        layout.addWidget(self.grid_combo)

        # Status Pill
        self.status_pill = QLabel("IDLE")
        self.status_pill.setObjectName("StatusPill")
        self.status_pill.setProperty("state", "IDLE")
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_pill.setFixedHeight(24)
        layout.addWidget(self.status_pill)

        # Auto Copy Checkbox
        self.auto_copy_cb = QCheckBox("Auto")
        self.auto_copy_cb.setChecked(True)
        self.auto_copy_cb.setToolTip("Automatically copy to MuseScore clipboard when recording stops")
        layout.addWidget(self.auto_copy_cb)

        # Copy to MuseScore Action Button
        self.copy_btn = QPushButton("Copy to MuseScore")
        self.copy_btn.setObjectName("CopyBtn")
        self.copy_btn.setToolTip("Quantize and Copy XML directly to system clipboard (Ctrl+Shift+C)")
        self.copy_btn.clicked.connect(self.copy_clicked.emit)
        layout.addWidget(self.copy_btn)

        # Theme Switcher Quick Toggle (☀️ / 🌙)
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("ThemeBtn")
        self.theme_btn.setFixedWidth(28)
        self.theme_btn.setToolTip("Switch Theme (Light / Dark)")
        self.theme_btn.clicked.connect(self.theme_toggled.emit)
        layout.addWidget(self.theme_btn)

        # Expand Drawer Button
        self.drawer_btn = QPushButton("▼")
        self.drawer_btn.setFixedWidth(28)
        self.drawer_btn.setToolTip("Toggle Scratchpad & Advanced Settings Drawer")
        self.drawer_btn.clicked.connect(self._toggle_drawer)
        layout.addWidget(self.drawer_btn)

    def _on_meter_change(self, text: str) -> None:
        parts = text.split("/")
        if len(parts) == 2:
            num = int(parts[0])
            den = int(parts[1])
            self.time_sig_changed.emit(num, den)

    def _on_grid_change(self) -> None:
        grid = self.grid_combo.currentData()
        if isinstance(grid, QuantizeGrid):
            self.grid_changed.emit(grid)

    def _toggle_drawer(self) -> None:
        self.drawer_expanded = not self.drawer_expanded
        self.drawer_btn.setText("▲" if self.drawer_expanded else "▼")
        self.drawer_toggled.emit(self.drawer_expanded)

    def _on_arm_toggled(self, armed: bool) -> None:
        self.arm_btn.setProperty("armed", "true" if armed else "false")
        self.arm_btn.style().unpolish(self.arm_btn)
        self.arm_btn.style().polish(self.arm_btn)
        self.arm_toggled.emit(armed)

    def set_theme_icon(self, theme_mode: str) -> None:
        self.theme_btn.setText("🌙" if theme_mode == "light" else "☀️")
        self.theme_btn.setToolTip(f"Switch to {'Dark' if theme_mode == 'light' else 'Light'} Theme")

    def set_status(self, text: str, state_prop: str) -> None:
        self.status_pill.setText(text)
        self.status_pill.setProperty("state", state_prop)
        self.status_pill.style().unpolish(self.status_pill)
        self.status_pill.style().polish(self.status_pill)

    def set_recording_active(self, active: bool) -> None:
        self.record_btn.blockSignals(True)
        self.record_btn.setChecked(active)
        self.record_btn.setProperty("recording", "true" if active else "false")
        self.record_btn.setText("■ STOP" if active else "● REC")
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.record_btn.blockSignals(False)
