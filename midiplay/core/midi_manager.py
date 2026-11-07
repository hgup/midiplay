"""
MIDI Device Management and Real-time Event Capture via python-rtmidi.
"""

from __future__ import annotations
import time
import threading
from dataclasses import dataclass
from typing import Callable, List, Optional
import rtmidi


@dataclass
class RawMidiEvent:
    event_type: str  # "note_on", "note_off", "sustain"
    pitch: int       # 0-127
    velocity: int    # 0-127
    timestamp: float # time.perf_counter() seconds
    channel: int = 0


class MidiManager:
    """Manages MIDI input port detection, hotplugging, and event capture."""

    def __init__(self, on_event_callback: Optional[Callable[[RawMidiEvent], None]] = None):
        self.on_event_callback = on_event_callback
        self.midi_in: Optional[rtmidi.MidiIn] = None
        self.current_port_name: Optional[str] = None
        self.current_port_index: Optional[int] = None
        
        # Hot-plug monitoring thread
        self._known_ports: List[str] = []
        self._on_ports_changed_callback: Optional[Callable[[List[str]], None]] = None
        self._monitor_running = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        self._init_midi()

    def _init_midi(self) -> None:
        try:
            self.midi_in = rtmidi.MidiIn()
            self._known_ports = self.get_ports()
        except Exception as e:
            print(f"[MidiManager] Failed to initialize MidiIn: {e}")
            self.midi_in = None

    def get_ports(self) -> List[str]:
        """Returns a list of available MIDI input port names."""
        if not self.midi_in:
            return []
        try:
            return self.midi_in.get_ports()
        except Exception:
            return []

    def open_port(self, port_identifier: int | str) -> bool:
        """Opens a MIDI input port by index or name."""
        if not self.midi_in:
            self._init_midi()
            if not self.midi_in:
                return False

        self.close_port()

        ports = self.get_ports()
        port_index = -1

        if isinstance(port_identifier, int):
            if 0 <= port_identifier < len(ports):
                port_index = port_identifier
        elif isinstance(port_identifier, str):
            for i, p in enumerate(ports):
                if p == port_identifier:
                    port_index = i
                    break

        if port_index == -1 and len(ports) > 0:
            port_index = 0  # Fallback to first available port

        if port_index >= 0 and port_index < len(ports):
            try:
                self.midi_in.open_port(port_index)
                self.midi_in.set_callback(self._on_midi_message)
                self.current_port_name = ports[port_index]
                self.current_port_index = port_index
                print(f"[MidiManager] Opened MIDI port: {self.current_port_name}")
                return True
            except Exception as e:
                print(f"[MidiManager] Error opening port {port_index}: {e}")
                return False
        return False

    def close_port(self) -> None:
        """Closes the currently active MIDI port."""
        if self.midi_in and self.midi_in.is_port_open():
            try:
                self.midi_in.close_port()
            except Exception:
                pass
        self.current_port_name = None
        self.current_port_index = None

    def _on_midi_message(self, message_data, data=None) -> None:
        """Callback executed on incoming raw MIDI bytes."""
        message, delta_time = message_data
        if not message:
            return

        now = time.perf_counter()
        status = message[0]
        cmd = status & 0xF0
        channel = status & 0x0F

        event = None

        if cmd == 0x90:  # Note On
            pitch = message[1]
            velocity = message[2] if len(message) > 2 else 0
            if velocity > 0:
                event = RawMidiEvent("note_on", pitch, velocity, now, channel)
            else:
                event = RawMidiEvent("note_off", pitch, 0, now, channel)
        elif cmd == 0x80:  # Note Off
            pitch = message[1]
            velocity = message[2] if len(message) > 2 else 0
            event = RawMidiEvent("note_off", pitch, velocity, now, channel)
        elif cmd == 0xB0:  # Control Change
            cc_num = message[1]
            cc_val = message[2] if len(message) > 2 else 0
            if cc_num == 64:  # Sustain pedal
                event = RawMidiEvent("sustain", 64, cc_val, now, channel)

        if event and self.on_event_callback:
            self.on_event_callback(event)

    def set_on_ports_changed(self, callback: Callable[[List[str]], None]) -> None:
        self._on_ports_changed_callback = callback

    def start_hotplug_monitor(self, interval_sec: float = 1.5) -> None:
        """Starts a background daemon thread to monitor MIDI port connection changes."""
        if self._monitor_running:
            return
        self._monitor_running = True

        def _monitor_loop():
            while self._monitor_running:
                time.sleep(interval_sec)
                try:
                    # Using a temporary probe instance so active streams are uninterrupted
                    probe = rtmidi.MidiIn()
                    current = probe.get_ports()
                    del probe
                    if current != self._known_ports:
                        self._known_ports = current
                        if self._on_ports_changed_callback:
                            self._on_ports_changed_callback(current)
                except Exception:
                    pass

        self._monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_hotplug_monitor(self) -> None:
        self._monitor_running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
