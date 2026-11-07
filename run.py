"""
Root runner for midiplay.
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from midiplay.main import main

if __name__ == "__main__":
    sys.exit(main())
