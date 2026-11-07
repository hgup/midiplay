"""
MuseScore 4 Native Clipboard Serialization and OLE System Clipboard Injection.
Serializes musical phrases into verified MuseScore 4 <StaffList> schema
under 'application/musescore/stafflist' with persistent Windows OLE flushing.
"""

from __future__ import annotations
import ctypes
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Optional

from PyQt6.QtCore import QMimeData, QByteArray
from PyQt6.QtGui import QGuiApplication

from midiplay.core.musical_parser import MeasureData, NotationElement
from midiplay.core.tpc import TpcCalculator

MIME_TYPE_STAFFLIST = "application/musescore/stafflist"
MIME_TYPE_MUSESCORE_XML = "application/x-musescore+xml"


class ClipboardExporter:
    """Serializes musical notation into MuseScore 4 StaffList XML and injects into OS clipboard."""

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
        num_measures = len(staff1_measures)
        staves_count = 2 if staff2_measures else 1
        len_attr = f"{num_measures * time_sig_num}/{time_sig_den}"

        root = ET.Element(
            "StaffList",
            version=musescore_version,
            tick="0/1",
            len=len_attr,
            staff="0",
            staves=str(staves_count)
        )

        # Staff 1 (Staff id="0" in MuseScore 4 clipboard)
        cls._append_staff_elements(root, staff_id=0, measures=staff1_measures, key_accidentals=key_accidentals)

        # Optional Staff 2 (Bass clef in Grand Staff: Staff id="1")
        if staff2_measures:
            cls._append_staff_elements(root, staff_id=1, measures=staff2_measures, key_accidentals=key_accidentals)

        xml_str = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(xml_str)
        return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    @classmethod
    def _append_staff_elements(
        cls,
        root_elem: ET.Element,
        staff_id: int,
        measures: List[MeasureData],
        key_accidentals: int
    ) -> None:
        staff = ET.SubElement(root_elem, "Staff", id=str(staff_id))

        # Default voice offset
        voice_offset = ET.SubElement(staff, "voiceOffset")
        voice_elem = ET.SubElement(voice_offset, "voice", id="0")
        voice_elem.text = "0"

        tie_counter = 1

        for m_data in measures:
            for elem in m_data.elements:
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
        """Injects native MuseScore 4 payload into OS clipboard with OLE persistence."""
        app = QGuiApplication.instance()
        if not app:
            print("[ClipboardExporter] No active QGuiApplication instance found.")
            return False

        clipboard = QGuiApplication.clipboard()
        mime_data = QMimeData()

        raw_bytes = xml_content.encode("utf-8")

        # Native MuseScore 4 format (verified working!)
        mime_data.setData(MIME_TYPE_STAFFLIST, QByteArray(raw_bytes))

        # Backward compatibility format
        mime_data.setData(MIME_TYPE_MUSESCORE_XML, QByteArray(raw_bytes))

        # Text format for debugging / inspection
        mime_data.setText(xml_content)

        clipboard.setMimeData(mime_data)

        # Flush to Windows OLE clipboard manager so it persists in system memory
        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "ole32"):
            try:
                ctypes.windll.ole32.OleFlushClipboard()
            except Exception as e:
                print(f"[ClipboardExporter] OleFlushClipboard warning: {e}")

        print(f"[ClipboardExporter] Successfully copied {len(raw_bytes)} bytes to clipboard under '{MIME_TYPE_STAFFLIST}'.")
        return True
