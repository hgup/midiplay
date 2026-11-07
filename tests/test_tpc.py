import unittest
from midiplay.core.tpc import TpcCalculator


class TestTpc(unittest.TestCase):
    def test_c_major_tpc(self):
        # In C major (0 accidentals)
        self.assertEqual(TpcCalculator.get_tpc(60, 0), 14)  # C4 -> 14
        self.assertEqual(TpcCalculator.get_tpc(62, 0), 16)  # D4 -> 16
        self.assertEqual(TpcCalculator.get_tpc(64, 0), 18)  # E4 -> 18
        self.assertEqual(TpcCalculator.get_tpc(65, 0), 13)  # F4 -> 13
        self.assertEqual(TpcCalculator.get_tpc(67, 0), 15)  # G4 -> 15
        self.assertEqual(TpcCalculator.get_tpc(69, 0), 17)  # A4 -> 17
        self.assertEqual(TpcCalculator.get_tpc(71, 0), 19)  # B4 -> 19

    def test_accidentals_tpc(self):
        # C# in sharp key (e.g. D major, +2)
        self.assertEqual(TpcCalculator.get_tpc(61, 2), 21)  # C# -> 21
        # Db in flat key (e.g. Ab major, -4)
        self.assertEqual(TpcCalculator.get_tpc(61, -4), 9)   # Db -> 9

        # F# in G major (+1)
        self.assertEqual(TpcCalculator.get_tpc(66, 1), 20)  # F# -> 20
        # Gb in Gb major (-6)
        self.assertEqual(TpcCalculator.get_tpc(66, -6), 8)   # Gb -> 8

    def test_key_detection(self):
        # Notes in C major: C, E, G, B
        c_major_pitches = [60, 64, 67, 71, 60, 64, 67, 60]
        detected = TpcCalculator.detect_key_signature(c_major_pitches)
        self.assertEqual(detected, 0)

        # Notes in G major: G, B, D, F#
        g_major_pitches = [67, 71, 62, 66, 67, 71, 66]
        detected_g = TpcCalculator.detect_key_signature(g_major_pitches)
        self.assertEqual(detected_g, 1)


if __name__ == "__main__":
    unittest.main()
