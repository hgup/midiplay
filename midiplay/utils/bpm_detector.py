"""
MuseScore 4 BPM / Tempo Auto-Detection via Windows UI Automation.
Optimized for non-blocking, fast retrieval.
"""

from __future__ import annotations
import re
from typing import Optional


def detect_musescore_bpm(hwnd: int) -> Optional[int]:
    """Scans MuseScore window for tempo indicator e.g. '♩ = 120' or '120'."""
    if not hwnd:
        return None

    try:
        import comtypes
        import comtypes.client

        # Ensure COM is initialized for the calling thread
        co_init = False
        try:
            comtypes.CoInitialize()
            co_init = True
        except Exception:
            pass

        try:
            uia_mod = comtypes.client.GetModule("UIAutomationCore.dll")
            uia = comtypes.client.CreateObject(uia_mod.CUIAutomation, interface=uia_mod.IUIAutomation)
            root = uia.ElementFromHandle(hwnd)
            if not root:
                return None

            # Filter for text, edit, and button controls only — avoids scanning thousands of non-text score staves
            cond_text = uia.CreatePropertyCondition(uia_mod.UIA_ControlTypePropertyId, uia_mod.UIA_TextControlTypeId)
            cond_edit = uia.CreatePropertyCondition(uia_mod.UIA_ControlTypePropertyId, uia_mod.UIA_EditControlTypeId)
            cond_btn = uia.CreatePropertyCondition(uia_mod.UIA_ControlTypePropertyId, uia_mod.UIA_ButtonControlTypeId)
            cond_custom = uia.CreatePropertyCondition(uia_mod.UIA_ControlTypePropertyId, uia_mod.UIA_CustomControlTypeId)
            cond_item = uia.CreatePropertyCondition(uia_mod.UIA_ControlTypePropertyId, uia_mod.UIA_DataItemControlTypeId)
            c1 = uia.CreateOrCondition(cond_text, cond_edit)
            c2 = uia.CreateOrCondition(c1, cond_btn)
            c3 = uia.CreateOrCondition(c2, cond_custom)
            combined_cond = uia.CreateOrCondition(c3, cond_item)

            elem_array = root.FindAll(uia_mod.TreeScope_Descendants, combined_cond)
            if not elem_array:
                return None

            pattern = re.compile(r'(?:Tempo\s+.*?=\s*|[♩\u2669\uECA0-\uECBF]\s*=\s*|tempo\s*:\s*)(\d{2,3})', re.IGNORECASE)

            # 1. Primary search: exact tempo pattern match
            count = elem_array.Length
            for i in range(count):
                try:
                    el = elem_array.GetElement(i)
                    name = el.CurrentName or ""
                    m = pattern.search(name)
                    if m:
                        return int(m.group(1))
                except Exception:
                    pass

            # 2. Secondary search: top toolbar controls with 2-3 digits in valid tempo range
            for i in range(count):
                try:
                    el = elem_array.GetElement(i)
                    name = (el.CurrentName or "").strip()
                    if name.isdigit():
                        val = int(name)
                        if 30 <= val <= 320:
                            rect = el.CurrentBoundingRectangle
                            if rect.top < 160:  # In upper playback toolbar region
                                return val
                except Exception:
                    pass

        finally:
            if co_init:
                try:
                    comtypes.CoUninitialize()
                except Exception:
                    pass

    except Exception:
        pass

    return None
