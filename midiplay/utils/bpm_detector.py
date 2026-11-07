import re
from typing import Optional

def detect_musescore_bpm(hwnd: int) -> Optional[int]:
    """Scans MuseScore window for tempo indicator e.g. '♩ = 120' or '120'."""
    try:
        import comtypes.client
        uia_mod = comtypes.client.GetModule("UIAutomationCore.dll")
        uia = comtypes.client.CreateObject(uia_mod.CUIAutomation, interface=uia_mod.IUIAutomation)
        root = uia.ElementFromHandle(hwnd)
        if not root:
            return None

        true_cond = uia.CreateTrueCondition()
        elem_array = root.FindAll(uia_mod.TreeScope_Descendants, true_cond)
        if not elem_array:
            return None

        # Look for pattern '♩ = 120' or '120' in name or value
        pattern = re.compile(r'(?:[♩\u2669]\s*=\s*|tempo\s*:\s*)(\d{2,3})', re.IGNORECASE)
        for i in range(elem_array.Length):
            el = elem_array.GetElement(i)
            name = el.CurrentName or ""
            m = pattern.search(name)
            if m:
                return int(m.group(1))

        # Secondary search: check elements near the top with pure digits in 30-320 range
        for i in range(elem_array.Length):
            el = elem_array.GetElement(i)
            name = (el.CurrentName or "").strip()
            if name.isdigit():
                val = int(name)
                if 30 <= val <= 300:
                    rect = el.CurrentBoundingRectangle
                    if rect.top < 200:  # In upper toolbar area
                        return val

    except Exception:
        pass
    return None
