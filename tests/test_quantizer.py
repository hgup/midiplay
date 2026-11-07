import unittest
from midiplay.core.midi_manager import RawMidiEvent
from midiplay.core.quantizer import Quantizer, QuantizeGrid, RecordingMode, PPQ


class TestQuantizer(unittest.TestCase):
    def setUp(self):
        self.quantizer = Quantizer(
            grid=QuantizeGrid.SIXTEENTH,
            mode=RecordingMode.CHORDS_AND_LEAD,
            chord_window_ms=40.0,
            legato_trim_threshold_ms=160.0
        )

    def test_chord_clustering(self):
        # 3 notes struck nearly simultaneously (within 20ms of each other)
        # Pitch 60 at t=1.000, Pitch 64 at t=1.015, Pitch 67 at t=1.020
        events = [
            RawMidiEvent("note_on", 60, 90, 1.000),
            RawMidiEvent("note_on", 64, 85, 1.015),
            RawMidiEvent("note_on", 67, 88, 1.020),
            RawMidiEvent("note_off", 60, 0, 1.480),
            RawMidiEvent("note_off", 64, 0, 1.500),
            RawMidiEvent("note_off", 67, 0, 1.510),
        ]

        # BPM = 120 -> 1 beat (480 ticks) = 0.500 sec
        chords = self.quantizer.process_raw_events(
            events=events,
            record_start_time=1.000,
            bpm=120.0
        )

        # Should be grouped into exactly 1 chord with 3 pitches
        self.assertEqual(len(chords), 1)
        self.assertEqual(sorted(chords[0].pitches), [60, 64, 67])
        self.assertEqual(chords[0].start_tick, 0)
        # Duration ~0.5s -> ~480 ticks (quarter note)
        self.assertEqual(chords[0].duration_ticks, PPQ)

    def test_legato_overlap_trimming(self):
        # Melody note 1: C4 (60) from t=1.0 to t=1.55
        # Melody note 2: D4 (62) struck at t=1.50 (50ms overlap due to sloppy finger release)
        # Note 2 releases at t=2.00
        events = [
            RawMidiEvent("note_on", 60, 90, 1.000),
            RawMidiEvent("note_on", 62, 90, 1.500),
            RawMidiEvent("note_off", 60, 0, 1.550), # Released 50ms AFTER note 2 started
            RawMidiEvent("note_off", 62, 0, 2.000),
        ]

        chords = self.quantizer.process_raw_events(
            events=events,
            record_start_time=1.000,
            bpm=120.0
        )

        # In Chords & Lead mode, the accidental 50ms overlap should be trimmed
        # So note 1 ends exactly where note 2 begins without overlapping chords
        self.assertEqual(len(chords), 2)
        self.assertEqual(chords[0].pitches, [60])
        self.assertEqual(chords[1].pitches, [62])
        # Note 1 start=0, duration=480 ticks (0.5s)
        self.assertEqual(chords[0].start_tick, 0)
        self.assertEqual(chords[0].duration_ticks, PPQ)
        # Note 2 start=480, duration=480 ticks
        self.assertEqual(chords[1].start_tick, PPQ)
        self.assertEqual(chords[1].duration_ticks, PPQ)


if __name__ == "__main__":
    unittest.main()
