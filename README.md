## Disclosure

I used Gemini 3.8 Flash and 6 hours to build this, since its just a utility I built for myself. If you find it useful, hit yourself. Raise an issue if you found something that can improve it. But, I am waiting for Musescore to get this feature soon. Once that rolls out, this will be redundant anyway. Until then, its a good replacement.

# midiplay — MIDI to MuseScore Companion Bridge

[![Latest Release](https://img.shields.io/github/v/release/hgup/midiplay?label=Latest%20Release&color=00c853&logo=github)](https://github.com/hgup/midiplay/releases/tag/latest)
[![Windows Download](https://img.shields.io/badge/Download-Windows%20x64-0078d4?logo=windows&logoColor=white)](https://github.com/hgup/midiplay/releases/download/latest/midiplay.exe)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/hgup/midiplay/release.yml?branch=main&label=Build%20%26%20Release&logo=githubactions&logoColor=white)](https://github.com/hgup/midiplay/actions)
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![MuseScore](https://img.shields.io/badge/MuseScore-4.x%20%7C%203.x-2e68c0?logo=musescore&logoColor=white)](https://musescore.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**`midiplay`** is a lightweight, zero-latency desktop companion HUD for **MuseScore 4** (and 3.x). It lets you record phrases on your MIDI keyboard, quantizes your performance cleanly without accidental finger-overlap fragmentation, and injects native notation directly into your active MuseScore score via the Windows clipboard.

Designed as a **non-activating HUD**, `midiplay` floats over MuseScore without ever stealing your keyboard focus — so your shortcut keys and MuseScore score playback always remain instant and uninterrupted.

---

## 📥 Download for Windows

Get the latest pre-compiled build (no Python installation required):

| Asset | Description | Download |
| :--- | :--- | :--- |
| **`midiplay.exe`** | Standalone portable executable | [⬇️ **Download `midiplay.exe`**](https://github.com/hgup/midiplay/releases/download/latest/midiplay.exe) |
| **`MidiplaySync.qml`** | MuseScore 4 companion sync plugin | [⬇️ **Download `MidiplaySync.qml`**](https://github.com/hgup/midiplay/releases/download/latest/MidiplaySync.qml) |

> 🔗 You can also browse all builds on the [**Latest GitHub Release Page**](https://github.com/hgup/midiplay/releases/tag/latest).

---

## ⚡ Quickstart (3 Steps)

### Step 1: Install the MuseScore Companion Plugin
1. Download [**`MidiplaySync.qml`**](https://github.com/hgup/midiplay/releases/download/latest/MidiplaySync.qml).
2. Copy it into your MuseScore 4 Plugins directory:
   ```text
   %USERPROFILE%\Documents\MuseScore4\Plugins\
   ```
3. In MuseScore 4, go to **Plugins → Manage Plugins**, check **Midiplay Companion Sync**, and launch it from **Plugins → Midiplay Companion Sync**.

### Step 2: Launch `midiplay`
1. Download and run [**`midiplay.exe`**](https://github.com/hgup/midiplay/releases/download/latest/midiplay.exe).
2. The sleek floating HUD appears over MuseScore.
3. Click the drag handle (`⋮⋮`) to position it anywhere (e.g. right in MuseScore's top toolbar area).

### Step 3: Record and Insert Notation
1. **Select a measure** in MuseScore.
2. Click the **`IDLE`** status pill on `midiplay` — it instantly reads the exact prevailing tempo (BPM) and time signature of your selected measure!
3. Press **`Shift + Space`** to record your take.
4. Hit **`Space`** to stop — your notation is automatically quantized, formatted, and inserted directly into MuseScore!

---

## 🎹 Core Features

- **Zero-Focus Non-Activating HUD (`WS_EX_NOACTIVATE`):**
  Interact with buttons, dropdowns, and sliders on `midiplay` with your mouse while Windows focus stays permanently on MuseScore. Pressing `Space` while idle continues MuseScore score playback seamlessly without triggering clicked buttons.
- **Dynamic Window Z-Order:**
  Stays cleanly pinned on top of MuseScore while you work, but automatically recedes when you switch to other applications (e.g., browser, DAW).
- **Measure-Aware Tempo & Meter Sync:**
  Reads exact meter (e.g. `7/8`, `6/8`, `4/4`) and tempo changes throughout complex scores via the companion MuseScore plugin.
- **Intelligent "Chords & Lead" Quantization:**
  Notes struck within a 40ms micro-window are unified into a single chord. Sloppy sequential finger overlaps are automatically trimmed into clean single-voice legato transitions — preventing accidental ghost ties or voice fragmentation.
- **Native MuseScore 4 `<StaffList>` Clipboard Formatting:**
  Injects notation under `application/musescore/stafflist` (MS4) or `application/x-musescore+xml` (MS3) with persistent Windows OLE flushing.
- **Tonal Pitch Class (TPC) Enharmonic Matrix:**
  Accurate Circle-of-Fifths key signature recognition ($C=14, G=15, F=13$) preventing awkward accidental spellings.
- **Grand Staff Split (Optional):**
  Split phrases at C4 into Treble (Staff 1) and Bass (Staff 2) for two-handed piano passages.
- **Low-Latency Synth & Metronome:**
  Built-in polyphonic acoustic piano synth with WASAPI low-latency output for live monitoring, plus 4-tap latency calibration.

---

## ⌨️ Global Shortcuts & HUD Controls

| Trigger | Context | Action |
| :--- | :--- | :--- |
| **`Shift + Space`** | MuseScore Focused (ARM On) | **Start Recording** (or restart take if already recording) |
| **`Space`** | While Recording | **Stop Recording & Auto-Insert** notation into MuseScore |
| **`Space`** | While Idle | Passed directly to MuseScore to **Play / Pause score** |
| **`Ctrl + Alt + R`** | Any | Toggle **ARM** state manually |
| **`IDLE` Pill (Click)** | Toolbar | **Sync Tempo & Time Signature** from selected MuseScore measure |
| **`Insert` (Click)** | Toolbar | Quantize and paste active buffer into MuseScore |
| **BPM Badge (Scroll)** | Toolbar | Adjust tempo with mouse wheel |
| **`▼` / `▲` (Click)** | Toolbar | Open / close Settings Drawer (Piano Roll, MIDI ports, Audio, Key, Latency) |

---

## 🛠️ Running from Source (Development)

### Requirements
- Python 3.10 or higher
- Windows 10/11 (or macOS / Linux for core quantization tests)
- USB / DIN MIDI keyboard controller

### Setup
```powershell
# Clone repository
git clone https://github.com/hgup/midiplay.git
cd midiplay

# Create virtual environment & activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Run
```powershell
python -m midiplay.main
```

### Run Tests
```powershell
python -m unittest discover tests
```

### Build Standalone Executable
```powershell
python build_exe.py
```

---

## 🔄 Automated CI/CD

`midiplay` uses GitHub Actions to automatically run unit tests and compile standalone Windows binaries on every push to the `main` branch. The resulting build is continuously published to the [**`latest` Release**](https://github.com/hgup/midiplay/releases/tag/latest).

---

## 📄 License

Distributed under the [MIT License](LICENSE).

