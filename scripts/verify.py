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
        ".py",
        ".svg",
        ".toml",
        ".cff",
        ".yml",
        ".yaml",
        ".cfg",
        ".ini",
        ".txt",
        ".manifest",
        ".editorconfig",
        ".gitattributes",
        ".gitignore",
    }
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.endswith(".egg-info")]
        for name in filenames:
            ext = os.path.splitext(name)[1]
            base = name
            if ext in text_exts or base in {".editorconfig", ".gitattributes", ".gitignore"}:
                yield os.path.join(dirpath, name)


def _iter_svgs():
    """Yield paths of every .svg under docs/assets/."""
    if not os.path.isdir(ASSETS):
        return
    for dirpath, _dirnames, filenames in os.walk(ASSETS):
        for name in filenames:
            if name.endswith(".svg"):
                yield os.path.join(dirpath, name)


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def check_svg_parses():
    """Check 1: every .svg under docs/assets/ parses as XML."""
    failures = []
    for path in _iter_svgs():
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            failures.append("{0}: {1}".format(os.path.relpath(path, ROOT), exc))
    return failures


def check_no_banned_filters():
    """Check 2: no .svg contains a banned filter primitive."""
    failures = []
    for path in _iter_svgs():
        text = _read(path)
        for banned in BANNED_SVG_FILTERS:
            if banned in text:
                failures.append("{0}: contains {1}".format(os.path.relpath(path, ROOT), banned))
    return failures


def check_no_double_hyphen_in_comments():
    """Check 3: no XML comment in any .svg contains the illegal `--` sequence."""
    failures = []
    comment_re = re.compile(r"<!--(.*?)-->", re.DOTALL)
    for path in _iter_svgs():
        text = _read(path)
        for match in comment_re.finditer(text):
            if "--" in match.group(1):
                failures.append(
                    "{0}: XML comment contains '--'".format(os.path.relpath(path, ROOT))
                )
    return failures


def check_no_em_dash():
    """Check 4: no tracked text file contains U+2014, &#8212;, or &mdash;."""
    failures = []
    for path in _iter_tracked_text_files():
        # Do not flag this checker itself, which must name the forms it bans.
        if os.path.abspath(path) == os.path.abspath(__file__):
            continue
        try:
            text = _read(path)
        except (UnicodeDecodeError, OSError):
            continue
        for form in EM_DASH_FORMS:
            if form in text:
                label = "U+2014" if form == "\u2014" else form
                failures.append(
                    "{0}: contains {1}".format(os.path.relpath(path, ROOT), label)
                )
    return failures


def check_readme_no_pandoc_image_attrs():
    """Check 5: README.md has no pandoc style image attribute block."""
    failures = []
    if not os.path.isfile(README):
        return failures
    text = _read(README)
    # Match `){` then, before the closing brace, a width or height attribute.
    pattern = re.compile(r"\)\{[^}]*\b(?:width|height)\b[^}]*\}")
    if pattern.search(text):
        failures.append("README.md: pandoc style image attribute block found")
    return failures


def check_readme_no_marketing():
    """Check 6: README.md contains none of the banned marketing terms."""
    failures = []
    if not os.path.isfile(README):
        return failures
    text = _read(README).lower()
    for term in BANNED_MARKETING:
        if re.search(r"\b" + re.escape(term) + r"\b", text):
            failures.append("README.md: banned marketing term '{0}'".format(term))
    return failures


def check_svg_accessibility():
    """Check 7: every .svg carries viewBox, role=img, a <title>, and a <desc>."""
    failures = []
    for path in _iter_svgs():
        rel = os.path.relpath(path, ROOT)
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            failures.append("{0}: does not parse, cannot check a11y".format(rel))
            continue
        root = tree.getroot()
        if root.get("viewBox") is None:
            failures.append("{0}: missing viewBox".format(rel))
        if root.get("role") != "img":
            failures.append("{0}: missing role=\"img\"".format(rel))
        if root.find(".//{0}title".format(SVG_NS)) is None:
            failures.append("{0}: missing <title>".format(rel))
        if root.find(".//{0}desc".format(SVG_NS)) is None:
            failures.append("{0}: missing <desc>".format(rel))
    return failures


def _char_width_em(font_family):
    """Return the per-character em estimate for a font-family string."""
    fam = (font_family or "").lower()
    if "mono" in fam or "consolas" in fam:
        return EM_PER_CHAR_MONO
    return EM_PER_CHAR_SANS


def _text_edges(elem, inherited_family):
    """Return (y, left, right) for a <text> element, or None if not placeable."""
    try:
        x = float(elem.get("x", "0"))
        y = float(elem.get("y"))
    except (TypeError, ValueError):
        return None
    font_size = elem.get("font-size")
    if font_size is None:
        return None
    try:
        size = float(font_size)
    except ValueError:
        return None
    family = elem.get("font-family", inherited_family)
    text = "".join(elem.itertext())
