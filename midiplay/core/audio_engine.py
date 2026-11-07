"""
Ultra-low-latency audio engine using sounddevice, WASAPI, precomputed wavetables,
natural acoustic/EP piano envelope decay, and polyphonic soft limiting.
"""

from __future__ import annotations
import math
import threading
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None

WAVETABLE_SIZE = 4096

# Precompute a warm, silky electric/acoustic piano wavetable (harmonic balance)
_t = np.linspace(0, 2.0 * math.pi, WAVETABLE_SIZE, endpoint=False, dtype=np.float32)
WAVETABLE = (
    0.70 * np.sin(_t) +
    0.20 * np.sin(2.0 * _t) +
    0.10 * np.sin(3.0 * _t)
).astype(np.float32)


class Voice:
    """Precomputed wavetable oscillator with natural acoustic/EP piano envelope."""
    __slots__ = ('pitch', 'step', 'phase', 'velocity', 'active', 'released',
                 'sample_rate', 'held_samples', 'release_env', 'peak_amp')

    def __init__(self, pitch: int, velocity: int, sample_rate: int):
        freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
        self.pitch = pitch
        self.sample_rate = sample_rate
        self.step = (freq * WAVETABLE_SIZE) / sample_rate
        self.phase = 0.0
        self.peak_amp = (velocity / 127.0) * 0.35
        self.active = True
        self.released = False
        self.held_samples = 0
        self.release_env = 1.0

    def render(self, frames: int, out_buffer: np.ndarray) -> None:
        if not self.active:
            return

        # Phase stepping into wavetable
        phases = (self.phase + np.arange(frames, dtype=np.float32) * self.step) % WAVETABLE_SIZE
        indices = phases.astype(np.int32)
        raw_wave = WAVETABLE[indices]
        self.phase = (phases[-1] + self.step) % WAVETABLE_SIZE

        # Dynamic Piano Envelope:
        # Initial attack + smooth piano string decay while held (half-life ~ 1.2 seconds)
        t_held_start = self.held_samples / self.sample_rate
        self.held_samples += frames
        t_held_end = self.held_samples / self.sample_rate
        t_held = np.linspace(t_held_start, t_held_end, frames, dtype=np.float32)

        # Smooth percussive exponential decay while held
        held_decay = np.exp(-t_held * 0.95)

        if not self.released:
            out_buffer += raw_wave * (self.peak_amp * held_decay)
        else:
            # Quick acoustic damping on key release (~80ms release)
            decay_curve = np.linspace(self.release_env, self.release_env * 0.02, frames, dtype=np.float32)
            self.release_env *= 0.02
            if self.release_env < 0.001:
                self.active = False
            out_buffer += raw_wave * (self.peak_amp * held_decay * decay_curve)


