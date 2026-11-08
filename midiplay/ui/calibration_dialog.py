"""
4-Tap Latency Calibration Wizard and Timing Offset Controls.
"""

from __future__ import annotations
import time
import threading
from typing import Callable, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from midiplay.core.audio_engine import AudioEngine


class CalibrationWorker(QObject):
    step_signal = pyqtSignal(int, str)  # (tap_index, instructions)
    finished_signal = pyqtSignal(float) # calculated_offset_ms

    def __init__(self, audio_engine: AudioEngine):
        super().__init__()
        self.audio_engine = audio_engine
        self.is_running = False
        self.click_times: List[float] = []
        self.tap_times: List[float] = []

    def record_tap(self) -> None:
        if self.is_running:
            self.tap_times.append(time.perf_counter())

    def run_wizard(self) -> None:
        self.is_running = True
        self.click_times.clear()
        self.tap_times.clear()

        interval = 0.55  # ~110 BPM comfortable tap rate

        # Pre-count 2 clicks
        self.step_signal.emit(0, "Get ready... Listen to the click")
        self.audio_engine.trigger_click(is_downbeat=True)
        time.sleep(interval)
        self.audio_engine.trigger_click(is_downbeat=False)
        time.sleep(interval)

        # 4 measurement clicks
        for i in range(4):
            click_t = time.perf_counter()
            self.click_times.append(click_t)
            self.audio_engine.trigger_click(is_downbeat=(i == 0))
            self.step_signal.emit(i + 1, f"Tap Beat {i + 1} of 4 now!")
            time.sleep(interval)

        time.sleep(0.3)
        self.is_running = False

        # Calculate average offset
        if len(self.tap_times) >= 2 and len(self.click_times) >= 4:
            # Pair each tap with closest click
            deltas = []
            for tap_t in self.tap_times:
                closest_click = min(self.click_times, key=lambda c: abs(c - tap_t))
                delta_ms = (tap_t - closest_click) * 1000.0
                if abs(delta_ms) < 300:  # Reasonable range
                    deltas.append(delta_ms)

            if deltas:
                avg_offset_ms = sum(deltas) / len(deltas)
                self.finished_signal.emit(avg_offset_ms)
                return

        self.finished_signal.emit(0.0)


class CalibrationDialog(QDialog):
    """Dialog for calibrating hardware/audio latency."""

    offset_changed = pyqtSignal(float)

    def __init__(self, audio_engine: AudioEngine, current_offset_ms: float = 0.0, parent=None):
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.current_offset_ms = current_offset_ms
        self.worker = CalibrationWorker(audio_engine)

        self.setWindowTitle("Latency Calibration Wizard")
        self.setFixedSize(380, 260)

        layout = QVBoxLayout(self)

        self.info_label = QLabel(
            "Compensates for audio driver output lag & human keyboard anticipation.\n"
            "Click 'Start 4-Tap Wizard' and tap any MIDI key along with the 4 clicks."
        )
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.status_label = QLabel("Status: Ready to calibrate.")
        self.status_label.setObjectName("CalibrationStatus")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 4)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.start_btn = QPushButton("Start 4-Tap Calibration Wizard")
        self.start_btn.clicked.connect(self._start_wizard)
        layout.addWidget(self.start_btn)

        # Manual offset slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Offset:"))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(-100, 100)
        self.slider.setValue(int(current_offset_ms))
        self.slider.valueChanged.connect(self._on_slider_change)
        slider_layout.addWidget(self.slider)

        self.offset_value_label = QLabel(f"{int(current_offset_ms)} ms")
        self.offset_value_label.setFixedWidth(50)
        slider_layout.addWidget(self.offset_value_label)
        layout.addLayout(slider_layout)

        close_btn = QPushButton("Done")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        # Connect worker signals
        self.worker.step_signal.connect(self._on_wizard_step)
        self.worker.finished_signal.connect(self._on_wizard_finished)

    def register_tap(self) -> None:
        """Called when a physical MIDI note on arrives during calibration."""
        self.worker.record_tap()

    def _start_wizard(self) -> None:
        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        threading.Thread(target=self.worker.run_wizard, daemon=True).start()

    def _on_wizard_step(self, step: int, instruction: str) -> None:
        self.progress_bar.setValue(step)
        self.status_label.setText(f"Beat {step}/4: {instruction}")

    def _on_wizard_finished(self, offset_ms: float) -> None:
        self.start_btn.setEnabled(True)
        self.slider.setValue(int(offset_ms))
        self.status_label.setText(f"Calibration Complete! Detected offset: {offset_ms:+.1f} ms")

    def _on_slider_change(self, val: int) -> None:
        self.current_offset_ms = float(val)
        self.offset_value_label.setText(f"{val:+d} ms")
        self.offset_changed.emit(self.current_offset_ms)
