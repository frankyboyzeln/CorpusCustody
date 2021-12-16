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
