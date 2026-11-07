"""
Horizontal Mini Piano Roll Scratchpad Widget.
"""

from __future__ import annotations
from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF

from midiplay.core.quantizer import QuantizedChord, PPQ
from midiplay.ui.styles import PIANO_ROLL_PALETTES


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def pitch_to_name(pitch: int) -> str:
    octave = (pitch // 12) - 1
    name = NOTE_NAMES[pitch % 12]
    return f"{name}{octave}"


class PianoRollWidget(QWidget):
    """Visualizes quantized notes and measures in a compact horizontal strip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(110)
        self.chords: List[QuantizedChord] = []
        self.measure_ticks = PPQ * 4  # Default 4/4
        self.playhead_tick: Optional[int] = None
        self.theme_mode: str = "light"

    def set_theme(self, theme_mode: str) -> None:
        self.theme_mode = theme_mode
        self.update()

    def set_data(self, chords: List[QuantizedChord], measure_ticks: int) -> None:
        self.chords = chords
        self.measure_ticks = measure_ticks
        self.update()

    def set_playhead(self, tick: Optional[int]) -> None:
        self.playhead_tick = tick
        self.update()

    def clear(self) -> None:
        self.chords = []
        self.playhead_tick = None
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        palette = PIANO_ROLL_PALETTES.get(self.theme_mode, PIANO_ROLL_PALETTES["light"])

        # Background
        painter.fillRect(0, 0, w, h, QColor(palette["background"]))

        # Outer border
        painter.setPen(QPen(QColor(palette["border"]), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        if not self.chords:
            # Empty placeholder text
            painter.setPen(QColor(palette["placeholder"]))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Ready. Play controller or press Space to record...")
            return

        # Determine tick span
        total_ticks = max(self.measure_ticks, max(c.start_tick + c.duration_ticks for c in self.chords))
        num_bars = max(1, (total_ticks + self.measure_ticks - 1) // self.measure_ticks)
        span_ticks = num_bars * self.measure_ticks

        # Determine pitch span
        all_pitches = [p for c in self.chords for p in c.pitches]
        min_p = max(0, min(all_pitches) - 2)
        max_p = min(127, max(all_pitches) + 2)
        pitch_range = max(12, max_p - min_p + 1)

        # Draw Grid: Barlines & Beats
        painter.setFont(QFont("Segoe UI", 8))
        for m in range(num_bars + 1):
            m_tick = m * self.measure_ticks
            x = (m_tick / span_ticks) * (w - 30) + 10

            # Measure barline
            painter.setPen(QPen(QColor(palette["barline"]), 1.5))
            painter.drawLine(int(x), 0, int(x), h)

            if m < num_bars:
                painter.setPen(QColor(palette["measure_label"]))
                painter.drawText(int(x) + 4, 12, f"M{m + 1}")

        # Draw Chords / Notes
        for chord in self.chords:
            x_start = (chord.start_tick / span_ticks) * (w - 30) + 10
            chord_w = max(6.0, (chord.duration_ticks / span_ticks) * (w - 30))

            for pitch in chord.pitches:
                rel_p = (pitch - min_p) / pitch_range
                y = h - 20 - (rel_p * (h - 35))
                note_h = max(7.0, (h - 35) / pitch_range)

                rect = QRectF(x_start, y, chord_w - 2, note_h - 1)

                # Modern note fill & border
                painter.setBrush(QBrush(QColor(palette["note_fill"])))
                painter.setPen(QPen(QColor(palette["note_border"]), 1))
                painter.drawRoundedRect(rect, 3, 3)

                # Pitch name label
                if chord_w > 24 and note_h >= 8:
                    painter.setPen(QColor(palette["note_text"]))
                    painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
                    painter.drawText(QRectF(x_start + 2, y, chord_w - 4, note_h), Qt.AlignmentFlag.AlignVCenter, pitch_to_name(pitch))

        # Playhead line
        if self.playhead_tick is not None:
            px = (self.playhead_tick / span_ticks) * (w - 30) + 10
            painter.setPen(QPen(QColor(palette["playhead"]), 2))
            painter.drawLine(int(px), 0, int(px), h)
