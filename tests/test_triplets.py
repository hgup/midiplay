import unittest
from midiplay.core.quantizer import Quantizer, QuantizedChord, PPQ, QuantizeGrid, RawMidiEvent
from midiplay.core.musical_parser import MusicalParser, NotationElement, MeasureData
from midiplay.core.clipboard_exporter import ClipboardExporter

class TestTriplets(unittest.TestCase):
    def test_triplet_grid_quantization_flag(self):
        quantizer = Quantizer(grid=QuantizeGrid.TRIPLET_EIGHTH)
        events = [
            RawMidiEvent("note_on", 60, 80, 1.000),
            RawMidiEvent("note_off", 60, 0, 1.150),
        ]
        chords = quantizer.process_raw_events(events, record_start_time=1.000, bpm=120.0)
        self.assertEqual(len(chords), 1)
        self.assertTrue(chords[0].is_triplet)

    def test_triplet_measure_and_xml_export(self):
        # Beat 1 (0..480): quarter note
        # Beat 2 (480..960): 3 triplet eighths (480, 640, 800)
        # Beat 3-4 (960..1920): half note (960)
        chords = [
            QuantizedChord(start_tick=0, duration_ticks=480, pitches=[72]),
            QuantizedChord(start_tick=480, duration_ticks=160, pitches=[74], is_triplet=True),
            QuantizedChord(start_tick=640, duration_ticks=160, pitches=[76], is_triplet=True),
            QuantizedChord(start_tick=800, duration_ticks=160, pitches=[77], is_triplet=True),
            QuantizedChord(start_tick=960, duration_ticks=960, pitches=[79]),
        ]
        parser = MusicalParser(time_sig_num=4, time_sig_den=4, grid=QuantizeGrid.TRIPLET_EIGHTH)
        staff1, _ = parser.build_measures(chords)
        self.assertEqual(len(staff1), 1)
        elems = staff1[0].elements

        # Element 0: quarter note
        self.assertFalse(elems[0].is_rest)
        self.assertEqual(elems[0].duration_type, "quarter")
        self.assertFalse(elems[0].tuplet_start)

        # Elements 1..3: eighth triplet
        self.assertTrue(elems[1].tuplet_start)
        self.assertFalse(elems[1].tuplet_stop)
        self.assertEqual(elems[1].duration_type, "eighth")

        self.assertFalse(elems[2].tuplet_start)
        self.assertFalse(elems[2].tuplet_stop)
        self.assertEqual(elems[2].duration_type, "eighth")

        self.assertFalse(elems[3].tuplet_start)
        self.assertTrue(elems[3].tuplet_stop)
        self.assertEqual(elems[3].duration_type, "eighth")

        # Element 4: half note
        self.assertEqual(elems[4].duration_type, "half")
        self.assertFalse(elems[4].tuplet_stop)

        # Verify XML export
        xml = ClipboardExporter.generate_musescore_xml(
            staff1_measures=staff1,
            time_sig_num=4,
            time_sig_den=4
        )
        self.assertIn("<Tuplet>", xml)
        self.assertIn("<normalNotes>2</normalNotes>", xml)
        self.assertIn("<actualNotes>3</actualNotes>", xml)
        self.assertIn("<baseNote>eighth</baseNote>", xml)
        self.assertIn("<endTuplet/>", xml)

    def test_empty_beat_decomposes_as_standard_quarter_rest(self):
        # Only 1 triplet note on Beat 1 (at tick 0)
        chords = [
            QuantizedChord(start_tick=0, duration_ticks=160, pitches=[60], is_triplet=True),
        ]
        parser = MusicalParser(time_sig_num=4, time_sig_den=4, grid=QuantizeGrid.TRIPLET_EIGHTH)
        staff1, _ = parser.build_measures(chords)
        elems = staff1[0].elements
        
        # Beat 1 has 3 triplet slots (note + 2 triplet rests)
        self.assertTrue(elems[0].tuplet_start)
        self.assertTrue(elems[2].tuplet_stop)

        # Beats 2, 3, 4 are empty and should decompose as standard rests (half + quarter)
        rest_types = [e.duration_type for e in elems[3:] if e.is_rest]
        self.assertTrue("half" in rest_types or "quarter" in rest_types)


if __name__ == "__main__":
    unittest.main()
