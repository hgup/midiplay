"""
Musical Measure Parsing, Rest Gap Decomposition, and Barline Splitting.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from midiplay.core.quantizer import QuantizedChord, PPQ, QuantizeGrid


@dataclass
class NotationElement:
    is_rest: bool
    duration_ticks: int
    duration_type: str        # "whole", "half", "quarter", "eighth", "16th", "32nd"
    dots: int = 0
    pitches: List[int] = field(default_factory=list)
    has_tie_start: bool = False
    has_tie_stop: bool = False
    prev_tie_ticks: int = 0
    tuplet_start: bool = False
    tuplet_stop: bool = False
    tuplet_actual_notes: int = 3
    tuplet_normal_notes: int = 2
    tuplet_base_note: str = "eighth"
    tuplet_text: str = "3" 


@dataclass
class MeasureData:
    measure_index: int
    elements: List[NotationElement] = field(default_factory=list)


class MusicalParser:
    """Parses quantized chords into strict musical measures with rests and ties."""

    DURATION_TABLE = [
        (PPQ * 4, "whole", 0),
        (PPQ * 3, "half", 1),         # Dotted half
        (PPQ * 2, "half", 0),
        (int(PPQ * 1.5), "quarter", 1),# Dotted quarter
        (PPQ, "quarter", 0),
        (int(PPQ * 0.75), "eighth", 1), # Dotted eighth
        (PPQ // 2, "eighth", 0),
        (PPQ // 4, "16th", 0),
        (PPQ // 8, "32nd", 0),
    ]

    def __init__(self, time_sig_num: int = 4, time_sig_den: int = 4, grid: Optional[QuantizeGrid] = None):
        self.time_sig_num = time_sig_num
        self.time_sig_den = time_sig_den
        # Measure duration in ticks: (num * 480 * 4) / den
        self.measure_ticks = int((time_sig_num * PPQ * 4) / time_sig_den)
        self.grid = grid

    @classmethod
    def decompose_duration(cls, total_ticks: int) -> List[Tuple[int, str, int]]:
        """Decomposes a duration into standard duration_type and dots."""
        result = []
        remaining = total_ticks

        while remaining > 0:
            matched = False
            for ticks, dtype, dots in cls.DURATION_TABLE:
                if remaining >= ticks:
                    result.append((ticks, dtype, dots))
                    remaining -= ticks
                    matched = True
                    break
            if not matched:
                # Smallest fallback (32nd note)
                result.append((remaining, "32nd", 0))
                break

        return result

    def build_measures(
        self,
        chords: List[QuantizedChord],
        split_grand_staff: bool = False,
        split_pitch: int = 60
    ) -> Tuple[List[MeasureData], Optional[List[MeasureData]]]:
        """
        Builds measure structures for Staff 1, and optionally Staff 2 (Bass).
        """
        if not chords:
            empty_m = MeasureData(0, [NotationElement(is_rest=True, duration_ticks=self.measure_ticks, duration_type="whole")])
            return [empty_m], ([empty_m] if split_grand_staff else None)

        is_triplet_grid = self.grid in (QuantizeGrid.TRIPLET_QUARTER, QuantizeGrid.TRIPLET_EIGHTH, QuantizeGrid.TRIPLET_SIXTEENTH)
        builder = self._build_triplet_staff if is_triplet_grid else self._build_single_staff

        if not split_grand_staff:
            staff1_measures = builder(chords)
            return staff1_measures, None
        else:
            staff1_chords: List[QuantizedChord] = []
            staff2_chords: List[QuantizedChord] = []

            for c in chords:
                treble_p = [p for p in c.pitches if p >= split_pitch]
                bass_p = [p for p in c.pitches if p < split_pitch]

                if treble_p:
                    staff1_chords.append(QuantizedChord(c.start_tick, c.duration_ticks, treble_p, is_triplet=c.is_triplet))
                if bass_p:
                    staff2_chords.append(QuantizedChord(c.start_tick, c.duration_ticks, bass_p, is_triplet=c.is_triplet))

            staff1_measures = builder(staff1_chords)
            staff2_measures = builder(staff2_chords)

            # Ensure both staves have identical measure counts
            max_m = max(len(staff1_measures), len(staff2_measures))
            while len(staff1_measures) < max_m:
                idx = len(staff1_measures)
                staff1_measures.append(MeasureData(idx, [NotationElement(True, self.measure_ticks, "whole")]))
            while len(staff2_measures) < max_m:
                idx = len(staff2_measures)
                staff2_measures.append(MeasureData(idx, [NotationElement(True, self.measure_ticks, "whole")]))

            return staff1_measures, staff2_measures

    def _build_triplet_staff(self, chords: List[QuantizedChord]) -> List[MeasureData]:
        if not chords:
            return [MeasureData(0, [NotationElement(is_rest=True, duration_ticks=self.measure_ticks, duration_type="whole")])]

        if self.grid == QuantizeGrid.TRIPLET_SIXTEENTH:
            sub_ticks = 80
            span_ticks = 240
            base_dtype = "16th"
            double_dtype = "eighth"
        elif self.grid == QuantizeGrid.TRIPLET_QUARTER:
            sub_ticks = 320
            span_ticks = 960
            base_dtype = "quarter"
            double_dtype = "half"
        else:  # TRIPLET_EIGHTH
            sub_ticks = 160
            span_ticks = 480
            base_dtype = "eighth"
            double_dtype = "quarter"

        last_chord = chords[-1]
        total_span_ticks = last_chord.start_tick + last_chord.duration_ticks
        num_measures = max(1, (total_span_ticks + self.measure_ticks - 1) // self.measure_ticks)

        measures: List[MeasureData] = [MeasureData(i) for i in range(num_measures)]
        chord_map = {c.start_tick: c for c in chords}

        tuplet_kwargs = {
            "tuplet_actual_notes": 3,
            "tuplet_normal_notes": 2,
            "tuplet_base_note": base_dtype,
            "tuplet_text": "3"
        }

        for m_idx in range(num_measures):
            m_start = m_idx * self.measure_ticks
            m_end = m_start + self.measure_ticks

            current_tick = m_start
            while current_tick < m_end:
                span_start = current_tick
                span_end = min(span_start + span_ticks, m_end)
                span_len = span_end - span_start

                # Chords falling in this span
                span_chords = [c for c in chords if span_start <= c.start_tick < span_end]

                if not span_chords:
                    # Empty span -> standard rest decomposition
                    for dticks, dtype, ddots in self.decompose_duration(span_len):
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=True,
                            duration_ticks=dticks,
                            duration_type=dtype,
                            dots=ddots
                        ))
                    current_tick = span_end
                    continue

                # Check if it's a single straight note that fills the span or more
                if len(span_chords) == 1 and span_chords[0].start_tick == span_start and span_chords[0].duration_ticks >= span_ticks:
                    chord = span_chords[0]
                    straight_dur = min(chord.duration_ticks, m_end - span_start)
                    straight_dur = (straight_dur // span_ticks) * span_ticks
                    if straight_dur <= 0:
                        straight_dur = span_ticks

                    for dticks, dtype, ddots in self.decompose_duration(straight_dur):
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=dticks,
                            duration_type=dtype,
                            dots=ddots,
                            pitches=chord.pitches
                        ))
                    current_tick = span_start + straight_dur
                    continue

                # Tuplet with 3 slots
                c0 = chord_map.get(span_start)
                c1 = chord_map.get(span_start + sub_ticks)
                c2 = chord_map.get(span_start + 2 * sub_ticks)

                if c0 and c0.duration_ticks >= 2 * sub_ticks:
                    # Slot 0 + 1 combined (double_dtype)
                    measures[m_idx].elements.append(NotationElement(
                        is_rest=False,
                        duration_ticks=2 * sub_ticks,
                        duration_type=double_dtype,
                        pitches=c0.pitches,
                        tuplet_start=True,
                        **tuplet_kwargs
                    ))
                    # Slot 2
                    if c2:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            pitches=c2.pitches,
                            tuplet_stop=True,
                            **tuplet_kwargs
                        ))
                    else:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=True,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            tuplet_stop=True,
                            **tuplet_kwargs
                        ))
                elif c1 and c1.duration_ticks >= 2 * sub_ticks:
                    # Slot 0 (single)
                    if c0:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            pitches=c0.pitches,
                            tuplet_start=True,
                            **tuplet_kwargs
                        ))
                    else:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=True,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            tuplet_start=True,
                            **tuplet_kwargs
                        ))
                    # Slot 1 + 2 combined
                    measures[m_idx].elements.append(NotationElement(
                        is_rest=False,
                        duration_ticks=2 * sub_ticks,
                        duration_type=double_dtype,
                        pitches=c1.pitches,
                        tuplet_stop=True,
                        **tuplet_kwargs
                    ))
                else:
                    # 3 separate slots
                    # Slot 0
                    if c0:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            pitches=c0.pitches,
                            tuplet_start=True,
                            **tuplet_kwargs
                        ))
                    else:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=True,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            tuplet_start=True,
                            **tuplet_kwargs
                        ))

                    # Slot 1
                    if c1:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            pitches=c1.pitches,
                            **tuplet_kwargs
                        ))
                    else:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=True,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            **tuplet_kwargs
                        ))

                    # Slot 2
                    if c2:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            pitches=c2.pitches,
                            tuplet_stop=True,
                            **tuplet_kwargs
                        ))
                    else:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=True,
                            duration_ticks=sub_ticks,
                            duration_type=base_dtype,
                            tuplet_stop=True,
                            **tuplet_kwargs
                        ))

                current_tick = span_end

        return measures

    def _build_single_staff(self, chords: List[QuantizedChord]) -> List[MeasureData]:
        if not chords:
            return [MeasureData(0, [NotationElement(is_rest=True, duration_ticks=self.measure_ticks, duration_type="whole")])]

        last_chord = chords[-1]
        total_span_ticks = last_chord.start_tick + last_chord.duration_ticks
        num_measures = max(1, (total_span_ticks + self.measure_ticks - 1) // self.measure_ticks)

        measures: List[MeasureData] = [MeasureData(i) for i in range(num_measures)]

        # Timeline of occupied intervals: (start_tick, end_tick, pitches)
        events = sorted(chords, key=lambda c: c.start_tick)

        current_tick = 0
        chord_idx = 0

        while current_tick < (num_measures * self.measure_ticks):
            m_idx = current_tick // self.measure_ticks
            m_start = m_idx * self.measure_ticks
            m_end = m_start + self.measure_ticks

            # Next event
            next_chord = events[chord_idx] if chord_idx < len(events) else None

            # If chord starts earlier than current_tick (due to quantization overlap), clamp to current_tick
            if next_chord is not None and next_chord.start_tick < current_tick:
                overlap = current_tick - next_chord.start_tick
                next_chord.start_tick = current_tick
                next_chord.duration_ticks = max(self.DURATION_TABLE[-1][0], next_chord.duration_ticks - overlap)

            if next_chord is not None and next_chord.start_tick == current_tick:
                # Place chord, clipping or splitting across barline if needed
                chord_end = current_tick + next_chord.duration_ticks
                if chord_end <= m_end:
                    # Fits entirely in current measure
                    slices = self.decompose_duration(next_chord.duration_ticks)
                    for i, (dticks, dtype, ddots) in enumerate(slices):
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=dticks,
                            duration_type=dtype,
                            dots=ddots,
                            pitches=next_chord.pitches,
                            has_tie_start=(i < len(slices) - 1),
                            has_tie_stop=(i > 0 or (i == 0 and next_chord.is_tie_continuation)),
                            prev_tie_ticks=(slices[i - 1][0] if i > 0 else (next_chord.prev_tie_ticks if next_chord.is_tie_continuation else 0))
                        ))
                    current_tick = chord_end
                    chord_idx += 1
                else:
                    # Crosses barline: slice up to barline, tie remainder
                    first_dur = m_end - current_tick
                    slices = self.decompose_duration(first_dur)
                    for i, (dticks, dtype, ddots) in enumerate(slices):
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=False,
                            duration_ticks=dticks,
                            duration_type=dtype,
                            dots=ddots,
                            pitches=next_chord.pitches,
                            has_tie_start=True,
                            has_tie_stop=(i > 0 or (i == 0 and next_chord.is_tie_continuation)),
                            prev_tie_ticks=(slices[i - 1][0] if i > 0 else (next_chord.prev_tie_ticks if next_chord.is_tie_continuation else 0))
                        ))
                    # Modify next_chord to continue in next measure
                    remaining_dur = chord_end - m_end
                    events[chord_idx] = QuantizedChord(
                        m_end, remaining_dur, next_chord.pitches,
                        is_tie_continuation=True,
                        prev_tie_ticks=slices[-1][0]
                    )
                    current_tick = m_end
            elif next_chord is not None and next_chord.start_tick > current_tick:
                # Gap before next chord
                gap_end = min(next_chord.start_tick, m_end)
                gap_ticks = gap_end - current_tick
                slices = self.decompose_duration(gap_ticks)
                for dticks, dtype, ddots in slices:
                    measures[m_idx].elements.append(NotationElement(
                        is_rest=True,
                        duration_ticks=dticks,
                        duration_type=dtype,
                        dots=ddots
                    ))
                current_tick = gap_end
            else:
                # No more chords: fill rest to end of bar
                gap_ticks = m_end - current_tick
                if gap_ticks > 0:
                    slices = self.decompose_duration(gap_ticks)
                    for dticks, dtype, ddots in slices:
                        measures[m_idx].elements.append(NotationElement(
                            is_rest=True,
                            duration_ticks=dticks,
                            duration_type=dtype,
                            dots=ddots
                        ))
                current_tick = m_end

        # Final pass: guarantee every measure has exactly measure_ticks duration
        dur_map = {
            "whole": PPQ * 4, "half": PPQ * 2, "quarter": PPQ,
            "eighth": PPQ // 2, "16th": PPQ // 4, "32nd": PPQ // 8
        }
        for m in measures:
            tot = 0
            for el in m.elements:
                b = dur_map.get(el.duration_type, 0)
                if el.dots == 1:
                    b = int(b * 1.5)
                tot += b
            if tot < self.measure_ticks:
                diff = self.measure_ticks - tot
                for dticks, dtype, ddots in self.decompose_duration(diff):
                    m.elements.append(NotationElement(
                        is_rest=True,
                        duration_ticks=dticks,
                        duration_type=dtype,
                        dots=ddots
                    ))

        return measures
