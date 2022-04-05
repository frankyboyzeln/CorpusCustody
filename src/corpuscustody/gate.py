"""The pass or refuse decision and the cleared manifest writer.

The gate takes a set of records and a purpose, evaluates compatibility, and
decides:

  PASS    no blocking findings. A cleared manifest may be emitted.
  REFUSE  at least one blocking finding. No cleared manifest is emitted.

A cleared manifest is only written on PASS. It lists every record that was
checked, its resolved SPDX identifier, and the purpose it was cleared for. The
gate refuses rather than clearing when any record's provenance is unknown,
because unknown is a blocking finding for every purpose (see compat.py).
"""

from dataclasses import dataclass
from typing import List

from .compat import Issue, SetResult, evaluate
from .manifest import Record
from .spdx import resolve

PASS = "PASS"
REFUSE = "REFUSE"


@dataclass
class GateResult:
    """The outcome of a gate decision."""

    purpose: str
    decision: str
    record_count: int
    result: SetResult

    @property
    def refused(self) -> bool:
        return self.decision == REFUSE

    @property
    def findings(self) -> List[Issue]:
        return self.result.findings

    @property
    def notes(self) -> List[Issue]:
