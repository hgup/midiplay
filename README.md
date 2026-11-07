# midiplay — MIDI to MuseScore Clipboard Bridge

`midiplay` is a lightweight, zero-latency desktop companion utility that records real-time MIDI input from connected MIDI keyboards, intelligently quantizes the performance, eliminates accidental human finger-overlaps, and copies formatted notation directly onto your system clipboard under MuseScore's native MIME type (`application/x-musescore+xml`).

---

## 🎹 The Workflow
1. Keep MuseScore open with your score.
2. In MuseScore or `midiplay`, press **`Space`** to start play-along recording.
3. Play your phrase on your MIDI controller.
4. Hit **`Space`** to stop recording.
5. `midiplay` automatically quantizes and copies the phrase to your clipboard.
6. Click any rest or measure in MuseScore and press **`Ctrl + V`** (**`Cmd + V`** on macOS) — your notation lands instantaneously!

---

## 🚀 Key Features

- **Accidental Overlap Removal ("Chords & Lead" Mode):** Notes struck together within a 40ms micro-window are unified into a single chord. Sloppy sequential finger overlaps are automatically trimmed into clean single-voice legato transitions — preventing accidental ghost ties or voice fragmentation.
- **Direct Clipboard Injection:** Formats XML directly to `application/x-musescore+xml` so you can paste into MuseScore without exporting or opening `.mid` files.
- **Latency Calibration Wizard:** Interactive 4-tap calibration tool measures audio driver output delay and player anticipation, auto-setting compensation from -100ms to +100ms.
- **MuseScore Play-along Sync:** Global transparent Spacebar listener synchronizes recording with MuseScore's audio playback.
- **TPC & Enharmonic Matrix:** Automatic Circle-of-Fifths Tonal Pitch Class calculation ($C=14, G=15, F=13$) respecting key signatures and chromatic pitch histograms.
- **Grand Staff Split (Optional):** Split at C4 into Treble (Staff 1) and Bass (Staff 2) for two-handed piano passages.
- **Ultra-lightweight HUD:** Sleek dark-mode floating bar with expandable drawer, staying cleanly on top beside MuseScore (<50MB RAM).

---

## 🛠️ Quickstart (Run from Source)

### 1. Requirements
- Python 3.10+
- Windows, macOS, or Linux
- Connected USB/DIN MIDI Keyboard

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/hgup/midiplay.git
cd midiplay

# Create virtual environment & activate
python -m venv .venv
.venv\Scripts\activate   # On Windows
# source .venv/bin/activate # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Run
```bash
python -m midiplay.main
```

---

## ⌨️ Shortcuts & Controls

| Shortcut / Trigger | Action |
| :--- | :--- |
| **`Space`** | Start / Stop recording (synchronized with MuseScore playback) |
| **`Ctrl + Shift + C`** | Quantize and copy active phrase to MuseScore clipboard |
| **`Esc`** | Clear / Discard buffer |
| **`▼` / `▲`** | Toggle Scratchpad Drawer (Piano roll, MIDI port, Key, Latency) |

---

## 📦 Build Standalone Executable (Windows)

To package `midiplay` into a standalone, zero-install portable Windows `.exe`:

```bash
python build_exe.py
```
The executable will be generated in `dist/midiplay/midiplay.exe`.

---

## 🧪 Running Tests

```bash
python -m unittest discover tests
```
