"""
Main Floating HUD Window and Core Controller for midiplay.
"""

from __future__ import annotations
import time
import threading
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
from midiplay.utils.global_hotkey import GlobalHotkeyManager


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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("midiplay — MuseScore Bridge")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

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

        # Start Global Hotkeys
        self.hotkey_manager = GlobalHotkeyManager(
            on_space_toggle=lambda: self.global_space_triggered.emit(),
            on_copy_shortcut=lambda: self.global_copy_triggered.emit(),
            on_arm_toggle=lambda: self.global_arm_triggered.emit()
        )
        self.hotkey_manager.start()

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
        self.transport_bar.tap_tempo_clicked.connect(self._on_tap_tempo)
        self.transport_bar.time_sig_changed.connect(self._on_time_sig_changed)
        self.transport_bar.grid_changed.connect(self._on_grid_changed)
        self.transport_bar.copy_clicked.connect(self.quantize_and_copy)
        self.transport_bar.drawer_toggled.connect(self._set_drawer_visible)
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
        self.mute_synth_cb.setToolTip("Silences local piano synth if your keyboard or MuseScore already plays sound")
        self.mute_synth_cb.toggled.connect(self._on_mute_synth_toggled)
        row1.addWidget(self.mute_synth_cb)
        self.drawer_layout.addLayout(row1)

        # Drawer Row 2: Mode, Key, Grand Staff & Options
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Chords & Lead", RecordingMode.CHORDS_AND_LEAD)
        self.mode_combo.addItem("Strict Lead", RecordingMode.STRICT_LEAD)
        self.mode_combo.addItem("Polyphonic", RecordingMode.POLYPHONIC)
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
        self.count_in_combo.currentIndexChanged.connect(self._on_count_in_changed)
        row2.addWidget(self.count_in_combo)

        self.mute_click_cb = QCheckBox("Mute Click")
        self.mute_click_cb.setToolTip("Mutes local click during MuseScore play-along")
        self.mute_click_cb.toggled.connect(lambda v: self.audio_engine.set_metronome_muted(v))
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
        self.sync_delay_spin.setValue(45)
        self.sync_delay_spin.setSuffix(" ms")
        self.sync_delay_spin.setToolTip("Delays midiplay's click to match MuseScore audio playback startup latency")
        self.sync_delay_spin.valueChanged.connect(self._on_sync_delay_changed)
        row4.addWidget(self.sync_delay_spin)

        row4.addWidget(QLabel("Offset:"))
        self.latency_slider = QSlider(Qt.Orientation.Horizontal)
        self.latency_slider.setRange(-100, 100)
        self.latency_slider.setValue(0)
        self.latency_slider.valueChanged.connect(self._on_latency_slider_changed)
        row4.addWidget(self.latency_slider)

        self.latency_val_label = QLabel("+0 ms")
        self.latency_val_label.setFixedWidth(45)
        row4.addWidget(self.latency_val_label)

        self.clear_btn = QPushButton("Clear Buffer")
        self.clear_btn.clicked.connect(self.clear_buffer)
        row4.addWidget(self.clear_btn)

        self.drawer_layout.addLayout(row4)
        self.main_layout.addWidget(self.drawer_widget)

        # Drawer visible by default so user immediately sees device & piano roll
        self.drawer_widget.setVisible(True)
        self.transport_bar.drawer_expanded = True
        self.transport_bar.drawer_btn.setText("▲")
        self.setMinimumWidth(840)
        self.adjustSize()
        self.raise_()
        self.activateWindow()

    # --- Drawer Visibility & Sizing ---
    def _set_drawer_visible(self, visible: bool) -> None:
        self.drawer_widget.setVisible(visible)
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        target_h = self.minimumSizeHint().height()
        self.setFixedHeight(target_h)
        QApplication.processEvents()
        
        # Unlock constraints so user/system can freely expand
        self.setMaximumHeight(16777215)
        self.setMinimumHeight(0)

    def _on_arm_toggled(self, armed: bool) -> None:
        self.hotkey_manager.set_space_sync_enabled(armed)

    # --- MIDI Ports ---
    def _refresh_midi_ports(self) -> None:
        ports = self.midi_manager.get_ports()
        self.midi_port_combo.blockSignals(True)
        self.midi_port_combo.clear()
        if not ports:
            self.midi_port_combo.addItem("No MIDI Devices Connected", None)
        else:
            for p in ports:
                self.midi_port_combo.addItem(p, p)
            # Open first port by default if none active
            if self.midi_manager.current_port_name is None:
                self.midi_manager.open_port(0)
        self.midi_port_combo.blockSignals(False)

    def _on_ports_changed(self, ports: List[str]) -> None:
        QTimer.singleShot(0, self._refresh_midi_ports)

    def _on_port_selected(self, index: int) -> None:
        port_name = self.midi_port_combo.currentData()
        if port_name:
            self.midi_manager.open_port(port_name)

    # --- Audio Devices ---
    def _refresh_audio_devices(self) -> None:
        devices = self.audio_engine.get_output_devices()
        self.audio_device_combo.blockSignals(True)
        self.audio_device_combo.clear()
        
        current_idx = self.audio_engine.current_device_index
        selected_combo_idx = 0

        for combo_idx, (dev_idx, dev_name, is_wasapi) in enumerate(devices):
            self.audio_device_combo.addItem(dev_name, dev_idx)
            if dev_idx == current_idx:
                selected_combo_idx = combo_idx

        if devices:
            self.audio_device_combo.setCurrentIndex(selected_combo_idx)

        self.audio_device_combo.blockSignals(False)

    def _on_audio_device_selected(self, index: int) -> None:
        dev_idx = self.audio_device_combo.currentData()
        if dev_idx is not None:
            self.audio_engine.set_output_device(dev_idx)

    def _on_mute_synth_toggled(self, checked: bool) -> None:
        self.synth_muted = checked
        if checked:
            self.audio_engine.all_notes_off()

    # --- Transport & Recording ---
    def _on_record_toggled(self, active: bool) -> None:
        if active:
            self.recorded_events.clear()
            self.piano_roll.clear()
            self.clock.start_recording()
        else:
            self.clock.stop()
            self._on_recording_stopped()

    def _on_space_toggled(self) -> None:
        is_rec = self.clock.state in (TransportState.COUNT_IN, TransportState.RECORDING)
        self.transport_bar.record_btn.setChecked(not is_rec)

    def _toggle_arm_hotkey(self) -> None:
        self.transport_bar.arm_btn.setChecked(not self.transport_bar.arm_btn.isChecked())

    def _on_recording_stopped(self) -> None:
        if self.recorded_events:
            self.quantize_and_copy()
        else:
            self.transport_bar.set_status("IDLE", "IDLE")

    def _quantize_buffer(self) -> None:
        self.current_quantized_chords = self.quantizer.process_raw_events(
            events=self.recorded_events,
            record_start_time=self.clock.record_start_time,
            bpm=self.clock.bpm,
            latency_offset_ms=self.clock.latency_offset_ms
        )
        measure_ticks = int((self.clock.time_sig_num * PPQ * 4) / self.clock.time_sig_den)
        self.piano_roll.set_data(self.current_quantized_chords, measure_ticks)

    def quantize_and_copy(self) -> None:
        """Quantizes active buffer, serializes to MuseScore XML, and copies to OS clipboard."""
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
            self.transport_bar.set_status("COPIED TO CLIPBOARD", "COPIED")
            # Auto-revert status pill to IDLE after 2 seconds
            QTimer.singleShot(2500, lambda: self.transport_bar.set_status("IDLE", "IDLE"))

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

    def _on_grid_changed(self, grid: QuantizeGrid) -> None:
        self.quantizer.grid = grid

    def _on_mode_changed(self, index: int) -> None:
        mode = self.mode_combo.currentData()
        if isinstance(mode, RecordingMode):
            self.quantizer.mode = mode

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

    def _on_latency_slider_changed(self, val: int) -> None:
        self.clock.set_latency_offset_ms(float(val))
        self.latency_val_label.setText(f"{val:+d} ms")

    def _on_sync_delay_changed(self, val: int) -> None:
        self.clock.set_sync_delay_ms(float(val))

    def _on_count_in_changed(self, index: int) -> None:
        bars = self.count_in_combo.currentData()
        if isinstance(bars, int):
            self.clock.set_count_in_bars(bars)

    def closeEvent(self, event) -> None:
        self.clock.stop()
        self.audio_engine.stop()
        self.midi_manager.close_port()
        self.midi_manager.stop_hotplug_monitor()
        self.hotkey_manager.stop()
        event.accept()
