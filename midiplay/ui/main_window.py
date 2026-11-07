"""
Main Floating HUD Window and Core Controller for midiplay.
"""

from __future__ import annotations
import os
import json
import time
import threading
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QCheckBox, QPushButton,
    QMessageBox, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from midiplay.core.midi_manager import MidiManager, RawMidiEvent
from midiplay.core.audio_engine import AudioEngine
from midiplay.core.clock import Clock, TransportState
from midiplay.core.quantizer import Quantizer, QuantizeGrid, RecordingMode, QuantizedChord, PPQ
from midiplay.core.musical_parser import MusicalParser
from midiplay.core.tpc import TpcCalculator, KEY_SIGNATURES
from midiplay.core.clipboard_exporter import ClipboardExporter
from midiplay.ui.transport_bar import TransportBar
from midiplay.ui.piano_roll import PianoRollWidget
from midiplay.ui.calibration_dialog import CalibrationDialog
from midiplay.ui.styles import LIGHT_THEME_QSS, DARK_THEME_QSS
from midiplay.utils.global_hotkey import GlobalHotkeyManager
from midiplay.utils.config import ConfigManager
from midiplay.utils.musescore_window import MuseScoreWindowManager
from midiplay.utils.musescore_sync import MuseScoreSyncManager


class MainWindow(QMainWindow):
    """Floating HUD companion window for MuseScore."""

    # Thread-safe Qt signal bridge for worker callbacks
    midi_event_received = pyqtSignal(object)
    beat_received = pyqtSignal(int, bool, object)
    state_changed_signal = pyqtSignal(object)
    global_space_triggered = pyqtSignal()
    global_copy_triggered = pyqtSignal()
    global_clear_triggered = pyqtSignal()
    global_arm_triggered = pyqtSignal()
    record_start_signal = pyqtSignal()
    record_stop_signal = pyqtSignal()
    record_restart_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("midiplay — MuseScore Bridge")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Core Engines
        self.audio_engine = AudioEngine()
        self.audio_engine.start()

        self.clock = Clock(
            bpm=120.0,
            time_sig_num=4,
            time_sig_den=4,
            count_in_bars=0,  # Default to 0 bars for instant sync on Space
            on_beat_callback=self._on_clock_beat,
            on_state_change=self._on_clock_state_change
        )

        self.quantizer = Quantizer(
            grid=QuantizeGrid.SIXTEENTH,
            mode=RecordingMode.CHORDS_AND_LEAD
        )

        self.midi_manager = MidiManager(on_event_callback=self._on_raw_midi_event)
        self.midi_manager.set_on_ports_changed(self._on_ports_changed)
        self.midi_manager.start_hotplug_monitor()

        # Recorded phrase buffer
        self.recorded_events: List[RawMidiEvent] = []
        self.current_quantized_chords: List[QuantizedChord] = []

        # Configuration state
        self.key_accidentals: int = 0
        self.split_grand_staff: bool = False
        self.musescore_version: str = "4.70"
        self.synth_muted: bool = False
        self.current_theme: str = ConfigManager.get_theme()
        self._self_pid: int = os.getpid()
        self._is_topmost: bool = False
        self.musescore_sync = MuseScoreSyncManager()

        # Debounced position persistence timer
        self._pos_save_timer = QTimer(self)
        self._pos_save_timer.setSingleShot(True)
        self._pos_save_timer.timeout.connect(lambda: ConfigManager.set_window_pos(self.x(), self.y()))

        # Calibration dialog reference
        self.calib_dialog: Optional[CalibrationDialog] = None

        # Build UI
        self._init_ui()

        # Connect Signal Bridges
        self.midi_event_received.connect(self._handle_midi_event_in_qt)
        self.beat_received.connect(self._handle_beat_in_qt)
        self.state_changed_signal.connect(self._handle_state_change_in_qt)
        self.global_space_triggered.connect(self._on_space_toggled)
        self.global_copy_triggered.connect(self.quantize_and_copy)
        self.global_clear_triggered.connect(self.clear_buffer)
        self.global_arm_triggered.connect(self._toggle_arm_hotkey)

        self.record_start_signal.connect(self._start_recording_hotkey)
        self.record_stop_signal.connect(self._stop_recording_hotkey)
        self.record_restart_signal.connect(self.restart_recording)

        # Start Global Hotkeys with context-aware state machine
        self.hotkey_manager = GlobalHotkeyManager(
            on_start_record=lambda: self.record_start_signal.emit(),
            on_stop_record=lambda: self.record_stop_signal.emit(),
            on_restart_record=lambda: self.record_restart_signal.emit(),
            on_copy_shortcut=lambda: self.global_copy_triggered.emit(),
            on_arm_toggle=lambda: self.global_arm_triggered.emit()
        )
        self.hotkey_manager.start()

        # Poll window focus and MuseScore state file (every 150ms)
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_focus_and_state)
        self._poll_timer.start(150)

        # Initial device port scan
        self._refresh_midi_ports()
        self._refresh_audio_devices()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Transport Bar
        self.transport_bar = TransportBar()
        self.transport_bar.record_toggled.connect(self._on_record_toggled)
        self.transport_bar.arm_toggled.connect(self._on_arm_toggled)
        self.transport_bar.preview_clicked.connect(self._play_phrase_preview)
        self.transport_bar.bpm_changed.connect(self._on_bpm_changed)
        self.transport_bar.time_sig_changed.connect(self._on_time_sig_changed)
        self.transport_bar.grid_changed.connect(self._on_grid_changed)
        self.transport_bar.insert_clicked.connect(self.quantize_and_insert)
        self.transport_bar.status_clicked.connect(lambda: self.sync_from_plugin(show_status=True))
        self.transport_bar.drawer_toggled.connect(self._set_drawer_visible)
        self.transport_bar.close_clicked.connect(self.close)
        self.main_layout.addWidget(self.transport_bar)

        # 2. Expandable Drawer
        self.drawer_widget = QWidget()
        self.drawer_widget.setObjectName("DrawerWidget")
        self.drawer_layout = QVBoxLayout(self.drawer_widget)
        self.drawer_layout.setContentsMargins(10, 8, 10, 8)
        self.drawer_layout.setSpacing(8)

        # Drawer Row 1: MIDI Port, Audio Output & Mute Synth
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("MIDI:"))
        self.midi_port_combo = QComboBox()
        self.midi_port_combo.currentIndexChanged.connect(self._on_port_selected)
        row1.addWidget(self.midi_port_combo, 2)

        self.refresh_ports_btn = QPushButton("↻")
        self.refresh_ports_btn.setFixedWidth(26)
        self.refresh_ports_btn.clicked.connect(self._refresh_midi_ports)
        row1.addWidget(self.refresh_ports_btn)

        row1.addWidget(QLabel("Audio:"))
        self.audio_device_combo = QComboBox()
        self.audio_device_combo.currentIndexChanged.connect(self._on_audio_device_selected)
        row1.addWidget(self.audio_device_combo, 3)

        self.mute_synth_cb = QCheckBox("Mute Synth")
        saved_mute_synth = ConfigManager.get_mute_synth()
        self.mute_synth_cb.setChecked(saved_mute_synth)
        self.synth_muted = saved_mute_synth
        self.mute_synth_cb.setToolTip("Silences local piano synth if your keyboard or MuseScore already plays sound")
        self.mute_synth_cb.toggled.connect(self._on_mute_synth_toggled)
        row1.addWidget(self.mute_synth_cb)

        self.theme_btn = QPushButton("Dark" if self.current_theme == "light" else "Light")
        self.theme_btn.setToolTip("Toggle Light / Dark Theme")
        self.theme_btn.clicked.connect(self._toggle_theme)
        row1.addWidget(self.theme_btn)
        self.drawer_layout.addLayout(row1)

        # Drawer Row 2: Mode, Key, Grand Staff & Options
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Chords & Lead", RecordingMode.CHORDS_AND_LEAD)
        self.mode_combo.addItem("Strict Lead", RecordingMode.STRICT_LEAD)
        self.mode_combo.addItem("Polyphonic", RecordingMode.POLYPHONIC)
        saved_mode = ConfigManager.get_recording_mode()
        idx_m = self.mode_combo.findText(saved_mode)
        if idx_m != -1:
            self.mode_combo.setCurrentIndex(idx_m)
            m_data = self.mode_combo.currentData()
            if m_data:
                self.quantizer.mode = m_data
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        row2.addWidget(self.mode_combo)

        row2.addWidget(QLabel("Key:"))
        self.key_combo = QComboBox()
        for name, acc in KEY_SIGNATURES:
            self.key_combo.addItem(name, acc)
        self.key_combo.currentIndexChanged.connect(self._on_key_changed)
        row2.addWidget(self.key_combo)

        self.auto_key_btn = QPushButton("Auto-Key")
        self.auto_key_btn.setToolTip("Detect key signature from recorded notes")
        self.auto_key_btn.clicked.connect(self._auto_detect_key)
        row2.addWidget(self.auto_key_btn)

        self.grand_staff_cb = QCheckBox("Grand Staff (C4)")
        saved_grand_staff = ConfigManager.get_split_grand_staff()
        self.grand_staff_cb.setChecked(saved_grand_staff)
        self.split_grand_staff = saved_grand_staff
        self.grand_staff_cb.toggled.connect(self._on_grand_staff_toggled)
        row2.addWidget(self.grand_staff_cb)

        self.ms_version_combo = QComboBox()
        self.ms_version_combo.addItem("MuseScore 4.x", "4.70")
        self.ms_version_combo.addItem("MuseScore 3.x", "3.02")
        self.ms_version_combo.currentIndexChanged.connect(self._on_ms_version_changed)
        row2.addWidget(self.ms_version_combo)

        row2.addWidget(QLabel("Count-In:"))
        self.count_in_combo = QComboBox()
        self.count_in_combo.addItem("None (Instant)", 0)
        self.count_in_combo.addItem("1 Bar", 1)
        self.count_in_combo.addItem("2 Bars", 2)
        saved_count_in = ConfigManager.get_count_in_bars()
        idx_ci = self.count_in_combo.findData(saved_count_in)
        if idx_ci != -1:
            self.count_in_combo.setCurrentIndex(idx_ci)
        self.clock.set_count_in_bars(saved_count_in)
        self.count_in_combo.currentIndexChanged.connect(self._on_count_in_changed)
        row2.addWidget(self.count_in_combo)

        self.mute_click_cb = QCheckBox("Mute Click")
        saved_mute_click = ConfigManager.get_mute_click()
        self.mute_click_cb.setChecked(saved_mute_click)
        self.audio_engine.set_metronome_muted(saved_mute_click)
        self.mute_click_cb.setToolTip("Mutes local click during MuseScore play-along")
        self.mute_click_cb.toggled.connect(self._on_mute_click_toggled)
        row2.addWidget(self.mute_click_cb)
        self.drawer_layout.addLayout(row2)

        # Drawer Row 3: Piano Roll Scratchpad
        self.piano_roll = PianoRollWidget()
        self.drawer_layout.addWidget(self.piano_roll)

        # Drawer Row 4: Calibration & Quick Actions
        row4 = QHBoxLayout()
        self.calib_btn = QPushButton("Calibrate Latency (4-Tap)")
        self.calib_btn.clicked.connect(self._open_calibration)
        row4.addWidget(self.calib_btn)

        row4.addWidget(QLabel("Sync Delay:"))
        self.sync_delay_spin = QSpinBox()
        self.sync_delay_spin.setRange(0, 300)
        saved_sync_delay = ConfigManager.get_sync_delay_ms()
        self.sync_delay_spin.setValue(int(saved_sync_delay))
        self.clock.set_sync_delay_ms(saved_sync_delay)
        self.sync_delay_spin.setSuffix(" ms")
        self.sync_delay_spin.setToolTip("Delays midiplay's click to match MuseScore audio playback startup latency")
        self.sync_delay_spin.valueChanged.connect(self._on_sync_delay_changed)
        row4.addWidget(self.sync_delay_spin)

        row4.addWidget(QLabel("Offset:"))
        self.latency_slider = QSlider(Qt.Orientation.Horizontal)
        self.latency_slider.setRange(-100, 100)
        saved_offset = ConfigManager.get_latency_offset_ms()
        self.latency_slider.setValue(int(saved_offset))
        self.clock.set_latency_offset_ms(saved_offset)
        self.latency_slider.valueChanged.connect(self._on_latency_slider_changed)
        row4.addWidget(self.latency_slider)

        self.latency_val_label = QLabel(f"{int(saved_offset):+d} ms")
        self.latency_val_label.setFixedWidth(45)
        row4.addWidget(self.latency_val_label)

        self.clear_btn = QPushButton("Clear Buffer")
        self.clear_btn.clicked.connect(self.clear_buffer)
        row4.addWidget(self.clear_btn)

        self.drawer_layout.addLayout(row4)
        self.main_layout.addWidget(self.drawer_widget)

        # Drawer collapsed by default for clean MuseScore toolbar integration
        self.drawer_widget.setVisible(False)
        self.transport_bar.drawer_expanded = False
        self.transport_bar.drawer_btn.setText("▼")
        self.setFixedHeight(34)
        self.set_theme(self.current_theme)
        self.adjustSize()
        self.raise_()

        # Apply Win32 WS_EX_NOACTIVATE so midiplay never steals focus from MuseScore
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            SWP_FLAGS = 0x0002 | 0x0001 | 0x0010 | 0x0020  # NOMOVE | NOSIZE | NOACTIVATE | FRAMECHANGED
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_FLAGS)
        except Exception:
            pass

        # Zero-focus policy: ensure all controls reject keyboard focus
        self._apply_no_focus_recursively(self)

        # Restore user's custom window position
        saved_pos = ConfigManager.get_window_pos()
        if saved_pos:
            self.move(saved_pos[0], saved_pos[1])
        else:
            self.move(300, 40)

    def _apply_no_focus_recursively(self, root: QWidget) -> None:
        """Enforces Qt.FocusPolicy.NoFocus on all widgets so midiplay never steals keyboard focus."""
        root.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for child in root.findChildren(QWidget):
            child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def nativeEvent(self, eventType, message):
        """Win32 event hook: handles WM_MOUSEACTIVATE to keep MuseScore active when midiplay is clicked."""
        try:
            msg = wintypes.MSG.from_address(int(message))
            WM_MOUSEACTIVATE = 0x0021
            MA_NOACTIVATE = 3
            if msg.message == WM_MOUSEACTIVATE:
                return True, MA_NOACTIVATE
        except Exception:
            pass
        return False, 0

    def keyPressEvent(self, event) -> None:
        """Rejects all focus-based key events — midiplay only responds to global OS-level hotkeys."""
        event.ignore()

    def keyReleaseEvent(self, event) -> None:
        """Rejects all focus-based key events — midiplay only responds to global OS-level hotkeys."""
        event.ignore()

    def moveEvent(self, event) -> None:
        """Debounced position save during/after window movement."""
        super().moveEvent(event)
        if hasattr(self, '_pos_save_timer'):
            self._pos_save_timer.start(500)

    def set_theme(self, theme_mode: str) -> None:
        self.current_theme = theme_mode
        ConfigManager.set_theme(theme_mode)
        qss = LIGHT_THEME_QSS if theme_mode == "light" else DARK_THEME_QSS
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)
        if hasattr(self, 'theme_btn'):
            self.theme_btn.setText("Dark" if theme_mode == "light" else "Light")
        if hasattr(self, 'transport_bar'):
            self.transport_bar.set_theme(theme_mode)
        self.piano_roll.set_theme(theme_mode)

    def _toggle_theme(self) -> None:
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)

    # --- Drawer Visibility & Sizing (Anchored to Top-Right Corner) ---
    def _set_drawer_visible(self, visible: bool) -> None:
        top_right_x = self.x() + self.width()
        top_right_y = self.y()

        self.drawer_widget.setVisible(visible)
        self.transport_bar.drawer_expanded = visible
        self.transport_bar.drawer_btn.setText("▲" if visible else "▼")

        if visible:
            self._apply_no_focus_recursively(self.drawer_widget)
            target_w = 820
            target_h = 270
            self.setMinimumSize(target_w, 268)
            self.setMaximumSize(16777215, 16777215)
            self.setGeometry(top_right_x - target_w, top_right_y, target_w, target_h)
        else:
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 34)
            self.setFixedHeight(34)
            self.adjustSize()
            compact_w = self.width()
            self.move(top_right_x - compact_w, top_right_y)

    # --- MIDI Ports ---
    def _refresh_midi_ports(self) -> None:
        ports = self.midi_manager.get_ports()
        self.midi_port_combo.blockSignals(True)
        self.midi_port_combo.clear()
        if not ports:
            self.midi_port_combo.addItem("No MIDI Devices Connected", None)
        else:
            saved_port = ConfigManager.get_midi_port()
            selected_idx = 0
            for idx, p in enumerate(ports):
                self.midi_port_combo.addItem(p, p)
                if saved_port and p == saved_port:
                    selected_idx = idx

            self.midi_port_combo.setCurrentIndex(selected_idx)
            chosen_port = ports[selected_idx]
            if self.midi_manager.current_port_name != chosen_port:
                self.midi_manager.open_port(chosen_port)
        self.midi_port_combo.blockSignals(False)

    def _on_ports_changed(self, ports: List[str]) -> None:
        QTimer.singleShot(0, self._refresh_midi_ports)

    def _on_port_selected(self, index: int) -> None:
        port_name = self.midi_port_combo.currentData()
        if port_name:
            self.midi_manager.open_port(port_name)
            ConfigManager.set_midi_port(port_name)

    # --- Audio Devices ---
    def _refresh_audio_devices(self) -> None:
        devices = self.audio_engine.get_output_devices()
        self.audio_device_combo.blockSignals(True)
        self.audio_device_combo.clear()

        current_idx = self.audio_engine.current_device_index
        saved_device = ConfigManager.get_audio_device()
        selected_combo_idx = 0

        for combo_idx, (dev_idx, dev_name, is_wasapi) in enumerate(devices):
            self.audio_device_combo.addItem(dev_name, dev_idx)
            if saved_device and dev_name == saved_device:
                selected_combo_idx = combo_idx
            elif not saved_device and dev_idx == current_idx:
                selected_combo_idx = combo_idx

        if devices:
            self.audio_device_combo.setCurrentIndex(selected_combo_idx)
            chosen_dev = devices[selected_combo_idx][0]
            if chosen_dev != current_idx:
                self.audio_engine.set_output_device(chosen_dev)

        self.audio_device_combo.blockSignals(False)

    def _on_audio_device_selected(self, index: int) -> None:
        dev_idx = self.audio_device_combo.currentData()
        if dev_idx is not None:
            self.audio_engine.set_output_device(dev_idx)
            ConfigManager.set_audio_device(self.audio_device_combo.currentText())

    def _on_mute_synth_toggled(self, checked: bool) -> None:
        self.synth_muted = checked
        if checked:
            self.audio_engine.all_notes_off()
        ConfigManager.set_mute_synth(checked)

    def _on_mute_click_toggled(self, checked: bool) -> None:
        self.audio_engine.set_metronome_muted(checked)
        ConfigManager.set_mute_click(checked)

    # --- Transport & Recording ---
    def _start_recording_hotkey(self) -> None:
        """Triggered by Shift+Space when ARM=on."""
        if not self.transport_bar.record_btn.isChecked():
            self.transport_bar.record_btn.setChecked(True)

    def _stop_recording_hotkey(self) -> None:
        """Triggered by plain Space while recording."""
        if self.transport_bar.record_btn.isChecked():
            self.transport_bar.record_btn.setChecked(False)

    def restart_recording(self) -> None:
        """Restarts current take immediately on Shift+Space while recording (no insert)."""
        self.recorded_events.clear()
        self.piano_roll.clear()
        self.clock.stop()
        self.clock.start_recording()
        self.transport_bar.set_status("RESTART", "COUNT_IN")
        self.transport_bar.set_recording_active(True)
        QTimer.singleShot(800, lambda: self.transport_bar.set_status("RECORDING", "RECORDING"))

    def _on_record_toggled(self, active: bool) -> None:
        self.hotkey_manager.set_recording(active)
        self.transport_bar.set_recording_active(active)
        if active:
            self.recorded_events.clear()
            self.piano_roll.clear()
            self.clock.start_recording()
        else:
            self.clock.stop()
            self._on_recording_stopped()

    def _on_recording_stopped(self) -> None:
        if self.recorded_events:
            self.quantize_and_insert()
        else:
            self.transport_bar.set_status("IDLE", "IDLE")

    def _on_space_toggled(self) -> None:
        is_rec = self.clock.state in (TransportState.COUNT_IN, TransportState.RECORDING)
        self.transport_bar.record_btn.setChecked(not is_rec)

    def _toggle_arm_hotkey(self) -> None:
        self.transport_bar.arm_btn.setChecked(not self.transport_bar.arm_btn.isChecked())

    def _on_arm_toggled(self, armed: bool) -> None:
        self.hotkey_manager.set_armed(armed)

    def _poll_focus_and_state(self) -> None:
        """Polls active foreground window for auto-arm & window z-order."""
        # 1. Focus detection
        is_focused = MuseScoreWindowManager.is_musescore_or_self_focused(self._self_pid)

        # Auto-arm / disarm based on MuseScore focus (when idle)
        if not self.hotkey_manager.is_recording:
            if is_focused != self.hotkey_manager.armed:
                self.hotkey_manager.set_armed(is_focused)
                self.transport_bar.arm_btn.blockSignals(True)
                self.transport_bar.arm_btn.setChecked(is_focused)
                self.transport_bar._on_arm_toggled(is_focused)
                self.transport_bar.arm_btn.blockSignals(False)

        # Dynamic Window Stay-on-Top z-order (topmost when MuseScore focused, sink when unfocused)
        if is_focused != self._is_topmost:
            self._is_topmost = is_focused
            hwnd = int(self.winId())
            MuseScoreWindowManager.set_window_topmost(hwnd, is_focused)
            if is_focused:
                self.raise_()

    def sync_from_plugin(self, show_status: bool = True) -> bool:
        """Pulls tempo and meter from MuseScore plugin on demand (triggered by IDLE button)."""
        state = self.musescore_sync.get_active_state()
        if not state:
            if show_status and not self.hotkey_manager.is_recording:
                self.transport_bar.set_status("NO SYNC", "IDLE")
                QTimer.singleShot(1500, lambda: self.transport_bar.set_status("IDLE", "IDLE"))
            return False

        bpm = state.get("bpm")
        num = state.get("time_sig_num")
        den = state.get("time_sig_den")
        title = state.get("title", "")

        updated = False
        if bpm and int(bpm) != int(self.clock.bpm):
            self.clock.set_bpm(float(bpm))
            self.transport_bar.set_bpm_display(int(bpm))
            updated = True

        if num and den:
            meter_str = f"{num}/{den}"
            if int(num) != self.clock.time_sig_num or int(den) != self.clock.time_sig_den:
                self.clock.set_time_signature(int(num), int(den))
                self.transport_bar.meter_combo.blockSignals(True)
                if self.transport_bar.meter_combo.findText(meter_str) == -1:
                    self.transport_bar.meter_combo.addItem(meter_str)
                self.transport_bar.meter_combo.setCurrentText(meter_str)
                self.transport_bar.meter_combo.blockSignals(False)
                updated = True

        if show_status and not self.hotkey_manager.is_recording:
            self.transport_bar.set_status("SYNCED", "COPIED")
            QTimer.singleShot(1500, lambda: self.transport_bar.set_status("IDLE", "IDLE"))
            if title:
                self.transport_bar.status_pill.setToolTip(f"Synced with: {title} (Click to re-sync)")

        return updated

    def _quantize_buffer(self) -> None:
        self.current_quantized_chords = self.quantizer.process_raw_events(
            events=self.recorded_events,
            record_start_time=self.clock.record_start_time,
            bpm=self.clock.bpm,
            latency_offset_ms=self.clock.latency_offset_ms
        )
        measure_ticks = int((self.clock.time_sig_num * PPQ * 4) / self.clock.time_sig_den)
        self.piano_roll.set_data(self.current_quantized_chords, measure_ticks)

    def quantize_and_insert(self) -> None:
        """Quantizes active buffer, formats MuseScore 4 XML, and auto-inserts into selected measure."""
        if not self.recorded_events and not self.current_quantized_chords:
            return

        self.transport_bar.set_status("QUANTIZING", "QUANTIZING")
        self._quantize_buffer()

        parser = MusicalParser(self.clock.time_sig_num, self.clock.time_sig_den)
        staff1_m, staff2_m = parser.build_measures(
            chords=self.current_quantized_chords,
            split_grand_staff=self.split_grand_staff,
            split_pitch=60
        )

        xml_content = ClipboardExporter.generate_musescore_xml(
            staff1_measures=staff1_m,
            staff2_measures=staff2_m,
            key_accidentals=self.key_accidentals,
            musescore_version=self.musescore_version,
            time_sig_num=self.clock.time_sig_num,
            time_sig_den=self.clock.time_sig_den
        )

        is_ms4 = not self.musescore_version.startswith("3")
        success = ClipboardExporter.copy_to_clipboard(xml_content, is_musescore_4=is_ms4)
        if success:
            # Auto-focus MuseScore and simulate Ctrl+V into active measure
            inserted = MuseScoreWindowManager.focus_and_paste()
            if inserted:
                self.transport_bar.set_status("INSERTED", "COPIED")
            else:
                self.transport_bar.set_status("COPIED", "COPIED")
            QTimer.singleShot(2500, lambda: self.transport_bar.set_status("IDLE", "IDLE"))

    def quantize_and_copy(self) -> None:
        self.quantize_and_insert()

    def clear_buffer(self) -> None:
        self.recorded_events.clear()
        self.current_quantized_chords.clear()
        self.piano_roll.clear()
        self.audio_engine.all_notes_off()
        self.transport_bar.set_status("IDLE", "IDLE")

    def _play_phrase_preview(self) -> None:
        """Plays back the quantized phrase through the built-in synthesizer."""
        if not self.current_quantized_chords:
            return

        bpm = self.clock.bpm
        seconds_per_tick = (60.0 / bpm) / PPQ

        def _preview_worker():
            for chord in self.current_quantized_chords:
                # Play note
                for p in chord.pitches:
                    self.audio_engine.note_on(p, 90)
                dur_sec = max(0.05, chord.duration_ticks * seconds_per_tick)
                time.sleep(dur_sec * 0.9)
                for p in chord.pitches:
                    self.audio_engine.note_off(p)
                time.sleep(dur_sec * 0.1)

        threading.Thread(target=_preview_worker, daemon=True).start()

    # --- MIDI & Audio Callbacks ---
    def _on_raw_midi_event(self, event: RawMidiEvent) -> None:
        # Live monitor sound
        if event.event_type == "note_on":
            if not self.synth_muted:
                self.audio_engine.note_on(event.pitch, event.velocity)
            if self.calib_dialog and self.calib_dialog.isVisible():
                self.calib_dialog.register_tap()
        elif event.event_type == "note_off":
            if not self.synth_muted:
                self.audio_engine.note_off(event.pitch)

        self.midi_event_received.emit(event)

    def _handle_midi_event_in_qt(self, event: RawMidiEvent) -> None:
        if self.clock.state == TransportState.RECORDING:
            self.recorded_events.append(event)

    def _on_clock_beat(self, beat_index: int, is_downbeat: bool, state: TransportState) -> None:
        # Audible metronome click
        self.audio_engine.trigger_click(is_downbeat)
        self.beat_received.emit(beat_index, is_downbeat, state)

    def _handle_beat_in_qt(self, beat_index: int, is_downbeat: bool, state: TransportState) -> None:
        if state == TransportState.COUNT_IN:
            count_num = (beat_index % self.clock.time_sig_num) + 1
            self.transport_bar.set_status(f"COUNT-IN: {count_num}", "COUNT_IN")
        elif state == TransportState.RECORDING:
            bar_num = (beat_index // self.clock.time_sig_num) + 1
            beat_num = (beat_index % self.clock.time_sig_num) + 1
            self.transport_bar.set_status(f"REC: BAR {bar_num} . {beat_num}", "RECORDING")

    def _on_clock_state_change(self, state: TransportState) -> None:
        self.state_changed_signal.emit(state)

    def _handle_state_change_in_qt(self, state: TransportState) -> None:
        is_rec = state in (TransportState.COUNT_IN, TransportState.RECORDING)
        self.transport_bar.set_recording_active(is_rec)
        if state == TransportState.IDLE:
            self.transport_bar.set_status("IDLE", "IDLE")

    # --- Controls Handlers ---
    def _on_bpm_changed(self, bpm: float) -> None:
        self.clock.set_bpm(bpm)

    def _on_tap_tempo(self) -> None:
        new_bpm = self.clock.register_tap()
        if new_bpm:
            self.transport_bar.bpm_box.setValue(int(new_bpm))

    def _on_time_sig_changed(self, num: int, den: int) -> None:
        self.clock.set_time_signature(num, den)
        self._user_meter_override = True

    def _on_grid_changed(self, grid: QuantizeGrid) -> None:
        self.quantizer.grid = grid

    def _on_mode_changed(self, index: int) -> None:
        mode = self.mode_combo.currentData()
        if isinstance(mode, RecordingMode):
            self.quantizer.mode = mode
            ConfigManager.set_recording_mode(self.mode_combo.currentText())

    def _on_key_changed(self, index: int) -> None:
        acc = self.key_combo.currentData()
        if isinstance(acc, int):
            self.key_accidentals = acc

    def _auto_detect_key(self) -> None:
        pitches = [ev.pitch for ev in self.recorded_events if ev.event_type == "note_on"]
        if not pitches and self.current_quantized_chords:
            pitches = [p for c in self.current_quantized_chords for p in c.pitches]

        if not pitches:
            QMessageBox.information(self, "Auto-Key", "Record some notes first to detect the key!")
            return

        acc = TpcCalculator.detect_key_signature(pitches)
        for i in range(self.key_combo.count()):
            if self.key_combo.itemData(i) == acc:
                self.key_combo.setCurrentIndex(i)
                break
        self.key_accidentals = acc

    def _on_grand_staff_toggled(self, checked: bool) -> None:
        self.split_grand_staff = checked
        ConfigManager.set_split_grand_staff(checked)

    def _on_ms_version_changed(self, index: int) -> None:
        ver = self.ms_version_combo.currentData()
        if isinstance(ver, str):
            self.musescore_version = ver

    def _open_calibration(self) -> None:
        self.calib_dialog = CalibrationDialog(
            audio_engine=self.audio_engine,
            current_offset_ms=self.clock.latency_offset_ms,
            parent=self
        )
        self.calib_dialog.offset_changed.connect(self._on_calibration_offset_changed)
        self.calib_dialog.exec()

    def _on_calibration_offset_changed(self, offset_ms: float) -> None:
        self.latency_slider.setValue(int(offset_ms))
        self.clock.set_latency_offset_ms(offset_ms)
        self.latency_val_label.setText(f"{int(offset_ms):+d} ms")
        ConfigManager.set_latency_offset_ms(offset_ms)

    def _on_latency_slider_changed(self, val: int) -> None:
        self.clock.set_latency_offset_ms(float(val))
        self.latency_val_label.setText(f"{val:+d} ms")
        ConfigManager.set_latency_offset_ms(float(val))

    def _on_sync_delay_changed(self, val: int) -> None:
        self.clock.set_sync_delay_ms(float(val))
        ConfigManager.set_sync_delay_ms(float(val))

    def _on_count_in_changed(self, index: int) -> None:
        bars = self.count_in_combo.currentData()
        if isinstance(bars, int):
            self.clock.set_count_in_bars(bars)
            ConfigManager.set_count_in_bars(bars)

    def closeEvent(self, event) -> None:
        ConfigManager.set_window_pos(self.x(), self.y())
        self.clock.stop()
        self.audio_engine.stop()
        self.midi_manager.close_port()
        self.midi_manager.stop_hotplug_monitor()
        self.hotkey_manager.stop()
        event.accept()
