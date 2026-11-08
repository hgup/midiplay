"""
Musical Quantization, Legato Overlap Trimming, and Chord Clustering.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from midiplay.core.midi_manager import RawMidiEvent

PPQ = 480  # Pulses per quarter note


class QuantizeGrid(Enum):
    QUARTER = "1/4"
    EIGHTH = "1/8"
    SIXTEENTH = "1/16"
    THIRTY_SECOND = "1/32"
    TRIPLET_QUARTER = "1/4T"
    TRIPLET_EIGHTH = "1/8T"
    TRIPLET_SIXTEENTH = "1/16T"

    @property
    def ticks(self) -> int:
        mapping = {
            QuantizeGrid.QUARTER: PPQ,              # 480
            QuantizeGrid.EIGHTH: PPQ // 2,          # 240
            QuantizeGrid.SIXTEENTH: PPQ // 4,       # 120
            QuantizeGrid.THIRTY_SECOND: PPQ // 8,   # 60
            QuantizeGrid.TRIPLET_QUARTER: (PPQ * 2) // 3,    # 320
            QuantizeGrid.TRIPLET_EIGHTH: (PPQ) // 3,         # 160
            QuantizeGrid.TRIPLET_SIXTEENTH: (PPQ // 2) // 3, # 80
        }
        return mapping[self]


class RecordingMode(Enum):
    CHORDS_AND_LEAD = "chords_and_lead"
    STRICT_LEAD = "strict_lead"
    POLYPHONIC = "polyphonic"


@dataclass
class ProcessedNote:
    pitch: int
    velocity: int
    start_time: float   # seconds relative to record_start
    end_time: float     # seconds relative to record_start


@dataclass
class QuantizedChord:
    start_tick: int
    duration_ticks: int
    pitches: List[int]
    velocities: List[int] = field(default_factory=list)
    is_tie_continuation: bool = False
    prev_tie_ticks: int = 0
    is_triplet: bool = False


class Quantizer:
    """Transforms raw MIDI stream into clean, quantized musical chords/notes."""

    def __init__(
        self,
        grid: QuantizeGrid = QuantizeGrid.SIXTEENTH,
        mode: RecordingMode = RecordingMode.CHORDS_AND_LEAD,
        chord_window_ms: float = 40.0,
        legato_trim_threshold_ms: float = 160.0
    ):
        self.grid = grid
        self.mode = mode
        self.chord_window_ms = chord_window_ms
        self.legato_trim_threshold_ms = legato_trim_threshold_ms

    def process_raw_events(
        self,
        events: List[RawMidiEvent],
        record_start_time: float,
        bpm: float,
        latency_offset_ms: float = 0.0
    ) -> List[QuantizedChord]:
        if not events:
            return []

        # 1. Pair Note On and Note Off with Sustain pedal resolution
        raw_notes = self._pair_note_events(events, record_start_time, latency_offset_ms)
        if not raw_notes:
            return []

        # 2. Apply recording mode heuristics (Overlap trimming & Chord clustering)
        cleaned_notes = self._clean_overlaps_and_chords(raw_notes)

        # 3. Snap onsets and durations to rhythmic grid
        quantized_chords = self._snap_to_grid(cleaned_notes, bpm)

        return quantized_chords

    def _pair_note_events(
        self,
        events: List[RawMidiEvent],
        start_time: float,
        latency_offset_ms: float
    ) -> List[ProcessedNote]:
        latency_sec = latency_offset_ms / 1000.0
        active_notes: Dict[int, List[RawMidiEvent]] = {}  # pitch -> list of note_on
        sustain_down = False
        sustain_held_releases: List[tuple[int, float]] = []  # (pitch, release_time)
        completed_notes: List[ProcessedNote] = []

        for ev in events:
            t = ev.timestamp - start_time - latency_sec
            if t < 0:
                t = 0.0

            if ev.event_type == "sustain":
                sustain_down = (ev.velocity >= 64)
                if not sustain_down:
                    # Flush notes released while pedal was held
                    for pitch, rel_time in sustain_held_releases:
                        if pitch in active_notes and active_notes[pitch]:
                            on_ev = active_notes[pitch].pop(0)
                            on_t = on_ev.timestamp - start_time - latency_sec
                            completed_notes.append(ProcessedNote(pitch, on_ev.velocity, max(0.0, on_t), max(on_t + 0.05, t)))
                    sustain_held_releases.clear()

            elif ev.event_type == "note_on":
                # If note already active, close it out (retrigger)
                if ev.pitch in active_notes and active_notes[ev.pitch]:
                    prev = active_notes[ev.pitch].pop(0)
                    prev_t = prev.timestamp - start_time - latency_sec
                    completed_notes.append(ProcessedNote(ev.pitch, prev.velocity, max(0.0, prev_t), max(prev_t + 0.05, t)))

                active_notes.setdefault(ev.pitch, []).append(ev)

            elif ev.event_type == "note_off":
                if ev.pitch in active_notes and active_notes[ev.pitch]:
                    if sustain_down:
                        sustain_held_releases.append((ev.pitch, t))
                    else:
                        on_ev = active_notes[ev.pitch].pop(0)
                        on_t = on_ev.timestamp - start_time - latency_sec
                        completed_notes.append(ProcessedNote(ev.pitch, on_ev.velocity, max(0.0, on_t), max(on_t + 0.03, t)))

        # Flush any remaining unclosed notes
        fallback_end = (events[-1].timestamp - start_time - latency_sec) + 0.2 if events else 1.0
        for pitch, note_list in active_notes.items():
            for on_ev in note_list:
                on_t = on_ev.timestamp - start_time - latency_sec
                completed_notes.append(ProcessedNote(pitch, on_ev.velocity, max(0.0, on_t), max(on_t + 0.1, fallback_end)))

        completed_notes.sort(key=lambda n: n.start_time)
        return completed_notes

    def _clean_overlaps_and_chords(self, notes: List[ProcessedNote]) -> List[ProcessedNote]:
        if not notes:
            return []

        chord_win_sec = self.chord_window_ms / 1000.0
        legato_thresh_sec = self.legato_trim_threshold_ms / 1000.0

        if self.mode == RecordingMode.STRICT_LEAD:
            # Strictly monophonic: each note ends when next note starts
            for i in range(len(notes) - 1):
                next_start = notes[i + 1].start_time
                if notes[i].end_time > next_start:
                    notes[i].end_time = max(notes[i].start_time + 0.03, next_start)
            return notes

        if self.mode == RecordingMode.POLYPHONIC:
            # Keep raw durations without trimming
            return notes

        # Mode: CHORDS_AND_LEAD
        # 1. Detect chord clusters (notes starting within chord_win_sec)
        clusters: List[List[ProcessedNote]] = []
        current_cluster: List[ProcessedNote] = [notes[0]]

        for n in notes[1:]:
            cluster_start = current_cluster[0].start_time
            if (n.start_time - cluster_start) <= chord_win_sec:
                current_cluster.append(n)
            else:
                clusters.append(current_cluster)
                current_cluster = [n]
        if current_cluster:
            clusters.append(current_cluster)

        # 2. Unify onset and duration within each chord cluster
        cleaned: List[ProcessedNote] = []
        for cluster in clusters:
            base_start = cluster[0].start_time
            # Median end time to reject early/late finger releases in a chord
            sorted_ends = sorted([n.end_time for n in cluster])
            unified_end = sorted_ends[len(sorted_ends) // 2]
            if unified_end <= base_start:
                unified_end = base_start + 0.1

            for n in cluster:
                cleaned.append(ProcessedNote(
                    pitch=n.pitch,
                    velocity=n.velocity,
                    start_time=base_start,
                    end_time=unified_end
                ))

        # 3. Legato overlap trimming between consecutive clusters
        for i in range(len(clusters) - 1):
            curr_c = clusters[i]
            next_c = clusters[i + 1]
            next_start = next_c[0].start_time

            for n in curr_c:
                # If note extends past next note's onset
                if n.end_time > next_start:
                    overlap = n.end_time - next_start
                    # If it's a transient legato overlap, trim it
                    if overlap <= legato_thresh_sec or True:
                        n.end_time = max(n.start_time + 0.03, next_start)

        return cleaned

    def _snap_to_grid(self, notes: List[ProcessedNote], bpm: float) -> List[QuantizedChord]:
        if not notes:
            return []

        grid_ticks = self.grid.ticks
        seconds_per_tick = (60.0 / bpm) / PPQ

        # Group directly by snapped_tick so simultaneous notes coalesce into single chords
        grid_buckets: Dict[int, List[ProcessedNote]] = {}
        for n in notes:
            raw_start_tick = n.start_time / seconds_per_tick
            snapped_tick = int(round(raw_start_tick / grid_ticks) * grid_ticks)
            grid_buckets.setdefault(snapped_tick, []).append(n)

        chords: List[QuantizedChord] = []
        for snapped_start_tick in sorted(grid_buckets.keys()):
            group = grid_buckets[snapped_start_tick]
            pitches = sorted(list(set(n.pitch for n in group)))
            velocities = [n.velocity for n in group]

            raw_duration_sec = max(n.end_time - n.start_time for n in group)
            raw_dur_tick = raw_duration_sec / seconds_per_tick
            snapped_dur_tick = max(grid_ticks, int(round(raw_dur_tick / grid_ticks) * grid_ticks))

            is_triplet_grid = self.grid in (QuantizeGrid.TRIPLET_QUARTER, QuantizeGrid.TRIPLET_EIGHTH, QuantizeGrid.TRIPLET_SIXTEENTH)
            chords.append(QuantizedChord(
                start_tick=snapped_start_tick,
                duration_ticks=snapped_dur_tick,
                pitches=pitches,
                velocities=velocities,
                is_triplet=is_triplet_grid
            ))

        # Clamp durations of consecutive chords so they do not overlap into the next chord
        for i in range(len(chords) - 1):
            curr_c = chords[i]
            next_c = chords[i + 1]
            max_dur = next_c.start_tick - curr_c.start_tick
            if curr_c.duration_ticks > max_dur and max_dur > 0:
                curr_c.duration_ticks = max_dur

        return chords
