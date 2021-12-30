"""Offline SPDX identifier table with mechanical obligations.

This is a small, hand-maintained table of common SPDX identifiers mapped to the
obligations that matter for combining datasets. It is a mechanical lookup, not a
legal interpretation. See the README limitations section.

Obligations tracked per license:
  attribution     the license requires preserving attribution or notices
  share_alike     derivatives or the combined work must carry the same license
  non_commercial  commercial use is not permitted
  no_derivatives  modified or derived works are not permitted
  unknown         provenance or license is not established

The `unknown` obligation is never inferred as permissive. A record with no
resolvable license is treated as carrying every restrictive obligation, so it
can never silently pass a gate.
"""

from dataclasses import dataclass, field
from typing import Dict, List

# Obligation keys, declared once so callers can iterate deterministically.
OBLIGATIONS: List[str] = [
    "attribution",
    "share_alike",
    "non_commercial",
    "no_derivatives",
    "unknown",
]


@dataclass(frozen=True)
class License:
    """A license identifier and the obligations it imposes."""

    spdx_id: str
    attribution: bool = False
    share_alike: bool = False
    non_commercial: bool = False
    no_derivatives: bool = False
    unknown: bool = False

    def obligations(self) -> List[str]:
        """Return the active obligation names in declared order."""
        active = []
        for name in OBLIGATIONS:
            if getattr(self, name):
                active.append(name)
        return active


# The table. Kept short and honest. Every entry is a common identifier whose
# obligations are well established and mechanical to state.
_TABLE: Dict[str, License] = {
    "CC0-1.0": License("CC0-1.0"),
    "Unlicense": License("Unlicense"),
    "MIT": License("MIT", attribution=True),
    "BSD-2-Clause": License("BSD-2-Clause", attribution=True),
    "BSD-3-Clause": License("BSD-3-Clause", attribution=True),
    "Apache-2.0": License("Apache-2.0", attribution=True),
    "CC-BY-4.0": License("CC-BY-4.0", attribution=True),
    "CC-BY-SA-4.0": License("CC-BY-SA-4.0", attribution=True, share_alike=True),
    "GPL-3.0-only": License("GPL-3.0-only", attribution=True, share_alike=True),
    "LGPL-3.0-only": License("LGPL-3.0-only", attribution=True, share_alike=True),
    "MPL-2.0": License("MPL-2.0", attribution=True, share_alike=True),
