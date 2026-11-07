"""
Transport Clock, Metronome Timing Thread, and Musical Subdivisions.
"""

from __future__ import annotations
import time
import threading
from typing import Callable, Optional
from enum import Enum


class TransportState(Enum):
    IDLE = "IDLE"
    COUNT_IN = "COUNT_IN"
    RECORDING = "RECORDING"
    PLAYING_PREVIEW = "PLAYING_PREVIEW"


class Clock:
    """High-precision musical transport clock decoupled from UI thread."""

    def __init__(
        self,
        bpm: float = 120.0,
        time_sig_num: int = 4,
        time_sig_den: int = 4,
        count_in_bars: int = 1,
        on_beat_callback: Optional[Callable[[int, bool, TransportState], None]] = None,
        on_state_change: Optional[Callable[[TransportState], None]] = None
    ):
        self.bpm = bpm
        self.time_sig_num = time_sig_num
        self.time_sig_den = time_sig_den
        self.count_in_bars = count_in_bars
        self.latency_offset_ms = 0.0  # -100ms to +100ms

        self.on_beat_callback = on_beat_callback
        self.on_state_change = on_state_change

        self.state = TransportState.IDLE
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Timing anchors
        self.record_start_time: float = 0.0
        self.current_beat_index: int = 0

        # Tap tempo history
        self._tap_times: list[float] = []

    def set_bpm(self, bpm: float) -> None:
        self.bpm = max(20.0, min(320.0, bpm))

    def set_time_signature(self, num: int, den: int) -> None:
        self.time_sig_num = max(1, num)
        self.time_sig_den = max(1, den)

    def set_latency_offset_ms(self, offset_ms: float) -> None:
        self.latency_offset_ms = max(-200.0, min(200.0, offset_ms))

    def register_tap(self) -> Optional[float]:
        """Tap tempo calculation. Returns computed BPM if 2+ taps within 2.5s."""
        now = time.perf_counter()
        if self._tap_times and (now - self._tap_times[-1]) > 2.5:
            self._tap_times.clear()

        self._tap_times.append(now)
        if len(self._tap_times) > 5:
            self._tap_times.pop(0)

        if len(self._tap_times) >= 2:
            intervals = [self._tap_times[i] - self._tap_times[i - 1] for i in range(1, len(self._tap_times))]
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval > 0:
                bpm = 60.0 / avg_interval
                self.set_bpm(bpm)
                return self.bpm
        return None

    def start_recording(self) -> None:
        """Starts count-in (if enabled) then transitions to recording."""
        self.stop()
        self._stop_event.clear()

        if self.count_in_bars > 0:
            self.state = TransportState.COUNT_IN
        else:
            self.state = TransportState.RECORDING
            self.record_start_time = time.perf_counter() + (self.latency_offset_ms / 1000.0)

        if self.on_state_change:
            self.on_state_change(self.state)

        self._thread = threading.Thread(target=self._clock_worker, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stops playback or recording."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        self.state = TransportState.IDLE
        if self.on_state_change:
            self.on_state_change(self.state)

    def _clock_worker(self) -> None:
        """High-resolution timing loop that calculates drift and triggers beats."""
        beat_duration = 60.0 / self.bpm
        total_count_in_beats = self.count_in_bars * self.time_sig_num
        current_beat = 0

        next_beat_time = time.perf_counter()

        while not self._stop_event.is_set():
            now = time.perf_counter()
            if now >= next_beat_time:
                # Determine downbeat
                is_downbeat = (current_beat % self.time_sig_num) == 0

                # Check transition from COUNT_IN to RECORDING
                if self.state == TransportState.COUNT_IN and current_beat >= total_count_in_beats:
                    self.state = TransportState.RECORDING
                    self.record_start_time = next_beat_time + (self.latency_offset_ms / 1000.0)
                    current_beat = 0
                    is_downbeat = True
                    if self.on_state_change:
                        self.on_state_change(self.state)

                # Fire callback
                if self.on_beat_callback:
                    self.on_beat_callback(current_beat, is_downbeat, self.state)

                current_beat += 1
                next_beat_time += beat_duration

            # Sleep tiny interval to prevent busy-wait CPU hogging while preserving <2ms jitter
            sleep_time = next_beat_time - time.perf_counter()
            if sleep_time > 0.002:
                time.sleep(sleep_time * 0.7)
            else:
                time.sleep(0.0005)
