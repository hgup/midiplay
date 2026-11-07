import unittest
import xml.etree.ElementTree as ET
from midiplay.core.quantizer import QuantizedChord, PPQ
from midiplay.core.musical_parser import MusicalParser
from midiplay.core.clipboard_exporter import ClipboardExporter


class TestClipboardExporter(unittest.TestCase):
    def test_xml_generation(self):
        parser = MusicalParser(4, 4)
        chords = [QuantizedChord(start_tick=0, duration_ticks=PPQ, pitches=[60, 64, 67])]
        staff1_m, _ = parser.build_measures(chords)

        xml_output = ClipboardExporter.generate_musescore_xml(
            staff1_measures=staff1_m,
            key_accidentals=0,
            musescore_version="4.70",
            time_sig_num=4,
            time_sig_den=4
        )

        self.assertIn('<StaffList version="4.70"', xml_output)
        self.assertIn('<Staff id="0">', xml_output)
        self.assertIn('<Chord>', xml_output)
        self.assertIn('<pitch>60</pitch>', xml_output)
        self.assertIn('<tpc>14</tpc>', xml_output)
        self.assertIn('<pitch>64</pitch>', xml_output)
        self.assertIn('<tpc>18</tpc>', xml_output)
        self.assertIn('<pitch>67</pitch>', xml_output)
        self.assertIn('<tpc>15</tpc>', xml_output)
        self.assertIn('<Rest>', xml_output)

        # Validate that the string is well-formed XML
        root = ET.fromstring(xml_output)
        self.assertEqual(root.tag, "StaffList")
        self.assertEqual(root.attrib.get("version"), "4.70")


if __name__ == "__main__":
    unittest.main()
