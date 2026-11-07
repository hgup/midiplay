"""
Low-latency audio engine using sounddevice and numpy.
Generates metronome clicks and lightweight polyphonic preview synthesis.
"""

from __future__ import annotations
import math
import threading
from typing import Dict, List, Optional
import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None


class Voice:
    """Represents an active playing note in the synth."""
    def __init__(self, pitch: int, velocity: int, sample_rate: int):
        self.pitch = pitch
        self.freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
        self.velocity = velocity / 127.0
        self.sample_rate = sample_rate
        self.phase = 0.0
        self.active = True
        self.released = False
        self.release_decay = 1.0

    def render(self, frames: int) -> np.ndarray:
        if not self.active:
            return np.zeros(frames, dtype=np.float32)

        t = np.arange(frames, dtype=np.float32)
        phase_increment = 2.0 * math.pi * self.freq / self.sample_rate
        phases = self.phase + t * phase_increment
        self.phase = (phases[-1] + phase_increment) % (2.0 * math.pi)

        # Warm electric piano timbre: Fundamental + 2nd & 3rd harmonics
        signal = (
            0.6 * np.sin(phases) +
            0.25 * np.sin(2.0 * phases) +
            0.15 * np.sin(3.0 * phases)
        )

        if self.released:
            decay_curve = np.linspace(self.release_decay, self.release_decay * 0.01, frames, dtype=np.float32)
            self.release_decay *= 0.01
            if self.release_decay < 0.001:
                self.active = False
            return signal * self.velocity * decay_curve
        else:
            return signal * self.velocity * 0.7


class AudioEngine:
    """Manages audio output stream for metronome clicks and phrase preview."""

    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.stream: Optional[sd.OutputStream] = None
        self._lock = threading.Lock()

        # Metronome click queue
        self.metronome_muted = False
        self._click_buffers: List[np.ndarray] = []

        # Pre-synthesize downbeat and regular clicks (exponential decay)
        self.downbeat_click = self._generate_click(1760.0, 0.035, 0.9)
        self.subbeat_click = self._generate_click(880.0, 0.025, 0.6)

        # Active synth voices: pitch -> Voice
        self.active_voices: Dict[int, Voice] = {}
        
        self.is_running = False

    def _generate_click(self, freq: float, duration_sec: float, amp: float) -> np.ndarray:
        num_samples = int(self.sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False, dtype=np.float32)
        sine = np.sin(2.0 * math.pi * freq * t)
        envelope = np.exp(-t * (1.0 / (duration_sec * 0.25)))
        return (sine * envelope * amp).astype(np.float32)

    def start(self) -> bool:
        if sd is None:
            print("[AudioEngine] sounddevice library not installed.")
            return False

        if self.is_running:
            return True

        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                channels=1,
                dtype=np.float32,
                callback=self._audio_callback,
                latency='low'
            )
            self.stream.start()
            self.is_running = True
            return True
        except Exception as e:
            print(f"[AudioEngine] Failed to start audio output stream: {e}")
            self.is_running = False
            return False

    def stop(self) -> None:
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def trigger_click(self, is_downbeat: bool = False) -> None:
        """Trigger an instantaneous low-latency metronome click."""
        if self.metronome_muted:
            return
        click = self.downbeat_click.copy() if is_downbeat else self.subbeat_click.copy()
        with self._lock:
            self._click_buffers.append(click)

    def note_on(self, pitch: int, velocity: int) -> None:
        """Start playing a synth note for live monitoring or preview."""
        if velocity <= 0:
            self.note_off(pitch)
            return

        with self._lock:
            self.active_voices[pitch] = Voice(pitch, velocity, self.sample_rate)

    def note_off(self, pitch: int) -> None:
        """Release an active synth note."""
        with self._lock:
            if pitch in self.active_voices:
                self.active_voices[pitch].released = True

    def all_notes_off(self) -> None:
        with self._lock:
            for voice in self.active_voices.values():
                voice.released = True
            self._click_buffers.clear()

    def set_metronome_muted(self, muted: bool) -> None:
        self.metronome_muted = muted

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        buffer = np.zeros(frames, dtype=np.float32)

        with self._lock:
            # 1. Mix active click samples
            remaining_clicks = []
            for click in self._click_buffers:
                if len(click) <= frames:
                    buffer[:len(click)] += click
                else:
                    buffer += click[:frames]
                    remaining_clicks.append(click[frames:])
            self._click_buffers = remaining_clicks

            # 2. Mix active synth voices
            dead_pitches = []
            for pitch, voice in self.active_voices.items():
                if voice.active:
                    buffer += voice.render(frames)
                else:
                    dead_pitches.append(pitch)

            for p in dead_pitches:
                del self.active_voices[p]

        # Soft clipping / limiter to prevent harsh distortion
        np.clip(buffer, -0.98, 0.98, out=buffer)
        outdata[:, 0] = buffer
