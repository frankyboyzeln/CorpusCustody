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
