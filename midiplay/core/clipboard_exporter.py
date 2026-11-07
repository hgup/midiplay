"""
MuseScore XML Serialization and System Clipboard Injection via QMimeData.
"""

from __future__ import annotations
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Optional

from PyQt6.QtCore import QMimeData, QByteArray
from PyQt6.QtGui import QGuiApplication

from midiplay.core.musical_parser import MeasureData, NotationElement
from midiplay.core.tpc import TpcCalculator

MIME_TYPE_MUSESCORE = "application/x-musescore+xml"


class ClipboardExporter:
    """Serializes musical notation into MuseScore XML and injects into OS clipboard."""

    @classmethod
    def generate_musescore_xml(
        cls,
        staff1_measures: List[MeasureData],
        staff2_measures: Optional[List[MeasureData]] = None,
        key_accidentals: int = 0,
        musescore_version: str = "4.40"
    ) -> str:
        root = ET.Element("museScore", version=musescore_version)
        score = ET.SubElement(root, "Score")

        # Staff 1
        cls._append_staff(score, staff_id=1, measures=staff1_measures, key_accidentals=key_accidentals)

        # Optional Staff 2 (Grand Staff)
        if staff2_measures:
            cls._append_staff(score, staff_id=2, measures=staff2_measures, key_accidentals=key_accidentals)

        xml_str = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(xml_str)
        return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    @classmethod
    def _append_staff(
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
                    ET.SubElement(rest, "durationType").text = elem.duration_type
                    if elem.dots > 0:
                        ET.SubElement(rest, "dots").text = str(elem.dots)
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
    def copy_to_clipboard(cls, xml_content: str) -> bool:
        """Injects raw byte payload into OS clipboard under application/x-musescore+xml."""
        app = QGuiApplication.instance()
        if not app:
            print("[ClipboardExporter] No active QGuiApplication instance found.")
            return False

        clipboard = QGuiApplication.clipboard()
        mime_data = QMimeData()

        # Custom MIME data for MuseScore native paste
        raw_bytes = xml_content.encode("utf-8")
        mime_data.setData(MIME_TYPE_MUSESCORE, QByteArray(raw_bytes))

        # Plain text fallback for inspection/debugging in text editors
        mime_data.setText(xml_content)

        clipboard.setMimeData(mime_data)
        print(f"[ClipboardExporter] Successfully copied {len(raw_bytes)} bytes to clipboard under '{MIME_TYPE_MUSESCORE}'.")
        return True
