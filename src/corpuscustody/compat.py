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
    },
}

_MESSAGES: Dict[str, str] = {
    "unknown": "provenance unknown, cannot clear",
    "share_alike": "share-alike terms attach to the combined set",
    "non_commercial": "non-commercial license, commercial use blocked",
    "no_derivatives": "no-derivatives license, transformation blocked",
    "attribution": "attribution must be preserved",
}


def check_purpose(purpose: str) -> str:
    """Validate and normalise a purpose string."""
    key = (purpose or "").strip().lower()
    if key not in PURPOSES:
        raise PurposeError(
            "unknown purpose {0!r}, expected one of {1}".format(
                purpose, ", ".join(PURPOSES)
            )
        )
    return key


def issues_for_license(record_id: str, lic: License, purpose: str) -> List[Issue]:
    """Return all issues a single license raises under the purpose."""
    found: List[Issue] = []
    for obligation in lic.obligations():
        severity = _RULES.get(obligation, {}).get(purpose)
        if severity is None:
            continue
        found.append(
            Issue(
                record_id=record_id,
                spdx_id=lic.spdx_id,
                obligation=obligation,
                severity=severity,
                message=_MESSAGES[obligation],
            )
        )
    return found


@dataclass
class SetResult:
    """The set level compatibility result for a manifest under a purpose."""

    purpose: str
    issues: List[Issue]

    @property
    def findings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == FINDING]
