"""
Build script to compile midiplay into a standalone Windows executable via PyInstaller.
"""

import sys
import subprocess
from pathlib import Path


def build():
    print("[midiplay build] Building standalone Windows executable...")
    root = Path(__file__).parent.resolve()
    main_script = root / "midiplay" / "main.py"

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "midiplay",
        "--clean",
        str(main_script)
    ]

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=root)
    if result.returncode == 0:
        print("[midiplay build] Build succeeded! Executable located in dist/midiplay/midiplay.exe")
    else:
        print(f"[midiplay build] Build failed with return code {result.returncode}")


if __name__ == "__main__":
    build()
