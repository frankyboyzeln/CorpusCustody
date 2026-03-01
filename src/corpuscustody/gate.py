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
        return self.result.notes


def decide(records: List[Record], purpose: str) -> GateResult:
    """Run the gate over records for the declared purpose."""
    result = evaluate(records, purpose)
    decision = PASS if result.clear else REFUSE
    return GateResult(
        purpose=result.purpose,
        decision=decision,
        record_count=len(records),
        result=result,
    )


def cleared_manifest_lines(records: List[Record], purpose: str) -> List[str]:
    """Build the cleared manifest lines for a passing set.

    Returns a header comment block followed by one cleared line per record.
    Lines are returned without trailing newlines so the caller controls the
    line terminator and byte-identical output stays under its control.
    """
    lines: List[str] = []
    lines.append("# corpuscustody cleared manifest")
    lines.append("# purpose: {0}".format(purpose))
    lines.append("# record_id | spdx_id | cleared_for")
    for record in records:
        lic = resolve(record.spdx_id)
        lines.append(
            "{0} | {1} | {2}".format(record.record_id, lic.spdx_id, purpose)
        )
    return lines


def write_cleared_manifest(path: str, records: List[Record], purpose: str) -> None:
    """Write a cleared manifest to disk with LF line endings.

    Uses a fixed "\\n" terminator regardless of platform so identical input
    produces byte-identical output.
    """
    body = "\n".join(cleared_manifest_lines(records, purpose)) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(body)
