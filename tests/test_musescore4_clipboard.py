import unittest
import xml.etree.ElementTree as ET
from midiplay.core.quantizer import Quantizer, QuantizedChord, PPQ, QuantizeGrid, ProcessedNote
from midiplay.core.musical_parser import MusicalParser
from midiplay.core.clipboard_exporter import ClipboardExporter

class TestMuseScore4Clipboard(unittest.TestCase):
    def test_ms4_spanner_tie_generation(self):
        # A half note at tick 1440 in 4/4 (bar ends at 1920, so 480 ticks in bar 1, 480 in bar 2)
        parser = MusicalParser(time_sig_num=4, time_sig_den=4)
        chords = [QuantizedChord(start_tick=1440, duration_ticks=960, pitches=[60])]
        measures, _ = parser.build_measures(chords)
        
        self.assertEqual(len(measures), 2)
        xml_out = ClipboardExporter.generate_musescore_xml(measures, musescore_version="4.70")
        
        root = ET.fromstring(xml_out)
        self.assertEqual(root.tag, "StaffList")
        self.assertEqual(root.attrib["version"], "4.70")
        self.assertEqual(root.attrib["len"], "8/4")
        
        # Check that Spanner Tie is present
        spanners = root.findall(".//Spanner[@type='Tie']")
        self.assertGreaterEqual(len(spanners), 2)
        
        # Check start spanner has next/location
        has_next = any(s.find("next/location/fractions") is not None for s in spanners)
        self.assertTrue(has_next)
        
        # Check stop spanner has prev/location
        has_prev = any(s.find("prev/location/fractions") is not None for s in spanners)
        self.assertTrue(has_prev)

    def test_11_measures_len_attribute(self):
        parser = MusicalParser(time_sig_num=4, time_sig_den=4)
        # 11 measures of 4 quarter notes
        chords = [QuantizedChord(t * 480, 480, [60]) for t in range(44)]
        measures, _ = parser.build_measures(chords)
        self.assertEqual(len(measures), 11)
        
        xml_out = ClipboardExporter.generate_musescore_xml(measures, musescore_version="4.70")
        root = ET.fromstring(xml_out)
        self.assertEqual(root.attrib["len"], "44/4")
        self.assertEqual(root.attrib["version"], "4.70")

    def test_overlapping_notes_no_drops(self):
        quantizer = Quantizer(grid=QuantizeGrid.SIXTEENTH)
        # Two notes: note 1 at t=0s dur=0.5s, note 2 at t=0.25s dur=0.5s at 120 bpm
        notes = [
            ProcessedNote(pitch=60, velocity=80, start_time=0.0, end_time=0.5),
            ProcessedNote(pitch=64, velocity=80, start_time=0.25, end_time=0.75),
        ]
        chords = quantizer._snap_to_grid(notes, bpm=120.0)
        self.assertEqual(len(chords), 2)
        # First chord clamped to not exceed second chord onset
        self.assertLessEqual(chords[0].duration_ticks, chords[1].start_tick - chords[0].start_tick)
        
        # Both chords must be parsed into measures without dropping chord 2
        parser = MusicalParser(4, 4)
        measures, _ = parser.build_measures(chords)
        found_pitches = []
        for m in measures:
            for el in m.elements:
                if not el.is_rest:
                    found_pitches.extend(el.pitches)
        self.assertIn(60, found_pitches)
        self.assertIn(64, found_pitches)

if __name__ == "__main__":
    unittest.main()