class AudioEngine:
    """Ultra-low-latency audio engine with polyphonic dynamic headroom & soft limiting."""

    def __init__(self, sample_rate: int = 48000, buffer_size: int = 128):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.stream: Optional[sd.OutputStream] = None
        self.current_device_index: Optional[int] = None
        self._lock = threading.Lock()

        # Metronome click queue
        self.metronome_muted = False
        self._click_buffers: List[np.ndarray] = []

        # Pre-synthesize clicks
        self.downbeat_click = self._generate_click(1760.0, 0.035, 0.85)
        self.subbeat_click = self._generate_click(880.0, 0.025, 0.55)

        # Active synth voices
        self.active_voices: Dict[int, Voice] = {}
        self.is_running = False

    def _generate_click(self, freq: float, duration_sec: float, amp: float) -> np.ndarray:
        num_samples = int(self.sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False, dtype=np.float32)
        sine = np.sin(2.0 * math.pi * freq * t)
        envelope = np.exp(-t * (1.0 / (duration_sec * 0.2)))
        return (sine * envelope * amp).astype(np.float32)

    @classmethod
    def get_output_devices(cls) -> List[Tuple[int, str, bool]]:
        """Returns list of (device_index, display_name, is_wasapi)."""
        if sd is None:
            return []
        try:
            devices = sd.query_devices()
            hostapis = sd.query_hostapis()
            results = []
            for i, d in enumerate(devices):
                if d['max_output_channels'] > 0:
                    api_name = hostapis[d['hostapi']]['name']
                    is_wasapi = "WASAPI" in api_name
                    tag = " [WASAPI]" if is_wasapi else f" [{api_name}]"
                    results.append((i, f"{d['name']}{tag}", is_wasapi))
            return results
        except Exception:
            return []

    def _find_best_wasapi_device(self) -> Optional[int]:
        """Finds the lowest latency WASAPI device matching default output."""
        if sd is None:
            return None
        try:
            devices = sd.query_devices()
            hostapis = sd.query_hostapis()

            wasapi_api_idx = next((i for i, a in enumerate(hostapis) if "WASAPI" in a["name"]), None)
            if wasapi_api_idx is None:
                return None

            default_out = sd.default.device[1]
            default_name = devices[default_out]["name"] if default_out >= 0 else ""

            # Match default name on WASAPI
            for i, d in enumerate(devices):
                if d["hostapi"] == wasapi_api_idx and d["max_output_channels"] > 0:
                    if d["name"] in default_name or default_name in d["name"]:
                        return i

            wasapi_def = hostapis[wasapi_api_idx]["default_output_device"]
            if wasapi_def >= 0:
                return wasapi_def
        except Exception as e:
            print(f"[AudioEngine] Error detecting WASAPI device: {e}")
        return None

    def start(self, device_index: Optional[int] = None) -> bool:
        if sd is None:
            print("[AudioEngine] sounddevice library not installed.")
            return False

        self.stop()

        target_device = device_index if device_index is not None else self._find_best_wasapi_device()
        self.current_device_index = target_device

        try:
            dev_info = sd.query_devices(target_device) if target_device is not None else None
            dev_name = dev_info['name'] if dev_info else "System Default"
            lat_ms = (dev_info.get('default_low_output_latency', 0) * 1000.0) if dev_info else 0
            print(f"[AudioEngine] Starting audio stream on device [{target_device}]: {dev_name} (latency: {lat_ms:.1f}ms)")

            self.stream = sd.OutputStream(
                device=target_device,
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
            print(f"[AudioEngine] WASAPI start failed ({e}), falling back to default device.")
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
            except Exception as e2:
                print(f"[AudioEngine] Audio initialization failed completely: {e2}")
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

    def set_output_device(self, device_index: int) -> bool:
        return self.start(device_index)

    def trigger_click(self, is_downbeat: bool = False) -> None:
        if self.metronome_muted:
            return
        click = self.downbeat_click.copy() if is_downbeat else self.subbeat_click.copy()
        with self._lock:
            self._click_buffers.append(click)

    def note_on(self, pitch: int, velocity: int) -> None:
        if velocity <= 0:
            self.note_off(pitch)
            return

        with self._lock:
            self.active_voices[pitch] = Voice(pitch, velocity, self.sample_rate)

    def note_off(self, pitch: int) -> None:
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
        synth_buffer = np.zeros(frames, dtype=np.float32)

        with self._lock:
            # 1. Render active voices
            num_active = len(self.active_voices)
            dead_pitches = []

            for pitch, voice in self.active_voices.items():
                if voice.active:
                    voice.render(frames, synth_buffer)
                else:
                    dead_pitches.append(pitch)

            for p in dead_pitches:
                del self.active_voices[p]

            # 2. Dynamic Polyphonic Headroom Scaling:
            # When playing chords (e.g. 3-6 notes), dynamically scale down by 1/sqrt(N)
            # to guarantee that polyphony never saturates into mud or distortion.
            if num_active > 1:
                scale_factor = 1.0 / math.sqrt(num_active * 0.8)
                synth_buffer *= scale_factor

            # 3. Smooth Soft Limiter (tanh saturation instead of harsh hard-clipping)
            # This produces silky acoustic warmth even on heavy fff chords
            synth_buffer = np.tanh(synth_buffer * 1.1) * 0.92

            # 4. Mix clicks (clicks bypass synth scaling so they remain crisp and audible)
            remaining_clicks = []
            for click in self._click_buffers:
                if len(click) <= frames:
                    synth_buffer[:len(click)] += click
                else:
                    synth_buffer += click[:frames]
                    remaining_clicks.append(click[frames:])
            self._click_buffers = remaining_clicks

        # Final safety clamp
        np.clip(synth_buffer, -0.98, 0.98, out=synth_buffer)
        outdata[:, 0] = synth_buffer
