#!/usr/bin/env python3
"""Quality gate for corpuscustody.

Standard library only. Run from the project root as `python scripts/verify.py`.
Exit 0 when every check passes, 1 when any check fails. One line per check is
printed, then a summary line such as `verify: 8 checks, 0 failures`.

Each check corresponds to a lesson taken from a real defect. The checks are
mechanical: they never trust a report, only the parsed bytes on disk.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "docs", "assets")
README = os.path.join(ROOT, "README.md")

# Banned marketing terms for check 6. Matched case-insensitively as whole words.
BANNED_MARKETING = [
    "blazing",
    "blazingly",
    "seamless",
    "seamlessly",
    "effortless",
    "effortlessly",
    "cutting-edge",
    "state-of-the-art",
    "revolutionary",
    "game-changing",
    "game changer",
    "next-generation",
    "world-class",
    "best-in-class",
    "turnkey",
    "supercharge",
    "unleash",
    "leverage",
    "synergy",
    "robust",
    "powerful",
]

# The three forms an em dash can take (Lesson 1).
EM_DASH_FORMS = ["\u2014", "&#8212;", "&mdash;"]

# Banned SVG filter primitives (glow, shadow, noise) per the standard.
BANNED_SVG_FILTERS = ["feGaussianBlur", "feDropShadow", "feTurbulence"]

SVG_NS = "{http://www.w3.org/2000/svg}"

# Per-character width estimate in em, by font family class (Lesson 4 / check 8).
EM_PER_CHAR_SANS = 0.58
EM_PER_CHAR_MONO = 0.60


def _iter_tracked_text_files():
    """Yield paths of tracked text files under the project root.

    Skips version-control, cache, and build directories, and skips files that
    do not decode as UTF-8 text (binary assets such as .pyc).
    """
    skip_dirs = {".git", "__pycache__", "build", "dist", ".venv"}
    text_exts = {
        ".md",
