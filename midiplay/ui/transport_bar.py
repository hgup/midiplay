"""
Ultra-Compact Toolbar Strip Widget for midiplay.
Designed to sit flush inside MuseScore 4's top toolbar area.
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSpinBox,
    QComboBox, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from midiplay.core.quantizer import QuantizeGrid


class DragHandle(QLabel):
    """MuseScore-style '⋮⋮' grab handle that drags the host window."""

    def __init__(self, parent=None):
        super().__init__("⋮⋮", parent)
        self.setObjectName("DragHandle")
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setToolTip("Click and drag to position or snap to MuseScore")
        self._drag_start_pos: QPoint | None = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            self._drag_start_pos = event.globalPosition().toPoint() - win.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            win = self.window()
            win.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_start_pos = None
        event.accept()


class TransportBar(QWidget):
    """Ultra-compact 34px horizontal toolbar strip."""

    record_toggled = pyqtSignal(bool)
    arm_toggled = pyqtSignal(bool)
    preview_clicked = pyqtSignal()
    bpm_changed = pyqtSignal(float)
    time_sig_changed = pyqtSignal(int, int)
    grid_changed = pyqtSignal(QuantizeGrid)
    insert_clicked = pyqtSignal()
    drawer_toggled = pyqtSignal(bool)
    snap_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ToolbarStrip")
        self.drawer_expanded = False
        self.setFixedHeight(34)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # 1. MuseScore-style Drag Handle
        self.drag_handle = DragHandle(self)
        layout.addWidget(self.drag_handle)

        # 2. Record: red circular icon button
        self.record_btn = QPushButton("●")
        self.record_btn.setObjectName("RecordBtn")
        self.record_btn.setCheckable(True)
        self.record_btn.setToolTip("Record / Stop (Space or MIDI trigger)")
        self.record_btn.toggled.connect(self.record_toggled.emit)
        layout.addWidget(self.record_btn)

        # 3. ARM: single letter "R" button
        self.arm_btn = QPushButton("R")
        self.arm_btn.setObjectName("ArmBtn")
        self.arm_btn.setCheckable(True)
        self.arm_btn.setToolTip("Arm Spacebar Trigger (Ctrl+Alt+R)\nWhen active, Space starts/stops recording.")
        self.arm_btn.toggled.connect(self._on_arm_toggled)
        layout.addWidget(self.arm_btn)

        # 4. Preview: simple play icon
        self.preview_btn = QPushButton("▶")
        self.preview_btn.setObjectName("PreviewBtn")
        self.preview_btn.setToolTip("Preview Recorded Phrase")
        self.preview_btn.clicked.connect(self.preview_clicked.emit)
        layout.addWidget(self.preview_btn)

        # 5. BPM SpinBox (Compact badge, auto-reads from MuseScore)
        self.bpm_box = QSpinBox()
        self.bpm_box.setRange(20, 320)
        self.bpm_box.setValue(120)
        self.bpm_box.setFixedWidth(52)
        self.bpm_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bpm_box.setToolTip("Tempo (BPM) — Auto-detected from MuseScore; click or scroll to adjust")
        self.bpm_box.valueChanged.connect(lambda v: self.bpm_changed.emit(float(v)))
        layout.addWidget(self.bpm_box)

        # 6. Meter Combo
        self.meter_combo = QComboBox()
        self.meter_combo.addItems(["4/4", "3/4", "2/4", "6/8", "5/4", "7/8"])
        self.meter_combo.setFixedWidth(50)
        self.meter_combo.setToolTip("Time Signature")
        self.meter_combo.currentTextChanged.connect(self._on_meter_change)
        layout.addWidget(self.meter_combo)

        # 7. Grid Combo
        self.grid_combo = QComboBox()
        for g in QuantizeGrid:
            self.grid_combo.addItem(g.value, g)
        self.grid_combo.setCurrentText("1/16")
        self.grid_combo.setFixedWidth(54)
        self.grid_combo.setToolTip("Quantize Grid")
        self.grid_combo.currentIndexChanged.connect(self._on_grid_change)
        layout.addWidget(self.grid_combo)

        # 8. Insert Action Button (replaces Copy to MuseScore)
        self.insert_btn = QPushButton("Insert")
        self.insert_btn.setObjectName("InsertBtn")
        self.insert_btn.setToolTip("Insert notes into currently selected MuseScore measure")
        self.insert_btn.clicked.connect(self.insert_clicked.emit)
        layout.addWidget(self.insert_btn)

        # 9. Status Micro-Pill
        self.status_pill = QLabel("IDLE")
        self.status_pill.setObjectName("StatusPill")
        self.status_pill.setProperty("state", "IDLE")
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_pill)

        # 10. Snap / Dock to MuseScore button
        self.snap_btn = QPushButton("🧲")
        self.snap_btn.setObjectName("SnapBtn")
        self.snap_btn.setToolTip("Snap / Dock into MuseScore 4 Toolbar Notch")
        self.snap_btn.clicked.connect(self.snap_clicked.emit)
        layout.addWidget(self.snap_btn)

        # 11. Expand Drawer Button
        self.drawer_btn = QPushButton("▼")
        self.drawer_btn.setFixedWidth(22)
        self.drawer_btn.setToolTip("Settings, Theme Switcher & Piano Roll")
        self.drawer_btn.clicked.connect(self._toggle_drawer)
        layout.addWidget(self.drawer_btn)

        # 12. Minimalist Close Button
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("WindowCloseBtn")
        self.close_btn.setToolTip("Close midiplay")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)

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

    def set_bpm_display(self, bpm: int) -> None:
        self.bpm_box.blockSignals(True)
        self.bpm_box.setValue(bpm)
        self.bpm_box.blockSignals(False)

    def set_status(self, text: str, state_prop: str) -> None:
        self.status_pill.setText(text)
        self.status_pill.setProperty("state", state_prop)
        self.status_pill.style().unpolish(self.status_pill)
        self.status_pill.style().polish(self.status_pill)

    def set_recording_active(self, active: bool) -> None:
        self.record_btn.blockSignals(True)
        self.record_btn.setChecked(active)
        self.record_btn.setProperty("recording", "true" if active else "false")
        self.record_btn.setText("■" if active else "●")
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.record_btn.blockSignals(False)
