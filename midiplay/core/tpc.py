"""
MuseScore Tonal Pitch Class (TPC) Calculator & Key Detection.
"""

from __future__ import annotations
from typing import Dict, List, Tuple

# Key signature definitions: (name, accidental_count: negative=flats, positive=sharps)
KEY_SIGNATURES: List[Tuple[str, int]] = [
    ("C Major / A Minor", 0),
    ("G Major (1#)", 1),
    ("D Major (2#)", 2),
    ("A Major (3#)", 3),
    ("E Major (4#)", 4),
    ("B Major (5#)", 5),
    ("F# Major (6#)", 6),
    ("C# Major (7#)", 7),
    ("F Major (1b)", -1),
    ("Bb Major (2b)", -2),
    ("Eb Major (3b)", -3),
    ("Ab Major (4b)", -4),
    ("Db Major (5b)", -5),
    ("Gb Major (6b)", -6),
    ("Cb Major (7b)", -7),
]

# Standard circle of fifths TPC values
# C = 14
# G=15, D=16, A=17, E=18, B=19, F#=20, C#=21, G#=22, D#=23, A#=24
# F=13, Bb=12, Eb=11, Ab=10, Db=9, Gb=8, Cb=7

class TpcCalculator:
    """Computes MuseScore TPC values and detects key signatures."""

    # Default TPC mapping for chromatic pitches 0-11 when accidentals >= 0 (sharp-leaning / C major)
    SHARP_TPC_MAP = {
        0: 14,  # C
        1: 21,  # C#
        2: 16,  # D
        3: 23,  # D#
        4: 18,  # E
        5: 13,  # F
        6: 20,  # F#
        7: 15,  # G
        8: 22,  # G#
        9: 17,  # A
        10: 12, # Bb (Standard in C major unless B-dominant)
        11: 19, # B
    }

    # TPC mapping for chromatic pitches 0-11 when accidentals < 0 (flat-leaning)
    FLAT_TPC_MAP = {
        0: 14,  # C
        1: 9,   # Db
        2: 16,  # D
        3: 11,  # Eb
        4: 18,  # E
        5: 13,  # F
        6: 8,   # Gb
        7: 15,  # G
        8: 10,  # Ab
        9: 17,  # A
        10: 12, # Bb
        11: 19, # B
    }

    @classmethod
    def get_tpc(cls, midi_pitch: int, key_accidentals: int = 0) -> int:
        pitch_class = midi_pitch % 12
        if key_accidentals < 0:
            return cls.FLAT_TPC_MAP[pitch_class]
        else:
            return cls.SHARP_TPC_MAP[pitch_class]

    @classmethod
    def detect_key_signature(cls, pitches: List[int]) -> int:
        """Heuristic pitch-histogram key detector returning accidental count (-7 to +7)."""
        if not pitches:
            return 0

        # Pitch class histogram
        counts = [0] * 12
        for p in pitches:
            counts[p % 12] += 1

        # Krumhansl-Schmuckler Major key profile weights
        major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]

        # Standard major keys and their accidentals
        # (tonic_pc, accidentals)
        major_keys = [
            (0, 0),    # C
            (7, 1),    # G
            (2, 2),    # D
            (9, 3),    # A
            (4, 4),    # E
            (11, 5),   # B
            (6, 6),    # F#
            (1, 7),    # C#
            (5, -1),   # F
            (10, -2),  # Bb
            (3, -3),   # Eb
            (8, -4),   # Ab
            (1, -5),   # Db
            (6, -6),   # Gb
            (11, -7),  # Cb
        ]

        best_score = -float('inf')
        best_accidentals = 0

        for tonic, acc in major_keys:
            score = 0.0
            for i in range(12):
                score += counts[(tonic + i) % 12] * major_profile[i]
            if score > best_score:
                best_score = score
                best_accidentals = acc

        return best_accidentals
