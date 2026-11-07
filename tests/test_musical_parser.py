import unittest
from midiplay.core.quantizer import QuantizedChord, PPQ
from midiplay.core.musical_parser import MusicalParser


class TestMusicalParser(unittest.TestCase):
    def setUp(self):
        # 4/4 meter -> 1920 ticks per measure
        self.parser = MusicalParser(time_sig_num=4, time_sig_den=4)

    def test_single_quarter_note_padded_with_rests(self):
        # Quarter note on beat 1 (tick 0 to 480)
        chords = [QuantizedChord(start_tick=0, duration_ticks=PPQ, pitches=[60])]
        staff1_m, staff2_m = self.parser.build_measures(chords)

        self.assertEqual(len(staff1_m), 1)
        elements = staff1_m[0].elements

        # Should have: 1 chord (quarter) followed by rests adding up to 1440 ticks (quarter + half rest, or dotted half)
        self.assertFalse(elements[0].is_rest)
        self.assertEqual(elements[0].duration_type, "quarter")
        self.assertEqual(elements[0].pitches, [60])

        total_rest_ticks = sum(e.duration_ticks for e in elements if e.is_rest)
        self.assertEqual(total_rest_ticks, 1440)  # 3 beats of rests

    def test_barline_splitting_with_ties(self):
        # Note starting on beat 4 (tick 1440) and held for 2 beats (960 ticks)
        # Ends on beat 2 of measure 2 (tick 2400)
        chords = [QuantizedChord(start_tick=1440, duration_ticks=960, pitches=[60])]
        staff1_m, staff2_m = self.parser.build_measures(chords)

        # Should span 2 measures
        self.assertEqual(len(staff1_m), 2)

        # Measure 1: Rests for beats 1-3 (1440 ticks) + Note on beat 4 with tie start
        m1_elements = staff1_m[0].elements
        tied_note_m1 = m1_elements[-1]
        self.assertFalse(tied_note_m1.is_rest)
        self.assertEqual(tied_note_m1.duration_ticks, 480)
        self.assertTrue(tied_note_m1.has_tie_start)

        # Measure 2: Tied continuation on beat 1 + rests for remaining beats
        m2_elements = staff1_m[1].elements
        tied_note_m2 = m2_elements[0]
        self.assertFalse(tied_note_m2.is_rest)
        self.assertEqual(tied_note_m2.duration_ticks, 480)
        self.assertTrue(tied_note_m2.has_tie_stop)


if __name__ == "__main__":
    unittest.main()
