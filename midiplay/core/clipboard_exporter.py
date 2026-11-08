"""
MuseScore Native Clipboard Serialization and OLE System Clipboard Injection.
Supports:
- MuseScore 4.x via 'application/musescore/stafflist' with <StaffList version="4.70">
  and native <Spanner type="Tie"> representation.
- MuseScore 3.x via 'application/x-musescore+xml' with <museScore version="3.02">.
- Persistent Windows OLE clipboard flushing via OleFlushClipboard().
"""

from __future__ import annotations
import ctypes
from fractions import Fraction
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Optional

from PyQt6.QtCore import QMimeData, QByteArray
from PyQt6.QtGui import QGuiApplication

from midiplay.core.quantizer import PPQ
from midiplay.core.musical_parser import MeasureData, NotationElement
from midiplay.core.tpc import TpcCalculator

MIME_TYPE_STAFFLIST = "application/musescore/stafflist"
MIME_TYPE_MUSESCORE_XML = "application/x-musescore+xml"


class ClipboardExporter:
    """Serializes musical notation into verified MuseScore clipboard XML."""

    @classmethod
    def generate_musescore_xml(
        cls,
        staff1_measures: List[MeasureData],
        staff2_measures: Optional[List[MeasureData]] = None,
        key_accidentals: int = 0,
        musescore_version: str = "4.70",
        time_sig_num: int = 4,
        time_sig_den: int = 4
    ) -> str:
        is_ms4 = not str(musescore_version).startswith("3")
        if is_ms4:
            return cls._generate_ms4_stafflist(
                staff1_measures=staff1_measures,
                staff2_measures=staff2_measures,
                key_accidentals=key_accidentals,
                time_sig_num=time_sig_num,
                time_sig_den=time_sig_den
            )
        else:
            return cls._generate_ms3_xml(
                staff1_measures=staff1_measures,
                staff2_measures=staff2_measures,
                key_accidentals=key_accidentals,
                time_sig_num=time_sig_num,
                time_sig_den=time_sig_den
            )

    @classmethod
    def _generate_ms4_stafflist(
        cls,
        staff1_measures: List[MeasureData],
        staff2_measures: Optional[List[MeasureData]],
        key_accidentals: int,
        time_sig_num: int,
        time_sig_den: int
    ) -> str:
        num_measures = len(staff1_measures)
        staves_count = 2 if staff2_measures else 1
        len_attr = f"{num_measures * time_sig_num}/{time_sig_den}"

        root = ET.Element(
            "StaffList",
            version="4.70",
            tick="0/1",
            len=len_attr,
            staff="0",
            staves=str(staves_count)
        )

        cls._append_ms4_staff_elements(root, staff_id=0, measures=staff1_measures, key_accidentals=key_accidentals)
        if staff2_measures:
            cls._append_ms4_staff_elements(root, staff_id=1, measures=staff2_measures, key_accidentals=key_accidentals)

        xml_str = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(xml_str)
        return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    @classmethod
    def _append_ms4_staff_elements(
        cls,
        root_elem: ET.Element,
        staff_id: int,
        measures: List[MeasureData],
        key_accidentals: int
    ) -> None:
        staff = ET.SubElement(root_elem, "Staff", id=str(staff_id))

        voice_offset = ET.SubElement(staff, "voiceOffset")
        voice_elem = ET.SubElement(voice_offset, "voice", id="0")
        voice_elem.text = "0"

        whole_ticks = PPQ * 4

        for m_data in measures:
            for elem in m_data.elements:
                if elem.tuplet_start:
                    tuplet = ET.SubElement(staff, "Tuplet")
                    ET.SubElement(tuplet, "normalNotes").text = str(elem.tuplet_normal_notes)
                    ET.SubElement(tuplet, "actualNotes").text = str(elem.tuplet_actual_notes)
                    ET.SubElement(tuplet, "baseNote").text = elem.tuplet_base_note
                    num = ET.SubElement(tuplet, "Number")
                    ET.SubElement(num, "style").text = "tuplet"
                    ET.SubElement(num, "text").text = elem.tuplet_text

                if elem.is_rest:
                    rest = ET.SubElement(staff, "Rest")
                    if elem.dots > 0:
                        ET.SubElement(rest, "dots").text = str(elem.dots)
                    ET.SubElement(rest, "durationType").text = elem.duration_type
                else:
                    chord = ET.SubElement(staff, "Chord")
                    if elem.dots > 0:
                        ET.SubElement(chord, "dots").text = str(elem.dots)
                    ET.SubElement(chord, "durationType").text = elem.duration_type

                    curr_frac = Fraction(elem.duration_ticks, whole_ticks)
                    curr_frac_str = f"{curr_frac.numerator}/{curr_frac.denominator}"

                    for pitch in elem.pitches:
                        note = ET.SubElement(chord, "Note")

                        # MuseScore 4 Tie Continuation / End
                        if elem.has_tie_stop and elem.prev_tie_ticks > 0:
                            prev_frac = Fraction(elem.prev_tie_ticks, whole_ticks)
                            sp_prev = ET.SubElement(note, "Spanner", type="Tie")
                            prev_node = ET.SubElement(sp_prev, "prev")
                            loc_prev = ET.SubElement(prev_node, "location")
                            ET.SubElement(loc_prev, "fractions").text = f"-{prev_frac.numerator}/{prev_frac.denominator}"

                        # MuseScore 4 Tie Start
                        if elem.has_tie_start:
                            sp_next = ET.SubElement(note, "Spanner", type="Tie")
                            tie_node = ET.SubElement(sp_next, "Tie")
                            ET.SubElement(tie_node, "ticks_f").text = curr_frac_str
                            next_node = ET.SubElement(sp_next, "next")
                            loc_next = ET.SubElement(next_node, "location")
                            ET.SubElement(loc_next, "fractions").text = curr_frac_str

                        ET.SubElement(note, "pitch").text = str(pitch)
                        ET.SubElement(note, "tpc").text = str(TpcCalculator.get_tpc(pitch, key_accidentals))

                if elem.tuplet_stop:
                    ET.SubElement(staff, "endTuplet")

    @classmethod
    def _generate_ms3_xml(
        cls,
        staff1_measures: List[MeasureData],
        staff2_measures: Optional[List[MeasureData]],
        key_accidentals: int,
        time_sig_num: int,
        time_sig_den: int
    ) -> str:
        root = ET.Element("museScore", version="3.02")
        score = ET.SubElement(root, "Score")

        cls._append_ms3_staff(score, staff_id=1, measures=staff1_measures, key_accidentals=key_accidentals)
        if staff2_measures:
            cls._append_ms3_staff(score, staff_id=2, measures=staff2_measures, key_accidentals=key_accidentals)

        xml_str = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(xml_str)
        return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    @classmethod
    def _append_ms3_staff(
        cls,
        score_elem: ET.Element,
        staff_id: int,
        measures: List[MeasureData],
        key_accidentals: int
    ) -> None:
        staff = ET.SubElement(score_elem, "Staff", id=str(staff_id))
        tie_counter = 1

        for m_data in measures:
            measure = ET.SubElement(staff, "Measure")
            voice = ET.SubElement(measure, "voice")

            for elem in m_data.elements:
                if elem.is_rest:
                    rest = ET.SubElement(voice, "Rest")
                    if elem.dots > 0:
                        ET.SubElement(rest, "dots").text = str(elem.dots)
                    ET.SubElement(rest, "durationType").text = elem.duration_type
                else:
                    chord = ET.SubElement(voice, "Chord")
                    if elem.dots > 0:
                        ET.SubElement(chord, "dots").text = str(elem.dots)
                    ET.SubElement(chord, "durationType").text = elem.duration_type

                    for pitch in elem.pitches:
                        note = ET.SubElement(chord, "Note")
                        if elem.has_tie_start:
                            tie = ET.SubElement(note, "Tie")
                            tie.set("id", str(tie_counter))
                            tie_counter += 1
                        ET.SubElement(note, "pitch").text = str(pitch)
                        ET.SubElement(note, "tpc").text = str(TpcCalculator.get_tpc(pitch, key_accidentals))

    @classmethod
    def copy_to_clipboard(cls, xml_content: str, is_musescore_4: bool = True) -> bool:
        """Injects native MuseScore payload into OS clipboard with OLE persistence."""
        app = QGuiApplication.instance()
        if not app:
            print("[ClipboardExporter] No active QGuiApplication instance found.")
            return False

        clipboard = QGuiApplication.clipboard()
        mime_data = QMimeData()

        raw_bytes = xml_content.encode("utf-8")

        if is_musescore_4:
            # Native MuseScore 4 format (strict application/musescore/stafflist)
            mime_data.setData(MIME_TYPE_STAFFLIST, QByteArray(raw_bytes))
        else:
            # Legacy MuseScore 3 XML format
            mime_data.setData(MIME_TYPE_MUSESCORE_XML, QByteArray(raw_bytes))

        # Plain text representation for external diagnostics
        mime_data.setText(xml_content)

        clipboard.setMimeData(mime_data)

        # Flush to Windows OLE clipboard manager so it persists in system memory
        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "ole32"):
            try:
                ctypes.windll.ole32.OleFlushClipboard()
            except Exception as e:
                print(f"[ClipboardExporter] OleFlushClipboard warning: {e}")

        used_mime = MIME_TYPE_STAFFLIST if is_musescore_4 else MIME_TYPE_MUSESCORE_XML
        print(f"[ClipboardExporter] Successfully copied {len(raw_bytes)} bytes to clipboard under '{used_mime}'.")
        return True
