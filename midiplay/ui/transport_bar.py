"""
Ultra-Compact Toolbar Strip Widget for midiplay.
Designed to sit flush and unobtrusive alongside MuseScore 4's top toolbar area.
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QLineEdit
)
from PyQt6.QtCore import pyqtSignal, Qt, QPoint, QPointF, QRectF
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from midiplay.core.quantizer import QuantizeGrid
from midiplay.utils.config import ConfigManager


class CircleButton(QPushButton):
    """Guaranteed pixel-perfect circular button with antialiased rendering."""

    def __init__(self, size: int = 26, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hovered = False
        self._theme = "light"

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        self.update()

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self.update()

    def checkStateSet(self) -> None:
        super().checkStateSet()
        self.update()

    def nextCheckState(self) -> None:
        super().nextCheckState()
        self.update()


class RecordButton(CircleButton):
    def __init__(self, size: int = 26, parent=None):
        super().__init__(size, parent)
        self.setCheckable(True)
        self.setObjectName("RecordBtn")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w, h = float(self.width()), float(self.height())
        rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        cx, cy = w / 2.0, h / 2.0
        is_rec = self.isChecked()
        is_dark = self._theme == "dark"

        if is_rec:
            # Active recording: solid red circle with white stop square
            bg_color = QColor("#ef4444")
            border_color = QColor("#b91c1c")
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 1.2))
            painter.drawEllipse(rect)

            # Centered white stop square (8x8)
            sq_size = 8.0
            sq_rect = QRectF(cx - sq_size / 2.0, cy - sq_size / 2.0, sq_size, sq_size)
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(sq_rect, 1.5, 1.5)
        else:
            # Idle / Hover: off-white/dark circle with red center dot
            if self._hovered:
                bg_color = QColor("#3b1219" if is_dark else "#fee2e2")
                border_color = QColor("#7f1d1d" if is_dark else "#fca5a5")
                dot_color = QColor("#f87171" if is_dark else "#dc2626")
            else:
                bg_color = QColor("#22252e" if is_dark else "#ffffff")
                border_color = QColor("#363b48" if is_dark else "#d2d6df")
                dot_color = QColor("#ef4444")

            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 1.0))
            painter.drawEllipse(rect)

            # Centered red recording dot (radius 4.5px, diameter 9px)
            dot_r = 4.5
            painter.setBrush(QBrush(dot_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), dot_r, dot_r)


class ArmButton(CircleButton):
    def __init__(self, size: int = 26, parent=None):
        super().__init__(size, parent)
        self.setCheckable(True)
        self.setObjectName("ArmBtn")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        w, h = float(self.width()), float(self.height())
        rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        is_armed = self.isChecked()
        is_dark = self._theme == "dark"

        if is_armed:
            bg_color = QColor("#d97706" if is_dark else "#f59e0b")
            border_color = QColor("#f59e0b" if is_dark else "#d97706")
            text_color = QColor("#ffffff")
        elif self._hovered:
            bg_color = QColor("#382405" if is_dark else "#fef3c7")
            border_color = QColor("#78350f" if is_dark else "#fde68a")
            text_color = QColor("#fbbf24" if is_dark else "#d97706")
        else:
            bg_color = QColor("#22252e" if is_dark else "#ffffff")
            border_color = QColor("#363b48" if is_dark else "#d2d6df")
            text_color = QColor("#9ca3b3" if is_dark else "#525866")

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.0 if not is_armed else 1.2))
        painter.drawEllipse(rect)

        # Centered "R" text
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(text_color))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "R")


class PreviewButton(CircleButton):
    def __init__(self, size: int = 26, parent=None):
        super().__init__(size, parent)
        self.setObjectName("PreviewBtn")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w, h = float(self.width()), float(self.height())
        rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        cx, cy = w / 2.0, h / 2.0
        is_dark = self._theme == "dark"

        if self._hovered:
            bg_color = QColor("#333846" if is_dark else "#f4f6f9")
            border_color = QColor("#545b6e" if is_dark else "#b8bec9")
            icon_color = QColor("#ffffff" if is_dark else "#1c1f26")
        else:
            bg_color = QColor("#22252e" if is_dark else "#ffffff")
            border_color = QColor("#363b48" if is_dark else "#d2d6df")
            icon_color = QColor("#9ca3b3" if is_dark else "#525866")

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.0))
        painter.drawEllipse(rect)

        # Centered play triangle pointing right (centroid compensated)
        painter.setBrush(QBrush(icon_color))
        painter.setPen(Qt.PenStyle.NoPen)
        poly = QPolygonF([
            QPointF(cx - 3.0, cy - 4.5),
            QPointF(cx - 3.0, cy + 4.5),
            QPointF(cx + 4.5, cy),
        ])
        painter.drawPolygon(poly)


class BpmBadge(QLineEdit):
    """Clean interactive tempo badge with mouse wheel adjustments and direct editing."""

    valueChanged = pyqtSignal(int)

    def __init__(self, val: int = 120, parent=None):
        super().__init__(f"{val} BPM", parent)
        self.setObjectName("BpmBox")
        self._val = val
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(64)
        self.setFixedHeight(24)
        self.setToolTip("Tempo (BPM) — Auto-detected from MuseScore; scroll wheel or type to edit")
        self.returnPressed.connect(self._on_edit)

    def wheelEvent(self, event) -> None:
        delta = 1 if event.angleDelta().y() > 0 else -1
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            delta *= 5
        self.setValue(self._val + delta)

    def mouseDoubleClickEvent(self, event) -> None:
        self.selectAll()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event) -> None:
        self._on_edit()
        super().focusOutEvent(event)

    def setValue(self, val: int | float) -> None:
        self._val = max(20, min(320, int(val)))
        self.setText(f"{self._val} BPM")
        self.valueChanged.emit(self._val)

    def value(self) -> int:
        return self._val

    def _on_edit(self) -> None:
        digits = "".join(c for c in self.text() if c.isdigit())
        if digits:
            self.setValue(int(digits))
        else:
            self.setValue(self._val)
        self.clearFocus()


class DragHandle(QLabel):
    """MuseScore-style '⋮⋮' grab handle that drags the host window."""

    def __init__(self, parent=None):
        super().__init__("⋮⋮", parent)
        self.setObjectName("DragHandle")
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setToolTip("Click and drag anywhere on toolbar to move")
        self._drag_start_pos: QPoint | None = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            wh = win.windowHandle()
            if wh is not None and wh.startSystemMove():
                event.accept()
                return
            self._drag_start_pos = event.globalPosition().toPoint() - win.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            win = self.window()
            win.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._drag_start_pos is not None:
            win = self.window()
            ConfigManager.set_window_pos(win.x(), win.y())
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
    status_clicked = pyqtSignal()
    drawer_toggled = pyqtSignal(bool)
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ToolbarStrip")
        self.drawer_expanded = False
        self.setFixedHeight(36)
        self._drag_start_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(5)

        # 1. Drag Handle
        self.drag_handle = DragHandle(self)
        layout.addWidget(self.drag_handle)

        # 2. Record: circular icon button
        self.record_btn = RecordButton(26, self)
        self.record_btn.setToolTip("Record / Stop (Shift+Space or Click)\nAuto-inserts into MuseScore on stop.")
        self.record_btn.toggled.connect(self.record_toggled.emit)
        layout.addWidget(self.record_btn)

        # 3. ARM: circular letter "R" button
        self.arm_btn = ArmButton(26, self)
        self.arm_btn.setToolTip("Arm Sync (Shift+Space to record when armed)\nAuto-arms when MuseScore is focused.")
        self.arm_btn.toggled.connect(self._on_arm_toggled)
        layout.addWidget(self.arm_btn)

        # 4. Preview: circular play icon
        self.preview_btn = PreviewButton(26, self)
        self.preview_btn.setToolTip("Preview Recorded Phrase")
        self.preview_btn.clicked.connect(self.preview_clicked.emit)
        layout.addWidget(self.preview_btn)

        # 5. BPM Tempo Badge: clean borderless badge
        self.bpm_box = BpmBadge(120, self)
        self.bpm_box.valueChanged.connect(lambda v: self.bpm_changed.emit(float(v)))
        layout.addWidget(self.bpm_box)

        # 6. Meter Combo: clean toolbar badge
        self.meter_combo = QComboBox()
        self.meter_combo.setObjectName("MeterCombo")
        self.meter_combo.addItems(["4/4", "3/4", "2/4", "6/8", "5/4", "7/8"])
        self.meter_combo.setFixedWidth(52)
        self.meter_combo.setFixedHeight(24)
        self.meter_combo.setToolTip("Time Signature")
        self.meter_combo.currentTextChanged.connect(self._on_meter_change)
        layout.addWidget(self.meter_combo)

        # 7. Grid Combo: clean toolbar badge
        self.grid_combo = QComboBox()
        self.grid_combo.setObjectName("GridCombo")
        for g in QuantizeGrid:
            self.grid_combo.addItem(g.value, g)
        self.grid_combo.setCurrentText("1/16")
        self.grid_combo.setFixedWidth(56)
        self.grid_combo.setFixedHeight(24)
        self.grid_combo.setToolTip("Quantize Grid")
        self.grid_combo.currentIndexChanged.connect(self._on_grid_change)
        layout.addWidget(self.grid_combo)

        # 8. Insert Action Button (compact 24px height)
        self.insert_btn = QPushButton("Insert")
        self.insert_btn.setObjectName("InsertBtn")
        self.insert_btn.setFixedHeight(24)
        self.insert_btn.setToolTip("Insert notes into currently selected MuseScore measure")
        self.insert_btn.clicked.connect(self.insert_clicked.emit)
        layout.addWidget(self.insert_btn)

        # 9. Status Micro-Pill (Fixed width 68px, 24px height, clickable to sync)
        self.status_pill = QLabel("IDLE")
        self.status_pill.setObjectName("StatusPill")
        self.status_pill.setProperty("state", "IDLE")
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_pill.setFixedWidth(68)
        self.status_pill.setFixedHeight(24)
        self.status_pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_pill.setToolTip("Status / Click to Sync with MuseScore")
        self.status_pill.mousePressEvent = lambda e: self.status_clicked.emit()
        layout.addWidget(self.status_pill)

        # 10. Expand Drawer Button (borderless 24x24)
        self.drawer_btn = QPushButton("▼")
        self.drawer_btn.setObjectName("DrawerBtn")
        self.drawer_btn.setFixedSize(24, 24)
        self.drawer_btn.setToolTip("Settings, Theme Switcher & Piano Roll")
        self.drawer_btn.clicked.connect(self._toggle_drawer)
        layout.addWidget(self.drawer_btn)

        # 11. Minimalist Close Button (borderless 24x24)
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("WindowCloseBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setToolTip("Close midiplay")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)

    def set_theme(self, theme: str) -> None:
        """Propagate theme to custom painted circle buttons."""
        self.record_btn.set_theme(theme)
        self.arm_btn.set_theme(theme)
        self.preview_btn.set_theme(theme)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Allow dragging the window by clicking anywhere on the toolbar background."""
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            wh = win.windowHandle()
            if wh is not None and wh.startSystemMove():
                event.accept()
                return
            self._drag_start_pos = event.globalPosition().toPoint() - win.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            win = self.window()
            win.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._drag_start_pos is not None:
            win = self.window()
            ConfigManager.set_window_pos(win.x(), win.y())
        self._drag_start_pos = None
        event.accept()

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
        self.arm_btn.blockSignals(True)
        self.arm_btn.setChecked(armed)
        self.arm_btn.update()
        self.arm_btn.blockSignals(False)
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
        self.record_btn.update()
        self.record_btn.blockSignals(False)
