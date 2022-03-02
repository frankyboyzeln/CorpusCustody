"""Compatibility resolution against a declared purpose.

Three purposes are recognised:

    internal   internal research use, not distributed outside the org
    commercial a commercial product, distributed, possibly proprietary
    redistribute  redistributed as a dataset or corpus to third parties

Each obligation is checked against the purpose to decide whether it produces a
finding. The rules are mechanical and intentionally conservative:

  unknown         a finding for every purpose. Unknown provenance never passes.
  non_commercial  a finding for commercial. Internal and redistribute are
                  assumed non commercial here, so it is only reported as a note.
  share_alike     a finding for commercial, because a share-alike corpus mixed
                  into a proprietary release forces the release to share alike.
                  For redistribute it is a note: the combined set must then
                  carry the share-alike terms.
  no_derivatives  a finding for commercial and redistribute, because both
                  typically transform or repackage the data. A note for
                  internal.
  attribution     never a blocking finding. It is a note: attribution must be
                  preserved.

A finding blocks the gate. A note is informational and does not block.
"""

from dataclasses import dataclass
from typing import Dict, List

from .manifest import Record
from .spdx import License, resolve

PURPOSES: List[str] = ["internal", "commercial", "redistribute"]

# severity levels
FINDING = "finding"
NOTE = "note"


class PurposeError(ValueError):
    """Raised when an unrecognised purpose is supplied."""


@dataclass(frozen=True)
class Issue:
    """A single obligation issue found for a record under a purpose."""

    record_id: str
    spdx_id: str
    obligation: str
    severity: str
    message: str


# Per obligation, per purpose severity. Missing entries mean no issue.
_RULES: Dict[str, Dict[str, str]] = {
    "unknown": {
        "internal": FINDING,
        "commercial": FINDING,
        "redistribute": FINDING,
    },
    "share_alike": {
        "commercial": FINDING,
        "redistribute": NOTE,
    },
    "non_commercial": {
        "commercial": FINDING,
    },
    "no_derivatives": {
        "commercial": FINDING,
        "redistribute": FINDING,
        "internal": NOTE,
    },
    "attribution": {
        "internal": NOTE,
        "commercial": NOTE,
        "redistribute": NOTE,
